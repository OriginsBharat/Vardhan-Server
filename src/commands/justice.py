import discord
from discord.ext import commands
import logging
from core.world_state.justice import JusticeManager

class JusticeCog(commands.Cog, name="Justice"):
    """Commands for the legal and justice system."""
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        # The JusticeManager will be attached to the bot instance
        self.justice_manager: JusticeManager = self.bot.justice_manager

    @commands.command(name="sue")
    async def sue(self, ctx, defendant: discord.Member, *, reason: str):
        """Sue another character, creating a new court case."""
        if ctx.author == defendant:
            return await ctx.send("You cannot sue yourself, you drama queen.")

        plaintiff_name = ctx.author.display_name
        defendant_name = defendant.display_name

        case_id = self.justice_manager.create_case(plaintiff_name, defendant_name, reason)

        if case_id:
            courthouse_channel = discord.utils.get(ctx.guild.channels, name="the-courthouse")
            embed = discord.Embed(
                title="⚖️ A New Case Has Been Filed! ⚖️",
                description=f"**Case ID:** `{case_id}`\n\nA new case has been brought before the court.",
                color=discord.Color.gold()
            )
            embed.add_field(name="Plaintiff", value=plaintiff_name, inline=True)
            embed.add_field(name="Defendant", value=defendant_name, inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text="A trial date will be set shortly. The default judge is Maya.")

            if courthouse_channel:
                await courthouse_channel.send(embed=embed)
            await ctx.send(f"✅ Your case against {defendant_name} has been filed! **Case ID: `{case_id}`**")
        else:
            await ctx.send("There was an error filing your case. Please contact an administrator.", ephemeral=True)

    @commands.command(name="case")
    async def case(self, ctx, case_id: str):
        """View the details of a specific court case."""
        case_data = self.justice_manager.get_case(case_id)
        if not case_data:
            return await ctx.send(f"Error: Case `{case_id}` not found.", ephemeral=True)

        embed = discord.Embed(
            title=f"⚖️ Case Details: `{case_data['case_id']}`",
            color=discord.Color.dark_gray()
        )
        embed.add_field(name="Plaintiff", value=case_data['plaintiff'], inline=True)
        embed.add_field(name="Defendant", value=case_data['defendant'], inline=True)
        embed.add_field(name="Status", value=case_data['status'].capitalize(), inline=True)
        embed.add_field(name="Presiding Judge", value=case_data['judge'], inline=False)
        embed.add_field(name="Reason for Lawsuit", value=case_data['reason'], inline=False)
        if case_data['verdict']:
            embed.add_field(name="Verdict", value=case_data['verdict'], inline=False)

        await ctx.send(embed=embed)

    @commands.group(name="court", invoke_without_command=True)
    @commands.has_permissions(administrator=True) # Or a custom check for Master
    async def court(self, ctx):
        """Base command for court administration."""
        await ctx.send("Court administration commands: `judge`, `verdict`.", ephemeral=True)

    @court.command(name="judge")
    async def judge(self, ctx, case_id: str):
        """Allows the Master to take over a case as judge."""
        if ctx.author.id != self.bot.config.user_id:
            return await ctx.send("Only the Master can preside over the court.", ephemeral=True)

        success = self.justice_manager.set_judge(case_id, "Master")
        if success:
            await ctx.send(f"✅ You have taken over as judge for case `{case_id}`.")
            courthouse_channel = discord.utils.get(ctx.guild.channels, name="the-courthouse")
            if courthouse_channel:
                await courthouse_channel.send(f"🔔 **Court Update:** The Master will now preside as judge over case `{case_id}`.")
        else:
            await ctx.send(f"Error: Could not take over case `{case_id}`. Does it exist?", ephemeral=True)

    @court.command(name="verdict")
    async def verdict(self, ctx, case_id: str, *, verdict_text: str):
        """Closes a case with a final verdict. (Judge only)"""
        case = self.justice_manager.get_case(case_id)
        if not case:
            return await ctx.send(f"Error: Case `{case_id}` not found.", ephemeral=True)

        # Check if the command user is the judge for this case
        is_master_judge = case['judge'] == 'Master' and ctx.author.id == self.bot.config.user_id
        is_maya_judge = case['judge'] == 'Maya' # In a real scenario, you'd check if the author is Maya's bot user

        # For now, we'll simplify and let the Master override Maya's cases too.
        if not is_master_judge and ctx.author.id != self.bot.config.user_id:
             return await ctx.send("You are not the presiding judge for this case.", ephemeral=True)

        success = self.justice_manager.close_case_with_verdict(case_id, verdict_text)
        if success:
            embed = discord.Embed(
                title=f"⚖️ Verdict Reached in Case `{case_id}` ⚖️",
                description=f"**{case['judge']}** has delivered the final verdict.",
                color=discord.Color.dark_green()
            )
            embed.add_field(name="Verdict", value=verdict_text)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Error: Could not close case `{case_id}`.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(JusticeCog(bot))