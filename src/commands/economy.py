import discord
from discord.ext import commands
import logging
import uuid

class EconomyCog(commands.Cog, name="Economy"):
    """Commands for all economic activities."""
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.pending_loans = {} # A simple in-memory store for loan requests: {request_id: data}

    @commands.command(name="balance", aliases=["bal"])
    async def balance(self, ctx, member: discord.Member = None):
        """Checks your or another user's balance."""
        target_user = member or ctx.author
        balance = self.bot.economy_manager.get_balance(target_user.display_name)
        await ctx.send(f"💰 **{target_user.display_name}**'s balance is `{balance}` Rs.")

    @commands.command(name="give")
    async def give(self, ctx, recipient: discord.Member, amount: int):
        """Gives a certain amount of Rs to another user."""
        if amount <= 0:
            return await ctx.send("You must give a positive amount.")
        if recipient == ctx.author:
            return await ctx.send("You can't give money to yourself.")

        sender_name = ctx.author.display_name
        recipient_name = recipient.display_name

        success = self.bot.economy_manager.transaction(sender_name, recipient_name, amount)
        if success:
            await ctx.send(f"💸 You have given `{amount}` Rs to **{recipient_name}**.")
        else:
            await ctx.send("Transaction failed. You may not have enough funds.")

    @commands.command(name="request_loan")
    async def request_loan(self, ctx, amount: int, interest_rate: float, duration_days: int):
        """Request a loan from the bank or other users in #bank-of-vardhan."""
        if ctx.channel.name != "bank-of-vardhan":
            return await ctx.send("Loan requests can only be made in the #bank-of-vardhan channel.", ephemeral=True)
        if not (amount > 0 and interest_rate >= 0 and duration_days > 0):
            return await ctx.send("All loan parameters must be positive numbers.", ephemeral=True)

        request_id = str(uuid.uuid4())[:6]

        embed = discord.Embed(
            title="🏦 New Loan Request",
            description=f"A new loan has been requested by **{ctx.author.display_name}**.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Amount Requested", value=f"`{amount}` Rs", inline=True)
        embed.add_field(name="Interest Rate", value=f"`{interest_rate}%`", inline=True)
        embed.add_field(name="Duration", value=f"`{duration_days}` days", inline=True)
        embed.set_footer(text=f"Request ID: {request_id}\nUse !grant_loan {request_id} to fund this loan.")

        msg = await ctx.send(embed=embed)

        self.pending_loans[request_id] = {
            "requester_id": ctx.author.id,
            "requester_name": ctx.author.display_name,
            "amount": amount,
            "interest_rate": interest_rate,
            "duration_days": duration_days,
            "message_id": msg.id,
            "channel_id": ctx.channel.id
        }

    @commands.command(name="grant_loan")
    async def grant_loan(self, ctx, request_id: str):
        """Grant a pending loan request."""
        if request_id not in self.pending_loans:
            return await ctx.send(f"Error: Loan request with ID `{request_id}` not found or already fulfilled.", ephemeral=True)

        loan_request = self.pending_loans[request_id]

        if ctx.author.id == loan_request['requester_id']:
            return await ctx.send("You cannot grant your own loan request.", ephemeral=True)

        loan_id = self.bot.loan_manager.create_loan(
            lender=ctx.author.display_name,
            borrower=loan_request['requester_name'],
            amount=loan_request['amount'],
            interest=loan_request['interest_rate'],
            duration_days=loan_request['duration_days']
        )

        if loan_id:
            await ctx.send(f"✅ You have successfully granted the loan to **{loan_request['requester_name']}**. Loan ID: `{loan_id}`")

            # Update the original message
            try:
                channel = self.bot.get_channel(loan_request['channel_id'])
                original_msg = await channel.fetch_message(loan_request['message_id'])
                if original_msg:
                    embed = original_msg.embeds[0]
                    embed.title = "✅ Loan Granted"
                    embed.description = f"This loan was granted by **{ctx.author.display_name}**."
                    embed.color = discord.Color.green()
                    await original_msg.edit(embed=embed)
            except Exception as e:
                self.logger.error(f"Could not edit original loan request message: {e}")

            del self.pending_loans[request_id]
        else:
            await ctx.send("Failed to grant the loan. You may not have sufficient funds.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(EconomyCog(bot))