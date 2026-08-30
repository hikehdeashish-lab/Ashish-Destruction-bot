import os
import threading
import asyncio
import json
import random
import time
import sys
import logging
import html
from datetime import datetime
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode, ChatType
from telegram.error import TelegramError, RetryAfter, TimedOut, NetworkError

# ===================== FLASK WEB SERVER (FOR RENDER 24/7) =====================
app = Flask(__name__)

@app.route('/')
def home():
    return "⚡ Ashish Destruction Bot is Running Live 24/7! ⚡"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

server_thread = threading.Thread(target=run_web, daemon=True)
server_thread.start()

# ===================== CONFIGURATION =====================
BOT_TOKEN = os.getenv('BOT_TOKEN', '8007925386:AAFrVLoIaOL0yTvBp1pwXXgEAJA6ClluKXE')
BOT_USERNAME = os.getenv('BOT_USERNAME', 'Ashish_Destruction_Bot')
OWNER_IDS = [8882297263, 8725940249, 8538439635, 8672896246]
MAIN_OWNER_ID = "8882297263" # God Level ID (Unremovable)

# ===================== DYNAMIC SPEED & MODE PROFILES =====================
current_mode = "HARD"

# Files
OWNERS_FILE = 'owners.json'
SUDO_USERS_FILE = 'sudo_users.json'
RAID_HISTORY_FILE = 'raid_history.json'
PHOTO_FILE = 'photo.json'

# ===================== STATIC TEXTS (BLOCKQUOTE FORMAT) =====================
START_CAPTION = (
    "<blockquote><b>𝐀sʜɪsʜ 𝐃ᴇsᴛʀᴜᴄᴛɪᴏɴ 𝐁ᴏᴛ ❤️‍🔥❤️‍🔥</b></blockquote>\n\n"
    "<blockquote><b>𝐒ʏsᴛᴇᴍ 𝐈ɴɪᴛɪᴀʟɪᴢɪɴɢ..\n"
    "𝐂ʜᴇᴄᴋɪɴɢ 𝐀ʟʟ 𝐌ᴏᴅᴜʟᴇs...\n"
    "𝐏ᴏᴡᴇʀ 𝐌ᴏᴅᴇ: 𝐀ᴄᴛɪᴠᴇ\n"
    "𝐃ᴇsᴛʀᴜᴄᴛɪᴏɴ 𝐌ᴏᴅᴇ: 𝐑ᴇᴀᴅʏ</b></blockquote>\n\n"
    "<blockquote><b>𝐖ᴇʟᴄᴏᴍᴇ 𝐓ᴏ 𝐀sʜɪsʜ 𝐃ᴇsᴛʀᴜᴄᴛɪᴏɴ 𝐁ᴏᴛ ❤️‍🔥❤️‍🔥</b></blockquote>\n\n"
    "<blockquote><b>𝐁ᴜɪʟᴛ 𝐅ᴏʀ 𝐌ᴀxɪᴍᴜᴍ 𝐏ᴏᴡᴇʀ ❤️‍🔥❤️‍🔥</b></blockquote>"
)

HELP_TEXT = (
    "<blockquote><b>ALL COMMANDS:</b>\n\n"
    "<b>RAID & SPAM COMMANDS:</b>\n"
    "• <code>.RAID [COUNT]</code> - ULTRA RAID ON A USER\n"
    "• <code>.SPAM [COUNT] [TEXT]</code> - SPAM (REPLY KAROGE TOH TAG HOGA)\n"
    "• <code>.PING</code> - CHECK BOT STATUS\n"
    "• <code>.STOP</code> - STOP ALL ACTIVE OPERATIONS\n"
    "• <code>.ALIVE</code> - CHECK BOT IS ALIVE OR NOT\n\n"
    "⚡ <b>MODE CONTROLS:</b>\n"
    "• <code>.MEDIUM</code> - STABLE 0.5s SPEED ATTACK\n"
    "• <code>.HARD</code> - ULTRA FAST 1000+ MSG/SEC DESTRUCTION</blockquote>"
)

ABOUT_TEXT = (
    "<blockquote><b>𝐇ᴇᴀᴠʏ 𝐏ᴏᴡᴇʀꜰᴜʟ 𝐒ᴘᴀᴍ 𝐁ᴏᴛ ⚡</b>\n"
    "<b>𝐅ᴀsᴛ • 𝐒ᴍᴏᴏᴛʜ • 𝐏ᴏᴡᴇʀꜰᴜʟ</b>\n"
    "<b>𝐁uɪʟᴛ 𝐅ᴏʀ 𝐒ᴘᴇᴇᴅ & 𝐏ᴇʀꜰᴏʀᴍᴀɴᴄᴇ</b>\n"
    "<b>𝐒ᴍᴀʀᴛ 𝐒ʏsᴛᴇᴍ • 𝐒ᴛᴀʙʟᴇ 𝐖ᴏʀᴋɪɴɢ</b>\n"
    "<b>𝐑ᴇᴀᴅʏ 𝐓ᴏ 𝐑ᴜɴ 𝐖ʜᴇɴᴇᴠᴇʀ 𝐘ᴏᴜ 𝐍ᴇᴇᴅ</b>\n"
    "<b>𝐒ɪᴍᴘʟᴇ 𝐂ᴏᴍᴍᴀɴds • 𝐄ᴀsʏ 𝐓ᴏ 𝐔sᴇ</b>\n"
    "<b>𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ @ll_NAGUMO_ll</b>\n"
    "<b>𝐖ᴇʟᴄᴏᴍᴇ 𝐓ᴏ 𝐓ʜᴇ 𝐍ᴇxᴛ 𝐋ᴇᴠᴇʟ ⚡</b></blockquote>"
)

