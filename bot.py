#!/usr/bin/env python3

import asyncio, os, importlib

from irctokens import build, Line
from ircrobots import Bot as BaseBot
from ircrobots import Server as BaseServer
from ircrobots import ConnectionParams, SASLUserPass, SASLSCRAM

from auth import username, password
import shared

def is_admin(func):
    async def decorator(self,channel,nick,msg):
        if nick.lower() in self.users and self.users[nick.lower()].account in self.admins:
            await func(self,channel,nick,msg)
        else:
            await message(self,'core',channel,'you do not have permission to do that')
    return decorator

def command(commandname):
    def decorator(func):
        shared.commands[commandname] = func
        return func
    return decorator

#def is_chanop(func):

async def message(self,modname,channel,msg):
    await self.send(build("PRIVMSG",[channel,f'[\x036{modname}\x0f] {msg}']))




class Server(BaseServer):
    async def line_read(self, line: Line):
        print(f"{self.name} < {line.format()}")
        if 'on_'+line.command.lower() in dir(self):
            asyncio.create_task(self.__getattribute__('on_'+line.command.lower())(line))
        for listener in shared.listeners:
            if listener[0] == line.command:
                asyncio.create_task(listener[1](self,line))
    
    async def line_send(self, line: Line):
        print(f"{self.name} > {line.format()}")


    async def on_001(self, line):
        asyncio.create_task(self.load_modules())


    async def load_modules(self):
        for i in [s for s in os.listdir('modules') if '.py' in s and '.swp' not in s]:
            i = i[:-3]
            m = importlib.import_module('modules.' + i)
            asyncio.create_task(m.init(self))
            shared.modules[i] = m

    async def on_privmsg(self, line):
        channel = line.params[0]
        nick = line.source.split('!')[0]
        msg = line.params[1]

        await self.handle_rawm(channel,nick,msg)
        await self.handle_command(channel,nick,msg)
    async def handle_rawm(self,channel,nick,msg):
        for i in shared.rawm:
            await shared.rawm[i](self,channel,nick,msg)
    async def handle_command(self,channel,nick,msg):
        if msg[:len(shared.prefix)] == shared.prefix:
            msg = msg[len(shared.prefix):]
            cmd = msg.split(' ')[0]
            msg = msg[len(cmd)+1:]
            if len(cmd) < 1:
                return

            if cmd in shared.commands:
                await shared.commands[cmd](self,channel,nick,msg)
                return

            results = [i for i in shared.commands if i.startswith(cmd)]
            if len(results) == 1:
                await sharedcommands[results[0]](self,channel,nick,msg)


class Bot(BaseBot):
    def create_server(self, name: str):
        return Server(self, name)


async def main():
    bot = Bot()

    sasl_params = SASLUserPass(username, password)
    params      = ConnectionParams(
        "balun",
        host = "irc.tilde.chat",
        port = 6697,
        tls  = True,
        sasl = sasl_params)

    await bot.add_server("tilde", params)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())

