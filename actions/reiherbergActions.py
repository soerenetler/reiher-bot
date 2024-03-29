import base64
import logging
import os
import re
from io import BytesIO

import yaml
from PIL import Image
from telegram import (CallbackQuery, InlineKeyboardButton,
                      InlineKeyboardMarkup, InputFile, InputMediaPhoto,
                      KeyboardButton, ParseMode, Poll, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, Update)
from telegram.ext import CallbackContext, ConversationHandler

from actions import utils

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def eval_schaetzfrage_bahnhof(update, context):
    schaetzung = int(update.message.text)
    echter_wert = 106
    if schaetzung == echter_wert:
        update.message.reply_text('Nicht schlecht! (Das ist brandenburgisch für "gut gemacht!") 😉',
                                  reply_markup=ReplyKeyboardRemove())
    elif schaetzung >= echter_wert-echter_wert*0.2 and schaetzung <= echter_wert+echter_wert*0.2:
        update.message.reply_text('Du bist schon nah dran!',
                                  reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text('Nicht ganz!',
                                  reply_markup=ReplyKeyboardRemove())


def eval_quiz(update: Update, context: CallbackContext, correct_option_id: int, correct_answer_text: str, wrong_answer_text: str, correct_answer_sticker=None):
    if update.poll_answer.option_ids == [correct_option_id]:
        if correct_answer_sticker:
            update.poll_answer.user.send_sticker(correct_answer_sticker)
        update.poll_answer.user.send_message(correct_answer_text.format(name=context.user_data["name"]),
                                             reply_markup=ReplyKeyboardRemove())
    else:
        update.poll_answer.user.send_message(wrong_answer_text.format(name=context.user_data["name"]),
                                             reply_markup=ReplyKeyboardRemove())


def eval_schaetzfrage_reiherberg(update, context):
    schaetzung = int(re.findall(r"\d{1,}", update.message.text)[0])
    echter_wert = 68
    if schaetzung == echter_wert:
        update.message.reply_text('Richtig!',
                                  reply_markup=ReplyKeyboardRemove())
    elif schaetzung >= echter_wert-echter_wert*0.1 and schaetzung <= echter_wert+echter_wert*0.1:
        update.message.reply_text('Fast!',
                                  reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text('Knapp daneben!',
                                  reply_markup=ReplyKeyboardRemove())


def eval_kirche_wortraetsel(update, context):
    antwort = update.message.text
    echter_wert = "Kaiser-Friedrich-Kirche"

    if re.sub('\W+', '', antwort.lower()) == re.sub('\W+', '', echter_wert.lower()):
        update.message.reply_text('Richtig!',
                                  reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text('Fast!', reply_markup=ReplyKeyboardRemove())


def eval_storchenbank(update, context):
    antwort = update.message.text
    echter_wert = "2012"
    if antwort.lower() == echter_wert.lower():
        update.message.reply_text('Du hast die Tafel also entdeckt! Dort werden die Rückkehrzeiten und der Nachwuchs des Storchenpaares festgehalten.',
                                  reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text(
            'Fast! Neben der Storchenbank findest du eine Tafel, auf der die Rückkehrzeiten und der Nachwuchs des Storchenpaares festgehalten werden.', reply_markup=ReplyKeyboardRemove())


def reiherberg_medaille(update, context):
    try:
        photo_files = update.from_user.get_profile_photos(
        ).photos[0][-1].get_file().download_as_bytearray()
        # convert image to file-like object
        profile_file = BytesIO(photo_files)
        # img is now PIL Image object
        background = Image.open(profile_file)
        logger.info(background.size)
        foreground = Image.open('assets/Skyline_02_gelb.png')

        update.message.reply_photo(
            utils.overlay_images(background, foreground))
    except:
        update.message.reply_photo(
            open("assets/Skyline_02_gelb.png", 'rb'))


action_functions = {"eval_schaetzfrage_bahnhof": eval_schaetzfrage_bahnhof,
                    "eval_schaetzfrage_reiherberg": eval_schaetzfrage_reiherberg,
                    "eval_kirche_wortraetsel": eval_kirche_wortraetsel,
                    "eval_storchenbank": eval_storchenbank,
                    "reiherberg_medaille": reiherberg_medaille,
                    "eval_quiz": eval_quiz
                    }