# ===================== 100+ GAALI RAID MESSAGES =====================
RAID_MESSAGES = [
    "𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘 𝗖𝗛𝗔𝗞𝗨 𝗗𝗔𝗔𝗟 𝗞𝗔𝗥 𝗖𝗛𝗨𝗧 𝗞𝗔 𝗞𝗛𝗢𝗢𝗡 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔",
    "𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘 𝗞𝗘𝗟𝗘 𝗞𝗘 𝗖𝗛𝗜𝗟𝗞𝗘",
    "𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗟𝗘𝗧𝗜 𝗠𝗘𝗥𝗜 𝗟𝗨𝗡𝗗 𝗕𝗔𝗗𝗘 𝗠𝗔𝗦𝗧𝗜 𝗦𝗘",
    "𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗢 𝗠𝗘𝗡𝗘 𝗖𝗛𝗢𝗗 𝗗𝗔𝗟𝗔 𝗕𝗢𝗛𝗢𝗧 𝗦𝗔𝗦𝗧𝗘 𝗦𝗘",
    "𝗧𝗘𝗥𝗘 𝗕𝗔𝗔𝗣 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗠𝗔𝗗𝗔𝗥𝗖𝗛𝗢𝗗",
    "𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗟𝗘𝗞𝗘 𝗕𝗛𝗔𝗚 𝗝𝗔𝗔𝗨𝗡𝗚𝗔",
    "𝗞𝗜𝗗𝗭 𝗠𝗔𝗗𝗔𝗥𝗖𝗛𝗢𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗖𝗛𝗢𝗗 𝗖𝗛𝗢𝗗𝗞𝗘",
    "𝗝𝗨𝗡𝗚𝗟𝗘 𝗠𝗘 𝗡𝗔𝗖𝗛𝗧𝗔 𝗛𝗘 𝗠𝗢𝗥𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗗𝗔𝗜",
    "𝗚𝗔𝗟𝗜 𝗚𝗔𝗟𝗜 𝗠𝗘 𝗥𝗘𝗛𝗧𝗔 𝗛𝗘 𝗦𝗔𝗡𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗖𝗛𝗢𝗗 𝗗𝗔𝗟𝗔",
    "𝗦𝗔𝗕 𝗕𝗢𝗟𝗧𝗘 𝗠𝗨𝗝𝗛𝗞𝗢 𝗣𝗔𝗣𝗔 𝗞𝗬𝗢𝗨𝗡𝗞𝗜 𝗠𝗘𝗡𝗘 𝗕𝗔𝗡𝗔𝗗𝗜𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗣𝗥𝗘𝗚𝗡𝗘𝗡𝗧",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗢𝗧𝗢 𝗖𝗛𝗢𝗗 𝗖𝗛𝗢𝗗𝗞𝗘 𝗣𝗨𝗥𝗔 𝗙𝗔𝗔𝗗 𝗗𝗜𝗔 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗔𝗕𝗕 𝗧𝗘𝗥𝗜 𝗚𝗙 𝗞𝗢 𝗕𝗛𝗘𝗝 😆💦🤤",
    "𝗧𝗘𝗥𝗜 𝗚𝗙 𝗞𝗢 𝗘𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗔 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗘 𝗟𝗢𝗗𝗘 𝗧𝗘𝗥𝗜 𝗚𝗙 𝗧𝗢 𝗠𝗘𝗥𝗜 𝗥Æ𝗡𝗗𝗜 𝗕𝗔𝗡𝗚𝗔𝗬𝗜 𝗔𝗕𝗕 𝗖𝗛𝗔𝗟 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗖𝗛𝗢𝗗𝗧𝗔 𝗙𝗜𝗥𝗦𝗘 ♥️💦😆😆😆😆",
    "𝗛𝗔𝗥𝗜 𝗛𝗔𝗥𝗜 𝗚𝗛𝗔𝗔𝗦 𝗠𝗘 𝗝𝗛𝗢𝗣𝗗𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 🤣🤣💋💦",
    "𝗖𝗛𝗔𝗟 𝗧𝗘𝗥𝗘 𝗕𝗔𝗔𝗣 𝗞𝗢 𝗕𝗛𝗘𝗝 𝗧𝗘𝗥𝗔 𝗕𝗔𝗦𝗞𝗔 𝗡𝗛𝗜 𝗛𝗘 𝗣𝗔𝗣𝗔 𝗦𝗘 𝗟𝗔𝗗𝗘𝗚𝗔 𝗧𝗨",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗠𝗘 𝗕𝗢𝗠𝗕 𝗗𝗔𝗟𝗞𝗘 𝗨𝗗𝗔 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗞𝗘 𝗟𝗔𝗪𝗗𝗘",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗧𝗥𝗔𝗜𝗡 𝗠𝗘 𝗟𝗘𝗝𝗔𝗞𝗘 𝗧𝗢𝗣 𝗕𝗘𝗗 𝗣𝗘 𝗟𝗜𝗧𝗔𝗞𝗘 𝗖𝗛𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗦𝗨𝗔𝗥 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 🤣🤣💋💋",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗔𝗞𝗘 𝗡𝗨𝗗𝗘𝗦 𝗚𝗢𝗢𝗚𝗟𝗘 𝗣𝗘 𝗨𝗣𝗟𝗢𝗔𝗗 𝗞𝗔𝗥𝗗𝗨𝗡𝗚𝗔 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗘 𝗟𝗔𝗘𝗪𝗗𝗘 👻🔥",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗢 𝗖𝗛𝗢𝗗 𝗖𝗛𝗢𝗗𝗞𝗘 𝗩𝗜𝗗𝗘𝗢 𝗕𝗔𝗡𝗔𝗞𝗘 𝗫𝗡𝗫𝗫.𝗖𝗢𝗠 𝗣𝗘 𝗡𝗘𝗘𝗟𝗔𝗠 𝗞𝗔𝗥𝗗𝗨𝗡𝗚𝗔 𝗞𝗨𝗧𝗧𝗘 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 💦💋",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗔𝗞𝗜 𝗖𝗛𝗨𝗗𝗔𝗜 𝗞𝗢 𝗣𝗢𝗥𝗡𝗛𝗨𝗕.𝗖𝗢𝗠 𝗣𝗘 𝗨𝗣𝗟𝗢𝗔𝗗 𝗞𝗔𝗥𝗗𝗨𝗡𝗚𝗔 𝗦𝗨𝗔𝗥 𝗞𝗘 𝗖𝗛𝗢𝗗𝗘 🤣💋💦",
    "𝗔𝗕𝗘 𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗢 𝗖𝗛𝗢𝗗𝗨 𝗥Æ𝗡𝗗𝗜𝗞𝗘 𝗕𝗔𝗖𝗛𝗛𝗘 𝗧𝗘𝗥𝗘𝗞𝗢 𝗖𝗛𝗔𝗞𝗞𝗢 𝗦𝗘 𝗣𝗜𝗟𝗪𝗔𝗩𝗨𝗡𝗚𝗔 𝗥Æ𝗡𝗗𝗜𝗞𝗘 𝗕𝗔𝗖𝗛𝗛𝗘 🤣🤣",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗙𝗔𝗔𝗗𝗞𝗘 𝗥𝗔𝗞𝗗𝗜𝗔 𝗠𝗔‌𝗔‌𝗞𝗘 𝗟𝗢𝗗𝗘 𝗝𝗔𝗔 𝗔𝗕𝗕 𝗦𝗜𝗟𝗪𝗔𝗟𝗘 👄👄",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗠𝗘 𝗠𝗘𝗥𝗔 𝗟𝗨𝗡𝗗 𝗞𝗔𝗔𝗟𝗔",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗟𝗘𝗧𝗜 𝗠𝗘𝗥𝗜 𝗟𝗨𝗡𝗗 𝗕𝗔𝗗𝗘 𝗠𝗔𝗦𝗧𝗜 𝗦𝗘 𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗢 𝗠𝗘𝗡𝗘 𝗖𝗛𝗢𝗗 𝗗𝗔𝗟𝗔 𝗕𝗢𝗛𝗢𝗧 𝗦𝗔𝗦𝗧𝗘 𝗦𝗘",
    "𝗕𝗘𝗧𝗘 𝗧𝗨 𝗕𝗔𝗔𝗣 𝗦𝗘 𝗟𝗘𝗚𝗔 𝗣𝗔𝗡𝗚𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗔 𝗞𝗢 𝗖𝗛𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗞𝗔𝗥𝗞𝗘 𝗡𝗔𝗡𝗚𝗔 💦💋",
    "𝗛𝗔𝗛𝗔𝗛𝗔𝗛 𝗠𝗘𝗥𝗘 𝗕𝗘𝗧𝗘 𝗔𝗚𝗟𝗜 𝗕𝗔𝗔𝗥 𝗔𝗣𝗡𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗟𝗘𝗞𝗘 𝗔𝗔𝗬𝗔 𝗠𝗔𝗧𝗛 𝗞𝗔𝗧 𝗢𝗥 𝗠𝗘𝗥𝗘 𝗠𝗢𝗧𝗘 𝗟𝗨𝗡𝗗 𝗦𝗘 𝗖𝗛𝗨𝗗𝗪𝗔𝗬𝗔 𝗠𝗔𝗧𝗛 𝗞𝗔𝗥",
    "𝗖𝗛𝗔𝗟 𝗕𝗘𝗧𝗔 𝗧𝗨𝗝𝗛𝗘 𝗠𝗔‌𝗔‌𝗙 𝗞𝗜𝗔 🤣 𝗔𝗕𝗕 𝗔𝗣𝗡𝗜 𝗚𝗙 𝗞𝗢 𝗕𝗛𝗘𝗝",
    "𝗦𝗛𝗔𝗥𝗔𝗠 𝗞𝗔𝗥 𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗞𝗜𝗧𝗡𝗔 𝗚𝗔𝗔𝗟𝗜𝗔 𝗦𝗨𝗡𝗪𝗔𝗬𝗘𝗚𝗔 𝗔𝗣𝗡𝗜 𝗠𝗔‌𝗔‌𝗔 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗘 𝗨𝗣𝗘𝗥",
    "𝗔𝗕𝗘 𝗥Æ𝗡𝗗𝗜𝗞𝗘 𝗕𝗔𝗖𝗛𝗛𝗘 𝗔𝗨𝗞𝗔𝗧 𝗡𝗛𝗜 𝗛𝗘𝗧𝗢 𝗔𝗣𝗡𝗜 𝗥Æ𝗡𝗗𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗟𝗘𝗞𝗘 𝗔𝗔𝗬𝗔 𝗠𝗔𝗧𝗛 𝗞𝗔𝗥 𝗛𝗔𝗛𝗔𝗛𝗔𝗛𝗔",
    "𝗞𝗜𝗗𝗭 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗖𝗛𝗢𝗗 𝗖𝗛𝗢𝗗𝗞𝗘 𝗧𝗘𝗥𝗥 𝗟𝗜𝗬𝗘 𝗕𝗛𝗔𝗜 𝗗𝗘𝗗𝗜𝗬𝗔",
    "𝗝𝗨𝗡𝗚𝗟𝗘 𝗠𝗘 𝗡𝗔𝗖𝗛𝗧𝗔 𝗛𝗘 𝗠𝗢𝗥𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗜 𝗖𝗛𝗨𝗗𝗔𝗜 𝗗𝗘𝗞𝗞𝗘 𝗦𝗔𝗕 𝗕𝗢𝗟𝗧𝗘 𝗢𝗡𝗖𝗘 𝗠𝗢𝗥𝗘 𝗢𝗡𝗖𝗘 𝗠𝗢𝗥𝗘 🤣🤣💦💋",
    "𝗚𝗔𝗟𝗜 𝗚𝗔𝗟𝗜 𝗠𝗘 𝗥𝗘𝗛𝗧𝗔 𝗛𝗘 𝗦𝗔𝗡𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗖𝗛𝗢𝗗 𝗗𝗔𝗟𝗔 𝗢𝗥 𝗕𝗔𝗡𝗔 𝗗𝗜𝗔 𝗥𝗔𝗡𝗗 🤤🤣",
    "𝗦𝗔𝗕 𝗕𝗢𝗟𝗧𝗘 𝗠𝗨𝗝𝗛𝗞𝗢 𝗣𝗔𝗣𝗔 𝗞𝗬𝗢𝗨𝗡𝗞𝗜 𝗠𝗘𝗡𝗘 𝗕𝗔𝗡𝗔𝗗𝗜𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗣𝗥𝗘𝗚𝗡𝗘𝗡𝗧 🤣🤣",
    "𝗦𝗨𝗔𝗥 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗠𝗘 𝗦𝗨𝗔𝗥 𝗞𝗔 𝗟𝗢𝗨𝗗𝗔 𝗢𝗥 𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗠𝗘 𝗠𝗘𝗥𝗔 𝗟𝗢𝗗𝗔",
    "𝗖𝗛𝗔𝗟 𝗖𝗛𝗔𝗟 𝗔𝗣𝗡𝗜 𝗠𝗔‌𝗔‌𝗞𝗜 𝗖𝗛𝗨𝗖𝗛𝗜𝗬𝗔 𝗗𝗜𝗞𝗔",
    "𝗛𝗔𝗛𝗔𝗛𝗔𝗛𝗔 𝗕𝗔𝗖𝗛𝗛𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗔𝗞𝗢 𝗖𝗛𝗢𝗗 𝗗𝗜𝗔 𝗡𝗔𝗡𝗚𝗔 𝗞𝗔𝗥𝗞𝗘",
    "𝗧𝗘𝗥𝗜 𝗚𝗙 𝗛𝗘 𝗕𝗔𝗗𝗜 𝗦𝗘𝗫𝗬 𝗨𝗦𝗞𝗢 𝗣𝗜𝗟𝗔𝗞𝗘 𝗖𝗛𝗢𝗢𝗗𝗘𝗡𝗚𝗘 𝗣𝗘𝗣𝗦𝗜",
    "2 𝗥𝗨𝗣𝗔𝗬 𝗞𝗜 𝗣𝗘𝗣𝗦𝗜 𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗦𝗔𝗕𝗦𝗘 𝗦𝗘𝗫𝗬 💋💦",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗖𝗛𝗘𝗘𝗠𝗦 𝗦𝗘 𝗖𝗛𝗨𝗗𝗪𝗔𝗩𝗨𝗡𝗚𝗔 𝗠𝗔𝗗𝗘𝗥𝗖𝗛𝗢𝗢𝗗 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 💦🤣",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗠𝗘 𝗠𝗨𝗧𝗛𝗞𝗘 𝗙𝗔𝗥𝗔𝗥 𝗛𝗢𝗝𝗔𝗩𝗨𝗡𝗚𝗔 𝗛𝗨𝗜 𝗛𝗨𝗜 𝗛𝗨𝗜",
    "𝗦𝗣𝗘𝗘𝗗 𝗟𝗔𝗔𝗔 𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗖𝗛𝗢𝗗𝗨 𝗥Æ𝗡𝗗𝗜𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 💋💦🤣",
    "𝗧𝗨𝗝𝗛𝗘 𝗔𝗕 𝗧𝗔𝗞 𝗡𝗔𝗛𝗜 𝗦𝗠𝗝𝗛 𝗔𝗬𝗔 𝗞𝗜 𝗠𝗔𝗜 𝗛𝗜 𝗛𝗨 𝗧𝗨𝗝𝗛𝗘 𝗣𝗔𝗜𝗗𝗔 𝗞𝗔𝗥𝗡𝗘 𝗪𝗔𝗟𝗔 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘𝗘 𝗔𝗣𝗡𝗜 𝗠𝗔‌𝗔‌ 𝗦𝗘 𝗣𝗨𝗖𝗛 𝗥Æ𝗡𝗗𝗜 𝗞𝗘 𝗕𝗔𝗖𝗛𝗘𝗘𝗘𝗘 🤩👊👤😍",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗦𝗣𝗢𝗧𝗜𝗙𝗬 𝗗𝗔𝗟 𝗞𝗘 𝗟𝗢𝗙𝗜 𝗕𝗔𝗝𝗔𝗨𝗡𝗚𝗔 𝗗𝗜𝗡 𝗕𝗛𝗔𝗥 😍🎶🎶💥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗔 𝗡𝗔𝗬𝗔 𝗥Æ𝗡𝗗𝗜 𝗞𝗛𝗔𝗡𝗔 𝗞𝗛𝗢𝗟𝗨𝗡𝗚𝗔 𝗖𝗛𝗜𝗡𝗧𝗔 𝗠𝗔𝗧 𝗞𝗔𝗥 👊🤣🤣😳",
    "𝗧𝗘𝗥𝗔 𝗕𝗔𝗔𝗣 𝗛𝗨 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗥Æ𝗡𝗗𝗜 𝗞𝗛𝗔𝗡𝗘 𝗣𝗘 𝗖𝗛𝗨𝗗𝗪𝗔 𝗞𝗘 𝗨𝗦 𝗣𝗔𝗜𝗦𝗘 𝗞𝗜 𝗗𝗔𝗔𝗥𝗨 𝗣𝗘𝗘𝗧𝗔 𝗛𝗨 🍷🤩🔥",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗔𝗣𝗡𝗔 𝗕𝗔𝗗𝗔 𝗦𝗔 𝗟𝗢𝗗𝗔 𝗚𝗛𝗨𝗦𝗦𝗔 𝗗𝗨𝗡𝗚𝗔𝗔 𝗞𝗔𝗟𝗟𝗔𝗔𝗣 𝗞𝗘 𝗠𝗔𝗥 𝗝𝗔𝗬𝗘𝗚𝗜 🤩😳😳🔥",
    "𝗧𝗢𝗛𝗔𝗥 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗣𝗨𝗥𝗜 𝗞𝗜 𝗣𝗨𝗥𝗜 𝗞𝗜𝗡𝗚𝗙𝗜𝗦𝗛𝗘𝗥 𝗞𝗜 𝗕𝗢𝗧𝗧𝗟𝗘 𝗗𝗔𝗟 𝗞𝗘 𝗧𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗔𝗡𝗗𝗘𝗥 𝗛𝗜 😱😂🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗞𝗜 𝗦𝗔𝗣𝗡𝗘 𝗠𝗘𝗜 𝗕𝗛𝗜 𝗠𝗘𝗥𝗜 𝗖𝗛𝗨𝗗𝗔𝗜 𝗬𝗔𝗔𝗗 𝗞𝗔𝗥𝗘𝗚𝗜 𝗥Æ𝗡𝗗𝗜 🥳😍👊💥",
    "𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗔𝗨𝗥 𝗕𝗔𝗛𝗘𝗡 𝗞𝗢 𝗗𝗔𝗨𝗗𝗔 𝗗𝗔𝗨𝗗𝗔 𝗡𝗘 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗨𝗡𝗞𝗘 𝗡𝗢 𝗕𝗢𝗟𝗡𝗘 𝗣𝗘 𝗕𝗛𝗜 𝗟𝗔𝗡𝗗 𝗚𝗛𝗨𝗦𝗔 𝗗𝗨𝗡𝗚𝗔 𝗔𝗡𝗗𝗘𝗥 𝗧𝗔𝗞 😎😎🤣🔥",
    "𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗢 𝗢𝗡𝗟𝗜𝗡𝗘 𝗢𝗟𝗫 𝗣𝗘 𝗕𝗘𝗖𝗛𝗨𝗡𝗚𝗔 𝗔𝗨𝗥 𝗣𝗔𝗜𝗦𝗘 𝗦𝗘 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗔 𝗞𝗢𝗧𝗛𝗔 𝗞𝗛𝗢𝗟 𝗗𝗨𝗡𝗚𝗔 😎🤩😝😍",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗔 𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗞𝗜 𝗧𝗨 𝗖𝗔𝗛 𝗞𝗘 𝗕𝗛𝗜 𝗪𝗢 𝗠𝗔𝗦𝗧 𝗖𝗛𝗨𝗗𝗔𝗜 𝗦𝗘 𝗗𝗨𝗥 𝗡𝗛𝗜 𝗝𝗔 𝗣𝗔𝗬𝗘𝗚𝗔𝗔 😏😏🤩😍",
    "𝗦𝗨𝗡 𝗕𝗘 𝗥Æ𝗡𝗗𝗜 𝗞𝗜 𝗔𝗨𝗟𝗔𝗔𝗗 𝗧𝗨 𝗔𝗣𝗡𝗜 𝗕𝗔𝗛𝗘𝗡 𝗦𝗘 𝗦𝗘𝗘𝗞𝗛 𝗞𝗨𝗖𝗛 𝗞𝗔𝗜𝗦𝗘 𝗚𝗔𝗔𝗡𝗗 𝗠𝗔𝗥𝗪𝗔𝗧𝗘 𝗛𝗔𝗜😏🤬🔥💥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗔 𝗬𝗔𝗔𝗥 𝗛𝗨 𝗠𝗘𝗜 𝗔𝗨𝗥 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗔 𝗣𝗬𝗔𝗔𝗥 𝗛𝗨 𝗠𝗘𝗜 𝗔𝗝𝗔 𝗠𝗘𝗥𝗔 𝗟𝗔𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 𝗟𝗘 🤩🤣💥",
    "𝗧𝗘𝗥𝗜 𝗕𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗨𝗦𝗘𝗥𝗕𝗢𝗧 𝗟𝗔𝗚𝗔𝗔𝗨𝗡𝗚𝗔 𝗦𝗔𝗦𝗧𝗘 𝗦𝗣𝗔𝗠 𝗞𝗘 𝗖𝗛𝗢𝗗𝗘",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘 𝗦𝗔𝗥𝗜𝗬𝗔 𝗗𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗 𝗨𝗦𝗜 𝗦𝗔𝗥𝗜𝗬𝗘 𝗣𝗥 𝗧𝗔𝗡𝗚 𝗞𝗘 𝗕𝗔𝗖𝗛𝗘 𝗣𝗔𝗜𝗗𝗔 𝗛𝗢𝗡𝗚𝗘 😱😱",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 ✋ 𝗛𝗔𝗧𝗧𝗛 𝗗𝗔𝗟𝗞𝗘 👶 𝗕𝗔𝗖𝗛𝗘 𝗡𝗜𝗞𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 😍",
    "𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗞𝗘𝗟𝗘 𝗞𝗘 𝗖𝗛𝗜𝗟𝗞𝗘 🤤🤤",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗦𝗨𝗧𝗟𝗜 𝗕𝗢𝗠𝗕 𝗙𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗝𝗛𝗔𝗔𝗧𝗘 𝗝𝗔𝗟 𝗞𝗘 𝗞𝗛𝗔𝗔𝗞 𝗛𝗢 𝗝𝗔𝗬𝗘𝗚𝗜💣💋",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗢 𝗛𝗢𝗥𝗟𝗜𝗖𝗞𝗦 𝗣𝗘𝗘𝗟𝗔𝗞𝗘 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗😚",
    "𝗧𝗘𝗥𝗜 𝗜𝗧𝗘𝗠 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘 𝗟𝗨𝗡𝗗 𝗗𝗔𝗔𝗟𝗞𝗘,𝗧𝗘𝗥𝗘 𝗝𝗔𝗜𝗦𝗔 𝗘𝗞 𝗢𝗥 𝗡𝗜𝗞𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗😆🤤💋",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗢 𝗔𝗣𝗡𝗘 𝗟𝗨𝗡𝗗 𝗣𝗥 𝗜𝗧𝗡𝗔 𝗝𝗛𝗨𝗟𝗔𝗔𝗨𝗡𝗚𝗔 𝗞𝗜 𝗝𝗛𝗨𝗟𝗧𝗘 𝗝𝗛𝗨𝗟𝗧𝗘 𝗛𝗜 𝗕𝗔𝗖𝗛𝗔 𝗣𝗔𝗜𝗗𝗔 𝗞𝗥 𝗗𝗘𝗚𝗜 💦💋",
    "𝗦𝗨𝗔𝗥 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗦𝗔𝗗𝗔𝗞 𝗣𝗥 𝗟𝗜𝗧𝗔𝗞𝗘 𝗖𝗛𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 😂😆🤤",
    "𝗔𝗕𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗠𝗔𝗗𝗘𝗥𝗖𝗛𝗢𝗢𝗗 𝗞𝗥 𝗣𝗜𝗟𝗟𝗘 𝗣𝗔𝗣𝗔 𝗦𝗘 𝗟𝗔𝗗𝗘𝗚𝗔 𝗧𝗨 😼😂🤤",
    "𝗚𝗔𝗟𝗜 𝗚𝗔𝗟𝗜 𝗡𝗘 𝗦𝗛𝗢𝗥 𝗛𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗥Æ𝗡𝗗𝗜 𝗖𝗛𝗢𝗥 𝗛𝗘 💋💋💦",
    "𝗔𝗕𝗘 𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗢 𝗖𝗛𝗢𝗗𝗨 𝗥Æ𝗡𝗗𝗜𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 𝗞𝗨𝗧𝗧𝗘 𝗞𝗘 𝗖𝗛𝗢𝗗𝗘 😂👻🔥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗔𝗜𝗦𝗘 𝗖𝗛𝗢𝗗𝗔 𝗔𝗜𝗦𝗘 𝗖𝗛𝗢𝗗𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗔 𝗕𝗘𝗗 𝗣𝗘𝗛𝗜 𝗠𝗨𝗧𝗛 𝗗𝗜𝗔 💦💦💦💦",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘 𝗔𝗔𝗔𝗚 𝗟𝗔𝗚𝗔𝗗𝗜𝗔 𝗠𝗘𝗥𝗔 𝗠𝗢𝗧𝗔 𝗟𝗨𝗡𝗗 𝗗𝗔𝗟𝗞𝗘 🔥🔥💦😆😆",
    "𝗥Æ𝗡𝗗𝗜𝗞𝗘 𝗕𝗔𝗖𝗛𝗛𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗖𝗛𝗢𝗗𝗨 𝗖𝗛𝗔𝗟 𝗡𝗜𝗞𝗔𝗟",
    "𝗞𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗨 𝗧𝗘𝗥𝗜 𝗥Æ𝗡𝗗𝗜 𝗠𝗔‌𝗔‌𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗔𝗕𝗕 𝗔𝗣𝗡𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗢 𝗕𝗛𝗘𝗝 😆👻🤤",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗛𝗢𝗗 𝗞𝗘 𝗨𝗦𝗠𝗘 𝗖𝗬𝗟𝗜𝗡𝗗𝗘𝗥 ⛽️ 𝗙𝗜𝗧 𝗞𝗔𝗥𝗞𝗘 𝗨𝗦𝗠𝗘𝗘 𝗗𝗔𝗟 𝗠𝗔𝗞𝗛𝗔𝗡𝗜 𝗕𝗔𝗡𝗔𝗨𝗡𝗚𝗔𝗔𝗔🤩👊🔥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗦𝗛𝗘𝗘𝗦𝗛𝗔 𝗗𝗔𝗟 𝗗𝗨𝗡𝗚𝗔𝗔𝗔 𝗔𝗨𝗥 𝗖𝗛𝗔𝗨𝗥𝗔𝗛𝗘 𝗣𝗘 𝗧𝗔𝗔𝗡𝗚 𝗗𝗨𝗡𝗚𝗔 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘😈😱🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗖𝗥𝗘𝗗𝗜𝗧 𝗖𝗔𝗥𝗗 𝗗𝗔𝗟 𝗞𝗘 𝗔𝗚𝗘 𝗦𝗘 500 𝗞𝗘 𝗞𝗔𝗔𝗥𝗘 𝗞𝗔𝗔𝗥𝗘 𝗡𝗢𝗧𝗘 𝗡𝗜𝗞𝗔𝗟𝗨𝗡𝗚𝗔𝗔 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘💰💰🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗘 𝗦𝗔𝗧𝗛 𝗦𝗨𝗔𝗥 𝗞𝗔 𝗦𝗘𝗫 𝗞𝗔𝗥𝗪𝗔 𝗗𝗨𝗡𝗚𝗔𝗔 𝗘𝗞 𝗦𝗔𝗧𝗛 6-6 𝗕𝗔𝗖𝗛𝗘 𝗗𝗘𝗚𝗜💰🔥😱",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗔𝗣𝗣𝗟𝗘 𝗞𝗔 18𝗪 𝗪𝗔𝗟𝗔 𝗖𝗛𝗔𝗥𝗚𝗘𝗥 🔥🤩",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘𝗜 𝗢𝗡𝗘𝗣𝗟𝗨𝗦 𝗞𝗔 𝗪𝗥𝗔𝗣 𝗖𝗛𝗔𝗥𝗚𝗘𝗥 30𝗪 𝗛𝗜𝗚𝗛 𝗣𝗢𝗪𝗘𝗥 💥😂😎",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗢 𝗔𝗠𝗔𝗭𝗢𝗡 𝗦𝗘 𝗢𝗥𝗗𝗘𝗥 𝗞𝗔𝗥𝗨𝗡𝗚𝗔 10 𝗿𝘀 𝗠𝗘𝗜 𝗔𝗨𝗥 𝗙𝗟𝗜𝗣𝗞𝗔𝗥𝗧 𝗣𝗘 20 𝗥𝗦 𝗠𝗘𝗜 𝗕𝗘𝗖𝗛 𝗗𝗨𝗡𝗚𝗔🤮👿😈🤖",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗕𝗔𝗗𝗜 𝗕𝗛𝗨𝗡𝗗 𝗠𝗘 𝗭𝗢𝗠𝗔𝗧𝗢 𝗗𝗔𝗟 𝗞𝗘 𝗦𝗨𝗕𝗪𝗔𝗬 𝗞𝗔 𝗕𝗙𝗙 𝗩𝗘𝗚 𝗦𝗨𝗕 𝗖𝗢𝗠𝗕𝗢 [15𝗰𝗺 , 16 𝗶𝗻𝗰𝗵𝗲𝘀 ] 𝗢𝗥𝗗𝗘𝗥 𝗖𝗢𝗗 𝗞𝗥𝗩𝗔𝗨𝗡𝗚𝗔 𝗢𝗥 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗝𝗔𝗕 𝗗𝗜𝗟𝗜𝗩𝗘𝗥𝗬 𝗗𝗘𝗡𝗘 𝗔𝗬𝗘𝗚𝗜 𝗧𝗔𝗕 𝗨𝗦𝗣𝗘 𝗝𝗔𝗔𝗗𝗨 𝗞𝗥𝗨𝗡𝗚𝗔 𝗢𝗥 𝗙𝗜𝗥 9 𝗠𝗢𝗡𝗧𝗛 𝗕𝗔𝗔𝗗 𝗩𝗢 𝗘𝗞 𝗢𝗥 𝗙𝗥𝗘𝗘 𝗗𝗜𝗟𝗜𝗩𝗘𝗥𝗬 𝗗𝗘𝗚𝗜🙀👍🥳🔥",
    "𝗧𝗘𝗥𝗜 𝗕𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗔𝗔𝗟𝗜🙁🤣💥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗖𝗛𝗔𝗡𝗚𝗘𝗦 𝗖𝗢𝗠𝗠𝗜𝗧 𝗞𝗥𝗨𝗚𝗔 𝗙𝗜𝗥 𝗧𝗘𝗥𝗜 𝗕𝗛𝗘𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗔𝗨𝗧𝗢𝗠𝗔𝗧𝗜𝗖𝗔𝗟𝗟𝗬 𝗨𝗣𝗗𝗔𝗧𝗘 𝗛𝗢𝗝𝗔𝗔𝗬𝗘𝗚𝗜🤖🙏🤔",
    "𝗧𝗘𝗥𝗜 𝗠𝗔𝗨𝗦𝗜 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗜𝗡𝗗𝗜𝗔𝗡 𝗥𝗔𝗜𝗟𝗪𝗔𝗬 🚂💥😂",
    "𝗧𝗨 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗧𝗘𝗥𝗔 𝗞𝗛𝗔𝗡𝗗𝗔𝗡 𝗦𝗔𝗕 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗟𝗔𝗪𝗗𝗘 𝗥Æ𝗡𝗗𝗜 𝗛𝗔𝗜 𝗥Æ𝗡𝗗𝗜 🤢✅🔥",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗜𝗢𝗡𝗜𝗖 𝗕𝗢𝗡𝗗 𝗕𝗔𝗡𝗔 𝗞𝗘 𝗩𝗜𝗥𝗚𝗜𝗡𝗜𝗧𝗬 𝗟𝗢𝗢𝗦𝗘 𝗞𝗔𝗥𝗪𝗔 𝗗𝗨𝗡𝗚𝗔 𝗨𝗦𝗞𝗜 📚 😎🤩",
    "𝗧𝗘𝗥𝗜 𝗥Æ𝗡𝗗𝗜 𝗠𝗔‌𝗔‌ 𝗦𝗘 𝗣𝗨𝗖𝗛𝗡𝗔 𝗕𝗔𝗔𝗣 𝗞𝗔 𝗡𝗔𝗔𝗠 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗟𝗢𝗗𝗘𝗘𝗘𝗘𝗘 🤩🥳😳",
    "𝗧𝗨 𝗔𝗨𝗥 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗗𝗢𝗡𝗢 𝗞𝗜 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗠𝗘𝗧𝗥𝗢 𝗖𝗛𝗔𝗟𝗪𝗔 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔𝗗𝗔𝗥𝗫𝗛𝗢𝗗 🚇🤩😱🥶",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗧𝗘𝗥𝗔 𝗕𝗔𝗔𝗣 𝗕𝗛𝗜 𝗨𝗦𝗞𝗢 𝗣𝗔𝗛𝗖𝗛𝗔𝗡𝗔𝗡𝗘 𝗦𝗘 𝗠𝗔𝗡𝗔 𝗞𝗔𝗥 𝗗𝗘𝗚𝗔😂👿🤩",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗛𝗔𝗜𝗥 𝗗𝗥𝗬𝗘𝗥 𝗖𝗛𝗔𝗟𝗔 𝗗𝗨𝗡𝗚𝗔𝗔💥🔥🔥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗠 𝗞𝗜 𝗦𝗔𝗥𝗜 𝗥Æ𝗡𝗗𝗜𝗬𝗢𝗡 𝗞𝗔 𝗥Æ𝗡𝗗𝗜 𝗞𝗛𝗔𝗡𝗔 𝗞𝗛𝗢𝗟 𝗗𝗨𝗡𝗚𝗔𝗔👿🤮😎",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗔𝗟𝗘𝗫𝗔 𝗗𝗔𝗟 𝗞𝗘𝗘 𝗗𝗝 𝗕𝗔𝗝𝗔𝗨𝗡𝗚𝗔𝗔𝗔 🎶 ⬆️🤩💥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗚𝗜𝗧𝗛𝗨𝗕 𝗗𝗔𝗟 𝗞𝗘 𝗔𝗣𝗡𝗔 𝗕𝗢𝗧 𝗛𝗢𝗦𝗧 𝗞𝗔𝗥𝗨𝗡𝗚𝗔𝗔 🤩👊👤😍",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗔 𝗩𝗣𝗦 𝗕𝗔𝗡𝗔 𝗞𝗘 24*7 𝗕𝗔𝗦𝗛 𝗖𝗛𝗨𝗗𝗔𝗜 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 𝗗𝗘 𝗗𝗨𝗡𝗚𝗔𝗔 🤩💥🔥🔥",
    "𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗧𝗘𝗥𝗘 𝗟𝗔𝗡𝗗 𝗞𝗢 𝗗𝗔𝗟 𝗞𝗘 𝗞𝗔𝗔𝗧 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗 🔪😂🔥",
    "𝗦𝗨𝗡 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗔𝗨𝗥 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗔 𝗕𝗛𝗜 𝗕𝗛𝗢𝗦𝗗𝗔 👿😎👊",
    "𝗧𝗨𝗝𝗛𝗘 𝗗𝗘𝗞𝗛 𝗞𝗘 𝗧𝗘𝗥𝗜 𝗥Æ𝗡𝗗𝗜 𝗕𝗔𝗛𝗘𝗡 𝗣𝗘 𝗧𝗔𝗥𝗔𝗦 𝗔𝗧𝗔 𝗛𝗔𝗜 𝗠𝗨𝗝𝗛𝗘 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗟𝗢𝗗𝗘𝗘𝗘𝗘 👿💥🤩🔥",
    "𝗦𝗨𝗡 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗 𝗝𝗬𝗔𝗗𝗔 𝗡𝗔 𝗨𝗖𝗛𝗔𝗟 𝗠𝗔‌𝗔‌ 𝗖𝗛𝗢𝗗 𝗗𝗘𝗡𝗚𝗘 𝗘𝗞 𝗠𝗜𝗡 𝗠𝗘𝗜 ✅🤣🔥🤩",
    "𝗔𝗣𝗡𝗜 𝗔𝗠𝗠𝗔 𝗦𝗘 𝗣𝗨𝗖𝗛𝗡𝗔 𝗨𝗦𝗞𝗢 𝗨𝗦 𝗞𝗔𝗔𝗟𝗜 𝗥𝗔𝗔𝗧 𝗠𝗘𝗜 𝗞𝗔𝗨𝗡 𝗖𝗛𝗢𝗗𝗡𝗘𝗘 𝗔𝗬𝗔 𝗧𝗛𝗔𝗔𝗔! 𝗧𝗘𝗥𝗘 𝗜𝗦 𝗣𝗔𝗣𝗔 𝗞𝗔 𝗡𝗔𝗔𝗠 𝗟𝗘𝗚𝗜 😂👿😳",
    "𝗧𝗢𝗛𝗔𝗥 𝗕𝗔𝗛𝗜𝗡 𝗖𝗛𝗢𝗗𝗨 𝗕𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗟𝗔𝗪𝗗𝗘 𝗨𝗦𝗠𝗘 𝗠𝗜𝗧𝗧𝗜 𝗗𝗔𝗟 𝗞𝗘 𝗖𝗘𝗠𝗘𝗡𝗧 𝗦𝗘 𝗕𝗛𝗔𝗥 𝗗𝗨 🏠🤢🤩💥",
    "𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗚𝗛𝗨𝗧𝗞𝗔 𝗞𝗛𝗔𝗔𝗞𝗘 𝗧𝗛𝗢𝗢𝗞 𝗗𝗨𝗡𝗚𝗔 🤣🤣",
    "𝗧𝗘𝗥𝗘 𝗕𝗘‌𝗛𝗘𝗡 𝗞 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗖𝗛𝗔𝗞𝗨 𝗗𝗔𝗔𝗟 𝗞𝗔𝗥 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗔 𝗞𝗛𝗢𝗢𝗡 𝗞𝗔𝗥 𝗗𝗨𝗚𝗔",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗡𝗛𝗜 𝗛𝗔𝗜 𝗞𝗬𝗔? 9 𝗠𝗔𝗛𝗜𝗡𝗘 𝗥𝗨𝗞 𝗦𝗔𝗚𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗗𝗘𝗧𝗔 𝗛𝗨 🤣🤣🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘 𝗔𝗘𝗥𝗢𝗣𝗟𝗔𝗡𝗘𝗣𝗔𝗥𝗞 𝗞𝗔𝗥𝗞𝗘 𝗨𝗗𝗔𝗔𝗡 𝗕𝗛𝗔𝗥 𝗗𝗨𝗚𝗔 ✈️🛫",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗦𝗨𝗧𝗟𝗜 𝗕𝗢𝗠𝗕 𝗙𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗝𝗛𝗔𝗔𝗧𝗘 𝗝𝗔𝗟 𝗞𝗘 𝗞𝗛𝗔𝗔𝗞 𝗛𝗢 𝗝𝗔𝗬𝗘𝗚𝗜💣",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗦𝗖𝗢𝗢𝗧𝗘𝗥 𝗗𝗔𝗔𝗟 𝗗𝗨𝗚𝗔👅",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗔𝗞𝗧𝗘 🤱 𝗚𝗔𝗟𝗜 𝗞𝗘 𝗞𝗨𝗧𝗧𝗢 🦮 𝗠𝗘 𝗕𝗔𝗔𝗧 𝗗𝗨𝗡𝗚𝗔 𝗣𝗛𝗜𝗥 🍞 𝗕𝗥𝗘𝗔𝗗 𝗞𝗜 𝗧𝗔𝗥𝗛 𝗞𝗛𝗔𝗬𝗘𝗡𝗚𝗘 𝗪𝗢 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧",
    "𝗗𝗨𝗗𝗛 𝗛𝗜𝗟𝗔𝗔𝗨𝗡𝗚𝗔 𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗘 𝗨𝗣𝗥 𝗡𝗜𝗖𝗛𝗘 🆙🆒😙",
    "𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 @ll_ALPHA_BABY_lll 𝗞𝗔 𝗟𝗨𝗡𝗗 𝗗𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗙𝗜𝗥 𝗢 𝗣𝗥𝗘𝗚𝗡𝗘𝗡𝗧 𝗛𝗢 𝗝𝗔𝗬𝗘𝗚𝗜 🍌🍌😍",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗗𝗛𝗔𝗡𝗗𝗛𝗘 𝗩𝗔𝗔𝗟𝗜 😋😛",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘 𝗔𝗖 𝗟𝗔𝗚𝗔 𝗗𝗨𝗡𝗚𝗔 𝗦𝗔𝗔𝗥𝗜 𝗚𝗔𝗥𝗠𝗜 𝗡𝗜𝗞𝗔𝗟 𝗝𝗔𝗔𝗬𝗘𝗚𝗜",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗢 𝗛𝗢𝗥𝗟𝗜𝗖𝗞𝗦 𝗣𝗘𝗘𝗟𝗔𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗😚",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗞𝗢𝗟𝗞𝗔𝗧𝗔 𝗩𝗔𝗔𝗟𝗘 𝗝𝗜𝗧𝗨 𝗕𝗛𝗔𝗜𝗬𝗔 𝗞𝗔 𝗟𝗨𝗡𝗗 𝗠𝗨𝗕𝗔𝗥𝗔𝗞 🤩🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗙𝗔𝗡𝗧𝗔𝗦𝗬 𝗛𝗨 𝗟𝗔𝗪𝗗𝗘, 𝗧𝗨 𝗔𝗣𝗡𝗜 𝗕𝗛𝗘𝗡 𝗞𝗢 𝗦𝗠𝗕𝗛𝗔𝗔𝗟 😈😈",
    "𝗧𝗘𝗥𝗔 𝗣𝗘𝗛𝗟𝗔 𝗕𝗔𝗔𝗣 𝗛𝗨 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗 ",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘 𝗫𝗩𝗜𝗗𝗘𝗢𝗦.𝗖𝗢𝗠 𝗖𝗛𝗔𝗟𝗔 𝗞𝗘 𝗠𝗨𝗧𝗛 𝗠𝗔‌𝗔‌𝗥𝗨𝗡𝗚𝗔 🤡😹",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗔 𝗚𝗥𝗢𝗨𝗣 𝗩𝗔𝗔𝗟𝗢𝗡 𝗦𝗔𝗔𝗧𝗛 𝗠𝗜𝗟𝗞𝗘 𝗚𝗔𝗡𝗚 𝗕𝗔𝗡𝗚 𝗞𝗥𝗨𝗡𝗚𝗔🙌🏻☠️ ",
    "𝗧𝗘𝗥𝗜 𝗜𝗧𝗘𝗠 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘 𝗟𝗨𝗡𝗗 𝗗𝗔𝗔𝗟𝗞𝗘,𝗧𝗘𝗥𝗘 𝗝𝗔𝗜𝗦𝗔 𝗘𝗞 𝗢𝗥 𝗡𝗜𝗞𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗🤘🏻🙌🏻☠️ ",
    "𝗔𝗨𝗞𝗔𝗔𝗧 𝗠𝗘 𝗥𝗘𝗛 𝗩𝗥𝗡𝗔 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘 𝗗𝗔𝗡𝗗𝗔 𝗗𝗔𝗔𝗟 𝗞𝗘 𝗠𝗨𝗛 𝗦𝗘 𝗡𝗜𝗞𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗦𝗛𝗔𝗥𝗜𝗥 𝗕𝗛𝗜 𝗗𝗔𝗡𝗗𝗘 𝗝𝗘𝗦𝗔 𝗗𝗜𝗞𝗛𝗘𝗚𝗔 🙄🤭🤭",
    "𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗘 𝗦𝗔𝗔𝗧𝗛 𝗟𝗨𝗗𝗢 𝗞𝗛𝗘𝗟𝗧𝗘 𝗞𝗛𝗘𝗟𝗧𝗘 𝗨𝗦𝗞𝗘 𝗠𝗨𝗛 𝗠𝗘 𝗔𝗣𝗡𝗔 𝗟𝗢𝗗𝗔 𝗗𝗘 𝗗𝗨𝗡𝗚𝗔☝🏻☝🏻😬",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗢 𝗔𝗣𝗡𝗘 𝗟𝗨𝗡𝗗 𝗣𝗥 𝗜𝗧𝗡𝗔 𝗝𝗛𝗨𝗟𝗔𝗔𝗨𝗡𝗚𝗔 𝗞𝗜 𝗝𝗛𝗨𝗟𝗧𝗘 𝗝𝗛𝗨𝗟𝗧𝗘 𝗛𝗜 𝗕𝗔𝗖𝗛𝗔 𝗣𝗔𝗜𝗗𝗔 𝗞𝗥 𝗗𝗘𝗚𝗜👀👯 ",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗕𝗔𝗧𝗧𝗘𝗥𝗬 𝗟𝗔𝗚𝗔 𝗞𝗘 𝗣𝗢𝗪𝗘𝗥𝗕𝗔𝗡𝗞 𝗕𝗔𝗡𝗔 𝗗𝗨𝗡𝗚𝗔 🔋 🔥🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗖++ 𝗦𝗧𝗥𝗜𝗡𝗚 𝗘𝗡𝗖𝗥𝗬𝗣𝗧𝗜𝗢𝗡 𝗟𝗔𝗚𝗔 𝗗𝗨𝗡𝗚𝗔 𝗕𝗔𝗛𝗧𝗜 𝗛𝗨𝗬𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗥𝗨𝗞 𝗝𝗔𝗬𝗘𝗚𝗜𝗜𝗜𝗜😈🔥😍",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗘 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘𝗜 𝗝𝗛𝗔𝗔𝗗𝗨 𝗗𝗔𝗟 𝗞𝗘 𝗠𝗢𝗥 🦚 𝗕𝗔𝗡𝗔 𝗗𝗨𝗡𝗚𝗔𝗔 🤩🥵😱",
    "𝗧𝗘𝗥𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗦𝗛𝗢𝗨𝗟𝗗𝗘𝗥𝗜𝗡𝗚 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔𝗔 𝗛𝗜𝗟𝗔𝗧𝗘 𝗛𝗨𝗬𝗘 𝗕𝗛𝗜 𝗗𝗔𝗥𝗗 𝗛𝗢𝗚𝗔𝗔𝗔😱🤮👺",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗥𝗘𝗗𝗜 𝗣𝗘 𝗕𝗔𝗜𝗧𝗛𝗔𝗟 𝗞𝗘 𝗨𝗦𝗦𝗘 𝗨𝗦𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗕𝗜𝗟𝗪𝗔𝗨𝗡𝗚𝗔𝗔 💰 😵🤩",
    "𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 4 𝗛𝗢𝗟𝗘 𝗛𝗔𝗜 𝗨𝗡𝗠𝗘 𝗠𝗦𝗘𝗔𝗟 𝗟𝗔𝗚𝗔 𝗕𝗔𝗛𝗨𝗧 𝗕𝗔𝗛𝗘𝗧𝗜 𝗛𝗔𝗜 𝗕𝗛𝗢𝗙𝗗𝗜𝗞𝗘👊🤮🤢🤢",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗕𝗔𝗥𝗚𝗔𝗗 𝗞𝗔 𝗣𝗘𝗗 𝗨𝗚𝗔 𝗗𝗨𝗡𝗚𝗔𝗔 𝗖𝗢𝗥𝗢𝗡𝗔 𝗠𝗘𝗜 𝗦𝗔𝗕 𝗢𝗫𝗬𝗚𝗘𝗡 𝗟𝗘𝗞𝗔𝗥 𝗝𝗔𝗬𝗘𝗡𝗚𝗘🤢🤩🥳",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗦𝗨𝗗𝗢 𝗟𝗔𝗚𝗔 𝗞𝗘 𝗕𝗜𝗚𝗦𝗣𝗔𝗠 𝗟𝗔𝗚𝗔 𝗞𝗘 9999 𝗙𝗨𝗖𝗞 𝗟𝗔𝗚𝗔𝗔 𝗗𝗨 🤩🥳🔥",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗡 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘 𝗠𝗘𝗜 𝗕𝗘𝗦𝗔𝗡 𝗞𝗘 𝗟𝗔𝗗𝗗𝗨 𝗕𝗛𝗔𝗥 𝗗𝗨𝗡𝗚𝗔🤩🥳🔥😈",
]

