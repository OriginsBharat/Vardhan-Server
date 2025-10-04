# src/core/economic_system/auction_house.py
# Manages the auction system for high-value items and services.

import asyncio
import logging
import discord
from datetime import datetime, timedelta
from typing import List, Optional

from src.config import Config
from src.core.economic_system.economy_manager import EconomyManager
from src.utils.discord_utils import create_embed

class Auction:
    """Represents a single active auction, tracking its state and Discord message."""
    def __init__(self, auction_id: int, item_name: str, description: str, seller_id: int, starting_bid: float, duration_hours: float, channel_id: int):
        self.auction_id = auction_id
        self.item_name = item_name
        self.description = description
        self.seller_id = seller_id
        self.highest_bid = starting_bid
        self.highest_bidder_id: Optional[int] = None
        self.end_time = datetime.now() + timedelta(hours=duration_hours)
        self.channel_id = channel_id
        self.message_id: Optional[int] = None
        self.active = True

    def place_bid(self, bidder_id: int, bid_amount: float) -> bool:
        """Places a new bid on the auction. Returns True if successful."""
        if bid_amount > self.highest_bid:
            self.highest_bid = bid_amount
            self.highest_bidder_id = bidder_id
            return True
        return False

class AuctionHouse:
    """Manages all active auctions, including their creation, bidding, and finalization."""
    def __init__(self, config: Config, economy_manager: EconomyManager, client: discord.Client):
        self.config = config
        self.economy_manager = economy_manager
        self.client = client
        self.auctions: List[Auction] = []
        self._next_auction_id = 1
        self._loop_task: Optional[asyncio.Task] = None
        logging.info("AuctionHouse initialized.")

    def start_loop(self):
        """Starts the background loop to check for finished auctions."""
        if self._loop_task is None or self._loop_task.done():
            self._loop_task = asyncio.create_task(self._run_auction_loop())
            logging.info("AuctionHouse background loop started.")

    async def create_auction(self, item_name: str, description: str, seller_id: int, starting_bid: float, duration_hours: float) -> Optional[Auction]:
        """Creates a new auction, posts it to Discord, and adds it to the active list."""
        channel_id = self.config.DISCORD_AUCTION_CHANNEL_ID
        auction = Auction(self._next_auction_id, item_name, description, seller_id, starting_bid, duration_hours, channel_id)
        self._next_auction_id += 1

        channel = self.client.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            logging.error(f"Cannot create auction: Channel ID {channel_id} is not a valid text channel.")
            return None

        embed = self._create_auction_embed(auction)
        try:
            message = await channel.send(embed=embed)
            auction.message_id = message.id
            self.auctions.append(auction)
            logging.info(f"Auction #{auction.auction_id} for '{item_name}' created successfully.")
            return auction
        except (discord.Forbidden, discord.HTTPException) as e:
            logging.error(f"Failed to post auction message in channel {channel_id}: {e}")
            return None

    async def place_bid(self, auction_id: int, bidder_id: int, bid_amount: float) -> bool:
        """Processes a bid on an active auction."""
        auction = next((a for a in self.auctions if a.auction_id == auction_id and a.active), None)
        if not auction: return False

        if bidder_id == auction.seller_id: return False # Can't bid on your own auction

        if self.economy_manager.get_balance(bidder_id) < bid_amount: return False

        if auction.place_bid(bidder_id, bid_amount):
            await self._update_auction_message(auction)
            return True
        return False

    async def _run_auction_loop(self):
        """Periodically checks for and ends finished auctions."""
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            for auction in list(self.auctions):
                if auction.active and datetime.now() >= auction.end_time:
                    await self._finalize_auction(auction)
            await asyncio.sleep(30)

    async def _finalize_auction(self, auction: Auction):
        """Finalizes an auction, transferring funds and notifying users."""
        auction.active = False
        logging.info(f"Finalizing auction #{auction.auction_id} for '{auction.item_name}'.")

        result_text = f"The auction for **{auction.item_name}** has ended!\n"
        if auction.highest_bidder_id:
            success = self.economy_manager.make_transaction(
                from_user_id=auction.highest_bidder_id,
                to_user_id=auction.seller_id,
                amount=auction.highest_bid,
                description=f"Auction Win: {auction.item_name}"
            )
            if success:
                result_text += f"Congratulations to <@{auction.highest_bidder_id}> for winning with a bid of **{auction.highest_bid} Rs**!"
            else:
                result_text += "The final bid could not be processed due to a transaction error."
        else:
            result_text += "The auction ended with no bids."

        embed = self._create_auction_embed(auction, finished=True, result_text=result_text)
        await self._update_auction_message(auction, embed=embed)
        self.auctions.remove(auction)

    def _create_auction_embed(self, auction: Auction, finished: bool = False, result_text: str = "") -> discord.Embed:
        """Creates a standardized Discord embed for an auction."""
        status = "Finished" if finished else "Active"
        color = discord.Color.dark_red() if finished else discord.Color.dark_green()
        title = f"Auction {status}: {auction.item_name}"

        embed = create_embed(title=title, description=auction.description, color=color)
        embed.add_field(name="Seller", value=f"<@{auction.seller_id}>", inline=True)
        embed.add_field(name="Current Bid", value=f"**{auction.highest_bid} Rs**", inline=True)

        if auction.highest_bidder_id:
            embed.add_field(name="Highest Bidder", value=f"<@{auction.highest_bidder_id}>", inline=True)
        else:
            embed.add_field(name="Highest Bidder", value="None yet", inline=True)

        if not finished:
            embed.set_footer(text=f"Auction ends at {auction.end_time.strftime('%Y-%m-%d %H:%M')} UTC | ID: {auction.auction_id}")
        else:
            embed.add_field(name="Result", value=result_text, inline=False)
            embed.set_footer(text=f"Auction ID: {auction.auction_id}")

        return embed

    async def _update_auction_message(self, auction: Auction, embed: Optional[discord.Embed] = None):
        """Updates the Discord message for an auction."""
        channel = self.client.get_channel(auction.channel_id)
        if not isinstance(channel, discord.TextChannel) or not auction.message_id: return

        try:
            message = await channel.fetch_message(auction.message_id)
            if not embed:
                embed = self._create_auction_embed(auction)
            await message.edit(embed=embed)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
            logging.warning(f"Could not update auction message {auction.message_id}: {e}")