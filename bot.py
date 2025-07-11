from aiohttp import web
from plugins import web_server
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime
from config import API_HASH, API_ID, LOGGER, BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNEL, CHANNEL_ID, PORT
import pyrogram.utils




class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=API_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        if FORCE_SUB_CHANNEL:
            try:
                self.LOGGER(__name__).info(f"Attempting to access FORCE_SUB_CHANNEL: {FORCE_SUB_CHANNEL}")
                try:
                    chat = await self.get_chat(FORCE_SUB_CHANNEL)
                    self.LOGGER(__name__).info(f"Force Chat ID: {chat.id}, title: {chat.title}")
                    if not chat.invite_link:
                        await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                        self.invitelink = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                except Exception as e:
                    self.LOGGER(__name__).error(f"Failed to access FORCE_SUB_CHANNEL: {e}")
                    sys.exit()
            except Exception as a:
                self.LOGGER(__name__).error(f"Error accessing FORCE_SUB_CHANNEL: {FORCE_SUB_CHANNEL}")
                self.LOGGER(__name__).error(f"Exception details: {a}")
                self.LOGGER(__name__).warning("Bot Can't Export Invite link From Force Sub Channel!")
                self.LOGGER(__name__).warning(f"Please Double Check The FORCE_SUB_CHANNEL Value And Make Sure Bot Is Admin In Channel With Invite Users Via Link Permission, Current Force Sub Channel Value: {FORCE_SUB_CHANNEL}")
                self.LOGGER(__name__).info("\nBot Stopped...")
                sys.exit()

        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.LOGGER(__name__).info(f"Channel ID: {db_channel.id}, title: {db_channel.title}")
            self.db_channel = db_channel
            test = await self.send_message(chat_id = db_channel.id, text = "Hey 🖐")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"Make Sure Bot Is Admin In DB Channel, And Double Check The CHANNEL_ID Value, Current Value: {CHANNEL_ID}")
            self.LOGGER(__name__).info("\nBot Stopped...")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running...!")
        self.username = usr_bot_me.username
        #web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot Stopped...")
            
