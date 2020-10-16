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
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext,
                          ConversationHandler, CallbackQueryHandler, PollAnswerHandler, PollHandler, TypeHandler)

from states import GENERAL_STATES
from actions import generalActions, bahnhofActions, abschlussActions
from states import INTRO_STATES, BAHNHOF_STATES

from configparser import ConfigParser
import argparse

import os
import sys
import traceback
from threading import Thread

import logging
logging.basicConfig(level=logging.DEBUG, filename='bot.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read Telegram Token')
    parser.add_argument('telegram_token', type=str,
                        help='the telegram token for your bot')

    args = parser.parse_args()

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
    updater = Updater(args.telegram_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        per_chat=False,
        entry_points=[CommandHandler('start', generalActions.start_name)],

        states={
            INTRO_STATES["NAME"]: [MessageHandler(Filters.regex('^(Nein, nenn mich lieber anders! 👻|Nein|Ups, verschrieben 🙈)$'), generalActions.name_frage),
                                   MessageHandler(Filters.regex('^(Ja, gerne! 😎|Das klingt besser 😊|Ja)$'), generalActions.name_startpunkt)],

            INTRO_STATES["NAME_AENDERN"]: [MessageHandler(Filters.text & ~Filters.command, generalActions.name_aendern)],

            INTRO_STATES["STARTPUNKT"]: [MessageHandler(Filters.regex('^(schon da ⚓|Ja)$'), generalActions.welche_route),
                                        CommandHandler('weiter', generalActions.welche_route),
                                        MessageHandler(Filters.regex('^(noch auf dem Weg 😱|Nein)$'), generalActions.weg_zum_bahnhof)],

            INTRO_STATES["ROUTE_AUSWAEHLEN"]: [MessageHandler(Filters.regex('^(Testroute 🧪|Testroute)$'), generalActions.start_test_route)],

            INTRO_STATES["TESTROUTE_BESTAETIGEN"]: [CommandHandler('weiter', bahnhofActions.generate_action("frage_bahnhof_gif")),
                                                    MessageHandler(Filters.regex('^(Ja, ich bin bereit 🏁|Ja)$'), bahnhofActions.generate_action("frage_bahnhof_gif")),
                                                    MessageHandler(Filters.regex('^(Ich würde doch lieber eine andere Route gehen 🤔|Nein)$'), generalActions.welche_route)],

            #######DEMO-ROUTE#######
            BAHNHOF_STATES["BAHNHOF_FRAGE_GIF"]: [MessageHandler(Filters.photo, bahnhofActions.generate_action("frage_bahnhof_gif_aufloesung"))],

            BAHNHOF_STATES["BAHNHOF_FRAGE_GIF_AUFLOESUNG"]: [CallbackQueryHandler(bahnhofActions.generate_action("bahnhof_frage_callback_query"))],

            BAHNHOF_STATES["BAHNHOF_FRAGE"]: [CommandHandler('weiter', bahnhofActions.generate_action("frage_bahnhof_aufloesung")),
                                              MessageHandler(Filters.regex(r'^(\d)+'), bahnhofActions.generate_action("frage_bahnhof_aufloesung"))],
            BAHNHOF_STATES["BAHNHOF_FRAGE_AUFLOESUNG"]: [CommandHandler('weiter', bahnhofActions.generate_action("weg01")),
                                                        CallbackQueryHandler(bahnhofActions.generate_action("weg01_callback_query"))],
            BAHNHOF_STATES["WEG01"]: [CommandHandler('weiter', bahnhofActions.generate_action("frage_quiz")),
                                      CallbackQueryHandler(bahnhofActions.generate_action("frage_quiz_callback_query"))],
            BAHNHOF_STATES["FRAGE_QUIZ"]: [PollAnswerHandler(bahnhofActions.generate_action("frage_quiz_aufloesung"))],       
            BAHNHOF_STATES["FRAGE_QUIZ_AUFLOESUNG"]: [CommandHandler('weiter', bahnhofActions.generate_action("weg_01a")),
                                                      CallbackQueryHandler(bahnhofActions.generate_action("weg_01a_callback_query"))],

            BAHNHOF_STATES["WEG01A"]: [CommandHandler('weiter', bahnhofActions.generate_action("frage_ubahn")),
                                       CallbackQueryHandler(bahnhofActions.generate_action("frage_ubahn_callback_query"))],
            
            BAHNHOF_STATES["FRAGE_UBAHN"]: [PollAnswerHandler(bahnhofActions.generate_action("frage_ubahn_aufloesung"))],
            BAHNHOF_STATES["FRAGE_UBAHN_AUFLOESUNG"]: [CommandHandler('weiter', bahnhofActions.generate_action("weg02")),
                                                       CallbackQueryHandler(bahnhofActions.generate_action("weg02_callback_query"))],

            BAHNHOF_STATES["WEG02"]: [CommandHandler('weiter', bahnhofActions.generate_action("frage_weinmeisterstrasse")),
                                       CallbackQueryHandler(bahnhofActions.generate_action("frage_weinmeisterstrasse_callback_query"))],

            BAHNHOF_STATES["FRAGE_WEINMEISTERATRASSE"]: [PollAnswerHandler(bahnhofActions.generate_action("frage_weinmeisterstrasse_aufloesung"))],
            
            BAHNHOF_STATES["FRAGE_WEINMEISTERATRASSE_AUFLOESUNG"]: [CommandHandler('weiter', bahnhofActions.generate_action("fehlerbild_reiherberg_bank")),
                                                                    CallbackQueryHandler(bahnhofActions.generate_action("fehlerbild_reiherberg_bank_callback_query"))],

            BAHNHOF_STATES["FEHLERBILD_REIHERBERG"]: [CommandHandler('weiter', bahnhofActions.generate_action("fehlerbild_reiherberg_aufloesung")),
                                                      PollAnswerHandler(bahnhofActions.generate_action("fehlerbild_reiherberg_aufloesung"))],
            BAHNHOF_STATES["FEHLERBILD_REIHERBERG_AUFLOESUNG"]: [CommandHandler('weiter', bahnhofActions.generate_action("aufstieg_reiherberg")),
                                                                 CallbackQueryHandler(bahnhofActions.generate_action("aufstieg_reiherberg_callback_query"))],
            BAHNHOF_STATES["AUFSTIEG_REIHERBERG"]: [CommandHandler('weiter', bahnhofActions.generate_action("schaetzfrage_reiherberg")),
                                                    CallbackQueryHandler(bahnhofActions.generate_action("schaetzfrage_reiherberg_callback_query"))],
            BAHNHOF_STATES["SCHAETZFRAGE_REIHERBERG"]: [CommandHandler('weiter', bahnhofActions.generate_action("schaetzfrage_reiherberg_aufloesung")),
                                                        MessageHandler(Filters.regex(r'^(\d)+'),bahnhofActions.generate_action("schaetzfrage_reiherberg_aufloesung"))],
            BAHNHOF_STATES["SCHAETZFRAGE_REIHERBERG_AUFLOESUNG"]: [CommandHandler('weiter', bahnhofActions.generate_action("foto_reiherberg")),
                                                                   CallbackQueryHandler(bahnhofActions.generate_action("foto_reiherberg_callback_query"))],
            BAHNHOF_STATES["FOTO_REIHERBERG"]: [CommandHandler('weiter', bahnhofActions.generate_action("foto_reiherberg_aufloesung")),
                                                MessageHandler(Filters.photo, bahnhofActions.generate_action("foto_reiherberg_aufloesung")),
                                                CallbackQueryHandler(bahnhofActions.generate_action("foto_reiherberg_aufloesung_callback_query"))],

            BAHNHOF_STATES["FOTO_REIHERBERG_AUFLOESUNG"]: [CallbackQueryHandler(bahnhofActions.generate_action("weg_kirche_1_callback_query")),
                                                           CommandHandler('weiter', bahnhofActions.generate_action("weg_kirche_1"))],

            BAHNHOF_STATES["WEG_KIRCHE_1"]: [CallbackQueryHandler(bahnhofActions.generate_action("weg_kirche_2_callback_query")),
                                            CommandHandler('weiter', bahnhofActions.generate_action("weg_kirche_2"))],

            BAHNHOF_STATES["WEG_KIRCHE_2"]: [CallbackQueryHandler(bahnhofActions.generate_action("kirche_wortraetsel_callback_query")),
                                             CommandHandler('weiter', bahnhofActions.generate_action("kirche_wortraetsel"))],

            BAHNHOF_STATES["KIRCHE_WORTRAETSEL"]: [MessageHandler(Filters.regex(r'^(.)+'),bahnhofActions.generate_action("kirche_frage"))],

            BAHNHOF_STATES["FRAGE_KIRCHE"]: [PollAnswerHandler(bahnhofActions.generate_action("kirche_aufloesung"))],

            BAHNHOF_STATES["KIRCHE_AUFLOESEUNG"]: [CallbackQueryHandler(bahnhofActions.generate_action("storchenbank_callback_query")),
                                                    CommandHandler('weiter', bahnhofActions.generate_action("frage_storchenbank"))],

            BAHNHOF_STATES["FRAGE_STORCHENBANK"]: [MessageHandler(Filters.regex(r'^(\d)+'),bahnhofActions.generate_action("frage_storchenbank_aufloesung"))],

            BAHNHOF_STATES["KAPELLE"]: [CallbackQueryHandler(bahnhofActions.generate_action("weg_schule_callback_query")),
                                        CommandHandler('weiter', bahnhofActions.generate_action("weg_schule"))],
            
            BAHNHOF_STATES["WEG_SCHULE"]: [CallbackQueryHandler(bahnhofActions.generate_action("schule_callback_query")),
                                        CommandHandler('weiter', bahnhofActions.generate_action("schule"))],

            BAHNHOF_STATES["SCHULE"]: [CallbackQueryHandler(bahnhofActions.generate_action("weg_landhotel_callback_query")),
                                       CommandHandler('weiter', bahnhofActions.generate_action("weg_landhotel"))],

            BAHNHOF_STATES["WEG_LANDHOTEL"]: [CallbackQueryHandler(bahnhofActions.generate_action("weg_feuerwehr_callback_query")),
                                              CommandHandler('weiter', bahnhofActions.generate_action("weg_feuerwehr"))],
                                    
            BAHNHOF_STATES["FEUERWEHR"]: [CallbackQueryHandler(bahnhofActions.generate_action("frage_feuerwehr_callback_query")),
                                          CommandHandler('weiter', bahnhofActions.generate_action("frage_feuerwehr"))],

            BAHNHOF_STATES["FRAGE_FEUERWEHR"]: [PollAnswerHandler(bahnhofActions.generate_action("frage_feuerwehr_aufloesung"))],

            BAHNHOF_STATES["FRAGE_FEUERWEHR_AUFLOESUNG"]: [CallbackQueryHandler(bahnhofActions.generate_action("weg_vierseitenhof_callback_query")),
                                                           CommandHandler('weiter', bahnhofActions.generate_action("weg_vierseitenhof"))],
                                    
            BAHNHOF_STATES["WEG_VIERSEITENHOF"]: [CallbackQueryHandler(bahnhofActions.generate_action("vierseitenhof_callback_query")),
                                                  CommandHandler('weiter', bahnhofActions.generate_action("vierseitenhof"))],

            BAHNHOF_STATES["VIERSEITENHOF"]: [CallbackQueryHandler(bahnhofActions.generate_action("rueckweg_bahnhof_1_callback_query")),
                                             CommandHandler('weiter', bahnhofActions.generate_action("rueckweg_bahnhof_1"))],

            BAHNHOF_STATES["RUECKWEG_BAHNHOF_1"]: [CallbackQueryHandler(bahnhofActions.generate_action("rueckweg_bahnhof_2_callback_query")),
                                                  CommandHandler('weiter', bahnhofActions.generate_action("rueckweg_bahnhof_2"))],

            BAHNHOF_STATES["RUECKWEG_BAHNHOF_2"]: [CallbackQueryHandler(bahnhofActions.generate_action("ende_bahnhof_callback_query")),
                                                  CommandHandler('weiter', bahnhofActions.generate_action("ende_bahnhof"))],

        },

        fallbacks=[CommandHandler('cancel', generalActions.cancel),
                   CommandHandler('restart', restart, filters=Filters.user(username='@soeren101')),
                   CommandHandler('restart', restart, filters=Filters.user(username='@aehryk')),
                   TypeHandler(Update, generalActions.log_update)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error_handler)


    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
