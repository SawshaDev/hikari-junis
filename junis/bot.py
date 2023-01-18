# MIT License

# Copyright (c) 2023 SawshaDev

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

from typing import Dict, List, Sequence, Any

import hikari

from .commands import SlashCommand, Context
from .errors import BotNotInitialised


class JunisApp:
    def __init__(self, *, bot: hikari.GatewayBot, purge_extra: bool = True):
        self._purge_extra = purge_extra
        self._bot = bot

        self.slash_commands: Dict[str, SlashCommand] = {}

        self._bot.subscribe(hikari.StartedEvent, self._update_commands)
        
        self._bot.subscribe(hikari.InteractionCreateEvent, self.process_commands)

    @classmethod
    def from_gatewaybot(cls, bot: hikari.GatewayBot):
        return cls(bot=bot)
    
    def add_slash(self, command: SlashCommand):
        if self.slash_commands.get(name := command.name):
            raise ValueError("Command already exists.")

        self.slash_commands[name] = command

    def slash(self, command: SlashCommand):
        def inner() -> SlashCommand:
            nonlocal command
            self.add_slash(command)
            return command
        
        return inner()

    async def process_commands(self, event: hikari.InteractionCreateEvent):
        inter = event.interaction

        if isinstance(inter, hikari.CommandInteraction):
            if command := self.slash_commands.get(inter.command_name):
                await self.invoke_command(event, command)

    async def invoke_command(self, event: hikari.InteractionCreateEvent, command: SlashCommand):
        if not isinstance(inter := event.interaction, hikari.CommandInteraction):
            return

        context = Context(self, event)
        kwargs = await self.__prepare_command_kwargs(inter, inter.options or [])

        await command(context, **kwargs)

    async def _update_commands(self, event: hikari.StartedEvent) -> None:
        await self._handle_global_commands()

    async def __prepare_command_kwargs(self, inter: hikari.CommandInteraction, options: Sequence[hikari.CommandInteractionOption]):
        kwargs: Dict[str, Any] = {}

        for option in options or []:
            if option.type == hikari.OptionType.CHANNEL and isinstance(option.value, int):
                kwargs[option.name] = self._bot.cache.get_guild_channel(option.value)
            elif option.type == hikari.OptionType.USER and isinstance(option.value, int):
                if (g_id := inter.guild_id) is None:
                    kwargs[option.name] = None
                else:
                    kwargs[option.name] = self._bot.cache.get_member(
                        g_id, option.value
                    ) or await self._bot.rest.fetch_member(g_id, option.value)
            elif option.type == hikari.OptionType.ROLE and isinstance(option.value, int):
                if not inter.guild_id:
                    kwargs[option.name] = None
                else:
                    kwargs[option.name] = self._bot.cache.get_role(option.value)
            elif option.type == hikari.OptionType.ATTACHMENT and isinstance(
                option.value, hikari.Snowflake
            ):
                if (res := inter.resolved) is None:
                    raise Exception("")
                attachment = res.attachments.get(option.value)
                kwargs[option.name] = attachment
            else:
                kwargs[option.name] = option.value
        return kwargs         

    async def _handle_global_commands(self):
        userbot = self._bot.get_me()
        if not userbot:
            raise BotNotInitialised()


        command_builders: List[hikari.api.SlashCommandBuilder] = []

        if self._purge_extra is True:
            for command in [
                c
                for c in self.slash_commands.values()
            ]:
                command_builder = self._bot.rest.slash_command_builder(
                    command.name, command.description
                )
                [command_builder.add_option(option) for option in command.options]
                command_builders.append(command_builder)

            await self._bot.rest.set_application_commands(userbot.id, command_builders)

            return


        for command in self.slash_commands.values():
            builder = self._bot.rest.slash_command_builder(command.name, command.description)
            print(command.name)
            
            [
                builder.add_option(option) 
                for option in command.options
            ]

            await builder.create(self._bot.rest, userbot.id)
