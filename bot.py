#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, Update)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext,PicklePersistence, 
                          ConversationHandler, CallbackQueryHandler, PollAnswerHandler, PollHandler, TypeHandler)

from digitalguide.generateActions import Action, read_action_yaml, callback_query_handler

from actions import generalActions, en_reiherbergActions, reiherbergActions

from configparser import ConfigParser
import argparse

import os
import sys
import traceback
from threading import Thread

import logging
logging.basicConfig(level=logging.DEBUG, filename='../logs/bot_log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read Telegram Token')
    parser.add_argument('telegram_token', type=str,
                        help='the telegram token for your bot')

    args = parser.parse_args()

    from flask import Flask

    app = Flask(__name__)

    @app.route("/")
    def hello_world():
        return "<p>Hello, World!</p>"

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(update: Update, context: CallbackContext):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    def error_handler(update: Update, context: CallbackContext):
        """Log the error and send a telegram message to notify the developer."""
        # Log the error before we do anything else, so we can see it even if something breaks.
        logger.error(msg="Exception while handling an update:", exc_info=context.error)


    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    my_persistence = PicklePersistence(filename='../bot_persistence')
    updater = Updater(args.telegram_token, persistence=my_persistence, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    reiherbergActions = read_action_yaml("actions/reiherberg.yml", action_functions=reiherbergActions.action_functions)
    en_reiherbergActions = read_action_yaml("actions/en_reiherberg.yml", action_functions=en_reiherbergActions.action_functions)
    generalActions = read_action_yaml("actions/general.yml", action_functions=generalActions.action_functions)

    print(generalActions.keys())

    cqh = callback_query_handler({**generalActions, **reiherbergActions, **en_reiherbergActions})

    conv_handler = ConversationHandler(
        allow_reentry=True,
        per_chat=False,
        conversation_timeout = 6 * 60 * 60, 
        entry_points=[CommandHandler('start', generalActions["start_name"])],
        persistent=True, name='reiherbot',

        states={
            "NAME": [MessageHandler(Filters.regex('^(Nein, nenn mich lieber anders! 👻|Nein|Ups, verschrieben 🙈)$'), generalActions["name_frage"]),
                                   MessageHandler(Filters.regex('^(Ja, gerne! 😎|Das klingt besser 😊|Ja)$'), generalActions["datenschutz"])],

            "NAME_AENDERN": [MessageHandler(Filters.text & ~Filters.command, generalActions["name_aendern"])],

            "DATENSCHUTZ": [MessageHandler(Filters.regex('^(Nein|Ja|Ja, klar 🌻|Lieber nicht ⚔️)$'), generalActions["name_startpunkt"])],

            "STARTPUNKT": [MessageHandler(Filters.regex('^(schon da ⚓|Ja)$'), generalActions["welche_route"]),
                                        CommandHandler('weiter', generalActions["welche_route"]),
                                        MessageHandler(Filters.regex('^(noch auf dem Weg 😱|Nein)$'), generalActions["weg_zum_bahnhof"])],

            "ROUTE_AUSWAEHLEN": [MessageHandler(Filters.regex('^(Reiherbergaufstieg ⛰️|Reiherberg|Reiherbergaufstieg|Berg)$'), generalActions["start_reiherberg_route"]),
                                               MessageHandler(Filters.regex('^(Seeroute 🌊|Seeroute|Zernsee|See)$'), generalActions["start_see_route"])],

            "REIHERBERGROUTE_BESTAETIGEN": [CommandHandler('weiter', reiherbergActions["frage_bahnhof_gif"]),
                                                    MessageHandler(Filters.regex('^(Ja, ich bin bereit 🏁|Ja)$'), reiherbergActions["frage_bahnhof_gif"]),
                                                    MessageHandler(Filters.regex('^(Ich würde doch lieber eine andere Route gehen 🤔|Nein)$'), generalActions["welche_route"])],

            "EN_REIHERBERGROUTE_BESTAETIGEN": [CommandHandler('weiter', en_reiherbergActions["en_frage_bahnhof_gif"]),
                                                    MessageHandler(Filters.regex('^(Ja, ich bin bereit 🏁|Ja)$'), en_reiherbergActions["en_frage_bahnhof_gif"]),
                                                    MessageHandler(Filters.regex('^(Ich würde doch lieber eine andere Route gehen 🤔|Nein)$'), generalActions["welche_route"])],

            #######REIHERBERG-ROUTE#######
            "BAHNHOF_FRAGE_GIF": [MessageHandler(Filters.photo, reiherbergActions["frage_bahnhof_gif_aufloesung"])],

            "BAHNHOF_FRAGE_GIF_AUFLOESUNG": [CommandHandler('weiter', reiherbergActions["frage_bahnhof"])],

            "BAHNHOF_FRAGE": [CommandHandler('weiter', reiherbergActions["frage_bahnhof_aufloesung"]),
                                              MessageHandler(Filters.regex(r'^(\d)+'), reiherbergActions["frage_bahnhof_aufloesung"])],
            "BAHNHOF_FRAGE_AUFLOESUNG": [CommandHandler('weiter', reiherbergActions["weg01"])],
            "WEG01": [CommandHandler('weiter', reiherbergActions["frage_quiz"])],
            "FRAGE_QUIZ": [PollAnswerHandler(reiherbergActions["frage_quiz_aufloesung"])],       
            "FRAGE_QUIZ_AUFLOESUNG": [CommandHandler('weiter', reiherbergActions["weg_01a"])],

            "WEG01A": [CommandHandler('weiter', reiherbergActions["frage_ubahn"])],
            
            "FRAGE_UBAHN": [PollAnswerHandler(reiherbergActions["frage_ubahn_aufloesung"])],
            "FRAGE_UBAHN_AUFLOESUNG": [CommandHandler('weiter', reiherbergActions["weg02"])],

            "WEG02": [CommandHandler('weiter', reiherbergActions["frage_weinmeisterstrasse"])],

            "FRAGE_WEINMEISTERATRASSE": [PollAnswerHandler(reiherbergActions["frage_weinmeisterstrasse_aufloesung"])],
            
            "FRAGE_WEINMEISTERATRASSE_AUFLOESUNG": [CommandHandler('weiter', reiherbergActions["fehlerbild_reiherberg_bank"])],

            "FEHLERBILD_REIHERBERG": [CommandHandler('weiter', reiherbergActions["fehlerbild_reiherberg_aufloesung"]),
                                                      PollAnswerHandler(reiherbergActions["fehlerbild_reiherberg_aufloesung"])],
            "FEHLERBILD_REIHERBERG_AUFLOESUNG": [CommandHandler('weiter', reiherbergActions["aufstieg_reiherberg"])],
            "AUFSTIEG_REIHERBERG": [CommandHandler('weiter', reiherbergActions["schaetzfrage_reiherberg"])],
            "SCHAETZFRAGE_REIHERBERG": [CommandHandler('weiter', reiherbergActions["schaetzfrage_reiherberg_aufloesung"]),
                                                        MessageHandler(Filters.regex(r'^(\d)+'),reiherbergActions["schaetzfrage_reiherberg_aufloesung"])],
            "SCHAETZFRAGE_REIHERBERG_AUFLOESUNG": [CommandHandler('weiter', reiherbergActions["foto_reiherberg"])],
            "FOTO_REIHERBERG": [CommandHandler('weiter', reiherbergActions["foto_reiherberg_aufloesung"]),
                                                MessageHandler(Filters.photo, reiherbergActions["foto_reiherberg_aufloesung"])],

            "FOTO_REIHERBERG_AUFLOESUNG": [CommandHandler('weiter', reiherbergActions["weg_kirche_1"])],

            "WEG_KIRCHE_1": [CommandHandler('weiter', reiherbergActions["weg_kirche_2"])],

            "WEG_KIRCHE_2": [CommandHandler('weiter', reiherbergActions["kirche_wortraetsel"])],

            "KIRCHE_WORTRAETSEL": [MessageHandler(Filters.regex(r'^(.)+'),reiherbergActions["kirche_frage"])],

            "FRAGE_KIRCHE": [PollAnswerHandler(reiherbergActions["kirche_aufloesung"])],

            "KIRCHE_AUFLOESEUNG": [CommandHandler('weiter', reiherbergActions["weg_storchenbank"])],

            "WEG_STORCHENBANK": [CommandHandler('weiter', reiherbergActions["frage_storchenbank"])],

            "FRAGE_STORCHENBANK": [MessageHandler(Filters.regex(r'^(\d)+'),reiherbergActions["frage_storchenbank_aufloesung"])],

            "KAPELLE": [CommandHandler('weiter', reiherbergActions["weg_schule"])],
            
            "WEG_SCHULE": [CommandHandler('weiter', reiherbergActions["schule"])],

            "SCHULE": [CommandHandler('weiter', reiherbergActions["weg_landhotel"])],

            "WEG_LANDHOTEL": [CommandHandler('weiter', reiherbergActions["weg_feuerwehr"])],
                                    
            "FEUERWEHR": [CommandHandler('weiter', reiherbergActions["frage_feuerwehr"])],

            "FRAGE_FEUERWEHR": [PollAnswerHandler(reiherbergActions["frage_feuerwehr_aufloesung"])],

            "FRAGE_FEUERWEHR_AUFLOESUNG": [CommandHandler('weiter', reiherbergActions["rueckweg_bahnhof_2"])],
                                    
            #"WEG_VIERSEITENHOF": [CommandHandler('weiter', reiherbergActions["vierseitenhof"])],

            #"VIERSEITENHOF": [CommandHandler('weiter', reiherbergActions["rueckweg_bahnhof_1"])],

            "RUECKWEG_BAHNHOF_1": [CommandHandler('weiter', reiherbergActions["rueckweg_bahnhof_2"])],

            "RUECKWEG_BAHNHOF_2": [CommandHandler('weiter', reiherbergActions["bahnhof_ueberfuehrung"])],
            "BAHNHOF_UEBERFUERUNG": [CommandHandler('weiter', reiherbergActions["weg_science_park"])],
            "WEG_SCIENCE_PARK": [CommandHandler('weiter', reiherbergActions["blick_science_park"])],

            "BLICK_SCIENCE_PARK": [CommandHandler('weiter', reiherbergActions["ende_bahnhof"])],
                                        
            "FEEDBACK": [MessageHandler(Filters.voice, reiherbergActions["kontakt_rueckfragen"]),
                                         MessageHandler(Filters.text, reiherbergActions["kontakt_rueckfragen"]),
                                         CommandHandler('weiter', reiherbergActions["ende_feedback"])],
            "RUECKFRAGEN": [MessageHandler(Filters.regex('^(Ja|Ja, gerne! 😎|Nein)$'), reiherbergActions["ende_feedback"])],

            #######EN_REIHERBERG-ROUTE#######
            "EN_BAHNHOF_FRAGE_GIF": [MessageHandler(Filters.photo, en_reiherbergActions["en_frage_bahnhof_gif_aufloesung"])],

            "EN_BAHNHOF_FRAGE_GIF_AUFLOESUNG": [CommandHandler('weiter', en_reiherbergActions["en_frage_bahnhof"])],

            "EN_BAHNHOF_FRAGE": [CommandHandler('weiter', en_reiherbergActions["en_frage_bahnhof_aufloesung"]),
                                              MessageHandler(Filters.regex(r'^(\d)+'), en_reiherbergActions["en_frage_bahnhof_aufloesung"])],
            "EN_BAHNHOF_FRAGE_AUFLOESUNG": [CommandHandler('weiter', en_reiherbergActions["en_weg01"])],
            "EN_WEG01": [CommandHandler('weiter', en_reiherbergActions["en_frage_quiz"])],
            "EN_FRAGE_QUIZ": [PollAnswerHandler(en_reiherbergActions["en_frage_quiz_aufloesung"])],       
            "EN_FRAGE_QUIZ_AUFLOESUNG": [CommandHandler('weiter', en_reiherbergActions["en_weg_01a"])],

            "EN_WEG01A": [CommandHandler('weiter', en_reiherbergActions["en_frage_ubahn"])],
            
            "EN_FRAGE_UBAHN": [PollAnswerHandler(en_reiherbergActions["en_frage_ubahn_aufloesung"])],
            "EN_FRAGE_UBAHN_AUFLOESUNG": [CommandHandler('weiter', en_reiherbergActions["en_weg02"])],

            "EN_WEG02": [CommandHandler('weiter', en_reiherbergActions["en_frage_weinmeisterstrasse"])],

            "EN_FRAGE_WEINMEISTERATRASSE": [PollAnswerHandler(en_reiherbergActions["en_frage_weinmeisterstrasse_aufloesung"])],
            
            "EN_FRAGE_WEINMEISTERATRASSE_AUFLOESUNG": [CommandHandler('weiter', en_reiherbergActions["en_fehlerbild_reiherberg_bank"])],

            "EN_FEHLERBILD_REIHERBERG": [CommandHandler('weiter', en_reiherbergActions["en_fehlerbild_reiherberg_aufloesung"]),
                                                      PollAnswerHandler(en_reiherbergActions["en_fehlerbild_reiherberg_aufloesung"])],
            "EN_FEHLERBILD_REIHERBERG_AUFLOESUNG": [CommandHandler('weiter', en_reiherbergActions["en_aufstieg_reiherberg"])],
            "EN_AUFSTIEG_REIHERBERG": [CommandHandler('weiter', en_reiherbergActions["en_schaetzfrage_reiherberg"])],
            "EN_SCHAETZFRAGE_REIHERBERG": [CommandHandler('weiter', en_reiherbergActions["en_schaetzfrage_reiherberg_aufloesung"]),
                                                        MessageHandler(Filters.regex(r'^(\d)+'),en_reiherbergActions["en_schaetzfrage_reiherberg_aufloesung"])],
            "EN_SCHAETZFRAGE_REIHERBERG_AUFLOESUNG": [CommandHandler('weiter', en_reiherbergActions["en_foto_reiherberg"])],
            "EN_FOTO_REIHERBERG": [CommandHandler('weiter', en_reiherbergActions["en_foto_reiherberg_aufloesung"]),
                                                MessageHandler(Filters.photo, en_reiherbergActions["en_foto_reiherberg_aufloesung"])],

            "EN_FOTO_REIHERBERG_AUFLOESUNG": [CommandHandler('weiter', en_reiherbergActions["en_weg_kirche_1"])],

            "EN_WEG_KIRCHE_1": [CommandHandler('weiter', en_reiherbergActions["en_weg_kirche_2"])],

            "EN_WEG_KIRCHE_2": [CommandHandler('weiter', en_reiherbergActions["en_kirche_wortraetsel"])],

            "EN_KIRCHE_WORTRAETSEL": [MessageHandler(Filters.regex(r'^(.)+'),en_reiherbergActions["en_kirche_frage"])],

            "EN_FRAGE_KIRCHE": [PollAnswerHandler(en_reiherbergActions["en_kirche_aufloesung"])],

            "EN_KIRCHE_AUFLOESEUNG": [CommandHandler('weiter', en_reiherbergActions["en_weg_storchenbank"])],

            "EN_WEG_STORCHENBANK": [ CommandHandler('weiter', en_reiherbergActions["en_frage_storchenbank"])],

            "EN_FRAGE_STORCHENBANK": [MessageHandler(Filters.regex(r'^(\d)+'),en_reiherbergActions["en_frage_storchenbank_aufloesung"])],

            "EN_KAPELLE": [CommandHandler('weiter', en_reiherbergActions["en_weg_schule"])],
            
            "EN_WEG_SCHULE": [CommandHandler('weiter', en_reiherbergActions["en_schule"])],

            "EN_SCHULE": [CommandHandler('weiter', en_reiherbergActions["en_weg_landhotel"])],

            "EN_WEG_LANDHOTEL": [CommandHandler('weiter', en_reiherbergActions["en_weg_feuerwehr"])],
                                    
            "EN_FEUERWEHR": [CommandHandler('weiter', en_reiherbergActions["en_frage_feuerwehr"])],

            "EN_FRAGE_FEUERWEHR": [PollAnswerHandler(en_reiherbergActions["en_frage_feuerwehr_aufloesung"])],

            "EN_FRAGE_FEUERWEHR_AUFLOESUNG": [CommandHandler('weiter', en_reiherbergActions["en_rueckweg_bahnhof_2"])],
                                    
            #"EN_WEG_VIERSEITENHOF": [CommandHandler('weiter', en_reiherbergActions["vierseitenhof"])],

            #"EN_VIERSEITENHOF": [CommandHandler('weiter', en_reiherbergActions["rueckweg_bahnhof_1"])],

            "EN_RUECKWEG_BAHNHOF_1": [ CommandHandler('weiter', en_reiherbergActions["en_rueckweg_bahnhof_2"])],

            "EN_RUECKWEG_BAHNHOF_2": [CommandHandler('weiter', en_reiherbergActions["en_bahnhof_ueberfuehrung"])],
            "EN_BAHNHOF_UEBERFUERUNG": [CommandHandler('weiter', en_reiherbergActions["en_weg_science_park"])],
            "EN_WEG_SCIENCE_PARK": [CommandHandler('weiter', en_reiherbergActions["en_blick_science_park"])],

            "EN_BLICK_SCIENCE_PARK": [CommandHandler('weiter', en_reiherbergActions["en_ende_bahnhof"])],
                                        
            "EN_FEEDBACK": [MessageHandler(Filters.voice, en_reiherbergActions["en_kontakt_rueckfragen"]),
                                         MessageHandler(Filters.text, en_reiherbergActions["en_kontakt_rueckfragen"]),
                                         CommandHandler('weiter', en_reiherbergActions["en_ende_feedback"])],
            "EN_RUECKFRAGEN": [MessageHandler(Filters.regex('^(Ja|Ja, gerne! 😎|Nein)$'), en_reiherbergActions["en_ende_feedback"])],


            ConversationHandler.TIMEOUT: [MessageHandler(Filters.regex(r'^(.)+'), reiherbergActions["timeout"])],
        },

        fallbacks=[CommandHandler('cancel', generalActions["cancel"]),
                   CommandHandler('start', generalActions["start_name"]),
                   CallbackQueryHandler(cqh),
                   CommandHandler('restart', restart, filters=Filters.user(username='@soeren101')),
                   CommandHandler('restart', restart, filters=Filters.user(username='@aehryk')),
                   TypeHandler(Update, generalActions["log_update"])]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error_handler)


    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