# ===================== GLOBALS =====================
owners = {}
sudo_users = {}
active_operations = {}
raid_history = {}
bot_photo = "https://picsum.photos/800/400"

# ===================== FILE & DATA HANDLING =====================
def load_data():
    global owners, sudo_users, raid_history, bot_photo
    
    if os.path.exists(PHOTO_FILE):
        try:
            with open(PHOTO_FILE, 'r') as f:
                data = json.load(f)
                bot_photo = data.get("photo", bot_photo)
        except Exception:
            pass

    if os.path.exists(OWNERS_FILE):
        try:
            with open(OWNERS_FILE, 'r') as f:
                owners = json.load(f)
        except Exception:
            owners = {}
    for owner_id in OWNER_IDS:
        if str(owner_id) not in owners:
            owners[str(owner_id)] = {'added_by': 'system', 'added_date': datetime.now().isoformat()}
            
    if os.path.exists(SUDO_USERS_FILE):
        try:
            with open(SUDO_USERS_FILE, 'r') as f:
                sudo_users = json.load(f)
        except Exception:
            sudo_users = {}

def save_data():
    try:
        with open(OWNERS_FILE, 'w') as f: json.dump(owners, f, indent=2)
        with open(SUDO_USERS_FILE, 'w') as f: json.dump(sudo_users, f, indent=2)
        with open(PHOTO_FILE, 'w') as f: json.dump({"photo": bot_photo}, f, indent=2)
    except Exception:
        pass

