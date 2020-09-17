from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton,InlineKeyboardMarkup)

from states import ABSCHLUSS_STATES

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def get_feedback_callback_query(update, context):
    query = update.callback_query

    query.answer()
    query.edit_message_reply_markup(InlineKeyboardMarkup([]))
    if query.data == "ueberspringen":
        query.message.reply_text('🐾')
        return get_feedback(query, context)


def get_feedback(update, context):
    update.message.reply_text(
        'Unsere Demotour ist hier zu Ende. Ich hoffe, du hattest viel Spaß und konntest Golm von einer neuen Seite kennenlernen. '
        'Auf jeden Fall hast du dir die Golm-Medaillie verdient! 🏅')
    
    photo_files = update.message.from_user.get_profile_photos().photos
    if photo_files:
        if photo_files[0]:
            photo_files[0][-1].get_file().download('user.jpg')

    update.message.reply_photo(open("assets/golm_medaillie.png", 'rb'))
    update.message.reply_text("Sag uns gern deine Meinung zum Rundgang. Schreib dein Feedback in den Chat oder sende uns eine Sprachnachricht.")
    return ABSCHLUSS_STATES["ENDE"]