from telegram import (ParseMode, InputFile, InputMediaPhoto, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Poll, Update, CallbackQuery)
from telegram.ext import CallbackContext, ConversationHandler
from PIL import Image

import base64
from io import BytesIO
import yaml

from states import BAHNHOF_STATES

from actions import utils
from actions.utils import log

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='../log/bot.log',
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
                    keyboard[0].append(InlineKeyboardButton(button["text"]["de"], callback_data=button["data"]))

                    reply_markup = InlineKeyboardMarkup(keyboard)
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
                action_functions[item["func"]](update, context)
    return action



def send_bahnhof_gif(update, context):
    im_bytes = update.message.photo[0].get_file().download_as_bytearray()

    im_file = BytesIO(im_bytes)  # convert image to file-like object
    im1 = Image.open(im_file)   # img is now PIL Image object
    im2 = Image.open('assets/bahnhof_alt.jpg')

    gif = utils.generate_gif(im1, im2)

    update.message.reply_document(gif)

def eval_schaetzfrage_bahnhof(update, context):
    schaetzung = int(update.message.text)
    echter_wert = 139
    if schaetzung == echter_wert:
        update.message.reply_text('Nicht schlecht! (Das ist brandenburgisch für "gut gemacht!") 😉',
            reply_markup=ReplyKeyboardRemove())
    elif schaetzung >= echter_wert-echter_wert*0.2 and schaetzung <= echter_wert+echter_wert*0.2:
        update.message.reply_text('Du bist schon nah dran!',
            reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text('Nicht ganz!',
            reply_markup=ReplyKeyboardRemove())

def eval_frage_quiz(update, context):
    update = update["poll_answer"]
    
    if update.option_ids == [1]:
        user = context.user_data["name"] 
        update.user.send_message('Richtig, {} 🎉 '.format(user),
                                reply_markup=ReplyKeyboardRemove())
    
    else:
        update.user.send_message('Nicht ganz!',
                                reply_markup=ReplyKeyboardRemove())

def eval_ubahn_aufloesung(update, context):
    update = update["poll_answer"]

    if update.option_ids == [0]:
        user = context.user_data["name"] 
        update.user.send_message('Richtig, {} 🎉 es war der Kurfürstendamm! '.format(user),
                                reply_markup=ReplyKeyboardRemove())
    
    else:
        update.user.send_message('Hast du das Schild übersehen? Die richtige Antwort war Kurfürstendamm! ',
                                reply_markup=ReplyKeyboardRemove())

def eval_weinmeisterstrasse_aufloesung(update, context):
    update = update["poll_answer"]

    user = context.user_data["name"] 
    if update.option_ids == [0]:
        update.user.send_message('Richtig!',
                                reply_markup=ReplyKeyboardRemove())
    
    else:
        update.user.send_message('Das war nicht der Grund.',
                                reply_markup=ReplyKeyboardRemove())

def eval_fehlerbild_reiherberg(update, context):
    update = update["poll_answer"]

    user = context.user_data["name"] 
    if update.option_ids == [3]:
        update.user.send_message('Stimmt {}! Im Dorfkern gibt es keinen Supermarkt mehr. 🛍️'.format(user),
                                reply_markup=ReplyKeyboardRemove())
    
    else:
        update.user.send_message('Das war nicht der Fehler!',
                                reply_markup=ReplyKeyboardRemove())
        update.user.send_message('Im Dorfkern gibt es keinen Supermarkt mehr (und somit auch kein Supermarktschild). 🛍️',
                                reply_markup=ReplyKeyboardRemove())

def eval_schaetzfrage_reiherberg(update, context):
    schaetzung = int(update.message.text)
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

def foto_contest(update, context):
    if update.message.photo:
        user_id = update.effective_user.id
        name = update.effective_user.name
        photo_file = update.message.photo[-1].get_file()
        photo_file.download("../photos/" + str(user_id) + "_" + name + '.jpg')
        update.message.reply_text('Tolle Aussicht, oder? ')

def eval_kirche_wortraetsel(update, context):
    antwort = update.message.text
    echter_wert = "Kaiser-Friedrich-Kirche"
    if antwort.lower() == echter_wert.lower():
        update.message.reply_text('Richtig!',
            reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text('Fast!', reply_markup=ReplyKeyboardRemove())

def eval_kirche_frage(update, context):
    update = update["poll_answer"]

    user = context.user_data["name"] 
    if update.option_ids == [0]:
        update.user.send_message('Stimmt {}!'.format(user),
                                reply_markup=ReplyKeyboardRemove())
    else:
        update.user.send_message('Ups!', reply_markup=ReplyKeyboardRemove())

def eval_storchenbank(update, context):
    antwort = update.message.text
    echter_wert = "2013"
    if antwort.lower() == echter_wert.lower():
        update.message.reply_text('Richtig!',
            reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text('Fast!', reply_markup=ReplyKeyboardRemove())

def eval_frage_feuwerwehr(update, context):
    update = update["poll_answer"]

    user = context.user_data["name"] 
    if update.option_ids == [1]:
        update.user.send_message('Stimmt {}!'.format(user),
                                reply_markup=ReplyKeyboardRemove())
    else:
        update.user.send_message('Ups!', reply_markup=ReplyKeyboardRemove())

def reiherberg_medaille(update, context):

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

def bahnhof_timetable(update, context):
    update.message.reply_text('Der nächste Zug fährt in 3 Minuten!', reply_markup=ReplyKeyboardRemove())

def get_feedback(update, context):
    if type(update) == CallbackQuery:
        user_id = update.from_user.id
    else:
        user_id = update.effective_user.id
    
    if update.message.voice:
        voice_file = update.message.voice.get_file()
        voice_file.download('../feedback/' + str(user_id) + '.mp3')
    if update.message.text:
        with open('../feedback/'+ str(user_id) + '.txt','a+') as file_object:
            file_object.write(update.message.text + "\n")

def ende_feedback(update, context):
    user_id = update.effective_user.id
    name = update.effective_user.name
    if update.message.text:
        if update.message.text == "Ja, gerne! 😎":
            with open('../feedback/feedback_mapping.txt','a+') as file_object:
                file_object.write(str(user_id) + ", " + name + "\n")
        if update.message.text == "Nein":
            pass


action_functions = {"send_bahnhof_gif": send_bahnhof_gif,
                    "eval_schaetzfrage_bahnhof": eval_schaetzfrage_bahnhof,
                    "eval_frage_quiz": eval_frage_quiz,
                    "eval_ubahn_aufloesung": eval_ubahn_aufloesung,
                    "eval_weinmeisterstrasse_aufloesung": eval_weinmeisterstrasse_aufloesung,
                    "eval_fehlerbild_reiherberg": eval_fehlerbild_reiherberg,
                    "eval_schaetzfrage_reiherberg": eval_schaetzfrage_reiherberg,
                    "foto_contest": foto_contest,
                    "eval_kirche_wortraetsel": eval_kirche_wortraetsel,
                    "eval_kirche_frage": eval_kirche_frage,
                    "eval_storchenbank": eval_storchenbank,
                    "eval_frage_feuwerwehr": eval_frage_feuwerwehr,
                    "reiherberg_medaille": reiherberg_medaille,
                    "bahnhof_timetable": bahnhof_timetable,
                    "get_feedback": get_feedback,
                    "ende_feedback": ende_feedback
                    }