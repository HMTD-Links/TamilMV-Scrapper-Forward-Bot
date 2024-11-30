from asyncio import create_task, gather
from pyrogram import Client, filters
from pyrogram.filters import command, user
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from pyrogram.enums import MessageEntityType
from pyrogram.errors import QueryIdInvalid
import os
from plugins.core.bypass_checker import direct_link_checker, is_excep_link
from plugins.core.bot_utils import convert_time, BypassFilter, BypassFilter1
from time import time

# Configs
OWNER_ID = int(os.environ.get("OWNER_ID", 1391556668))
AUTO_BYPASS = bool(os.getenv("AUTO_BYPASS", "False") == "True")
CHAT_ID = int(os.environ.get("CHAT_ID", -1001542301808))

# Main bypass handler function
@Client.on_message(BypassFilter & (filters.user(OWNER_ID)))
async def bypass_check(client, message):
    uid = message.from_user.id
    if (reply_to := message.reply_to_message) and (
        reply_to.text or reply_to.caption
    ):
        txt = reply_to.text or reply_to.caption
        entities = reply_to.entities or reply_to.caption_entities
    elif AUTO_BYPASS or len(message.text.split()) > 1:
        txt = message.text
        entities = message.entities
    else:
        return await message.reply("<i>No Link Provided!</i>")

    wait_msg = await message.reply("<i>Bypassing...</i>")
    start = time()

    links = []
    tasks = []
    for entity in entities:
        if entity.type in (MessageEntityType.URL, MessageEntityType.TEXT_LINK):
            link = txt[entity.offset : entity.offset + entity.length]
            links.append(link)
            tasks.append(create_task(direct_link_checker(link)))

    results = await gather(*tasks, return_exceptions=True)

    output = []
    for result, link in zip(results, links):
        if isinstance(result, Exception):
            output.append(f"┖ <b>Error:</b> {result}")
        else:
            output.append(f"┖ <b>Bypass Link:</b> {result}")

    elapsed = time() - start
    reply_text = "\n".join(output)
    reply_text += f"\n\n<b>Total Links:</b> {len(links)}\n<b>Time:</b> {convert_time(elapsed)}"
    await wait_msg.edit(reply_text)

@Client.on_message(BypassFilter1 & (filters.user(OWNER_ID)))
async def bypass_check(client, message):
    uid = message.from_user.id
    if (reply_to := message.reply_to_message) and (
        reply_to.text or reply_to.caption
    ):
        txt = reply_to.text or reply_to.caption
        entities = reply_to.entities or reply_to.caption_entities
    elif AUTO_BYPASS or len(message.text.split()) > 1:
        txt = message.text
        entities = message.entities
    else:
        return await message.reply("<i>No Link Provided!</i>")

    # Send initial "Bypassing..." message
    wait_msg = await message.reply("<i>Bypassing...</i>")
    start = time()

    links = []
    tasks = []
    for entity in entities:
        if entity.type in (MessageEntityType.URL, MessageEntityType.TEXT_LINK):
            link = txt[entity.offset : entity.offset + entity.length]
            links.append(link)
            tasks.append(create_task(direct_link_checker(link)))

    # Await all link checks
    results = await gather(*tasks, return_exceptions=True)

    output = []
    for result, link in zip(results, links):
        if isinstance(result, Exception):
            output.append(f"┖ <b>Error:</b> {result}")
        else:
            output.append(f"┖ <b>Bypass Link:</b> {result}")

    # Send the full data with links to the user
    elapsed = time() - start
    reply_text = "\n".join(output)
    reply_text += f"\n\n<b>Total Links:</b> {len(links)}\n<b>Time:</b> {convert_time(elapsed)}"

    # Update the message with the bypass result
    await wait_msg.edit(reply_text)

    # Extract torrent links and send each one as a separate message to the group
    for link in links:
        try:
            # Check if the link is a valid torrent
            result = await direct_link_checker(link)

            # If the result is valid and contains a torrent link, send it to the group
            if "torrent" in result.lower():  # Case-insensitive check for "torrent"
                # Log the link being sent for debugging
                print(f"Sending torrent link: {result}")
                # Send each torrent link separately to the group
                await client.send_message(CHAT_ID, f"/qbleech {result}")
            else:
                print(f"Not a torrent link: {result}")  # Log if the link is not recognized as a torrent

        except Exception as e:
            print(f"Error processing {link}: {e}")

    # After sending the torrent links, update the message to show success
    await wait_msg.edit("<i>Torrent Links Sent Successfully!</i>")

# Inline query for bypass
@Client.on_inline_query()
async def inline_query(client, query):
    text = query.query.strip()
    if text.startswith("!bp "):
        link = text[4:]
        start = time()
        try:
            result = await direct_link_checker(link, True)
            elapsed = time() - start
            response = f"┎ <b>Source Link:</b> {link}\n┖ <b>Bypass Link:</b> {result}\n\n<b>Time:</b> {convert_time(elapsed)}"
        except Exception as e:
            response = f"<b>Error:</b> {e}"

        answer = InlineQueryResultArticle(
            title="Bypass Result",
            input_message_content=InputTextMessageContent(response, disable_web_page_preview=True),
            description=f"Bypass link: {link}",
        )
        await query.answer(results=[answer], cache_time=0)
    else:
        help_text = """<b><i>FZ Bypass Bot</i></b>
        
<i>Use the inline query format: !bp [link]</i>
"""
        answer = InlineQueryResultArticle(
            title="Bypass Help",
            input_message_content=InputTextMessageContent(help_text),
        )
        await query.answer(results=[answer], cache_time=0)
