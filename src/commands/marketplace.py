import discord
from discord.ext import commands
import logging

class MarketplaceCog(commands.Cog, name="Marketplace"):
    """Commands for the Living Marketplace and bot-to-bot contracts."""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    async def cog_check(self, ctx):
        """Checks if the command is used in the job board channel."""
        return ctx.channel.name == "job-board"

    @commands.group(name="contract", invoke_without_command=True)
    async def contract(self, ctx):
        """Base command for contracts. Use `!contract post` or `!contract list`."""
        await self.list(ctx)

    @contract.command(name="list")
    async def list(self, ctx):
        """Lists all open contracts on the job board."""
        open_contracts = self.bot.contract_manager.get_open_contracts()
        if not open_contracts:
            return await ctx.send("*The job board is currently empty. No contracts are available.*")

        embed = discord.Embed(
            title="📜 Open Contracts on the Job Board",
            description="The following tasks are available for any enterprising individual.",
            color=discord.Color.dark_teal()
        )
        for contract in open_contracts:
            embed.add_field(
                name=f"Contract ID: `{contract['contract_id']}` | Reward: `{contract['reward']}` Rs",
                value=f"**Client:** {contract['client_name']}\n**Task:** {contract['task_description']}",
                inline=False
            )
        embed.set_footer(text="Use !contract accept <contract_id> to take on a job.")
        await ctx.send(embed=embed)

    @contract.command(name="post")
    async def post(self, ctx, reward: int, *, task_description: str):
        """Posts a new contract to the job board."""
        if reward <= 0:
            return await ctx.send("You must offer a reward greater than zero.")

        client_name = ctx.author.display_name

        # Check balance before posting
        balance = self.bot.economy_manager.get_balance(client_name)
        if balance < reward and client_name.lower() != "master":
             return await ctx.send(f"You cannot afford to post this contract. You only have `{balance}` Rs.")

        contract_id = self.bot.contract_manager.create_contract(client_name, task_description, reward)
        if contract_id:
            await ctx.send(f"✅ Your contract has been posted to the job board! **Contract ID: `{contract_id}`**")
            self.bot.narrative_manager.log_event(
                f"{client_name} posted a new contract for '{task_description[:50]}...' with a reward of {reward} Rs.",
                level="normal"
            )
        else:
            await ctx.send("The contract could not be posted. The funds could not be secured in escrow.", ephemeral=True)

    @contract.command(name="accept")
    async def accept(self, ctx, contract_id: str):
        """Accepts an open contract."""
        contractor_name = ctx.author.display_name

        success = self.bot.contract_manager.accept_contract(contract_id, contractor_name)
        if success:
            await ctx.send(f"✅ You have accepted contract `{contract_id}`. Get to work!")
            self.bot.narrative_manager.log_event(f"{contractor_name} has accepted contract `{contract_id}`.", "normal")
        else:
            await ctx.send(f"Failed to accept contract `{contract_id}`. It may have already been taken or does not exist.", ephemeral=True)

    @contract.command(name="complete")
    async def complete(self, ctx, contract_id: str):
        """Marks a contract you have accepted as complete to receive payment."""
        contractor_name = ctx.author.display_name

        success = self.bot.contract_manager.complete_contract(contract_id, contractor_name)
        if success:
            await ctx.send(f"🎉 Congratulations! You have completed contract `{contract_id}` and received your payment.")
            self.bot.narrative_manager.log_event(f"{contractor_name} has successfully completed contract `{contract_id}`.", "major")
        else:
            await ctx.send(f"Failed to complete contract `{contract_id}`. Are you the assigned contractor, and have you truly finished the task?", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MarketplaceCog(bot))