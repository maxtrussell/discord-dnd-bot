import logging
import os
import random
import re

import discord
import requests

logging.basicConfig(
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s [%(levelname)s] [%(filename)s@%(lineno)s]: %(message)s',
)
logging.getLogger().setLevel(logging.INFO)

async def usage(message):
    response = (
        "Usage: dndbot [COMMAND]\n"
        "Options:\n"
        "\t- ping: pings the dndbot\n"
        "\t- roll: rolls dice (d20, 8d6, etc.)"
    )
    await message.channel.send(response)

async def ping(message):
    await message.channel.send('Pong!')  # TODO: temp

async def roll(message):
    tokens = message.content.split(' ')
    if len(tokens) != 3:
        await message.channel.send('dndbot roll takes 1 argument. E.g. dndbot roll d20')
        return

    pattern = re.compile('^(\d*)d(\d+)(([+-])(\d+))?$')
    match = pattern.match(tokens[2])
    if match == None:
        await message.channel.send(
            'Roll command must match format "^(\d*)d(\d+)(([+-])(\d+))?$", '
            'alternatively some examples for humans:\n'
            '- d20\n'
            '- 3d8\n'
            '- 2d6+1\n'
            '- 2d6-1'
        )
        return

    # Get number of die
    num_die = 1
    if match.group(1):
        num_die = int(match.group(1))

    # Get sides per die
    sides = int(match.group(2))

    # Get modifier
    operator, modifier = None, None
    if match.group(4):
        operator = match.group(4)
        modifier = int(match.group(5))

    # Roll the die!
    rolls = [random.randint(1, sides) for _ in range(num_die)]
    total = sum(rolls)
    response = f'{match.group(0)} yields {rolls}'
    if operator:
        if operator == '+':
            total += modifier
        elif operator == '-':
            total -= modifier
        response += f' {operator} {modifier}'
    response += f' = {total}'

    await message.channel.send(response)


class MyClient(discord.Client):

    commands = {
        'ping': ping,
        'roll': roll,
        'usage': usage,
    }

    async def on_ready(self):
        logging.info(f'Logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user or not message.content.startswith('dndbot'):
            return

        # Received message intended for bot, parse command
        logging.info(f'Message from {message.author}: {message.content}')
        tokens = message.content.split(' ')
        if len(tokens) < 2 or tokens[1] not in self.commands:
            await usage(message)
        else:
            await self.commands[tokens[1]](message)


def main():
    client = MyClient()
    token = os.getenv("DISCORD_TOKEN")
    client.run(token)
        
if __name__ == '__main__':
    main()
