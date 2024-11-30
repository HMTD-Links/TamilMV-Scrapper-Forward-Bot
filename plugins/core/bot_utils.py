from pyrogram.filters import create
from pyrogram.enums import MessageEntityType
from re import match
from FZBypass import Config

async def auto_bypass(_, c, message):
    if (
        Config.AUTO_BYPASS
        and message.entities
        and not match(r"^\/(bash|shell)($| )", message.text)
        and any(
            enty.type in [MessageEntityType.TEXT_LINK, MessageEntityType.URL]
            for enty in message.entities
        )
    ):
        return True
    elif (
        not Config.AUTO_BYPASS
        and (txt := message.text)
        and match(rf"^\/(bypass|bp)(@{c.me.username})?($| )", txt)
        and not match(r"^\/(bash|shell)($| )", txt)
    ):
        return True
    return False


BypassFilter = create(auto_bypass)


def convert_time(seconds):
    mseconds = seconds * 1000
    periods = [("d", 86400000), ("h", 3600000), ("m", 60000), ("s", 1000), ("ms", 1)]
    result = ""
    for period_name, period_seconds in periods:
        if mseconds >= period_seconds:
            period_value, mseconds = divmod(mseconds, period_seconds)
            result += f"{int(period_value)}{period_name}"
    if result == "":
        return "0ms"
    return result
  
