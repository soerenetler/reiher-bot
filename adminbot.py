import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, Update, User, Bot)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext,PicklePersistence, 
                          ConversationHandler, CallbackQueryHandler, PollAnswerHandler, PollHandler, TypeHandler)

from states import BAHNHOF_STATES

ADMIN_STATES = {key: value for value, key in enumerate(["ADMIN_TOKEN_FRAGE",
                                                        "ADMIN_MODE",
                                                        "MESSAGE_AN",
                                                        "MESSAGE_CONTENT",
                                                        "MESSAGE_CONFIRM",
                                                        "END"
                                                        ],10)}

def exit_admin(update, context):
    update.message.reply_text("Du kehrst nun in den Reiherbot zurück und kannst ihn mit /start wieder starten.")
    return ADMIN_STATES["END"]

def validate_admin_token(update, context):
    if update.message.text == "ADMIN_TOKEN":
        update.message.reply_text("Danke. Du bist nun als Admin eingeloggt")
        update.message.reply_text("Mit /hilfe bekommst du eine Übersicht über alle Funktionen des Admin Modus")
        return ADMIN_STATES["ADMIN_MODE"]
    else:
        update.message.reply_text("Der Admin Token stimmt nicht. Du bist nun zurück im Start Zusand und kannst den Reiherbot mit /start erneut starten.")
        return ADMIN_STATES["END"]

def message_an(update, context):
    update.message.reply_text("An wen möchtest du eine Nachricht schicken? Schreibe @all um an alle Nutzer eine Nachricht zu schreiben")
    return ADMIN_STATES["MESSAGE_AN"]

def message_content(update, context):
    context.chat_data["broadcast_to"] = update.message.text
    update.message.reply_text("Was möchstest du an {} schicken?".format(update.message.text))
    return ADMIN_STATES["MESSAGE_CONTENT"]

def message_confirm(update, context):
    context.chat_data["broadcast_content"] = update.message.text
    update.message.reply_text("Bist du sicher, dass du folgende Nachricht an {} schicken möchtest? \n {}".format(context.chat_data["broadcast_to"], context.chat_data["broadcast_content"]))
    return ADMIN_STATES["MESSAGE_CONFIRM"]

def message_send(update, context):
    Bot("1343354005:AAFH3uSlrQMVDrMcU_JfdurwC6gcuHYms84").send_message(chat_id=context.chat_data["broadcast_to"], text=context.chat_data["broadcast_content"])
    update.message.reply_text("Deine Nachricht wurde verschickt.")
    return ADMIN_STATES["ADMIN_MODE"]

admin_conv = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r'^(.)+'), validate_admin_token)],
        states={            
            ADMIN_STATES["ADMIN_MODE"]: [CommandHandler('broadcast', message_an)],
            ADMIN_STATES["MESSAGE_AN"]: [MessageHandler(Filters.regex(r'^(.)+'), message_content)],
            ADMIN_STATES["MESSAGE_CONTENT"]: [MessageHandler(Filters.regex(r'^(.)+'), message_confirm)],
            ADMIN_STATES["MESSAGE_CONFIRM"]: [MessageHandler(Filters.regex(r'^(.)+'), message_send)]
        },
        fallbacks=[
            CommandHandler('exit', exit_admin),
        ],
        map_to_parent={
            ADMIN_STATES["END"]: BAHNHOF_STATES["END"],
        },
    )

