from pymongo import MongoClient
import discord
from discord.ext import commands
import random

# MongoDB setup
client = MongoClient("mongodb+srv://siresirol937:t8gY9FXLV3JcfQ4P@cluster0.rabuteq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["mcscanner"]
collection = db["servers"]

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(title="📘 Available Commands", color=discord.Color.blue())
    embed.add_field(name="!help", value="Show this help message", inline=False)
    embed.add_field(name="!random", value="Get 10 random Minecraft servers", inline=False)
    embed.add_field(name="!find <version> [type]", value="Find servers by version and optional type (e.g., paper, vanilla)", inline=False)
    embed.add_field(name="!count", value="Show total number of servers in the database", inline=False)
    embed.add_field(name="!top", value="Show 10 servers with the most players", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="random")
async def random_servers(ctx):
    servers = list(collection.aggregate([{"$sample": {"size": 10}}]))
    if not servers:
        await ctx.send("No servers found.")
        return

    embed = discord.Embed(title="🎲 Random Minecraft Servers", color=discord.Color.green())
    for s in servers:
        players = s.get('players', 'N/A')
        embed.add_field(
            name=f"{s['ip']}:{s['port']}",
            value=f"**Version:** {s.get('version', 'N/A')}\n**Players:** {players}\n**Type:** {s.get('description', 'N/A')}",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command(name="find")
async def find_servers(ctx, version: str, type_filter: str = None):
    query = {
        "version": {"$regex": version, "$options": "i"}
    }

    if type_filter:
        query["description"] = {"$regex": type_filter, "$options": "i"}

    servers = list(collection.find(query).limit(10))

    if not servers:
        await ctx.send("No matching servers found.")
        return

    embed = discord.Embed(title=f"🔍 Results for `{version}`", color=discord.Color.orange())
    for s in servers:
        players = s.get('players', 'N/A')
        embed.add_field(
            name=f"{s['ip']}:{s['port']}",
            value=f"**Version:** {s.get('version', 'N/A')}\n**Players:** {players}\n**Type:** {s.get('description', 'N/A')}",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command(name="count")
async def count_servers(ctx):
    count = collection.count_documents({})
    embed = discord.Embed(title="📊 Server Count", description=f"Total Minecraft Servers in DB: **{count}**", color=discord.Color.purple())
    await ctx.send(embed=embed)

@bot.command(name="top")
async def top_servers(ctx):
    servers = list(collection.find().limit(500))

    def get_online(s):
        try:
            raw = s.get("players", "")
            online = int(str(raw).split("online=")[1].split(",")[0])
            return online
        except:
            return 0

    top = sorted(servers, key=get_online, reverse=True)[:10]
    if not top:
        await ctx.send("No player data available.")
        return

    embed = discord.Embed(title="🏆 Top Servers by Players", color=discord.Color.gold())
    for s in top:
        players = s.get('players', 'N/A')
        embed.add_field(
            name=f"{s['ip']}:{s['port']}",
            value=f"**Players:** {players}\n**Version:** {s.get('version', 'N/A')}\n**Type:** {s.get('description', 'N/A')}",
            inline=False
        )
    await ctx.send(embed=embed)

bot.run("TOKEN BE PLACED IN HERE DAWG")
