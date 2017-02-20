#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging, pytz, urllib3
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from db import DBHandler
urllib3.disable_warnings()

# Logger Config
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

# DB Config
db = DBHandler("logger.sqlite")


def start(bot, update):
    chat = update.message.chat
    if chat.type == "private":
        text = "*Oneplus Community Custom Care* ti dà il benvenuto!\n" \
               "Sei registrato per le notifiche!"
        db.set_started(update.message.from_user.id)
        bot.sendMessage(chat.id, text, parse_mode=ParseMode.MARKDOWN)


def msg_parse(bot, update):
    if update.message:
        message = update.message
    elif update.edited_message:
        message = update.edited_message
    chat_id = message.chat.id
    logged = db.log(message)
    admins = db.update_admins(bot.getChatAdministrators(chat_id), chat_id)
    notify = db.notify(message)
    keyboard = [[InlineKeyboardButton("Vai al messaggio", callback_data="goto.%s" % (notify["msg_id"]))]]
    if notify["chat_username"]:
        keyboard = [[InlineKeyboardButton("Vai al messaggio", url="https://t.me/%s/%s" % (notify["chat_username"], notify["msg_id"]))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if notify["tag_to_notify"]:
        for chat_id in notify["tag_to_notify"]:
            text = "%s ti ha nominato in *%s*\n\n_%s_" % (notify["from_user"], notify["chat_title"], notify["msg_text"])
            bot.sendMessage(chat_id, text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    if notify["reply_to_notify"]:
        text = "%s ti ha risposto in *%s*\n\n_%s_" % (notify["from_user"], notify["chat_title"], notify["msg_text"])
        bot.sendMessage(notify["reply_to_notify"], text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    if notify["admin_to_notify"]:
        for admin_id in notify["admin_to_notify"]:
            text = "%s ha chiamato un amministratore in *%s*\n\n_%s_" % (notify["from_user"], notify["chat_title"], notify["msg_text"])
            bot.sendMessage(admin_id, text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater("INSERT TOKEN HERE")
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.audio |
                                  Filters.command |
                                  Filters.contact |
                                  Filters.document |
                                  Filters.photo |
                                  Filters.sticker |
                                  Filters.text |
                                  Filters.video |
                                  Filters.voice |
                                  Filters.status_update, msg_parse, allow_edited=True))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