load_data()

# ===================== HELPER FUNCTIONS =====================
def is_owner(user_id: int) -> bool: return str(user_id) in owners or user_id in OWNER_IDS
def is_sudo(user_id: int) -> bool: return str(user_id) in sudo_users or is_owner(user_id)
def is_authorized(user_id: int) -> bool: return is_sudo(user_id)

def get_current_settings():
    if current_mode == "MEDIUM": return {"delay": 0.5, "batch_size": 1}
    else: return {"delay": 0.001, "batch_size": 50}

async def resolve_target_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    msg = update.effective_message
    if context and hasattr(context, 'args') and context.args:
        arg = context.args[0].strip()
        if arg.startswith('@'):
            try:
                chat = await context.bot.get_chat(arg)
                return str(chat.id)
            except Exception:
                return None
        return arg
    
    text = (msg.text or msg.caption or "").strip()
    parts = text.split()
    if len(parts) > 1:
        arg = parts[1].strip()
        if arg.startswith('@'):
            try:
                chat = await context.bot.get_chat(arg)
                return str(chat.id)
            except Exception:
                return None
        return arg
        
    if msg.reply_to_message and msg.reply_to_message.from_user:
        return str(msg.reply_to_message.from_user.id)
        
    return None

# ===================== ULTRA FAST MESSAGE HANDLING =====================
async def send_message_ultra_fast(context, chat_id: int, message: str, reply_to: int = None, retry_count: int = 0) -> bool:
    delay = get_current_settings()["delay"]
    try:
        await context.bot.send_message(
            chat_id=chat_id, text=message, parse_mode=ParseMode.HTML,
            disable_web_page_preview=True, reply_to_message_id=reply_to,
            read_timeout=30, write_timeout=30, connect_timeout=30, pool_timeout=30
        )
        await asyncio.sleep(delay)
        return True
    except RetryAfter as e:
        await asyncio.sleep(e.retry_after + 0.1)
        return await send_message_ultra_fast(context, chat_id, message, reply_to, retry_count + 1)
    except (TimedOut, NetworkError):
        await asyncio.sleep(0.5)
        if retry_count < 99999: return await send_message_ultra_fast(context, chat_id, message, reply_to, retry_count + 1)
        return False
    except Exception as e:
        if "Flood" in str(e):
            await asyncio.sleep(1)
            return await send_message_ultra_fast(context, chat_id, message, reply_to, retry_count + 1)
        return False

