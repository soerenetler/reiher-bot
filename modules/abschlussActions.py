from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton)

from states import ABSCHLUSS_STATES

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def get_feedback(update, context):
    update.message.reply_text(
        'Unsere Demotour ist hier zu Ende. Ich hoffe, du hattest viel Spaß und konntest Golm von einer neuen Seite kennenlernen. '
        'Auf jeden Fall hast du dir die Golm-Medaillie verdient! 🏅')
    
    photo_file = update.message.from_user.get_profile_photos().photos[0][-1]
    photo_file.get_file().download('user.jpg')

    update.message.reply_photo("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Die_Kirche_in_Golm.JPG/1200px-Die_Kirche_in_Golm.JPG")
    update.message.reply_text("Sag uns gern deine Meinung zum Rundgang. Schreib dein Feedback in den Chat oder sende uns eine Sprachnachricht.")
    return ABSCHLUSS_STATES["ENDE"]