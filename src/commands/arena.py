import discord
from discord.ext import commands
import logging
from typing import Dict, Any

class ArenaCog(commands.Cog, name="Arena"):
    """Commands for duels and combat in the Arena of Souls."""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.pending_duels: Dict[str, Any] = {} # opponent_id -> {challenger, duel_id}

    async def cog_check(self, ctx):
        """Checks if the command is used in the arena channel."""
        is_correct_channel = ctx.channel.name == "the-coliseum"
        if not is_correct_channel:
            try:
                await ctx.message.delete()
                await ctx.author.send("Blood and glory belong in #the-coliseum, not here.", ephemeral=True)
            except (discord.Forbidden, discord.HTTPException):
                pass
        return is_correct_channel

    @commands.command(name="challenge")
    async def challenge(self, ctx, opponent: discord.Member):
        """Challenge another character to a duel to the death (or humiliation)."""
        if ctx.author == opponent:
            return await ctx.send("You cannot challenge yourself to a duel. Find your courage elsewhere.")

        challenger_name = ctx.author.display_name
        opponent_name = opponent.display_name

        duel_id = self.bot.arena_manager.create_duel(challenger_name, opponent_name)
        if not duel_id:
            return await ctx.send("Failed to create the duel. The arena master may be busy.", ephemeral=True)

        self.pending_duels[str(opponent.id)] = {"challenger": ctx.author, "duel_id": duel_id}

        embed = discord.Embed(
            title="⚔️ A Challenge Has Been Issued! ⚔️",
            description=f"**{challenger_name}** has challenged **{opponent_name}** to a duel in the Arena of Souls!",
            color=discord.Color.dark_red()
        )
        embed.set_footer(text=f"Duel ID: {duel_id}\n{opponent_name}, use !accept to answer the call to glory or shame.")
        await ctx.send(content=opponent.mention, embed=embed)
        self.bot.narrative_manager.log_event(f"{challenger_name} has challenged {opponent_name} to a duel.", "major")

    @commands.command(name="accept")
    async def accept(self, ctx):
        """Accept a pending duel challenge."""
        challenge = self.pending_duels.get(str(ctx.author.id))
        if not challenge:
            return await ctx.send("You have no pending challenges to accept.")

        duel_id = challenge['duel_id']
        challenger = challenge['challenger']

        await ctx.send(f"**{ctx.author.display_name}** accepts the challenge from **{challenger.display_name}**! Let the duel begin! (Duel ID: `{duel_id}`)\n\n*The Master will declare the winner.*")
        self.bot.narrative_manager.log_event(f"{ctx.author.display_name} accepted {challenger.display_name}'s duel challenge.", "major")

        del self.pending_duels[str(ctx.author.id)]

    @commands.command(name="declare_winner")
    async def declare_winner(self, ctx, duel_id: str, winner: discord.Member):
        """Declare the winner of a duel. (Master only)"""
        if ctx.author.id != self.bot.config.user_id:
            return await ctx.send("Only the Master can declare the outcome of a duel.", ephemeral=True)

        duel = self.bot.arena_manager.get_duel(duel_id)
        if not duel or duel['status'] != 'pending':
            return await ctx.send(f"Error: Duel `{duel_id}` not found or has already concluded.", ephemeral=True)

        winner_name = winner.display_name

        if winner_name == duel['challenger_name']:
            loser_name = duel['opponent_name']
        elif winner_name == duel['opponent_name']:
            loser_name = duel['challenger_name']
        else:
            return await ctx.send(f"Error: {winner_name} was not a participant in duel `{duel_id}`.", ephemeral=True)

        self.bot.arena_manager.resolve_duel(duel_id, winner_name, loser_name)

        embed = discord.Embed(
            title=f"🏆 Duel Concluded - {winner_name} is Victorious! 🏆",
            description=f"The duel between **{duel['challenger_name']}** and **{duel['opponent_name']}** has ended.\n\n**{winner_name}** stands triumphant, while **{loser_name}** has been publicy defeated and scarred by humiliation.",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Duel ID: {duel_id}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ArenaCog(bot))