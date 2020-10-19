import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, Sticker, InlineKeyboardButton, InlineKeyboardMarkup, Update)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackContext)

from states import INTRO_STATES
from actions.utils import log

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='bot.log',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


@log(logger)
def log_update(update: Update, context: CallbackContext):
    pass

@log(logger)
def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

@log(logger)
def start_name(update: Update, context: CallbackContext):
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

@log(logger)
def name_startpunkt(update: Update, context: CallbackContext):
    yes_no_keyboard = [['schon da ⚓',
                        'noch auf dem Weg 😱']]
    user = update.message.from_user

    if not "name" in context.user_data:
        context.user_data["name"] = update.message.from_user.first_name
    
    update.message.reply_text('Super!')
    update.message.reply_text('Unsere Reise startet am Bahnhof Golm. Ich warte direkt vor dem orangen Bahnhofsgebäude auf dich. 🚉 ',
                              reply_markup=ReplyKeyboardRemove())
    update.message.reply_text('Bist du auch schon dort?',
                              reply_markup=ReplyKeyboardMarkup(yes_no_keyboard, one_time_keyboard=True))
    return INTRO_STATES["STARTPUNKT"]

@log(logger)
def name_frage(update: Update, context: CallbackContext):
    update.message.reply_text('Wie darf ich dich nennen?',
                            reply_markup=ReplyKeyboardRemove())
    return INTRO_STATES["NAME_AENDERN"]

@log(logger)
def name_aendern(update: Update, context: CallbackContext):
    yes_no_keyboard = [['Das klingt besser 😊', 'Ups, verschrieben 🙈']]
    update.message.reply_text('Ich nenne dich {}, okay?'.format(update.message.text),
                            reply_markup=ReplyKeyboardMarkup(yes_no_keyboard, one_time_keyboard=True))

    context.user_data["name"] = update.message.text

    return INTRO_STATES["NAME"]

@log(logger)
def weg_zum_bahnhof(update: Update, context: CallbackContext):
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
    
@log(logger)
def welche_route(update: Update, context: CallbackContext):
    keyboard = [["Reiherbergaufstieg ⛰️"],
                ["Seeroute 🌊"]]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_photo(open("assets/Infografik02.jpg", 'rb'))
    update.message.reply_text('Sehr gut 😊 Welche Route gehen wir heute? ',
                              #'Wenn du mehr über die Routen erfahren möchtest, schreibe /info routen und ich erzähle dir mehr.'
                              reply_markup=reply_markup)
    return INTRO_STATES["ROUTE_AUSWAEHLEN"]

@log(logger)
def start_reiherberg_route(update: Update,context: CallbackContext):
    yes_no_keyboard = [['Ja, ich bin bereit 🏁',
                        'Ich würde doch lieber eine andere Route gehen 🤔'
                        ]]
    update.message.reply_text('Klasse Wahl 👍 Auf der Testroute zeige ich dir mein Zuhause, den Reiherberg. '
                              'Für diesen Weg brauchen wir etwa eine Stunde.',
                              reply_markup=ReplyKeyboardRemove())

    update.message.reply_text('Kann’s losgehen?', reply_markup=ReplyKeyboardMarkup(yes_no_keyboard, one_time_keyboard=True))
    return INTRO_STATES["TESTROUTE_BESTAETIGEN"]


@log(logger)
def start_see_route(update: Update,context: CallbackContext):
    update.message.reply_text('Leider ist die Seeroute noch nicht verfügbar.')
    return welche_route(update, context)

@log(logger)
def nicht_verstanden(update: Update,context: CallbackContext):
    update.message.reply_text('Leider habe ich dich nicht verstanden. Versuche deine Eingabe anders zu formulieren oder nutze die hinterlegten Antwortbuttons.',
                              reply_markup=ReplyKeyboardRemove())
    return None