async def send_message_batch(context, chat_id: int, messages: list, reply_to: int = None) -> tuple:
    tasks = [send_message_ultra_fast(context, chat_id, msg, reply_to) for msg in messages]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return sum(1 for r in results if r is True), sum(1 for r in results if r is False or isinstance(r, Exception))

# ===================== WORKER FUNCTIONS =====================
async def raid_worker_ultra(chat_id: int, target_name: str, target_user_id: int, count: int, context, attacker_msg_id: int, target_reply_id: int = None):
    if is_owner(target_user_id):
        await context.bot.send_message(chat_id=chat_id, text="𝗧𝗨 𝗔𝗣𝗡𝗘 𝗕𝗔𝗔𝗣 𝗣𝗘 𝗥𝗔𝗜𝗗 𝗞𝗔𝗥𝗘𝗚𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗖𝗛𝗢𝗗 𝗞𝗘 𝗙𝗘𝗞 𝗗𝗨𝗡𝗚𝗔", reply_to_message_id=attacker_msg_id)
        return
    
    chat_id_str = str(chat_id)
    active_operations[chat_id_str] = {'type': 'raid', 'stop': False, 'target': target_name}
    batch_size = get_current_settings()["batch_size"]
    safe_name = html.escape(target_name)
    
    try:
        await send_message_ultra_fast(context, chat_id, "<b>𝐀sʜɪsʜ 𝐃ᴇsᴛʀᴜᴄᴛɪᴏɴ 𝐁ᴏᴛ — 𝐓ᴜᴍʜᴀʀɪ 𝐌ᴀɪʏᴀ 𝐃ᴀғᴀɴ 𝐊ᴀʀɴᴇ 𝐊ᴇ 𝐋ɪʏᴇ 𝐑ᴇᴀᴅʏ ❤️‍🔥❤️‍🔥</b>", reply_to=attacker_msg_id)
        batch_messages = []
        for i in range(count):
            if active_operations.get(chat_id_str, {}).get('stop', False): break
            msg = html.escape(random.choice(RAID_MESSAGES))
            batch_messages.append(f'<a href="tg://user?id={target_user_id}">{safe_name}</a> {msg}')
            
            if len(batch_messages) >= batch_size:
                await send_message_batch(context, chat_id, batch_messages, reply_to=target_reply_id)
                batch_messages = []
        
        if batch_messages and not active_operations.get(chat_id_str, {}).get('stop', False):
            await send_message_batch(context, chat_id, batch_messages, reply_to=target_reply_id)
        
        final_msg = f'<a href="tg://user?id={target_user_id}">{safe_name}</a> <b>𝗞𝗜𝗗𝗘 𝗞𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗗𝗔𝗜 𝗗𝗢𝗡𝗘</b>'
        await send_message_ultra_fast(context, chat_id, final_msg)
    except Exception:
        pass
    finally:
        if chat_id_str in active_operations: del active_operations[chat_id_str]

