import discord

class Eggman(discord.Client):
    intents = discord.Intents.default()
    intents.members = True

    token_filename = "token.txt"
    
    msg_prefix = "eggman"
    cmd_prefix = "!"

    help_str = f"Usage: `{msg_prefix} {cmd_prefix}<cmd[0]> <arg[0,0]> <arg[0,1]> ... <arg[0,n]> {cmd_prefix}<cmd[2]> <arg[2,0]> ... {cmd_prefix}<cmd[n]>`\nExample: `eggman !greet me`"

    @staticmethod
    def is_msg_prefix(s):
        return s == Eggman.msg_prefix

    @staticmethod
    def is_cmd(s):
        return s.startswith(Eggman.cmd_prefix)

    @staticmethod
    def is_special_cmd(s):
        return s in Eggman.special_cmd_fns.keys()

    @staticmethod
    def is_msg_for_eggman(msg):
        if (len(msg) < len(Eggman.msg_prefix)): return False
        return msg.startswith(Eggman.msg_prefix)

    @staticmethod
    def is_arg_str_start(s):
        return s.startswith('"')

    @staticmethod
    def is_arg_str_end(s):
        return s.endswith('"')

    @staticmethod
    def tokenize_msg(s):
        tokens = s.split()
        return tuple(tokens)
    
    @staticmethod
    def parse_tokens(tokens):
        if (len(tokens) == 1):
            return ([Eggman.msg_prefix], [tuple()])
        
        cmdlist = []
        argslist = []
        curr_cmd = None
        curr_arglist = None
        curr_arg = None

        for token in tokens:
            s = str(token)
            if (not Eggman.is_msg_prefix(s)):
                if (Eggman.is_cmd(s)):
                    if (curr_cmd is not None and curr_arglist is not None):
                        cmdlist.append(curr_cmd)
                        argslist.append(tuple(curr_arglist))
                    curr_cmd = s.replace(Eggman.cmd_prefix, "")
                    curr_arglist = []
                elif (curr_arglist is not None):
                    if (Eggman.is_arg_str_start(s) and Eggman.is_arg_str_end(s)):
                        curr_arglist.append(s.replace('"', ""))
                    if (Eggman.is_arg_str_start(s)):
                        curr_arg = s.replace('"', "")
                    elif (Eggman.is_arg_str_end(s)):
                        curr_arg += " " + s.replace('"', "")
                        curr_arglist.append(curr_arg)
                    elif (curr_arg is not None):
                        curr_arg += " " + s
                    else:
                        curr_arglist.append(s)
        if (curr_cmd is not None):
            cmdlist.append(curr_cmd)
            argslist.append(tuple(curr_arglist))

        return cmdlist, argslist
    
    def __init__(self, *args, **kwargs):
        
        with open(Eggman.token_filename, "r") as f: self.token = f.read()

        super().__init__(*args, **kwargs, intents = Eggman.intents)

    def run(self):
        super().run(self.token)

    async def exec_cmds(self, dmsg, cmdlist, argslist):
        for (cmd, args) in zip(cmdlist, argslist):
            await self.exec_cmd(dmsg, cmd, args)

    async def exec_cmd(self, dmsg, cmd, args):
        if (not Eggman.is_valid_cmd(cmd)):
            await dmsg.channel.send(f"{cmd} is not a valid eggman command")
            return
        cmd_meth = Eggman.cmd_fns[cmd]
        await cmd_meth(self, dmsg, args)
    
    async def exec_special_cmd(self, dmsg, cmd):
        cmd_meth = Eggman.special_cmd_fns[cmd]
        await cmd_meth(self, dmsg)

    async def on_message(self, dmsg):
        if (dmsg.author == self.user): return
        msg = dmsg.content
        if (Eggman.is_special_cmd(msg)):
            await self.exec_special_cmd(dmsg, msg)
            return
        if (not Eggman.is_msg_for_eggman(msg)): return
        cmdlist, argslist = Eggman.parse_tokens(Eggman.tokenize_msg(msg))
        await self.exec_cmds(dmsg, cmdlist, argslist)

    async def egghelp(self, dmsg, args):
        await dmsg.channel.send(Eggman.help_str)

    async def greet(self, dmsg, args):
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

    async def echo(self, dmsg, args):
        if (len(args) == 0):
            await dmsg.channel.send(f"`echo` takes at minimum 1 argument")
            return
        
        await dmsg.channel.send(f"{' '.join(args)}")

    async def ping(self, dmsg, args):
        await dmsg.channel.send("pong")

    async def hello(self, dmsg, args):
        await dmsg.channel.send(f"Hi, {dmsg.author.mention}. I hope your day is going nicely. :cooking:")

    async def gn(self, dmsg, args):
        await dmsg.channel.send(f"Goodnight, {dmsg.author.mention}. Sleep tight, don't let the bed bugs bite!")

    cmd_fns = {
        msg_prefix: egghelp,
        "help": egghelp,
        "greet": greet,
        "echo": echo,
        "ping": ping,
        "gn": gn
    }

    async def special_gn(self, dmsg):
        await dmsg.channel.send(f"Goodnight.")

    async def special_hello(self, dmsg):
        await dmsg.channel.send(f"Hi!")


    async def egg(self, dmsg):
        await dmsg.channel.send(f":egg:")

    special_cmd_fns = {
        "hi eggman": special_hello,
        "hello eggman": special_hello,
        "goodnight eggman": special_gn,
        "gn eggman": special_gn,
        "egg": egg
    }

    @staticmethod
    def is_valid_cmd(cmd):
        return cmd in Eggman.cmd_fns.keys()


if __name__ == "__main__":
    eggman = Eggman()
    eggman.run()
