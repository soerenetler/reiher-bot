import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton,
                      Sticker, InlineKeyboardButton, InlineKeyboardMarkup, Update)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackContext)

from actions.utils import log

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='./bot.log',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


@log(logger)
def log_update(update: Update, context: CallbackContext):
    pass


def return_end(update: Update, context: CallbackContext):
    return ConversationHandler.END

def entry_conversation(update: Update, context: CallbackContext):
    if context.args:
        keyboard = [[InlineKeyboardButton(
            "🐾 los", callback_data='action:' + context.args[0])]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            'Hi, freut mich, dass du dabei bist! Mit einem klick auf "los" kannst du direkt an die richtige Position in der Route springen',
            reply_markup=reply_markup)
        return None

def default_data(update: Update, context: CallbackContext):
    context.user_data["daten"] = False

def default_name(update: Update, context: CallbackContext):
    context.user_data["name"] = update.message.from_user.first_name

def change_data(update: Update, context: CallbackContext):
    if update.message.text == "Ja" or update.message.text == "Ja, klar 🌻":
        context.user_data["daten"] = True
    else:
        context.user_data["daten"] = False

def change_name(update: Update, context: CallbackContext):
    context.user_data["name"] = update.message.text

def pass_func(update: Update, context: CallbackContext):
    pass

action_functions = {"change_name": change_name,
                    "change_data": change_data,
                    "default_name": default_name,
                    "default_data": default_data,
                    "entry_conversation": entry_conversation,
                    "return_end": return_end,
                    "pass_func": pass_func}