async def spam_worker_ultra(chat_id: int, text: str, count: int, context, update_id: int, target_reply_id: int = None, target_name: str = None, target_id: int = None):
    chat_id_str = str(chat_id)
    active_operations[chat_id_str] = {'type': 'spam', 'stop': False}
    batch_size = get_current_settings()["batch_size"]
    
    safe_text = html.escape(text)
    if target_name and target_id:
        safe_name = html.escape(target_name)
        formatted_text = f'<a href="tg://user?id={target_id}">{safe_name}</a> {safe_text}'
    else:
        formatted_text = safe_text

    try:
        await send_message_ultra_fast(context, chat_id, "<b>𝐀sʜɪsʜ 𝐃ᴇsᴛʀᴜᴄᴛɪᴏɴ 𝐁ᴏᴛ — 𝐓ᴜᴍʜᴀʀɪ 𝐌ᴀɪʏᴀ 𝐃ᴀғᴀɴ 𝐊ᴀʀɴᴇ 𝐊ᴇ 𝐋ɪʏᴇ 𝐑ᴇᴀᴅʏ ❤️‍🔥❤️‍🔥</b>", reply_to=update_id)
        batch_messages = []
        for i in range(count):
            if active_operations.get(chat_id_str, {}).get('stop', False): break
            batch_messages.append(formatted_text)
            
            if len(batch_messages) >= batch_size:
                await send_message_batch(context, chat_id, batch_messages, reply_to=target_reply_id)
                batch_messages = []
        
        if batch_messages and not active_operations.get(chat_id_str, {}).get('stop', False):
            await send_message_batch(context, chat_id, batch_messages, reply_to=target_reply_id)
        
        if target_name and target_id:
            safe_name = html.escape(target_name)
            final_msg = f'<a href="tg://user?id={target_id}">{safe_name}</a> <b>𝗞𝗜𝗗𝗘 𝗞𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗗𝗔𝗜 𝗗𝗢𝗡𝗘</b>'
        else:
            final_msg = "<b>𝗞𝗜𝗗𝗘 𝗞𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗗𝗔𝗜 𝗗𝗢𝗡𝗘</b>"
            
        await send_message_ultra_fast(context, chat_id, final_msg)
    except Exception:
        pass
    finally:
        if chat_id_str in active_operations: del active_operations[chat_id_str]

