from telegram import (ParseMode, InputFile, InputMediaPhoto, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Poll, Update, CallbackQuery)
from telegram.ext import CallbackContext, ConversationHandler
from PIL import Image
import re

import base64
from io import BytesIO
import yaml

from states import BAHNHOF_STATES

from actions import utils, bahnhofActions
from actions.utils import log

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='../logs/bot_log',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

with open(r'actions/bahnhofText.yml') as file:
    bahnhofText = yaml.load(file)

def generate_action(action_set):
    
    @log(logger)
    def action(update: Update, context: CallbackContext):
        for item in bahnhofText[action_set]:

            if "InlineKeyboard" in item:
                keyboard = [[]]
                for button in item["InlineKeyboard"]:
                    if "data" in button:
                        callback_data = button["data"]
                    else:
                        callback_data = None

                    if "url" in button:
                        callback_url = button["url"]
                    else:
                        callback_url = None

                    keyboard[0].append(InlineKeyboardButton(button["text"]["de"], callback_data=callback_data, url=callback_url))
                
                reply_markup = InlineKeyboardMarkup(keyboard)

            elif "ReplyKeyboardMarkup" in item:
                keyboard = [[]]
                for button in item["ReplyKeyboardMarkup"]:
                    keyboard[0].append(button["text"]["de"])

                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            else:
                reply_markup = ReplyKeyboardRemove()

            if item["type"] == "message":
                parse_mode = None
                if "parse_mode" in item:
                    parse_mode = item["parse_mode"]

                if type(update) != CallbackQuery and update.poll_answer:
                    update.poll_answer.user.send_message(item["text"]["de"], reply_markup=reply_markup, parse_mode =parse_mode)
                else:   
                    update.message.reply_text(item["text"]["de"], reply_markup=reply_markup, parse_mode = parse_mode)
            elif item["type"] == "photo":
                if type(update) != CallbackQuery and update.poll_answer:
                    update.poll_answer.user.send_photo(open(item["file"], 'rb'), reply_markup=reply_markup)
                else: 
                    update.message.reply_photo(open(item["file"], 'rb'), reply_markup=reply_markup)
            elif item["type"] == "audio":
                update.message.reply_audio(open(item["file"], 'rb'), title=item["title"], performer=item["performer"], reply_markup=reply_markup)
            elif item["type"] == "poll":
                update.message.reply_poll(question=item["question"],
                              options=item["options"],
                              type=Poll.QUIZ,
                              correct_option_id=item["correct_option_id"],
                              is_anonymous=False
                              )

            elif item["type"] == "media_group":
                photoGroup = [InputMediaPhoto(media=open(photo, 'rb')) for photo in item["files"]]
                update.message.reply_media_group(media=photoGroup)
            elif item["type"] == "sticker":
                if type(update) != CallbackQuery and update.poll_answer:
                    update.poll_answer.user.send_sticker(item["id"])
                else:
                    update.message.reply_sticker(item["id"])
            elif item["type"] == "return":
                if item["state"] == "END":
                    return ConversationHandler.END
                return BAHNHOF_STATES[item["state"]]
            elif item["type"] == "callback":
                query = update.callback_query
                
                query.answer()
                query.edit_message_reply_markup(InlineKeyboardMarkup([]))
                for case in item["conditions"]:
                    if query.data == case["condition"]:
                        return generate_action(case["action"])(query, context)
            elif item["type"] == "function":
                bahnhofActions.action_functions[item["func"]](update, context)
    return action