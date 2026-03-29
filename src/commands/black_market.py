import discord
from discord.ext import commands
import logging

class BlackMarketCog(commands.Cog, name="Black Market"):
    """Commands for the illicit black market."""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    async def cog_check(self, ctx):
        """Checks if the command is used in the black market channel."""
        is_correct_channel = ctx.channel.name == "the-black-market"
        if not is_correct_channel:
            try:
                await ctx.message.delete()
                await ctx.author.send("Psst... Black market commands can only be used in the #the-black-market channel.")
            except (discord.Forbidden, discord.HTTPException):
                pass # Can't delete or DM, just fail silently.
        return is_correct_channel

    @commands.group(name="bm", invoke_without_command=True)
    async def bm(self, ctx):
        """Base command for the Black Market. Shows available listings."""
        await self.list(ctx)

    @bm.command(name="list")
    async def list(self, ctx):
        """Lists all available items on the black market."""
        listings = self.bot.black_market_manager.get_all_listings()
        if not listings:
            return await ctx.send("*The shadows are quiet. Nothing is for sale.*")

        embed = discord.Embed(
            title=" clandestine Wares",
            description="Whispers in the dark offer the following goods...",
            color=discord.Color.purple()
        )
        for listing in listings:
            embed.add_field(
                name=f"{listing['item_name']} - `{listing['price']}` Rs",
                value=f"ID: `{listing['listing_id']}` | Seller: {listing['seller_name']}\n> {listing['item_description']}",
                inline=False
            )
        embed.set_footer(text="Use !bm buy <listing_id> to purchase an item.")
        await ctx.send(embed=embed)

    @bm.command(name="sell")
    async def sell(self, ctx, price: int, item_name: str, *, description: str):
        """Puts an item up for sale on the black market. Only Sapt can use this command."""
        if price <= 0:
            return await ctx.send("You must set a price greater than zero.")

        # Sapt is the only one who can sell on the black market.
        if ctx.author.display_name != "Sapt":
            return await ctx.send("Only Sapt has the connections to sell goods in the shadows.", ephemeral=True)

        seller_name = ctx.author.display_name
        listing_id = self.bot.black_market_manager.create_listing(seller_name, item_name, description, price)

        if listing_id:
            await ctx.send(f"Your offer has been whispered into the shadows. **Listing ID: `{listing_id}`**")
            self.bot.narrative_manager.log_event(
                f"{seller_name} listed '{item_name}' on the black market for {price} Rs.",
                level="normal"
            )
        else:
            await ctx.send("The shadows reject your offer. The listing could not be created.", ephemeral=True)

    @bm.command(name="buy")
    async def buy(self, ctx, listing_id: str):
        """Buys an item from the black market."""
        listing = self.bot.black_market_manager.get_listing(listing_id)
        if not listing:
            return await ctx.send("This item is no longer available or the ID is incorrect.", ephemeral=True)

        buyer_name = ctx.author.display_name
        if buyer_name == listing['seller_name']:
            return await ctx.send("You cannot buy your own item.", ephemeral=True)

        success = self.bot.black_market_manager.purchase(listing_id, buyer_name)

        if success:
            await ctx.send(f"The deal is done. You have acquired **{listing['item_name']}** from {listing['seller_name']} for `{listing['price']}` Rs.")
            self.bot.narrative_manager.log_event(
                f"{buyer_name} purchased '{listing['item_name']}' from {listing['seller_name']} on the black market.",
                level="major"
            )
        else:
            await ctx.send("The transaction failed. Do you have the coin for such wares?", ephemeral=True)

async def setup(bot):
    # The World Architect in bot.py now ensures the channel exists, so we can load this directly.
    await bot.add_cog(BlackMarketCog(bot))