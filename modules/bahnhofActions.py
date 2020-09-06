from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup)

from states import BAHNHOF_STATES
from modules.infoActions import info_bahn

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def frage_bahnhof(update, context):
    logger.info(str(update))
    update.message.reply_text(
        'Da wir am Bahnhof starten: Was schätzt du, wie viele Regionalbahnen fahren täglich vom Bahnhof Golm ab?',
        reply_markup=ReplyKeyboardRemove())

    return BAHNHOF_STATES["BAHNHOF_FRAGE"]

def frage_bahnhof_aufloesung(update, context):
    logger.info(str(update))
    schaetzung = int(update.message.text)
    echter_wert = 139
    if schaetzung == echter_wert:
        update.message.reply_text('Nicht schlecht! (Das ist brandenburgisch für "gut gemacht!")',
            reply_markup=ReplyKeyboardRemove())
    elif schaetzung >= echter_wert-echter_wert*0.2 and schaetzung <= echter_wert+echter_wert*0.2:
        update.message.reply_text('Du bist schon nah dran!',
            reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text('Nicht ganz!',
            reply_markup=ReplyKeyboardRemove())

    update.message.reply_text('Unter der Woche fahren 139 Regionalbahnen von Golm ab. '
                              'Richtung Potsdam Hbf fahren die Züge zur vollen Stunde von Gleis 2 und '
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
        query.message.reply_text('INFOS',
                                reply_markup=reply_markup)

def weg01(update, context):
    update.message.reply_text('Dann lass uns losgehen, immerhin haben wir einen Berg zu erkunden!')

    update.message.reply_text('Der erste Weg verläuft parallel zur Bahnstrecke. 🛤️ '
                              'Die Bahnschienen sollten rechts von dir verlaufen. '
                              'Folge der Straße und dem anschließenden kleinen Fußweg, bis du an eine kleine Treppe gelangst. ',
                             reply_markup=ReplyKeyboardRemove())

    keyboard = [[InlineKeyboardButton("🐾 weiter", callback_data='weiter')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Gib mir dann Bescheid!',
        reply_markup=reply_markup)

    return BAHNHOF_STATES["WEG01"]

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

    update.message.reply_text('Hast du unterwegs die Berliner U-Bahn-Station gesehen? 🚇 '
                              'Weißt du noch, welche U-Bahn-Station es war?',
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
    keyboard = [["Ahorn",
                "Bushaltestelle"],
                ["Kotbeutelspender ",
                "Supermarktschild"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    update.message.reply_text('Unser Weg führt uns unter der Unterführung hindurch. Ein Stück dahinter findest du folgende Ansicht:',
                                reply_markup=ReplyKeyboardRemove())

    update.message.reply_photo(open("assets/fehlerbild_reiherberg_bank.jpg", 'rb'))
    update.message.reply_text('Na gut, ich geb’s zu, ich habe einen Fehler in das Bild eingebaut. Kannst du ihn entdecken? ',
                                reply_markup=reply_markup)
    return BAHNHOF_STATES["FEHLERBILD_REIHERBERG"]

def fehlerbild_reiherberg_aufloesung(update, context):
    if update.message.text == "Supermarktschild":
        update.message.reply_text('Stimmt! Im Dorfkern gibt es keinen Supermarkt mehr. 🛍️',
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
        query.message.reply_text('INFOS',
                                reply_markup=reply_markup)

def aufstieg_reiherberg(update, context):

    keyboard = [[InlineKeyboardButton("💡 mehr Infos", callback_data='info'),
                InlineKeyboardButton("🐾 weiter", callback_data='weiter')
                ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Jetzt stehst du bereits am Fuße des Reiherbergs! Folge dem kleinen Pfad nach oben, bis du zur Aussichtsplattform kommst! '
                              'Wir treffen uns oben wieder, dann kannst du in Ruhe die Natur genießen. '
                              'Sag mir Bescheid, wenn du die Aussichtsplattform erreicht hast.',
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
        query.message.reply_text('INFOS',
                                reply_markup=reply_markup)

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
        query.message.reply_text('INFOS',
                                reply_markup=reply_markup)

def foto_reiherberg(update, context):

    keyboard = [[InlineKeyboardButton("↪️ übringen", callback_data='ueberspringen')]]

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
    update.message.reply_photo("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Die_Kirche_in_Golm.JPG/1200px-Die_Kirche_in_Golm.JPG")

    return BAHNHOF_STATES["FOTO_REIHERBERG_AUFLOESUNG"]
