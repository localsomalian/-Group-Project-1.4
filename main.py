import discord
import json
import random
import requests
from discord.ext import tasks

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Global variables
user_scores = {}
trivia_question = ""
trivia_answer = ""
trivia_options = []

# Fetch trivia question from API
def fetch_trivia():
    url = "https://opentdb.com/api.php?amount=1&type=multiple"
    response = requests.get(url).json()
    question_data = response['results'][0]
    question = question_data['question']
    answer = question_data['correct_answer']
    options = question_data['incorrect_answers'] + [answer]
    random.shuffle(options)
    return question, answer, options

# Load and save scores from/to JSON file
def load_scores():
    global user_scores
    try:
        with open('scores.json', 'r') as file:
            user_scores = json.load(file)
    except FileNotFoundError:
        user_scores = {}

def save_scores():
    with open('scores.json', 'w') as file:
        json.dump(user_scores, file)

# Event when the bot is ready
@client.event
async def on_ready():
    load_scores()
    print(f"Logged in as {client.user}")
    
    daily_trivia.start()

# Event when a message is received
@client.event
async def on_message(message):
    global trivia_question, trivia_answer, trivia_options

    if message.author == client.user:
        return  # Prevent bot from responding to itself

  
   # !help command
    if message.content.startswith('!help'):
        help_text = """
**Welcome to the Trivia Bot! Here are the available commands:**

1. **!trivia** - Start a new trivia question. The bot will send you a question and options to choose from.
2. **!answer [your answer]** - Answer the current trivia question. Make sure to type the exact answer.
3. **!leaderboard** - View the leaderboard with all players' scores.
4. **!hint** - Get a hint for the current trivia question. This will list the available options again.
5. **!help** - Displays this help message with the list of commands.

Have fun, and good luck with the trivia! 🎉
        """
        embed = discord.Embed(
            title="**Trivia Bot Help**",
            description=help_text,
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)
  

  
    # !trivia command
    if message.content.startswith('!trivia'):
        trivia_question, trivia_answer, trivia_options = fetch_trivia()
        options_str = ', '.join(trivia_options)
        
        # Creating an embed for the trivia question
        embed = discord.Embed(
            title="**Trivia Question**",
            description=trivia_question,
            color=discord.Color.purple()
        )
        embed.add_field(name="Options", value=options_str, inline=False)
        await message.channel.send(embed=embed)

    # !answer command
    elif message.content.startswith('!answer'):
        user_answer = message.content[len('!answer '):].strip()
        if user_answer.lower() == trivia_answer.lower():
            user_scores[message.author.name] = user_scores.get(message.author.name, 0) + 1
            save_scores()

            # Creating an embed for the correct answer
            embed = discord.Embed(
                title="Correct Answer!",
                description=f"{message.author.mention} got it right!",
                color=discord.Color.green()
            )
            await message.channel.send(embed=embed)
        else:
            # Creating an embed for the incorrect answer
            embed = discord.Embed(
                title="Incorrect Answer",
                description=f"Wrong! The correct answer was: {trivia_answer}",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)

    # !leaderboard command
    elif message.content.startswith('!leaderboard'):
        if user_scores:
            leaderboard = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
            leaderboard_msg = "\n".join([f"{user}: {score}" for user, score in leaderboard])

            # Creating an embed for the leaderboard
            embed = discord.Embed(
                title="Leaderboard",
                description=leaderboard_msg,
                color=discord.Color.purple()
            )
            await message.channel.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Leaderboard",
                description="No scores yet!",
                color=discord.Color.orange()
            )
            await message.channel.send(embed=embed)

    # !hint command
    elif message.content.startswith('!hint'):
        # Creating an embed for the hint
        embed = discord.Embed(
            title="Hint",
            description=f"Hint: The correct answer is one of these options: {', '.join(trivia_options)}",
            color=discord.Color.gold()
        )
        await message.channel.send(embed=embed)

# Automatically post trivia question daily
@tasks.loop(hours=24)
async def daily_trivia():
    channel = client.get_channel("Your Channel ID")  # remove the "" and Replace with your channel ID
    trivia_question, trivia_answer, trivia_options = fetch_trivia()

    # Creating an embed for the daily trivia question
    embed = discord.Embed(
        title="**Daily Trivia Question**",
        description=trivia_question,
        color=discord.Color.blue()
    )
    embed.add_field(name="Options", value=', '.join(trivia_options), inline=False)
    await channel.send(embed=embed)

# Run the bot (use your bot token here directly)
client.run("YOUR BOT TOKEN")  # Replace with your bot token
