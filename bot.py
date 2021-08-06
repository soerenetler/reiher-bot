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

from digitalguide.mongo_persistence import DBPersistence
from digitalguide import writeActions

import os
import sys
import traceback
from threading import Thread

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    PORT = int(os.environ.get('PORT', '8080'))

    def error_handler(update: Update, context: CallbackContext):
        """Log the error and send a telegram message to notify the developer."""
        # Log the error before we do anything else, so we can see it even if something breaks.
        logger.error(msg="Exception while handling an update:", exc_info=context.error)


    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    my_persistence = DBPersistence("reiherbot_persistencedb")
    updater = Updater(TOKEN, persistence=my_persistence, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    reiherbergActions = read_action_yaml("actions/reiherberg.yml", action_functions={**reiherbergActions.action_functions, **writeActions.action_functions})
    en_reiherbergActions = read_action_yaml("actions/en_reiherberg.yml", action_functions=en_reiherbergActions.action_functions)
    generalActions = read_action_yaml("actions/general.yml", action_functions=generalActions.action_functions)

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

            "BAHNHOF_FRAGE_GIF_AUFLOESUNG": [CommandHandler('weiter', reiherbergActions["frage_bahnhof"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "BAHNHOF_FRAGE": [CommandHandler('weiter', reiherbergActions["frage_bahnhof_aufloesung"]),
                                              MessageHandler(Filters.regex(r'^(\d)+'), reiherbergActions["frage_bahnhof_aufloesung"])],
            "BAHNHOF_FRAGE_AUFLOESUNG": [CommandHandler('weiter', reiherbergActions["weg01"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],
            "WEG01": [CommandHandler('weiter', reiherbergActions["frage_quiz"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],
            "FRAGE_QUIZ": [PollAnswerHandler(reiherbergActions["frage_quiz_aufloesung"])],       
            "FRAGE_QUIZ_AUFLOESUNG": [CommandHandler('weiter', reiherbergActions["weg_01a"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "WEG01A": [CommandHandler('weiter', reiherbergActions["frage_ubahn"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],
            
            "FRAGE_UBAHN": [PollAnswerHandler(reiherbergActions["frage_ubahn_aufloesung"])],
            "FRAGE_UBAHN_AUFLOESUNG": [CommandHandler('weiter', reiherbergActions["weg02"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "WEG02": [CommandHandler('weiter', reiherbergActions["frage_weinmeisterstrasse"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "FRAGE_WEINMEISTERATRASSE": [PollAnswerHandler(reiherbergActions["frage_weinmeisterstrasse_aufloesung"])],
            
            "FRAGE_WEINMEISTERATRASSE_AUFLOESUNG": [CommandHandler('weiter', reiherbergActions["fehlerbild_reiherberg_bank"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "FEHLERBILD_REIHERBERG": [PollAnswerHandler(reiherbergActions["fehlerbild_reiherberg_aufloesung"])],
            
            "FEHLERBILD_REIHERBERG_AUFLOESUNG": [CommandHandler('weiter', reiherbergActions["aufstieg_reiherberg"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "AUFSTIEG_REIHERBERG": [CommandHandler('weiter', reiherbergActions["schaetzfrage_reiherberg"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "SCHAETZFRAGE_REIHERBERG": [MessageHandler(Filters.regex(r'^(\d)+'),reiherbergActions["schaetzfrage_reiherberg_aufloesung"])],

            "SCHAETZFRAGE_REIHERBERG_AUFLOESUNG": [CommandHandler('weiter', reiherbergActions["foto_reiherberg"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "FOTO_REIHERBERG": [CommandHandler('weiter', reiherbergActions["foto_reiherberg_aufloesung"]),
                                MessageHandler(Filters.photo, reiherbergActions["foto_reiherberg_aufloesung"])],

            "FOTO_REIHERBERG_AUFLOESUNG": [CommandHandler('weiter', reiherbergActions["weg_kirche_1"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "WEG_KIRCHE_1": [CommandHandler('weiter', reiherbergActions["weg_kirche_2"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "WEG_KIRCHE_2": [CommandHandler('weiter', reiherbergActions["kirche_wortraetsel"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "KIRCHE_WORTRAETSEL": [MessageHandler(Filters.regex(r'^(.)+'),reiherbergActions["kirche_frage"])],

            "FRAGE_KIRCHE": [PollAnswerHandler(reiherbergActions["kirche_aufloesung"])],

            "KIRCHE_AUFLOESEUNG": [CommandHandler('weiter', reiherbergActions["weg_storchenbank"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "WEG_STORCHENBANK": [CommandHandler('weiter', reiherbergActions["frage_storchenbank"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "FRAGE_STORCHENBANK": [MessageHandler(Filters.regex(r'^(\d)+'),reiherbergActions["frage_storchenbank_aufloesung"])],

            "KAPELLE": [CommandHandler('weiter', reiherbergActions["weg_schule"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],
            
            "WEG_SCHULE": [CommandHandler('weiter', reiherbergActions["schule"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "SCHULE": [CommandHandler('weiter', reiherbergActions["weg_landhotel"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "WEG_LANDHOTEL": [CommandHandler('weiter', reiherbergActions["weg_feuerwehr"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],
                                    
            "FEUERWEHR": [CommandHandler('weiter', reiherbergActions["frage_feuerwehr"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "FRAGE_FEUERWEHR": [PollAnswerHandler(reiherbergActions["frage_feuerwehr_aufloesung"])],

            "FRAGE_FEUERWEHR_AUFLOESUNG": [CommandHandler('weiter', reiherbergActions["rueckweg_bahnhof_2"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],
                                    
            #"WEG_VIERSEITENHOF": [CommandHandler('weiter', reiherbergActions["vierseitenhof"])],

            #"VIERSEITENHOF": [CommandHandler('weiter', reiherbergActions["rueckweg_bahnhof_1"])],

            "RUECKWEG_BAHNHOF_1": [CommandHandler('weiter', reiherbergActions["rueckweg_bahnhof_2"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "RUECKWEG_BAHNHOF_2": [CommandHandler('weiter', reiherbergActions["bahnhof_ueberfuehrung"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "BAHNHOF_UEBERFUERUNG": [CommandHandler('weiter', reiherbergActions["weg_science_park"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "WEG_SCIENCE_PARK": [CommandHandler('weiter', reiherbergActions["blick_science_park"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "BLICK_SCIENCE_PARK": [CommandHandler('weiter', reiherbergActions["ende_bahnhof"]),
                                            TypeHandler(Update, reiherbergActions["weiter_tipp"])],
                                        
            "FEEDBACK": [MessageHandler(Filters.voice, reiherbergActions["kontakt_rueckfragen"]),
                                         MessageHandler(Filters.text, reiherbergActions["kontakt_rueckfragen"]),
                                         CommandHandler('weiter', reiherbergActions["ende_feedback"])],
            "RUECKFRAGEN": [MessageHandler(Filters.regex('^(Ja|Ja, gerne! 😎|Nein)$'), reiherbergActions["ende_feedback"])],

            #######EN_REIHERBERG-ROUTE#######
            "EN_BAHNHOF_FRAGE_GIF": [MessageHandler(Filters.photo, en_reiherbergActions["en_frage_bahnhof_gif_aufloesung"])],

            "EN_BAHNHOF_FRAGE_GIF_AUFLOESUNG": [CommandHandler('weiter', en_reiherbergActions["en_frage_bahnhof"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_BAHNHOF_FRAGE": [MessageHandler(Filters.regex(r'^(\d)+'), en_reiherbergActions["en_frage_bahnhof_aufloesung"])],

            "EN_BAHNHOF_FRAGE_AUFLOESUNG": [CommandHandler('weiter', en_reiherbergActions["en_weg01"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_WEG01": [CommandHandler('weiter', en_reiherbergActions["en_frage_quiz"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_FRAGE_QUIZ": [PollAnswerHandler(en_reiherbergActions["en_frage_quiz_aufloesung"])],

            "EN_FRAGE_QUIZ_AUFLOESUNG": [CommandHandler('weiter', en_reiherbergActions["en_weg_01a"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_WEG01A": [CommandHandler('weiter', en_reiherbergActions["en_frage_ubahn"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],
            
            "EN_FRAGE_UBAHN": [PollAnswerHandler(en_reiherbergActions["en_frage_ubahn_aufloesung"])],

            "EN_FRAGE_UBAHN_AUFLOESUNG": [CommandHandler('weiter', en_reiherbergActions["en_weg02"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_WEG02": [CommandHandler('weiter', en_reiherbergActions["en_frage_weinmeisterstrasse"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_FRAGE_WEINMEISTERATRASSE": [PollAnswerHandler(en_reiherbergActions["en_frage_weinmeisterstrasse_aufloesung"])],
            
            "EN_FRAGE_WEINMEISTERATRASSE_AUFLOESUNG": [CommandHandler('weiter', en_reiherbergActions["en_fehlerbild_reiherberg_bank"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_FEHLERBILD_REIHERBERG": [PollAnswerHandler(en_reiherbergActions["en_fehlerbild_reiherberg_aufloesung"])],

            "EN_FEHLERBILD_REIHERBERG_AUFLOESUNG": [CommandHandler('weiter', en_reiherbergActions["en_aufstieg_reiherberg"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_AUFSTIEG_REIHERBERG": [CommandHandler('weiter', en_reiherbergActions["en_schaetzfrage_reiherberg"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_SCHAETZFRAGE_REIHERBERG": [MessageHandler(Filters.regex(r'^(\d)+'),en_reiherbergActions["en_schaetzfrage_reiherberg_aufloesung"])],

            "EN_SCHAETZFRAGE_REIHERBERG_AUFLOESUNG": [CommandHandler('weiter', en_reiherbergActions["en_foto_reiherberg"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_FOTO_REIHERBERG": [CommandHandler('weiter', en_reiherbergActions["en_foto_reiherberg_aufloesung"]),
                                   MessageHandler(Filters.photo, en_reiherbergActions["en_foto_reiherberg_aufloesung"])],

            "EN_FOTO_REIHERBERG_AUFLOESUNG": [CommandHandler('weiter', en_reiherbergActions["en_weg_kirche_1"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_WEG_KIRCHE_1": [CommandHandler('weiter', en_reiherbergActions["en_weg_kirche_2"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_WEG_KIRCHE_2": [CommandHandler('weiter', en_reiherbergActions["en_kirche_wortraetsel"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_KIRCHE_WORTRAETSEL": [MessageHandler(Filters.regex(r'^(.)+'),en_reiherbergActions["en_kirche_frage"])],

            "EN_FRAGE_KIRCHE": [PollAnswerHandler(en_reiherbergActions["en_kirche_aufloesung"])],

            "EN_KIRCHE_AUFLOESEUNG": [CommandHandler('weiter', en_reiherbergActions["en_weg_storchenbank"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_WEG_STORCHENBANK": [ CommandHandler('weiter', en_reiherbergActions["en_frage_storchenbank"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_FRAGE_STORCHENBANK": [MessageHandler(Filters.regex(r'^(\d)+'),en_reiherbergActions["en_frage_storchenbank_aufloesung"])],

            "EN_KAPELLE": [CommandHandler('weiter', en_reiherbergActions["en_weg_schule"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],
            
            "EN_WEG_SCHULE": [CommandHandler('weiter', en_reiherbergActions["en_schule"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_SCHULE": [CommandHandler('weiter', en_reiherbergActions["en_weg_landhotel"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_WEG_LANDHOTEL": [CommandHandler('weiter', en_reiherbergActions["en_weg_feuerwehr"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],
                                    
            "EN_FEUERWEHR": [CommandHandler('weiter', en_reiherbergActions["en_frage_feuerwehr"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_FRAGE_FEUERWEHR": [PollAnswerHandler(en_reiherbergActions["en_frage_feuerwehr_aufloesung"])],

            "EN_FRAGE_FEUERWEHR_AUFLOESUNG": [CommandHandler('weiter', en_reiherbergActions["en_rueckweg_bahnhof_2"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],
                                    
            #"EN_WEG_VIERSEITENHOF": [CommandHandler('weiter', en_reiherbergActions["vierseitenhof"])],

            #"EN_VIERSEITENHOF": [CommandHandler('weiter', en_reiherbergActions["rueckweg_bahnhof_1"])],

            "EN_RUECKWEG_BAHNHOF_1": [ CommandHandler('weiter', en_reiherbergActions["en_rueckweg_bahnhof_2"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_RUECKWEG_BAHNHOF_2": [CommandHandler('weiter', en_reiherbergActions["en_bahnhof_ueberfuehrung"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_BAHNHOF_UEBERFUERUNG": [CommandHandler('weiter', en_reiherbergActions["en_weg_science_park"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_WEG_SCIENCE_PARK": [CommandHandler('weiter', en_reiherbergActions["en_blick_science_park"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],

            "EN_BLICK_SCIENCE_PARK": [CommandHandler('weiter', en_reiherbergActions["en_ende_bahnhof"]),
                                            TypeHandler(Update, en_reiherbergActions["weiter_tipp"])],
                                        
            "EN_FEEDBACK": [MessageHandler(Filters.voice, en_reiherbergActions["en_kontakt_rueckfragen"]),
                                         MessageHandler(Filters.text, en_reiherbergActions["en_kontakt_rueckfragen"]),
                                         CommandHandler('weiter', en_reiherbergActions["en_ende_feedback"])],
            "EN_RUECKFRAGEN": [MessageHandler(Filters.regex('^(Ja|Ja, gerne! 😎|Nein)$'), en_reiherbergActions["en_ende_feedback"])],


            ConversationHandler.TIMEOUT: [MessageHandler(Filters.regex(r'^(.)+'), reiherbergActions["timeout"])],
        },

        fallbacks=[CommandHandler('cancel', generalActions["cancel"]),
                   CommandHandler('start', generalActions["start_name"]),
                   CallbackQueryHandler(cqh),
                   TypeHandler(Update, generalActions["log_update"])]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error_handler)


    updater.start_webhook(listen="0.0.0.0",
                        port=PORT,
                        url_path=TOKEN,
                        webhook_url=os.environ.get("APP_URL") + TOKEN)
    updater.idle()