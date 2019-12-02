from asyncio import sleep
from random import choice
from typing import Union

from discord import Embed
from discord.ext.commands import command, Cog


class Help(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(category='Hulpmiddelen', usage='<page number, category or command name>')
    async def help(self, ctx, *, bot_command: Union[int, str] = None):
        """Shows this very command!"""
        lang = self.bot.utils.get_language(ctx.guild.id)
        prefix = self.bot.settings_entry(ctx.guild.id).prefix
        pages = {"1": "Moderatie", "2": "Hulpmiddelen", "3": "Plezier"}
        commandos = dict()
        commandos['Other'] = list()
        if not bot_command:
            bot_command = 1

        async def reaction_listener(reaction, user):
            p_ges = {"1": 'Moderatie', "2": "Hulpmiddelen", "3": "Plezier"}
            if reaction.message.id == help_msg.id and user.id == ctx.author.id:
                page = self.bot.redis.get(f'help:{help_msg.id}:page')
                if help_msg.channel.permissions_for(ctx.guild.me).manage_messages:
                    await help_msg.remove_reaction(reaction, user)
                if str(reaction) == '➡' and page != '3':
                    self.bot.redis.incr(f'help:{help_msg.id}:page')
                    page = str(int(page) + 1)
                elif str(reaction) == '⬅' and page != '1':
                    self.bot.redis.decr(f'help:{help_msg.id}:page')
                    page = str(int(page) - 1)
                elif str(reaction) == '⏭' and page != '3':
                    self.bot.redis.set(f'help:{help_msg.id}:page', '3')
                    page = '3'
                elif str(reaction) == '⏮' and page != '1':
                    self.bot.redis.set(f'help:{help_msg.id}:page', '1')
                    page = '1'
                else:
                    return
                cm_list = list()
                try:
                    for cmdd in commandos[p_ges[page]]:
                        short = lang["commands"]["help"]["commands"][str(cmdd)]['short']
                        if cmdd.usage:
                            usage = lang["commands"]["help"]["commands"][str(cmdd)]['usage']
                            cm_list.append(f'**{prefix}{cmdd.qualified_name}** {usage}\n{short}')
                        else:
                            cm_list.append(f'**{prefix}{cmdd.qualified_name}**\n{short}')
                except Exception as e:
                    return print(e)
                try:
                    embed = help_msg.embeds[0]
                except IndexError:
                    cld = ', '.join(cm_list)
                    cld = cld.replace('*', '')
                    new_msg = f'```{self.bot.user.name}\n' + lang['commands']['help']['desc'] +  \
                    f'\n\n-\n\n{pages[page]}\n\n{cld}\n\n-\n\n' \
                    f'Tip\n\n{lang["commands"]["help"]["embed"]}' \
                    f'\n\n-\n\n' + lang['commands']['help']['page'] % page + '```'
                    try:
                        return await help_msg.edit(content=new_msg)
                    except:
                        return
                try:
                    embed.set_field_at(0, name=pages[page], value='\n'.join(cm_list))
                except IndexError:
                    return
                embed.set_footer(text=lang['commands']['help']['page'] % page, icon_url=ctx.guild.icon_url)
                await help_msg.edit(embed=embed)
                if help_msg.channel.permissions_for(ctx.guild.me).manage_messages:
                    await help_msg.remove_reaction(reaction, user)
        if isinstance(bot_command, int):
            for a in self.bot.commands:
                if hasattr(a, 'category'):
                    if not commandos.get(a.category, None):
                        commandos[a.category] = list()
                    commandos[a.category].append(a)
                else:
                    commandos['Other'].append(a)
            command_list = list()
            try:
                for cmd in commandos[pages[str(bot_command)]]:
                    try:
                        short = lang["commands"]["help"]["commands"][str(cmd)]["short"]
                    except KeyError:
                        short = 'No short description available'
                    if cmd.usage:
                        try:
                            usage = lang["commands"]["help"]["commands"][str(cmd)]["usage"]
                        except KeyError:
                            usage = 'Usage unknown'
                        command_list.append(f'**{prefix}{cmd.qualified_name}** {usage}\n{short}')
                    else:
                        command_list.append(f'**{prefix}{cmd.qualified_name}**\n{short}')
            except KeyError:
                return await ctx.send(lang['commands']['help']['doesnt_exist'])
            if not ctx.channel.permissions_for(ctx.guild.me).send_messages:
                em = Embed(title=lang['commands']['help']['title'], description=lang['commands']['help']['desc'])
                em.set_author(name=self.bot.user.name, url='https://altdentifier.com/commands',
                              icon_url=self.bot.user.avatar_url)
                em.set_footer(text=lang['commands']['help']['desc'] % bot_command, icon_url=ctx.guild.icon_url)
                em.add_field(name=pages[str(bot_command)], value='\n'.join(command_list))
                em.add_field(name=lang['commands']['help']['tip'], value=choice(lang['commands']['help']['tips']),
                             inline=False)
                try:
                    help_msg = await ctx.author.send(embed=em)
                except Exception as e:
                    pass
                try:
                    await ctx.message.add_reaction('📩')
                except Exception as e:
                    pass
            elif ctx.channel.permissions_for(ctx.guild.me).embed_links and ctx.channel.permissions_for(ctx.guild.me).send_messages:
                em = Embed(title=lang['commands']['help']['title'], description=lang['commands']['help']['desc'])
                em.set_author(name=self.bot.user.name, url='https://altdentifier.com/commands',
                              icon_url=self.bot.user.avatar_url)
                em.set_footer(text=lang['commands']['help']['page'] % bot_command, icon_url=ctx.guild.icon_url)
                em.add_field(name=pages[str(bot_command)], value='\n'.join(command_list))
                em.add_field(name=lang['commands']['help']['tip'], value=choice(lang['commands']['help']['tips']),
                             inline=False)
                try:
                    help_msg = await ctx.send(embed=em)
                except Exception as e:
                    pass
            else:
                cleaned = '\n'.join(command_list)
                cleaned = cleaned.replace('*', '')
                msg = f'```{self.bot.user.name}\n' + lang['commands']['help']['desc'] +  \
                      f'\n\n-\n\n{pages[str(bot_command)]}\n\n{cleaned}\n\n-\n\n' \
                      f'Tip\n\n{lang["commands"]["help"]["embed"]}' \
                      f'\n\n-\n\n' + lang['commands']['help']['page'] % bot_command + '```'
                help_msg = await ctx.send(msg)
            if ctx.channel.permissions_for(ctx.guild.me).add_reactions:
                await help_msg.add_reaction('⏮')
                await help_msg.add_reaction('⬅')
                await help_msg.add_reaction('➡')
                await help_msg.add_reaction('⏭')
                self.bot.redis.set(f'help:{help_msg.id}:page', str(bot_command), ex=180)
                self.bot.add_listener(reaction_listener, 'on_reaction_add')
                if not ctx.guild.me.permissions_in(ctx.channel).manage_messages:
                    self.bot.add_listener(reaction_listener, 'on_reaction_remove')
                await sleep(180)
                await help_msg.remove_reaction('⏮', self.bot.user)
                await help_msg.remove_reaction('⬅', self.bot.user)
                await help_msg.remove_reaction('➡', self.bot.user)
                await help_msg.remove_reaction('⏭', self.bot.user)
        elif isinstance(bot_command, str):
            wanted_page = None
            for page, name in pages.items():
                if bot_command.lower() == name.lower():
                    wanted_page = page
                    break
            if wanted_page:
                for a in self.bot.commands:
                    if hasattr(a, 'category'):
                        if not commandos.get(a.category, None):
                            commandos[a.category] = list()
                        commandos[a.category].append(a)
                    else:
                        commandos['Other'].append(a)
                command_list = list()
                for cmd in commandos[pages[wanted_page]]:
                    short = lang['commands']['help']['commands'][str(cmd)]['short']
                    if cmd.usage:
                        usage = lang['commands']['help']['commands'][str(cmd)]['usage']
                        command_list.append(f'**{prefix}{cmd.qualified_name}** {usage}\n{short}')
                    else:
                        command_list.append(f'**{prefix}{cmd.qualified_name}**\n{short}')
                if not ctx.channel.permissions_for(ctx.guild.me).send_messages:
                    em = Embed(title=lang['commands']['help']['title'], description=lang['commands']['help']['desc'])
                    em.set_author(name=self.bot.user.name, url='https://altdentifier.com/commands',
                                  icon_url=self.bot.user.avatar_url)
                    em.set_footer(text=lang['commands']['help']['page'] % wanted_page, icon_url=ctx.guild.icon_url)
                    em.add_field(name=pages[wanted_page], value='\n'.join(command_list))
                    em.add_field(name=lang['commands']['help']['tip'], value=choice(lang['commands']['help']['tips']),
                                 inline=False)
                    try:
                        help_msg = await ctx.author.send(embed=em)
                    except Exception as e:
                        pass
                    try:
                        await ctx.message.add_reaction('📩')
                    except Exception as e:
                        pass
                elif ctx.channel.permissions_for(ctx.guild.me).send_messages and ctx.channel.permissions_for(ctx.guild.me).embed_links:
                    em = Embed(title=lang['commands']['help']['title'], description=lang['commands']['help']['desc'])
                    em.set_author(name=self.bot.user.name, url='https://altdentifier.com/commands',
                                  icon_url=self.bot.user.avatar_url)
                    em.set_footer(text=lang['commands']['help']['page'] % wanted_page, icon_url=ctx.guild.icon_url)
                    em.add_field(name=pages[wanted_page], value='\n'.join(command_list))
                    em.add_field(name=lang['commands']['help']['tip'], value=choice(lang['commands']['help']['tips']),
                                 inline=False)
                    help_msg = await ctx.send(embed=em)
                else:
                    cleaned = '\n'.join(command_list)
                    cleaned = cleaned.replace('*', '')
                    msg = f'```{self.bot.user.name}\n' + lang['commands']['help']['desc'] +  \
                          f'\n\n-\n\n{pages[wanted_page]}\n\n{cleaned}\n\n-\n\n' \
                          f'Tip\n\n{lang["commands"]["help"]["embed"]}' \
                          f'\n\n-\n\n' + lang['commands']['help']['page'] % wanted_page + '```'
                    help_msg = await ctx.send(msg)
                if ctx.channel.permissions_for(ctx.guild.me).add_reactions:
                    await help_msg.add_reaction('⏮')
                    await help_msg.add_reaction('⬅')
                    await help_msg.add_reaction('➡')
                    await help_msg.add_reaction('⏭')
                    self.bot.redis.set(f'help:{help_msg.id}:page', wanted_page, ex=180)
                    self.bot.add_listener(reaction_listener, 'on_reaction_add')
                    if not ctx.guild.me.permissions_in(ctx.channel).manage_messages:
                        self.bot.add_listener(reaction_listener, 'on_reaction_remove')
                    await sleep(180)
                    await help_msg.remove_reaction('⏮', self.bot.user)
                    await help_msg.remove_reaction('⬅', self.bot.user)
                    await help_msg.remove_reaction('➡', self.bot.user)
                    await help_msg.remove_reaction('⏭', self.bot.user)
            else:
                cmd = self.bot.get_command(bot_command)
                if cmd.hidden and ctx.author.id != 66166172835385344:
                    return
                if not ctx.channel.permissions_for(ctx.guild.me).send_messages and not ctx.channel.permissions_for(ctx.guild.me).embed_links:
                    em = Embed(title=prefix + cmd.name,
                               description=lang['commands']['help']['commands'][str(cmd)]['short'])
                    if hasattr(cmd, 'long_doc'):
                        em.add_field(name=lang['commands']['help']['cmd_desc'],
                                     value=lang['commands']['help']['commands'][str(cmd)]['long'])
                    if cmd.usage:
                        em.add_field(name=lang['commands']['help']['usage'],
                                     value=lang['commands']['help']['commands'][str(cmd)]['usage'], inline=False)
                    else:
                        em.add_field(name=lang['commands']['help']['usage'],
                                     value=lang['commands']['help']['no_args'], inline=False)
                    if cmd.aliases:
                        em.add_field(name=lang['commands']['help']['aliases'],
                                     value=', '.join(cmd.aliases), inline=False)
                    else:
                        em.add_field(name=lang['commands']['help']['aliases'],
                                     value=lang['commands']['help']['no_usage'])
                    if hasattr(cmd, 'permissions'):
                        em.add_field(name=lang['commands']['help']['perms'],
                                     value=lang['commands']['help']['commands'][str(cmd)]['permissions'])
                    else:
                        em.add_field(name=lang['commands']['help']['perms'],
                                     value=lang['commands']['help']['no_perms'])
                    em.set_footer(text=lang['commands']['help']['requested_by'] % ctx.author,
                                  icon_url=ctx.author.avatar_url)
                    try:
                        await ctx.author.send(embed=em)
                    except Exception as e:
                        pass
                    try:
                        await ctx.message.add_reaction('📩')
                    except Exception as e:
                        pass
                elif ctx.channel.permissions_for(ctx.guild.me).send_messages and ctx.channel.permissions_for(ctx.guild.me).embed_links:
                    em = Embed(title=prefix + cmd.name, description=lang['commands']['help']['commands'][str(cmd)]['short'])
                    if hasattr(cmd, 'long_doc'):
                        em.add_field(name=lang['commands']['help']['cmd_desc'], value=lang['commands']['help']['commands'][str(cmd)]['long'])
                    if cmd.usage:
                        em.add_field(name=lang['commands']['help']['usage'], value=lang['commands']['help']['commands'][str(cmd)]['usage'], inline=False)
                    else:
                        em.add_field(name=lang['commands']['help']['usage'],
                                     value=lang['commands']['help']['no_args'], inline=False)
                    if cmd.aliases:
                        em.add_field(name=lang['commands']['help']['aliases'], value=', '.join(cmd.aliases),
                                     inline=False)
                    else:
                        em.add_field(name=lang['commands']['help']['aliases'],
                                     value=lang['commands']['help']['no_usage'])
                    if hasattr(cmd, 'permissions'):
                        em.add_field(name=lang['commands']['help']['perms'], value=lang['commands']['help']['commands'][str(cmd)]['permissions'])
                    else:
                        em.add_field(name=lang['commands']['help']['perms'],
                                     value=lang['commands']['help']['no_perms'])
                    em.set_footer(text=lang['commands']['help']['requested_by'] % ctx.author,
                                  icon_url=ctx.author.avatar_url)
                    await ctx.send(embed=em)
                else:
                    if hasattr(cmd, 'long_doc'):
                        description = lang['commands']['help']['commands'][str(cmd)]['long']
                    else:
                        description = lang['commands']['help']['no_desc']
                    if cmd.usage:
                        usage = lang['commands']['help']['commands'][str(cmd)]['usage']
                    else:
                        usage = lang['commands']['help']['no_args']
                    if cmd.aliases:
                        aliases = ', '.join(cmd.aliases)
                    else:
                        aliases = lang['commands']['help']['no_usage']
                    if hasattr(cmd, 'permissions'):
                        permissions = lang['commands']['help']['commands'][str(cmd)]['permissions']
                    else:
                        permissions = lang['commands']['help']['no_perms']
                    short = lang['commands']['help']['commands'][str(cmd)]['short']
                    msg = f'```{prefix}{cmd.name}\n{short}\n\n-\n\n{lang["commands"]["help"]["cmd_desc"]}\n{description}\n\n-\n\n{lang["commands"]["help"]["usage"]}\n{usage}\n\n-\n\n{lang["commands"]["help"]["aliases"]}\n{aliases}\n\n-\n\n{lang["commands"]["help"]["perms"]}\n{permissions}\n\n\n\nlang["commands"]["help"]["cmd_desc"]{lang["commands"]["help"]["cmd_desc"] % ctx.author}```'
                    await ctx.send(msg)


def setup(bot):
    bot.add_cog(Help(bot))