# ===================== START COMMAND =====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message: return
    add_to_group_url = f"https://t.me/{BOT_USERNAME}?startgroup=true"
    keyboard = [
        [InlineKeyboardButton("𝐇ᴇʟᴘ 𝐂ᴍᴅ", callback_data="btn_help"), InlineKeyboardButton("𝐀ʙᴏᴜᴛ", callback_data="btn_about")],
        [InlineKeyboardButton("𝐃ᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/ll_NAGUMO_ll"), InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url="https://t.me/Rinnegan_anime_group")],
        [InlineKeyboardButton("𝐂ʟɪᴄᴋ 𝐇ᴇʀᴇ 𝐓ᴏ 𝐒ᴇᴇ 𝐌ᴀɢɪᴄ ✨", url=add_to_group_url)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await update.effective_message.reply_photo(photo=bot_photo, caption=START_CAPTION, parse_mode="HTML", reply_markup=reply_markup)
    except Exception:
        await update.effective_message.reply_text(text=START_CAPTION, parse_mode="HTML", reply_markup=reply_markup)

# ===================== BUTTON HANDLER =====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 𝐁ᴀᴄᴋ ᴛᴏ 𝐌ᴀɪɴ 𝐌ᴇɴᴜ", callback_data="btn_back")]])
    if query.data == "btn_help":
        await query.message.reply_text(HELP_TEXT, parse_mode="HTML", reply_markup=back_keyboard)
    elif query.data == "btn_about":
        await query.message.reply_text(ABOUT_TEXT, parse_mode="HTML", reply_markup=back_keyboard)
    elif query.data == "btn_back":
        try: await query.message.delete()
        except Exception: pass

# ===================== STATUS & MODE COMMANDS =====================
async def alive_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): 
        return await update.effective_message.reply_text("𝗢𝗬𝗘 𝗧𝗔𝗧𝗧𝗘 𝗧𝗘𝗥𝗘 𝗕𝗔𝗔𝗣 𝗞𝗔 𝗕𝗢𝗧 𝗡𝗔𝗛𝗜 𝗛 𝗝𝗔𝗔 𝗣𝗘𝗟𝗘 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗢 𝗕𝗔𝗔𝗣 𝗕𝗢𝗟 𝗞𝗘 𝗔𝗔 𝗪𝗢 𝗗𝗘𝗚𝗔 𝗦𝗨𝗗𝗢", reply_to_message_id=update.effective_message.message_id)
    await update.effective_message.reply_text("𝗧𝗘𝗥𝗜 𝗠𝗞𝗖 𝗦𝗢𝗡𝗘 𝗕𝗛𝗜 𝗡𝗔𝗛𝗜 𝗗𝗘𝗧𝗔 𝗕𝗢𝗟 𝗧𝗔𝗧𝗧𝗘 𝗞𝗬𝗔 𝗞𝗔𝗠 𝗛 𝗕𝗔𝗦𝗦", reply_to_message_id=update.effective_message.message_id)

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): 
        return await update.effective_message.reply_text("𝗢𝗬𝗘 𝗧𝗔𝗧𝗧𝗘 𝗧𝗘𝗥𝗘 𝗕𝗔𝗔𝗣 𝗞𝗔 𝗕𝗢𝗧 𝗡𝗔𝗛𝗜 𝗛 𝗝𝗔𝗔 𝗣𝗘𝗟𝗘 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗢 𝗕𝗔𝗔𝗣 𝗕𝗢𝗟 𝗞𝗘 𝗔𝗔 𝗪𝗢 𝗗𝗘𝗚𝗔 𝗦𝗨𝗗𝗢", reply_to_message_id=update.effective_message.message_id)
    start_time = time.time()
    sent_msg = await update.effective_message.reply_text("𝗠𝗔𝗜𝗬𝗔 𝗖𝗛𝗢𝗗𝗡𝗘 𝗞𝗘 𝗟𝗜𝗬𝗘 𝗥𝗘𝗔𝗗𝗬 𝗕𝗢𝗦𝗦 𝗕𝗔𝗧𝗔𝗢 𝗞𝗜𝗦 𝗞𝗢 𝗖𝗛𝗢𝗗𝗡𝗔 𝗛", reply_to_message_id=update.effective_message.message_id)
    response_time = (time.time() - start_time) * 1000
    await update.effective_message.reply_text(f"ᴘɪɴɢ: {response_time:.2f}ᴍꜱ | Mode: {current_mode}", reply_to_message_id=sent_msg.message_id)

async def set_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_photo
    user_id, msg = update.effective_user.id, update.effective_message
    if not is_owner(user_id): return await msg.reply_text("❌ Only owner can change start photo!", reply_to_message_id=msg.message_id)
    photo_id = None
    if msg.reply_to_message and msg.reply_to_message.photo: photo_id = msg.reply_to_message.photo[-1].file_id
    elif msg.photo: photo_id = msg.photo[-1].file_id
    if photo_id:
        bot_photo = photo_id
        save_data()
        await msg.reply_text("✅ <b>Start Photo Successfully Updated!</b>", parse_mode="HTML", reply_to_message_id=msg.message_id)
    else:
        await msg.reply_text("⚠️ <b>Photo ke upar reply karke <code>.setphoto</code> bhejo!</b>", parse_mode="HTML", reply_to_message_id=msg.message_id)

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id, chat_id, msg = update.effective_user.id, update.effective_chat.id, update.effective_message
    if not is_authorized(user_id): return await msg.reply_text("𝗢𝗬𝗘 𝗧𝗔𝗧𝗧𝗘 𝗧𝗘𝗥𝗘 𝗕𝗔𝗔𝗣 𝗞𝗔 𝗕𝗢𝗧 𝗡𝗔𝗛𝗜 𝗛 𝗝𝗔𝗔 𝗣𝗘𝗟𝗘 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗢 𝗕𝗔𝗔𝗣 𝗕𝗢𝗟 𝗞𝗘 𝗔𝗔 𝗪𝗢 𝗗𝗘𝗚𝗔 𝗦𝗨𝗗𝗢", reply_to_message_id=msg.message_id)
    chat_id_str = str(chat_id)
    if chat_id_str in active_operations: 
        active_operations[chat_id_str]['stop'] = True
    await msg.reply_text("𝗗𝗜𝗞𝗛𝗔 𝗗𝗜 𝗧𝗔𝗧𝗧𝗘 𝗧𝗨𝗡𝗘 𝗔𝗣𝗡𝗜 𝗔𝗨𝗞𝗔𝗧 😒😒", reply_to_message_id=msg.message_id)

async def set_medium_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_mode
    user_id, msg = update.effective_user.id, update.effective_message
    if not is_authorized(user_id): return await msg.reply_text("𝗢𝗬𝗘 𝗧𝗔𝗧𝗧𝗘 𝗧𝗘𝗥𝗘 𝗕𝗔𝗔𝗣 𝗞𝗔 𝗕𝗢𝗧 𝗡𝗔𝗛𝗜 𝗛 𝗝𝗔𝗔 𝗣𝗘𝗟𝗘 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗢 𝗕𝗔𝗔𝗣 𝗕𝗢𝗟 𝗞𝗘 𝗔𝗔 𝗪𝗢 𝗗𝗘𝗚𝗔 𝗦𝗨𝗗𝗢", reply_to_message_id=msg.message_id)
    current_mode = "MEDIUM"
    text = "<b>𝐀sʜɪsʜ 𝐃ᴇsᴛʀᴜᴄᴛɪᴏɴ 𝐁ᴏᴛ ❤️‍🔥❤️‍🔥</b>\n\n<b>𝐌ᴇᴅɪᴜᴍ 𝐌ᴏᴅᴇ: 𝐀ᴄᴛɪᴠᴀᴛᴇᴅ</b>\n<b>𝐏ᴏᴡᴇʀ 𝐋ᴇᴠᴇʟ: 𝐌ᴇᴅɪᴜᴍ</b>\n<b>𝐌ᴀᴀ 𝐂ʜᴏᴅɴᴇ 𝐊ᴇ 𝐋ɪʏᴇ 𝐑ᴇᴀᴅʏ...</b>\n<b>𝐌ᴏᴅᴇ 𝐂ʜᴀɴɢᴇ 𝐒ᴜᴄᴄᴇssғᴜʟ</b>"
    await msg.reply_text(text, parse_mode="HTML", reply_to_message_id=msg.message_id)

async def set_hard_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_mode
    user_id, msg = update.effective_user.id, update.effective_message
    if not is_authorized(user_id): return await msg.reply_text("𝗢𝗬𝗘 𝗧𝗔𝗧𝗧𝗘 𝗧𝗘𝗥𝗘 𝗕𝗔𝗔𝗣 𝗞𝗔 𝗕𝗢𝗧 𝗡𝗔𝗛𝗜 𝗛 𝗝𝗔𝗔 𝗣𝗘𝗟𝗘 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗢 𝗕𝗔𝗔𝗣 𝗕𝗢𝗟 𝗞𝗘 𝗔𝗔 𝗪𝗢 𝗗𝗘𝗚𝗔 𝗦𝗨𝗗𝗢", reply_to_message_id=msg.message_id)
    current_mode = "HARD"
    text = "<b>𝐀sʜɪsʜ 𝐃ᴇsᴛʀᴜᴄᴛɪᴏɴ 𝐁ᴏᴛ</b>\n\n<b>𝐇ᴀʀᴅ 𝐌ᴏᴅᴇ: 𝐀ᴄᴛɪᴠᴀᴛᴇᴅ</b>\n<b>𝐏ᴏᴡᴇʀ 𝐋ᴇᴠᴇʟ: 𝐌ᴀxɪᴍᴜᴍ</b>\n<b>𝐌ᴀᴀ 𝐂ʜᴏᴅɴᴇ 𝐊ᴇ 𝐋ɪʏᴇ 𝐑ᴇᴀᴅʏ...</b>\n<b>𝐌ᴏᴅᴇ 𝐂ʜᴀɴɢᴇ 𝐒ᴜᴄᴄᴇssғᴜʟ</b>"
    await msg.reply_text(text, parse_mode="HTML", reply_to_message_id=msg.message_id)

