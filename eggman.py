from pickletools import read_uint1
from typing import Iterable
from attr import define
import discord
import asyncio as aio
import itertools

class Eggman(discord.Client):
    intents = discord.Intents.default()
    intents.members = True

    token_filename = "token.txt"
    

    msg_prefix = "eggman"
    cmd_prefix = "!"

    help_str = f"eggman usage:\n{msg_prefix} {cmd_prefix}cmd[0] arg[0,0] arg[0,1] ... arg[0,n] {cmd_prefix}cmd[2] arg[2,0] ... {cmd_prefix}cmd[n]\n"

    async def greet(self, dmsg:discord.Message, args:"list[str]"):
        mention_name = None
        mention_msg = None
        mention_user = None

        if (args is not None):
            if (len(args) >= 1):
                mention_name = args[0]
            if (len(args) > 1):
                mention_msg = " ".join(args[1:])
        
        if (mention_name == "me"):
            mention_user = dmsg.author
        else:
            mention_user = discord.utils.get(self.users, name = mention_name)

        send_str = f"Hi there"
        if (mention_user is not None):
            send_str = f"{send_str} {mention_user.mention}"
        if (mention_msg is not None):
            send_str = f"{send_str}. {dmsg.author.mention} says: {mention_msg}"

        await dmsg.channel.send(f"{send_str}")

    async def egghelp(self, dmsg:discord.Message, args:"list[str]"):
        await dmsg.channel.send(Eggman.help_str)

    cmd_fns = {
        msg_prefix: egghelp,
        "help": egghelp,
        "greet": greet
    }

    @staticmethod
    def is_msg_prefix(s:str)->bool:
        return s == Eggman.msg_prefix

    @staticmethod
    def is_cmd(s:str)->bool:
        return s.startswith(Eggman.cmd_prefix)

    @staticmethod
    def is_valid_cmd(cmd:str)->bool:
        return cmd in Eggman.cmd_strings

    @staticmethod
    def is_msg_for_eggman(msg:str)->bool:
        if (len(msg) < len(Eggman.msg_prefix)): return False
        return msg.startswith(Eggman.msg_prefix)

    @staticmethod
    def tokenize_msg(s:str)->tuple:
        tokens = s.split()
        return tuple(tokens)
    
    @staticmethod
    def parse_tokens(tokens:"Iterable[str]")->"tuple['tuple[str]']":
        cmdlist = []
        arglists = []
        curr_cmd = None
        curr_arglist = None
        if (len(tokens) == 1):
            return (tuple([Eggman.msg_prefix]), tuple())

        for token in tokens:
            s = str(token)
            if (not Eggman.is_msg_prefix(s)):
                if (Eggman.is_cmd(s)):
                    if (curr_cmd is not None and curr_arglist is not None):
                        cmdlist.append(curr_cmd)
                        arglists.append(tuple(curr_arglist))
                    curr_cmd = s.replace(Eggman.cmd_prefix, "")
                    curr_arglist = []
                else:
                    curr_arglist.append(s)
        if (curr_cmd is not None):
            cmdlist.append(curr_cmd)
            arglists.append(tuple(curr_arglist))

        return cmdlist, arglists
    
    def __init__(self, *args, **kwargs):
        
        with open(Eggman.token_filename, "r") as f: self.token = f.read()

        super().__init__(*args, **kwargs, intents = Eggman.intents)

    def run(self):
        super().run(self.token)

    async def exec_cmds(self, dmsg:discord.Message, cmdlist:"list[str]", argslist:"list[str]"):
        for (cmd, args) in zip(cmdlist, argslist):
            print(f"cmd: {cmd}, args: {str(args)}")
            await self.exec_cmd(dmsg, cmd, args)

    async def exec_cmd(self, dmsg:discord.Message, cmd:str, args:str):
        cmd_meth = Eggman.cmd_fns[cmd]
        await cmd_meth(self, dmsg, args)
    
    async def on_message(self, dmsg:discord.Message):
        if (dmsg.author == self.user): return
        msg = dmsg.content
        if (not Eggman.is_msg_for_eggman(msg)): return
        cmdlist, argslist = Eggman.parse_tokens(Eggman.tokenize_msg(msg))
        await self.exec_cmds(dmsg, cmdlist, argslist)


if __name__ == "__main__":
    eggman = Eggman()
    eggman.run()
