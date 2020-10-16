from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton,InlineKeyboardMarkup, Update)

from states import ABSCHLUSS_STATES

import logging
from actions.utils import log
from actions import utils

from PIL import Image

import base64
from io import BytesIO

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='bot.log',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

@log(logger)
def get_feedback_callback_query(update, context):
    query = update.callback_query

    query.answer()
    query.edit_message_reply_markup(InlineKeyboardMarkup([]))
    if query.data == "weiter":
        query.message.reply_text('🐾')
        return get_feedback(query, context)

@log(logger)
def get_feedback(update, context):
    update.message.reply_text(
        'Unsere Demotour ist hier zu Ende. Ich hoffe, du hattest viel Spaß und konntest Golm von einer neuen Seite kennenlernen. '
        'Auf jeden Fall hast du dir die Golm-Medaillie verdient! 🏅')
    
    

    photo_files = update.from_user.get_profile_photos().photos

    if photo_files:
        if photo_files[0]:
            profile_bytes = photo_files[0][-1].get_file().download_as_bytearray()

            profile_file = BytesIO(profile_bytes)  # convert image to file-like object
            background = Image.open(profile_file)   # img is now PIL Image object
            logger.info(background.size)
            foreground = Image.open('assets/golm_medaillie.png')


            update.message.reply_photo(utils.overlay_images(background, foreground))            
        else:
            update.message.reply_photo(open("assets/golm_medaillie.png", 'rb'))
    else:
        update.message.reply_photo(open("assets/golm_medaillie.png", 'rb'))

    
    update.message.reply_text("Sag uns gern deine Meinung zum Rundgang. Schreib dein Feedback in den Chat oder sende uns eine Sprachnachricht.")
    return ABSCHLUSS_STATES["ENDE"]