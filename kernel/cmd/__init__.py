from os import popen
from nonebot import on_command, get_driver, on_fullmatch
from nonebot.adapters import Message, Event
from nonebot.params import CommandArg

svcmd = on_command("cmd")
svping = on_fullmatch("!ping")

@svcmd.handle()
async def _(ev: Event, cmd: Message=CommandArg()):
    if ev.get_user_id() not in get_driver().config.superusers:
        await svcmd.finish("error: permission denied(you are not admin)")
    cmdline = cmd.extract_plain_text()
    if not cmdline:
        await svcmd.finish("error: command is None.")
    out = popen(cmdline)
    await svcmd.finish("execute result:\n" + out.read().strip())

@svping.handle()
async def _():
    await svping.finish("pong!")