import os
import discord
from discord.ext import commands
import requests
import json
from flask import Flask
from threading import Thread

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    await bot.change_presence(activity=discord.Game(name=".get <url>"))

@bot.command(name='get')
async def get_request(ctx, *, url=None):
    if not url:
        await ctx.send("Usage: `.get <url>`")
        return
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    loading_msg = await ctx.send("Processing...")
    
    try:
        response = requests.get(url, timeout=10)
        
        embed = discord.Embed(title="GET Request", color=0x00ff00)
        embed.add_field(name="URL", value=url, inline=False)
        embed.add_field(name="Status", value=response.status_code, inline=True)
        
        content_type = response.headers.get('content-type', 'unknown')
        
        if 'application/json' in content_type:
            try:
                data = response.json()
                text = json.dumps(data, indent=2)[:500]
                embed.add_field(name="Response", value=f"```json\n{text}\n```", inline=False)
            except:
                embed.add_field(name="Response", value=f"```\n{response.text[:500]}\n```", inline=False)
        elif 'text/' in content_type:
            embed.add_field(name="Response", value=f"```\n{response.text[:500]}\n```", inline=False)
        else:
            embed.add_field(name="Data", value=f"Binary data ({len(response.content)} bytes)", inline=False)
        
        await loading_msg.edit(content=None, embed=embed)
        
    except requests.exceptions.Timeout:
        await loading_msg.edit(content="Request timeout")
    except requests.exceptions.ConnectionError:
        await loading_msg.edit(content="Connection error")
    except Exception as e:
        await loading_msg.edit(content=f"Error: {str(e)}")

keep_alive()
bot.run(os.environ['DISCORD_TOKEN'])