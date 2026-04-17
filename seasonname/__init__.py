from .seasonname import SeasonName

async def setup(bot):
    await bot.add_cog(SeasonName(bot))
