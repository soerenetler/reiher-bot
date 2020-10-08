from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Poll)
from PIL import Image

import base64
from io import BytesIO

from states import BAHNHOF_STATES
from actions.infoActions import info_bahn

from actions import utils

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def frage_bahnhof_gif(update, context):
    update.message.reply_text("Du stehst hier vor dem Golmer Bahnhofsgebäude. Das sah früher mal so aus:",
        reply_markup=ReplyKeyboardRemove())
    update.message.reply_photo(open("assets/20200907_170905.jpg", 'rb'))
    update.message.reply_text("Versuche das Bahnhofsgebäude aus der gleichen Perspektive zu fotografieren und schick mir das Bild. 📸",
        reply_markup=ReplyKeyboardRemove())
    
    return BAHNHOF_STATES["BAHNHOF_FRAGE_GIF"]

def frage_bahnhof_gif_aufloesung(update, context):
    logger.info(str(update))
    im_bytes = update.message.photo[0].get_file().download_as_bytearray()

    im_file = BytesIO(im_bytes)  # convert image to file-like object
    im1 = Image.open(im_file)   # img is now PIL Image object
    im2 = Image.open('assets/20200907_170905.jpg')

    gif = utils.generate_gif(im1, im2)

    update.message.reply_document(gif)

    keyboard = [[InlineKeyboardButton("🐾 weiter", callback_data='weiter')
                ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        'So viel hat sich gar nicht geändert, oder?',
        reply_markup=reply_markup
    )

    return BAHNHOF_STATES["BAHNHOF_FRAGE_GIF_AUFLOESUNG"]

def bahnhof_frage_callback_query(update, context):
    logger.info(str(update))
    query = update.callback_query

    query.answer()
    query.edit_message_reply_markup(InlineKeyboardMarkup([]))
    if query.data == "weiter":
        query.message.reply_text('🐾')
        return frage_bahnhof(query, context)

def frage_bahnhof(update, context):
    update.message.reply_text(
        'Da wir am Bahnhof starten: Was schätzt du, wie viele Regionalbahnen fahren täglich vom Bahnhof Golm ab? 🚂',
        reply_markup=ReplyKeyboardRemove())

    return BAHNHOF_STATES["BAHNHOF_FRAGE"]

def frage_bahnhof_aufloesung(update, context):
    logger.info(str(update))
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

    trains = ('🚆'*10 + "\n") * 13 + '🚆'*9

    update.message.reply_text(trains,reply_markup=ReplyKeyboardRemove())

    update.message.reply_text('Unter der Woche fahren 139 Regionalbahnen von Golm ab. '
                              'Richtung Potsdam Hbf. fahren die Züge zur vollen Stunde von Gleis 2 und '
                              'zur halben Stunde von Gleis 1.',
        reply_markup=ReplyKeyboardRemove())

    keyboard = [[InlineKeyboardButton("💡 mehr Infos", callback_data='info'),
                 InlineKeyboardButton("🐾 weiter", callback_data='weiter')
                 ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Wenn du mehr Infos zum Bahnhof Golm haben möchtest, tippe auf \"mehr Infos\".',
        reply_markup=reply_markup)

    # update.message.reply_text('Wenn du bereit bist los zu gehen, dann schreib /weiter.', reply_markup=reply_markup)

    return BAHNHOF_STATES["BAHNHOF_FRAGE_AUFLOESUNG"]

def weg01_callback_query(update, context):
    logger.info(str(update))
    query = update.callback_query

    query.answer()
    query.edit_message_reply_markup(InlineKeyboardMarkup([]))
    if query.data == "weiter":
        query.message.reply_text('🐾')
        return weg01(query, context)
    elif query.data == "info":
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🐾 weiter", callback_data='weiter')]])
        query.message.reply_audio(open('assets/2020_09_17_Bahnhof.mp3', 'rb'), title="Bahnhof Golm", performer="Reiherbot", reply_markup=reply_markup)

def weg01(update, context):
    update.message.reply_text('Dann lass uns losgehen, immerhin haben wir einen Berg zu erkunden!')

    update.message.reply_text('Der erste Weg verläuft parallel zur Bahnstrecke. 🛤️ '
                              'Die Bahnschienen sollten rechts von dir verlaufen. '
                              'Folge der Straße, bis du an einen kleinen Fußweg gelangst.',
                             reply_markup=ReplyKeyboardRemove())

    keyboard = [[InlineKeyboardButton("🐾 weiter", callback_data='weiter')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Gib mir dann Bescheid!',
        reply_markup=reply_markup)

    return BAHNHOF_STATES["WEG01"]

def frage_quiz_callback_query(update, context):
    query = update.callback_query

    query.answer()
    query.edit_message_reply_markup(InlineKeyboardMarkup([]))
    if query.data == "weiter":
        query.message.reply_text('🐾')
        return frage_quiz(query, context)

def frage_quiz(update, context):
    update.message.reply_poll(question='Wusstest du, dass wir Reiher die Wappentiere von Golm sind? Was meinst du, woran das liegt?',
                              options=["Reiher waren das Leibgericht Kaiser Friedrichs IV.",
                                       "In den Mooren rund um Golm lebten viele Reiher.",
                                       "Reiher stehen mythologisch für gute Ernten."],
                              type=Poll.QUIZ,
                              correct_option_id=1,
                              is_anonymous=False
                              )
    # Save some info about the poll the bot_data for later use in receive_quiz_answer
    #payload = {message.poll.id: {"chat_id": update.message.id,
    #                             "message_id": message.message_id}}
    #context.bot_data.update(payload)

    #keyboard = [["Reiher waren das Leibgericht Kaiser Friedrichs IV."],
    #            ["In den Mooren rund um Golm lebten viele Reiher."],
    #            ["Reiher stehen mythologisch für gute Ernten."]]
    #reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    #update.message.reply_text('Wusstest du, dass wir Reiher die Wappentiere von Golm sind? Was meinst du, woran das liegt?',
    #                         reply_markup=reply_markup)
    return BAHNHOF_STATES["FRAGE_QUIZ"]

def frage_quiz_aufloesung(update, context):
    user = context.user_data["name"] 
    if update.option_ids == [1]:
        update.user.send_message('Richtig, {} 🎉 '.format(user),
                                reply_markup=ReplyKeyboardRemove())
    
    else:
        update.user.send_message('Nicht ganz!',
                                reply_markup=ReplyKeyboardRemove())

    keyboard = [[InlineKeyboardButton("🐾 weiter", callback_data='weiter')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
                        
    update.user.send_message('Um Golm herum lebten schon seit jeher viele Reiher. '
                            'Besonders in den Mooren und auf dem Reiherberg fühlten sie sich wohl. ',
                                reply_markup=reply_markup)

    return BAHNHOF_STATES["FRAGE_QUIZ_AUFLOESUNG"]

def quiz_callback(update,context):
    logger.info("=====")
    logger.info(str(update))
    return frage_quiz_aufloesung(update["poll_answer"], context)

def weg_01a_callback_query(update, context):
    query = update.callback_query

    query.answer()
    query.edit_message_reply_markup(InlineKeyboardMarkup([]))
    if query.data == "weiter":
        query.message.reply_text('🐾')
        return weg_01a(query, context)

def weg_01a(update, context):
    keyboard = [[InlineKeyboardButton("🐾 weiter", callback_data='weiter')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Folge dem Fußweg, bis du an eine kleine Treppe gelangst!',
                                reply_markup=ReplyKeyboardRemove())
    
    update.message.reply_text('Wenn du auf dem nächsten Wegabschnitt genau hinschaust, kannst du einen Berliner U-Bahnhof entdecken! 🔍 '
                              'Beachte besonders die Grundstücke auf der linken Seite.',
                                reply_markup=reply_markup)

    return BAHNHOF_STATES["WEG01A"]

def frage_ubahn_callback_query(update, context):
    query = update.callback_query

    query.answer()
    query.edit_message_reply_markup(InlineKeyboardMarkup([]))
    if query.data == "weiter":
        query.message.reply_text('🐾')
        return frage_ubahn(query, context)

def frage_ubahn(update, context):
    keyboard = [["Kurfürstendamm"],
                ["Unter den Linden"],
                ["Zoologischer Garten"]]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    update.message.reply_text('Hast du die Berliner U-Bahn-Station entdecken können? 🚇 '
                              'Wenn ja, weißt du noch, welche U-Bahn-Station es war?',
        reply_markup=reply_markup)

    return BAHNHOF_STATES["FRAGE_UBAHN"]

def frage_ubahn_aufloesung(update, context):
    keyboard = [[InlineKeyboardButton("💡 mehr Infos", callback_data='info'),
                InlineKeyboardButton("🐾 weiter", callback_data='weiter')
                ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    user = context.user_data["name"] 

    if update.message.text == 'Kurfürstendamm':
        update.message.reply_text('Richtig, {} 🎉 es war der Kurfürstendamm! '
                                'Das Schild hing über einer Gartenlaube auf der linken Seite deines Weges.'.format(user),
                                reply_markup=reply_markup)
    
    else:
        update.message.reply_text('Hast du das Schild übersehen? Die richtige Antwort war Kurfürstendamm! '
                                  'Das Schild hing über einer Gartenlaube auf der linken Seite deines Weges.',
                                reply_markup=reply_markup)



    #update.message.reply_text('Willst du mehr darüber erfahren, dann frag mich nach /info ubahn. '
    #                          'Ansonsten können wir weitergehen. /weiter?',
    #                          reply_markup=reply_markup)

    return BAHNHOF_STATES["FRAGE_UBAHN_AUFLOESUNG"]

def weg02_callback_query(update, context):
    query = update.callback_query

    query.answer()
    query.edit_message_reply_markup(InlineKeyboardMarkup([]))
    if query.data == "weiter":
        query.message.reply_text('🐾')
        return weg02(query, context)
    elif query.data == "info":
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🐾 weiter", callback_data='weiter')]])
        query.message.reply_text('INFOS',
                                reply_markup=reply_markup)

def weg02(update, context):
    update.message.reply_text('Unser Weg führt uns unter der Unterführung hindurch. '
                              'Kurz dahinter findest du auf der linken Seite die Weinmeisterstraße.',
                                reply_markup=ReplyKeyboardRemove())
    
    keyboard = [[InlineKeyboardButton("🐾 weiter", callback_data='weiter')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text('Gib mir Bescheid, wenn du das Straßenschild gefunden hast.',
                                reply_markup=reply_markup)

    
    return BAHNHOF_STATES["WEG02"]

def frage_weinmeisterstrasse(update, context):
    keyboard = [["Biersteuer"],
                ["Die Böden waren ausgetrocknet."],
                ["Das Klima änderte sich."]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    update.message.reply_text('Weil das Trinkwasser in Golm früher nicht so gut war, wurde sehr viel Wein angebaut. '
                              'Im 17. Jahrhundert änderte sich das.',
                                reply_markup=ReplyKeyboardRemove())

    update.message.reply_text('Was meinst, woran lag das?',
                                reply_markup=reply_markup)

    return BAHNHOF_STATES["FRAGE_WEINMEISTERATRASSE"]

def frage_weinmeisterstrasse_callback_query(update, context):
    query = update.callback_query

    query.answer()
    query.edit_message_reply_markup(InlineKeyboardMarkup([]))
    if query.data == "weiter":
        query.message.reply_text('🐾')
        return frage_weinmeisterstrasse(query, context)
    elif query.data == "info":
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🐾 weiter", callback_data='weiter')]])
        query.message.reply_text('INFOS',
                                reply_markup=reply_markup)

def frage_weinmeisterstrasse_aufloesung(update, context):
    if update.message.text == 'Biersteuer':
        update.message.reply_text('Richtig! Kaiser Friedrich Wilhelm war gelernter Bierbrauer und wollte Bier steuerlich bevorzugen. '
                                  'Die Menschen in Golm begannen daraufhin Hopfen statt Wein anzubauen.',
                                  reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text('Das war nicht der Grund. Tatsächlich war Kaiser Friedrich Wilhelm gelernter Bierbrauer '
                                  'und wollte Bier steuerlich bevorzugen. '
                                  'Die Menschen in Golm begannen daraufhin Hopfen statt Wein anzubauen.',
                                  reply_markup=ReplyKeyboardRemove())
    
    keyboard = [[InlineKeyboardButton("💡 mehr Infos", callback_data='info'),
                InlineKeyboardButton("🐾 weiter", callback_data='weiter')
                ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Die Weinmeisterstraße ist aus dieser Zeit jedoch geblieben.',
                              reply_markup=reply_markup)

    return BAHNHOF_STATES["FRAGE_WEINMEISTERATRASSE_AUFLOESUNG"]

def fehlerbild_reiherberg_bank(update, context):
    keyboard = [["Ahorn",
                "Bushaltestelle"],
                ["Kotbeutelspender ",
                "Supermarktschild"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('Weiter geht’s entlang der Reiherbergstraße! '
                              'Ein Stück die Straße hinauf findest du folgende Ansicht:')
    update.message.reply_photo(open("assets/fehlerbild_reiherberg_bank.jpg", 'rb'))
    update.message.reply_text('Na gut, ich geb’s zu, ich habe einen Fehler in das Bild eingebaut. Kannst du ihn entdecken? ',
                                reply_markup=reply_markup)

    return BAHNHOF_STATES["FEHLERBILD_REIHERBERG"]

def fehlerbild_reiherberg_bank_callback_query(update, context):
    query = update.callback_query

    query.answer()
    query.edit_message_reply_markup(InlineKeyboardMarkup([]))
    if query.data == "weiter":
        query.message.reply_text('🐾')
        return fehlerbild_reiherberg_bank(query, context)
    elif query.data == "info":
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🐾 weiter", callback_data='weiter')]])
        query.message.reply_voice(open('assets/2020_09_17_Weinmeister.mp3', 'rb'), reply_markup=reply_markup)

def fehlerbild_reiherberg_aufloesung(update, context):
    user = context.user_data["name"] 
    if update.message.text == "Supermarktschild":
        update.message.reply_text('Stimmt {}! Im Dorfkern gibt es keinen Supermarkt mehr. 🛍️'.format(user),
                                  reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text('Das war nicht der Fehler!',
                                reply_markup=ReplyKeyboardRemove())
        update.message.reply_text('Im Dorfkern gibt es keinen Supermarkt mehr (und somit auch kein Supermarktschild). 🛍️',
                                reply_markup=ReplyKeyboardRemove())
    
    keyboard = [[InlineKeyboardButton("💡 mehr Infos", callback_data='info'),
                InlineKeyboardButton("🐾 weiter", callback_data='weiter')
                ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Früher gab es hier einen kleinen Laden. '
                              'Heute befindet sich dort der art supermarket - eine kleine Gallerie.',
                              reply_markup=reply_markup)
    return BAHNHOF_STATES["FEHLERBILD_REIHERBERG_AUFLOESUNG"]

def aufstieg_reiherberg_callback_query(update, context):
    query = update.callback_query

    query.answer()
    query.edit_message_reply_markup(InlineKeyboardMarkup([]))
    if query.data == "weiter":
        query.message.reply_text('🐾')
        return aufstieg_reiherberg(query, context)
    elif query.data == "info":
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🐾 weiter", callback_data='weiter')]])
        query.message.reply_voice(open('assets/2020_09_17_supermarkt.mp3', 'rb'), reply_markup=reply_markup)

def aufstieg_reiherberg(update, context):
    update.message.reply_text('Jetzt stehst du bereits am Fuße des Reiherbergs! Folge dem kleinen Pfad nach oben, bis du zur Aussichtsplattform kommst! '
                              'Wir treffen uns oben wieder, dann kannst du in Ruhe die Natur genießen. ',
                              reply_markup=ReplyKeyboardRemove())

    keyboard = [[InlineKeyboardButton("💡 mehr Infos", callback_data='info')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Wenn dir das zu ruhig ist, kannst du dir auf dem Weg auch die Sage um die Entstehung des Reiherbergs anhören.',
                              reply_markup=reply_markup)

    
    keyboard = [[InlineKeyboardButton("🐾 weiter", callback_data='weiter')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Sag mir Bescheid, wenn du die Aussichtsplattform erreicht hast.',
                              reply_markup=reply_markup)
    return BAHNHOF_STATES["AUFSTIEG_REIHERBERG"]

def schaetzfrage_reiherberg_callback_query(update, context):
    query = update.callback_query

    query.answer()
    query.edit_message_reply_markup(InlineKeyboardMarkup([]))
    if query.data == "weiter":
        query.message.reply_text('🐾')
        return schaetzfrage_reiherberg(query, context)
    elif query.data == "info":
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🐾 weiter", callback_data='weiter')]])
        query.message.reply_voice(open('assets/2020_09_17_Reiherberg-Sage_Favorit.mp3', 'rb'), reply_markup=reply_markup)

def schaetzfrage_reiherberg(update, context):
    update.message.reply_text('Du hast es geschafft! Du stehst jetzt auf dem zweithöchsten Berg in Golm. ⛰️'
                              , reply_markup=ReplyKeyboardRemove())
    update.message.reply_text('Was glaubst du, wie hoch ist der Reiherberg?', reply_markup=ReplyKeyboardRemove())
    return BAHNHOF_STATES["SCHAETZFRAGE_REIHERBERG"]

def schaetzfrage_reiherberg_aufloesung(update, context):
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

    keyboard = [[InlineKeyboardButton("💡 mehr Infos", callback_data='info'),
                InlineKeyboardButton("🐾 weiter", callback_data='weiter')
                ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Mit 68 Metern ist der Reiherberg der zweithöchste Berg in Golm. '
                              'Höher ist nur der 71 Meter hohe Ehrenpfortenberg. '
                              'Doch dafür ist die Aussicht vom Reiherberg unvergleichlich und lädt zum Fotografieren ein. 🌄',
                              reply_markup=reply_markup)
    return BAHNHOF_STATES["SCHAETZFRAGE_REIHERBERG_AUFLOESUNG"]

def foto_reiherberg_callback_query(update, context):
    query = update.callback_query

    query.answer()
    query.edit_message_reply_markup(InlineKeyboardMarkup([]))
    if query.data == "weiter":
        query.message.reply_text('🐾')
        return foto_reiherberg(query, context)
    elif query.data == "info":
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🐾 weiter", callback_data='weiter')]])
        query.message.reply_voice(open('assets/2020_09_17_Reiherberg-Info.mp3', 'rb'), reply_markup=reply_markup)

def foto_reiherberg(update, context):

    keyboard = [[InlineKeyboardButton("↪️ überspringen", callback_data='ueberspringen')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Knipse ein Foto und schicke es mir zu. 📸 Unter allen gesendeten Fotos verlosen wir einmal im Monat einen Einkaufsgutschein. '
                              'Die Fotos findest du im Anschluss auf der unserer Website.',
                              reply_markup=reply_markup)
                    
    return BAHNHOF_STATES["FOTO_REIHERBERG"]

def foto_reiherberg_aufloesung_callback_query(update, context):
    query = update.callback_query

    query.answer()
    query.edit_message_reply_markup(InlineKeyboardMarkup([]))
    if query.data == "ueberspringen":
        query.message.reply_text('🐾')
        return foto_reiherberg_aufloesung(query, context)
    
def foto_reiherberg_aufloesung(update, context):
    if update.message.photo:
        photo_file = update.message.photo[-1].get_file()
        photo_file.download('user_photo.jpg')
        update.message.reply_text('Tolle Aussicht, oder? ')
    
    update.message.reply_text('Hier sind zwei Bilder, die andere Bergsteigende gemacht haben. '
                              'Der Reiherberg ist zu jeder Jahreszeit einen Ausflug wert.')
    keyboard = [[InlineKeyboardButton("🐾 weiter", callback_data='weiter')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_photo("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Die_Kirche_in_Golm.JPG/1200px-Die_Kirche_in_Golm.JPG",
                              reply_markup= reply_markup)

    return BAHNHOF_STATES["FOTO_REIHERBERG_AUFLOESUNG"]