# ===================== ADVANCED ADMIN COMMANDS =====================
async def add_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id, msg = update.effective_user.id, update.effective_message
    if not is_owner(user_id): return await msg.reply_text("❌ Only owner can add new owners!", reply_to_message_id=msg.message_id)
    target_id = await resolve_target_id(update, context)
    if not target_id: return await msg.reply_text("📝 Usage: .addowner [id] or reply to a user", reply_to_message_id=msg.message_id)
    
    owners[target_id] = {'added_by': str(user_id), 'added_date': datetime.now().isoformat()}
    save_data()
    await msg.reply_text(f"✅ User {target_id} added as OWNER!", reply_to_message_id=msg.message_id)

async def del_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id, msg = update.effective_user.id, update.effective_message
    if not is_owner(user_id): return await msg.reply_text("❌ Only owner can remove owners!", reply_to_message_id=msg.message_id)
    target_id = await resolve_target_id(update, context)
    if not target_id: return await msg.reply_text("📝 Usage: .removeowner [id] or reply to a user", reply_to_message_id=msg.message_id)
    
    if target_id == MAIN_OWNER_ID: return await msg.reply_text("𝗢𝗬𝗘 𝗧𝗔𝗧𝗧𝗘 𝗬𝗘 𝗠𝗘𝗥𝗔 𝗠𝗔𝗜𝗡 𝗕𝗔𝗔𝗣 𝗛𝗔𝗜, 𝗜𝗦𝗞𝗢 𝗞𝗢𝗜 𝗡𝗔𝗛𝗜 𝗛𝗔𝗧𝗔 𝗦𝗔𝗞𝗧𝗔! 🤬", reply_to_message_id=msg.message_id)
    if target_id not in owners: return await msg.reply_text("❌ Not an owner!", reply_to_message_id=msg.message_id)
    del owners[target_id]
    save_data()
    await msg.reply_text(f"✅ User {target_id} removed from OWNERS!", reply_to_message_id=msg.message_id)

async def add_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id, msg = update.effective_user.id, update.effective_message
    if not is_owner(user_id): return await msg.reply_text("❌ Only owner can add sudo users!", reply_to_message_id=msg.message_id)
    target_id = await resolve_target_id(update, context)
    if not target_id: return await msg.reply_text("📝 Usage: .addsudo [id] or reply to a user", reply_to_message_id=msg.message_id)
    
    sudo_users[target_id] = {'added_by': str(user_id), 'added_date': datetime.now().isoformat()}
    save_data()
    await msg.reply_text(f"𝗔𝗔𝗝 𝗦𝗘 𝗧𝗨 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗔 𝗕𝗘𝗧𝗔 𝗛 𝗝𝗔𝗔 𝗝𝗘𝗘 𝗟𝗘 𝗔𝗣𝗡𝗜 𝗭𝗜𝗡𝗗𝗔𝗚𝗜\n\n✅ User {target_id} added as sudo user!", reply_to_message_id=msg.message_id)

async def del_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id, msg = update.effective_user.id, update.effective_message
    if not is_owner(user_id): return await msg.reply_text("❌ Only owner can remove sudo users!", reply_to_message_id=msg.message_id)
    target_id = await resolve_target_id(update, context)
    if not target_id: return await msg.reply_text("📝 Usage: .dissudo [id] or reply to a user", reply_to_message_id=msg.message_id)
    
    if target_id not in sudo_users: return await msg.reply_text("❌ User is not a sudo user!", reply_to_message_id=msg.message_id)
    del sudo_users[target_id]
    save_data()
    await msg.reply_text(f"𝗝𝗔𝗔 𝗧𝗔𝗧𝗧𝗘 𝗧𝗨𝗡𝗘 𝗔𝗣𝗡𝗘 𝗣𝗔𝗣𝗔 𝗞𝗘 𝗦𝗔𝗧𝗛 𝗚𝗔𝗗𝗗𝗔𝗥𝗜 𝗞𝗜 𝗛 𝗝𝗔𝗔 𝗧𝗨𝗝𝗛𝗘 𝗩𝗔𝗦𝗛𝗜𝗬𝗔𝗧 𝗦𝗘 𝗔𝗕 𝗟𝗢𝗗𝗔 𝗡𝗔𝗛𝗜 𝗠𝗜𝗟𝗘𝗚𝗔 𝗝𝗔𝗔 𝗠𝗔𝗔 𝗖𝗛𝗨𝗗𝗔\n\n✅ User {target_id} removed from sudo users!", reply_to_message_id=msg.message_id)

async def sudolist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id, msg = update.effective_user.id, update.effective_message
    if not is_authorized(user_id): return await msg.reply_text("𝗢𝗬𝗘 𝗧𝗔𝗧𝗧𝗘 𝗧𝗘𝗥𝗘 𝗕𝗔𝗔𝗣 𝗞𝗔 𝗕𝗢𝗧 𝗡𝗔𝗛𝗜 𝗛 𝗝𝗔𝗔 𝗣𝗘𝗟𝗘 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗢 𝗕𝗔𝗔𝗣 𝗕𝗢𝗟 𝗞𝗘 𝗔𝗔 𝗪𝗢 𝗗𝗘𝗚𝗔 𝗦𝗨𝗗𝗢", reply_to_message_id=msg.message_id)
    message = "📋 𝗦𝗨𝗗𝗢 𝗨𝗦𝗘𝗥𝗦 𝗟𝗜𝗦𝗧 📋\n\n👑 𝗢𝗪𝗡𝗘𝗥𝗦:\n"
    for uid in owners:
        message += f"   • <code>{uid}</code> (God Owner 👑)\n" if uid == MAIN_OWNER_ID else f"   • <code>{uid}</code>\n"
    message += "\n⚡ 𝗦𝗨𝗗𝗢 𝗨𝗦𝗘𝗥𝗦:\n"
    if sudo_users:
        for uid in sudo_users: message += f"   • <code>{uid}</code>\n"
    else: message += "   • No sudo users added yet.\n"
    await msg.reply_text(message, parse_mode=ParseMode.HTML, reply_to_message_id=msg.message_id)

# ===================== ALL TEXT COMMAND ROUTING (./!) =====================
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message: return
    user_id, chat_id, msg = update.effective_user.id, update.effective_chat.id, update.effective_message
    text = (msg.text or msg.caption or "").strip()
    if not text: return
    parts = text.split()
    if not parts: return
    
    raw_cmd = parts[0].lower()
    if not raw_cmd.startswith(('.', '/', '!')): return
    cmd = raw_cmd.lstrip('./!').split('@')[0]
    
    context.args = parts[1:]
    
    if cmd == 'setphoto': return await set_photo(update, context)
    if cmd == 'medium': return await set_medium_mode(update, context)
    if cmd == 'hard': return await set_hard_mode(update, context)
    if cmd == 'ping': return await ping_command(update, context)
    if cmd == 'alive': return await alive_command(update, context)
    if cmd == 'stop': return await stop_command(update, context)
    
    if cmd == 'addsudo': return await add_sudo(update, context)
    if cmd == 'addowner': return await add_owner(update, context)
    if cmd == 'dissudo': return await del_sudo(update, context)
    if cmd == 'sudolist': return await sudolist_command(update, context)
    if cmd in ['removeowner', 'delowner']: return await del_owner(update, context)
    
    if cmd == 'raid':
        if not is_authorized(user_id): return await msg.reply_text("𝗢𝗬𝗘 𝗧𝗔𝗧𝗧𝗘 𝗧𝗘𝗥𝗘 𝗕𝗔𝗔𝗣 𝗞𝗔 𝗕𝗢𝗧 𝗡𝗔𝗛𝗜 𝗛 𝗝𝗔𝗔 𝗣𝗘𝗟𝗘 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗢 𝗕𝗔𝗔𝗣 𝗕𝗢𝗟 𝗞𝗘 𝗔𝗔 𝗪𝗢 𝗗𝗘𝗚𝗔 𝗦𝗨𝗗𝗢", reply_to_message_id=msg.message_id)
        target_id, target_name = None, None
        
        if len(parts) >= 2 and parts[-1].startswith('@'):
            try:
                chat = await context.bot.get_chat(f"@{parts[-1][1:]}")
                target_id, target_name = chat.id, chat.first_name or parts[-1][1:]
                parts = parts[:-1]
            except Exception: return await msg.reply_text("❌ User not found!", reply_to_message_id=msg.message_id)
            
        if not target_id and msg.reply_to_message:
            target_id, target_name = msg.reply_to_message.from_user.id, msg.reply_to_message.from_user.first_name
            
        count = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 999999
        target_reply_id = msg.reply_to_message.message_id if msg.reply_to_message else None
        
        asyncio.create_task(raid_worker_ultra(chat_id, target_name, target_id, count, context, msg.message_id, target_reply_id))
        
    elif cmd == 'spam':
        if not is_authorized(user_id): return await msg.reply_text("𝗢𝗬𝗘 𝗧𝗔𝗧𝗧𝗘 𝗧𝗘𝗥𝗘 𝗕𝗔𝗔𝗣 𝗞𝗔 𝗕𝗢𝗧 𝗡𝗔𝗛𝗜 𝗛 𝗝𝗔𝗔 𝗣𝗘𝗟𝗘 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗢 𝗕𝗔𝗔𝗣 𝗕𝗢𝗟 𝗞𝗘 𝗔𝗔 𝗪𝗢 𝗗𝗘𝗚𝗔 𝗦𝗨𝗗𝗢", reply_to_message_id=msg.message_id)
        if len(parts) < 3: return await msg.reply_text("Usage: .spam 50 text (reply to target to mention)", reply_to_message_id=msg.message_id)
        count = int(parts[1]) if parts[1].isdigit() else 999999
        spam_text = " ".join(parts[2:])
        
        target_reply_id = msg.reply_to_message.message_id if msg.reply_to_message else None
        target_spam_name = msg.reply_to_message.from_user.first_name if msg.reply_to_message else None
        target_spam_id = msg.reply_to_message.from_user.id if msg.reply_to_message else None
        
        asyncio.create_task(spam_worker_ultra(chat_id, spam_text, count, context, msg.message_id, target_reply_id, target_spam_name, target_spam_id))

# ===================== ERROR HANDLER =====================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    pass

# ===================== MAIN FUNCTION =====================
def main():
    application = Application.builder().token(BOT_TOKEN).connect_timeout(60.0).read_timeout(60.0).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("addowner", add_owner))
    application.add_handler(CommandHandler("removeowner", del_owner))
    application.add_handler(CommandHandler("delowner", del_owner))
    application.add_handler(CommandHandler("addsudo", add_sudo))
    application.add_handler(CommandHandler("dissudo", del_sudo))
    application.add_handler(CommandHandler("sudolist", sudolist_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("alive", alive_command))
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CommandHandler("medium", set_medium_mode))
    application.add_handler(CommandHandler("hard", set_hard_mode))
    
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_messages))
    application.add_error_handler(error_handler)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
