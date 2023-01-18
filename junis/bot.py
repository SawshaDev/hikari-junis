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

from typing import Dict, List

import hikari

from .commands import SlashCommand
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
            command = self.slash_commands.get(inter.command_name)
            print(command)

    async def _update_commands(self, event: hikari.StartedEvent) -> None:
        await self._handle_global_commands()
        
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
