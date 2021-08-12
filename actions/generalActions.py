import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton,
                      Sticker, InlineKeyboardButton, InlineKeyboardMarkup, Update, message)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackContext)

import mongoengine
import datetime
import os

from actions.utils import log

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
user_dbname = "reiherbot_user"
interaction_dbname = "reiherbot_interaction"
with open("ca-certificate.crt", "w") as text_file:
            text_file.write(os.getenv('DATABASE_CERT'))
mongoengine.connect(alias=user_dbname, host="mongodb+srv://"+ os.getenv("DATABASE_USERNAME")+":"+ os.getenv("DATABASE_PASSWORD") + "@" +os.getenv("DATABASE_HOST") +"/"+user_dbname+"?authSource=admin&tls=true&tlsCAFile=ca-certificate.crt")
mongoengine.connect(alias=interaction_dbname, host="mongodb+srv://"+ os.getenv("DATABASE_USERNAME")+":"+ os.getenv("DATABASE_PASSWORD") + "@" +os.getenv("DATABASE_HOST") +"/"+interaction_dbname+"?authSource=admin&tls=true&tlsCAFile=ca-certificate.crt")


def log_update(update: Update, context: CallbackContext):
    logger.warning("The incoming update was not handled: {}".format(update))

def return_end(update: Update, context: CallbackContext):
    return ConversationHandler.END

class User(mongoengine.Document):
    user_id = mongoengine.StringField(required=True)
    first_name = mongoengine.StringField(required=True, max_length=50)
    last_name = mongoengine.StringField(max_length=50)
    username = mongoengine.StringField(max_length=50)
    language_code = mongoengine.StringField(max_length=10)
    entry_time = mongoengine.DateTimeField(default=datetime.datetime.utcnow)
    meta = {'db_alias': user_dbname}

class Interaction(mongoengine.Document):
    user = mongoengine.ReferenceField(User)
    update_id  = mongoengine.IntField()
    message = mongoengine.DictField()
    meta = {'db_alias': interaction_dbname}


def entry_conversation(update: Update, context: CallbackContext):
    db_user = User(user_id=str(update.effective_user.id), first_name=update.effective_user.first_name, last_name=update.effective_user.last_name, username=update.effective_user.username, language_code=update.effective_user.language_code)
    db_user.save()
    context.user_data["user_id"] = db_user
    
    Interaction(user=context.user_data["user_id"], update_id=update.update_id, message=update.message.to_dict()).save()

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
    if update.message.text == "Ja" or update.message.text == "Ja, klar 🌻" or update.message.text == "/Ja":
        context.user_data["daten"] = True
    else:
        context.user_data["daten"] = False

def change_name(update: Update, context: CallbackContext):
    context.user_data["name"] = update.message.text

action_functions = {"change_name": change_name,
                    "change_data": change_data,
                    "default_name": default_name,
                    "default_data": default_data,
                    "entry_conversation": entry_conversation,
                    "return_end": return_end,
                    "log_update": log_update}