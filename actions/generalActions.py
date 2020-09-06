import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, Sticker, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from states import INTRO_STATES

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def start_name(update, context):
    yes_no_keyboard = [['Ja, gerne! 😎',
                        'Nein, nenn mich lieber anders! 👻']]

    user = update.message.from_user.first_name
    sticker = Sticker("CAACAgIAAxkBAAIGbl8_fWbeUAx5dTF6v9o0gc1bgs9SAAJUAANBtVYMarf4xwiNAfobBA",
                      'AgADVAADQbVWDA',
                      512,512,True)
    update.message.reply_sticker(sticker)
    update.message.reply_text(
        'Hi, ich bin Ronni der Reiher! Ich führe dich heute durch Golm.',
        reply_markup=ReplyKeyboardRemove())
    update.message.reply_text('Darf ich dich {} nennen? '.format(user),
        reply_markup=ReplyKeyboardMarkup(yes_no_keyboard, one_time_keyboard=True))
    return INTRO_STATES["NAME"]

def name_startpunkt(update, context):
    yes_no_keyboard = [['schon da ⚓',
                        'noch auf dem Weg 😱']]
    user = update.message.from_user
    logger.info("NAME of %s: %s", user.first_name, update.message.text)

    if not "name" in context.user_data:
        context.user_data["name"] = update.message.from_user.first_name
    
    update.message.reply_text('Super!')
    update.message.reply_text('Unsere Reise startet am Bahnhof Golm. Ich warte direkt vor dem orangen Bahnhofsgebäude auf dich. 🚉 ',
                              reply_markup=ReplyKeyboardRemove())
    update.message.reply_text('Bist du auch schon dort?',
                              reply_markup=ReplyKeyboardMarkup(yes_no_keyboard, one_time_keyboard=True))
    return INTRO_STATES["STARTPUNKT"]


def name_frage(update, context):
    logger.info(str(update))
    update.message.reply_text('Wie darf ich dich nennen?',
                            reply_markup=ReplyKeyboardRemove())
    return INTRO_STATES["NAME_AENDERN"]

def name_aendern(update, context):
    yes_no_keyboard = [['Das klingt besser 😊', 'Ups, verschrieben 🙈']]
    update.message.reply_text('Ich nenne dich {}, okay?'.format(update.message.text),
                            reply_markup=ReplyKeyboardMarkup(yes_no_keyboard, one_time_keyboard=True))

    context.user_data["name"] = update.message.text

    return INTRO_STATES["NAME"]

def weg_zum_bahnhof(update, context):
    update.message.reply_text('Kein Problem, ich schicke dir einfach den Standort, von dem aus wir losgehen.',
                              reply_markup=ReplyKeyboardRemove())
    update.message.reply_venue(latitude=52.4090401, longitude=12.9724552, address="Bahnhof Golm", title="Start der Rallye",
                              reply_markup=ReplyKeyboardRemove())
    
    keyboard = [[InlineKeyboardButton("🐾 weiter", callback_data='weiter')
                 ]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Tippe weiter, wenn du angekommen bist!',
                              reply_markup=reply_markup)
    return INTRO_STATES["STARTPUNKT"]

def welche_route_callback_query(update, context):
    logger.info(str(update))
    query = update.callback_query

    query.answer()
    query.edit_message_reply_markup(InlineKeyboardMarkup([]))
    if query.data == "weiter":
        query.message.reply_text('🐾')
        return welche_route(query, context)
    

def welche_route(update, context):
    keyboard = [["Testroute 🧪"],
                ["Reiherbergausfstieg ⛰️"],
                ["Seeroute 🌊"]]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    update.message.reply_text('Sehr gut 😊 Welche Route gehen wir heute? ',
                              #'Wenn du mehr über die Routen erfahren möchtest, schreibe /info routen und ich erzähle dir mehr.'
                              reply_markup=reply_markup)
    return INTRO_STATES["ROUTE_AUSWAEHLEN"]


def start_test_route(update,context):
    yes_no_keyboard = [['Ja, ich bin bereit 🏁',
                        'Ich würde doch lieber eine andere Route gehen 🤔'
                        ]]
    update.message.reply_text('Klasse Wahl 👍 Auf der Testroute zeige ich dir mein Zuhause, den Reiherberg. '
                              'Für diesen Weg brauchen wir etwa 30 Minuten.',
                              reply_markup=ReplyKeyboardRemove())

    update.message.reply_text('Kann’s losgehen?', reply_markup=ReplyKeyboardMarkup(yes_no_keyboard, one_time_keyboard=True))
    return INTRO_STATES["TESTROUTE_BESTAETIGEN"]