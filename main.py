from asyncio import set_event_loop_policy
from importlib import reload as reload_lib
from logging import getLogger, FileHandler, Formatter, WARN
from os import listdir, walk
from sys import argv
from textwrap import indent
from time import time
from traceback import print_exc, format_exc, format_tb

import ujson as json
from aiohttp import ClientSession
from discord import Game, HTTPException, Embed, utils as dutils
from discord.abc import PrivateChannel
from discord.ext import commands
from pymongo import MongoClient
from redis import Redis
from uvloop import EventLoopPolicy

from modules.classes import utils, settings_entry, checks, language


PATH = argv[0].replace("/main.py", "")


# Load bot config
settings = json.load(open('settings.json', encoding='utf-8'))
default_settings = json.load(open('default_settings.json', encoding='utf-8'))

# Start Sentry and Mongo connections
mdb = MongoClient(settings.get('mongo')[0], settings.get('mongo')[1]).cirkeltrekbot

# Use UVLoop
set_event_loop_policy(EventLoopPolicy())

# Load strings into cache
languages = {}
for file in listdir('modules/languages'):
    if file.endswith('.json'):
        languages[file.replace('.json', '')] = json.load(open(f'modules/languages/{file}', 'r', encoding='utf-8'))

# Start Logging Functions
logger = getLogger()
logger.setLevel(WARN)
handler = FileHandler(filename=f'cluster{argv[2]}.log', encoding='utf-8', mode='w')
handler.setFormatter(Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class Bot(commands.AutoShardedBot):
    """Subclassing Bot because we do some different things here"""
    def __init__(self, command_prefix, description=None, **options):
        super().__init__(command_prefix, description=description, **options)
        self.utils = utils.Utilities(self)
        self.status_string = settings.get('status', '')
        self.settings_entry = self.utils.settings_entry
        self.default_settings = default_settings
        self.mongo = mdb
        self.langs = languages
        self.cluster_id = int(argv[2])
        self.cluster_count = int(argv[4])
        self.cluster_name = argv[5]
        self.redis = Redis(host=settings.get('redis')[0], port=settings.get('redis')[1], decode_responses=True)
        self.settings = settings

    def load_modules(self, action='load'):
        cogs = []
        for f in listdir(PATH + '/modules/events'):
            # Load invisible cogs
            direc = 'modules.events.'
            if not f.startswith('__') and not f.startswith('.'):
                name = f.replace('.py', '')
                if action == 'load':
                    try:
                        self.load_extension(direc + name)
                    except commands.ExtensionAlreadyLoaded:
                        continue
                elif action == 'unload':
                    self.unload_extension(direc + name)
                elif action == 'reload':
                    self.unload_extension(direc + name)
                    self.reload_extension(direc + name)
                cogs.append(direc + name)
        for x in walk(PATH + '/modules/commands', topdown=False):
            # Load command cogs
            for y in x[1]:
                if not y.startswith('__') and not file.startswith('.'):
                    direc = f'modules.commands.{y}.'
                    for f in listdir(PATH + f'/modules/commands/{y}'):
                        if not f.startswith('__'):
                            name = f.replace('.py', '')
                            if action == 'load':
                                try:
                                    self.load_extension(direc + name)
                                except commands.ExtensionAlreadyLoaded:
                                    continue
                            elif action == 'unload':
                                self.unload_extension(direc + name)
                            elif action == 'reload':
                                self.unload_extension(direc + name)
                                self.reload_extension(direc + name)
                            cogs.append(direc + name)
        return cogs

    async def on_connect(self):
        self.web = ClientSession(loop=self.loop, connector=self.http.connector)
        self.load_modules()

    async def on_message(self, message):
        if message.author.bot or isinstance(message.channel, PrivateChannel):
            return
        if bot.user in message.mentions:
            clean = message.clean_content
            content = clean.replace(f'@{message.guild.me.display_name}', '')
            if not content:
                entry = bot.settings_entry(message.guild.id)
                lang = bot.utils.get_language_by_name(entry.locale)
                await message.channel.send(lang['prefix'] % entry.prefix)
        await bot.process_commands(message)

    async def on_ready(self):
        await self.change_presence(activity=Game(name=self.status_string))
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        print('All cogs loaded')
        print('------')
        print('Statistics')
        print(f'Cluster: {self.cluster_name} ({self.cluster_id})')
        print(f'Guilds: {len(self.guilds)}')
        print(f'Shards: {self.shard_count}')
        print('------')
        print('Initialization Complete')


# Calculate range of shards that should be started
if int(argv[2]) != 0:
    shard_start = (int(argv[2]) * int(argv[1])) + 1
    shard_end = (int(argv[2]) + 1) * int(argv[1]) + 1
else:
    shard_start = int(argv[2]) * int(argv[1])
    shard_end = (int(argv[2]) + 1) * int(argv[1])

shard_range = tuple(range(shard_start, shard_end))

# Create a bot instance
print(f'Starting Cluster {argv[5]} ({argv[2]}) with shards {shard_range} for a total of {argv[3]} shards!')

bot = Bot(command_prefix=utils.PrefixHelper.return_prefix, description=settings.get('description', ''), shard_count=int(argv[3]),
          shard_ids=shard_range, activity=Game(name='I\'m starting up! Please wait...'),
          owner_id=settings.get('owner', 66166172835385344), help_command=None)


# Commands here will not show in the commands function
@bot.command(hidden=True, category='Developer')
@commands.is_owner()
async def load(ctx, extension_name : str):
    """Loads an extension."""
    try:
        bot.load_extension('modules.' + extension_name)
    except (AttributeError, ImportError) as e:
        await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await ctx.send(f"{extension_name} loaded.")


@bot.command(hidden=True, category='Developer')
@commands.is_owner()
async def unload(ctx, extension_name : str):
    """Unloads an extension."""
    try:
        bot.unload_extension('modules.' + extension_name)
    except (AttributeError, ImportError) as e:
        return await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
    await ctx.send(f"{extension_name} unloaded.")


@bot.command(hidden=True, category='Developer')
@commands.is_owner()
async def reload(ctx, extension_name: str):
    """Reloads an extension."""
    try:
        bot.unload_extension('modules.' + extension_name)
        bot.load_extension('modules.' + extension_name)
    except (AttributeError, ImportError) as e:
        await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await ctx.send(f"{extension_name} reloaded.")


@bot.command(hidden=True, category='Developer')
@commands.is_owner()
async def reloadall(ctx):
    cogs = bot.load_modules('reload')
    em = Embed(title='All Reloaded!', description='\n'.join(cogs))
    await ctx.send(embed=em)


@bot.command(hidden=True, category='Developer')
@commands.is_owner()
async def loadall(ctx):
    cogs = bot.load_modules('load')
    em = Embed(title='All Loaded!', description='\n'.join(cogs))
    await ctx.send(embed=em)


@bot.command(hidden=True, category='Developer')
@commands.is_owner()
async def unloadall(ctx):
    cogs = bot.load_modules('unload')
    em = Embed(title='All Unloaded!', description='\n'.join(cogs))
    await ctx.send(embed=em)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    else:
        print(error)
        print('\033[93m' + ''.join(format_tb(error.__traceback__)) + '\033[0m')


@bot.event
async def on_error(event, *args, **kwargs):
    print_exc()


@bot.command(hidden=True, category='Developer', aliases=['eval'])
@commands.is_owner()
async def debug(ctx, *, code: str):
    """Eval's custom code"""
    def check(m):
        return m.author == ctx.author and m.content.lower() in ['yes', 'no'] and m.channel == ctx.channel

    if code == 'exit()':
        return await ctx.send('Environment cleared')

    blocklist = ['token']
    for word in blocklist:
        if word in code:
            return await ctx.send('very funny haha')
    env = {
        'self': bot,
        'bot': bot,
        'ctx': ctx,
        'message': ctx.message,
        'guild': ctx.guild,
        'channel': ctx.channel,
        'author': ctx.author
    }
    env.update(globals())
    if code.startswith('```py'):
        code = code[5:]
    code = code.strip('`').strip()
    _code = '''
async def func():
{}
'''.format(indent(code, ' ' * 4))
    await ctx.send('Do you want to eval this on every cluster? Type `yes` or `no`!')
    msg = await bot.wait_for('message', check=check)
    if msg.content.lower() == 'yes':
        _eval_start = time() * 1000
        result = await bot.get_cog('altdentifier-ipc').publish('eval', _code)
        _eval_end = time() * 1000
        _eval_time = _eval_end - _eval_start
        nice_text = ""
        for i, j in result.items():
            a = json.loads(j).get('result', None)
            nice_text += f"[CLUSTER {i}]: {str(a)}\n"
        async with bot.web.post('https://hastepaste.com/api/create',
                                data={"raw": "false", "text": f'{nice_text}\n\n{_eval_time:.3f}ms'}) as r:
            j = await r.text()
            await ctx.send(f'The results are in:\n{j}')
    else:
        _eval_start = time() * 1000
        try:
            exec(_code, env)
            result = await env['func']()
        except Exception as e:
            result = format_exc()
        _eval_end = time() * 1000
        _eval_time = _eval_end - _eval_start
        try:
            await ctx.send(f'```python\n{result}\n\n{_eval_time:.3f}ms```')
        except HTTPException:
            async with bot.web.post('https://hastepaste.com/api/create', data={"raw": "false", "text": f'{result}\n\n{_eval_time:.3f}ms'}) as r:
                j = await r.text()
                await ctx.send(j)


@bot.command(hidden=True, category='Developer')
@commands.is_owner()
async def reload_classes(ctx):
    reload_lib(checks)
    reload_lib(language)
    reload_lib(settings_entry)
    reload_lib(utils)
    await ctx.send('Reloaded all classes')


bot.run(settings['token'])
