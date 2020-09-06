from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton)

from states import INFO_STATES

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def get_info(update, context):
    yes_no_keyboard = [['Ja', 'Nein']]

    update.message.reply_text(
        'SHOW INFO?',
        reply_markup=ReplyKeyboardMarkup(yes_no_keyboard, one_time_keyboard=True))

    return INFO_STATES["INFO"]

def info_bahn(update, context):
    logger.info(str(context.bot_data))
    logger.info(str(context.chat_data))
    logger.info(str(context.user_data))
    update.message.reply_voice('https://www.w3schools.com/html/horse.ogg')
    return None