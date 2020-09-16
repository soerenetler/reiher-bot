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

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

from states import GENERAL_STATES
from actions import generalActions, bahnhofActions, infoActions, abschlussActions
from states import INTRO_STATES, BAHNHOF_STATES

from configparser import ConfigParser
import argparse

import os
import sys
from threading import Thread

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read Telegram Token')
    parser.add_argument('telegram_token', type=str,
                        help='the telegram token for your bot')

    args = parser.parse_args()

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(update, context):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()


    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(args.telegram_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', generalActions.start_name)],

        states={
            INTRO_STATES["NAME"]: [MessageHandler(Filters.regex('^(Nein, nenn mich lieber anders! 👻|Nein|Ups, verschrieben 🙈)$'), generalActions.name_frage),
                                   MessageHandler(Filters.regex('^(Ja, gerne! 😎|Das klingt besser 😊|Ja)$'), generalActions.name_startpunkt),
                                   MessageHandler(Filters.regex('^(.)*$'), generalActions.nicht_verstanden)],

            INTRO_STATES["NAME_AENDERN"]: [MessageHandler(Filters.text & ~Filters.command, generalActions.name_aendern),
                                   MessageHandler(Filters.regex('^(.)*$'), generalActions.nicht_verstanden)],

            INTRO_STATES["STARTPUNKT"]: [MessageHandler(Filters.regex('^(schon da ⚓|Ja)$'), generalActions.welche_route),
                                        CommandHandler('weiter', generalActions.welche_route),
                                        CallbackQueryHandler(generalActions.welche_route_callback_query),
                                        MessageHandler(Filters.regex('^(noch auf dem Weg 😱|Nein)$'), generalActions.weg_zum_bahnhof),
                                   MessageHandler(Filters.regex('^(.)*$'), generalActions.nicht_verstanden)],

            INTRO_STATES["ROUTE_AUSWAEHLEN"]: [MessageHandler(Filters.regex('^(Testroute 🧪|Testroute)$'), generalActions.start_test_route),
                                   MessageHandler(Filters.regex('^(.)*$'), generalActions.nicht_verstanden)],

            INTRO_STATES["TESTROUTE_BESTAETIGEN"]: [CommandHandler('weiter', bahnhofActions.frage_bahnhof),
                                                    MessageHandler(Filters.regex('^(Ja, ich bin bereit 🏁|Ja)$'), bahnhofActions.frage_bahnhof),
                                                    MessageHandler(Filters.regex('^(Ich würde doch lieber eine andere Route gehen 🤔|Nein)$'), generalActions.welche_route),
                                   MessageHandler(Filters.regex('^(.)*$'), generalActions.nicht_verstanden)],

            #######DEMO-ROUTE#######
            BAHNHOF_STATES["BAHNHOF_FRAGE"]: [CommandHandler('weiter', bahnhofActions.frage_bahnhof_aufloesung),
                                              MessageHandler(Filters.regex(r'^(\d)+'),bahnhofActions.frage_bahnhof_aufloesung),
                                   MessageHandler(Filters.regex('^(.)*$'), generalActions.nicht_verstanden)],
            BAHNHOF_STATES["BAHNHOF_FRAGE_AUFLOESUNG"]: [CommandHandler('weiter', bahnhofActions.weg01),
                                                        CallbackQueryHandler(bahnhofActions.weg01_callback_query),
                                   MessageHandler(Filters.regex('^(.)*$'), generalActions.nicht_verstanden)],
            BAHNHOF_STATES["WEG01"]: [CommandHandler('weiter', bahnhofActions.frage_ubahn),
                                      CallbackQueryHandler(bahnhofActions.frage_ubahn_callback_query),
                                   MessageHandler(Filters.regex('^(.)*$'), generalActions.nicht_verstanden)],
            BAHNHOF_STATES["FRAGE_UBAHN"]: [MessageHandler(Filters.regex('^(Kurfürstendamm|Unter den Linden|Zoologischer Garten)$'), bahnhofActions.frage_ubahn_aufloesung),
                                   MessageHandler(Filters.regex('^(.)*$'), generalActions.nicht_verstanden)],
            BAHNHOF_STATES["FRAGE_UBAHN_AUFLOESUNG"]: [CommandHandler('weiter', bahnhofActions.weg02),
                                                       CallbackQueryHandler(bahnhofActions.weg02_callback_query),
                                   MessageHandler(Filters.regex('^(.)*$'), generalActions.nicht_verstanden)],
            BAHNHOF_STATES["FEHLERBILD_REIHERBERG"]: [CommandHandler('weiter', bahnhofActions.fehlerbild_reiherberg_aufloesung),
                                                      MessageHandler(Filters.regex('^(Supermarktschild|Ahorn|Bushaltestelle|Kotbeutelspender)$'), bahnhofActions.fehlerbild_reiherberg_aufloesung),
                                   MessageHandler(Filters.regex('^(.)*$'), generalActions.nicht_verstanden)],
            BAHNHOF_STATES["FEHLERBILD_REIHERBERG_AUFLOESUNG"]: [CommandHandler('weiter', bahnhofActions.aufstieg_reiherberg),
                                                                 CallbackQueryHandler(bahnhofActions.aufstieg_reiherberg_callback_query),
                                   MessageHandler(Filters.regex('^(.)*$'), generalActions.nicht_verstanden)],
            BAHNHOF_STATES["AUFSTIEG_REIHERBERG"]: [CommandHandler('weiter', bahnhofActions.schaetzfrage_reiherberg),
                                                    CallbackQueryHandler(bahnhofActions.schaetzfrage_reiherberg_callback_query),
                                   MessageHandler(Filters.regex('^(.)*$'), generalActions.nicht_verstanden)],
            BAHNHOF_STATES["SCHAETZFRAGE_REIHERBERG"]: [CommandHandler('weiter', bahnhofActions.schaetzfrage_reiherberg_aufloesung),
                                                        MessageHandler(Filters.regex(r'^(\d)+'),bahnhofActions.schaetzfrage_reiherberg_aufloesung),
                                   MessageHandler(Filters.regex('^(.)*$'), generalActions.nicht_verstanden)],
            BAHNHOF_STATES["SCHAETZFRAGE_REIHERBERG_AUFLOESUNG"]: [CommandHandler('weiter', bahnhofActions.foto_reiherberg),
                                                                   CallbackQueryHandler(bahnhofActions.foto_reiherberg_callback_query),
                                   MessageHandler(Filters.regex('^(.)*$'), generalActions.nicht_verstanden)],
            BAHNHOF_STATES["FOTO_REIHERBERG"]: [CommandHandler('weiter', bahnhofActions.foto_reiherberg_aufloesung),
                                                MessageHandler(Filters.photo, bahnhofActions.foto_reiherberg_aufloesung),
                                                CallbackQueryHandler(bahnhofActions.foto_reiherberg_aufloesung_callback_query),
                                   MessageHandler(Filters.regex('^(.)*$'), generalActions.nicht_verstanden)],

            BAHNHOF_STATES["FOTO_REIHERBERG_AUFLOESUNG"]: [CommandHandler('weiter', abschlussActions.get_feedback),
                                   MessageHandler(Filters.regex('^(.)*$'), generalActions.nicht_verstanden)]
        },

        fallbacks=[CommandHandler('cancel', generalActions.cancel),
                   CommandHandler('restart', restart, filters=Filters.user(username='@soeren101')),
                   CommandHandler('restart', restart, filters=Filters.user(username='@aehryk'))]
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
