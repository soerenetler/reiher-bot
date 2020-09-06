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
                          ConversationHandler)

from states import GENERAL_STATES
from modules import introHandler, bahnhofHandler, abschlussHandler
import generalActions

from configparser import ConfigParser
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read Telegram Token')
    parser.add_argument('telegram_token', type=str,
                        help='the telegram token for your bot')

    args = parser.parse_args()

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(args.telegram_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[introHandler.conv_handler],

        states={
            GENERAL_STATES["BAHNHOF_START"]: [bahnhofHandler.conv_handler],
            GENERAL_STATES["ABSCHLUSS"]: [abschlussHandler.conv_handler],
            GENERAL_STATES["INFO_END"]: []
        },

        fallbacks=[CommandHandler('cancel', generalActions.cancel)]
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
