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

from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PicklePersistence,
                          ConversationHandler, CallbackQueryHandler, PollAnswerHandler, PollHandler, TypeHandler)

from digitalguide.generateActions import read_action_yaml, callback_query_handler
from digitalguide.generateStates import read_state_yml
from digitalguide.errorHandler import error_handler

from actions import generalActions, en_reiherbergActions, reiherbergActions

from digitalguide.mongo_persistence import DBPersistence
from digitalguide import writeActions

import os

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    PORT = int(os.environ.get('PORT', '8443'))

    my_persistence = DBPersistence("reiherbot_persistencedb")
    updater = Updater(TOKEN, persistence=my_persistence, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    reiherbergActions = read_action_yaml("actions/reiherberg.yml", action_functions={
                                         **reiherbergActions.action_functions, **writeActions.action_functions})
    en_reiherbergActions = read_action_yaml(
        "actions/en_reiherberg.yml", action_functions={**en_reiherbergActions.action_functions, **writeActions.action_functions})
    generalActions = read_action_yaml(
        "actions/general.yml", action_functions=generalActions.action_functions)

    cqh = callback_query_handler(
        {**generalActions, **reiherbergActions, **en_reiherbergActions})

    prechecks = [CommandHandler('cancel', generalActions["cancel"]),
                 CommandHandler('start', generalActions["start"]),
                 CallbackQueryHandler(cqh)]

    conv_handler = ConversationHandler(
        allow_reentry=True,
        per_chat=False,
        conversation_timeout=6 * 60 * 60,
        entry_points=[CommandHandler('start', generalActions["start"])],
        persistent=True, name='reiherbot',

        states={
            **read_state_yml("states/general.yml", actions={**reiherbergActions, **en_reiherbergActions, **generalActions}, prechecks=prechecks),
            **read_state_yml("states/reiherberg.yml", actions={**reiherbergActions}, prechecks=prechecks),
            **read_state_yml("states/en_reiherberg.yml", actions={**en_reiherbergActions}, prechecks=prechecks),

            ConversationHandler.TIMEOUT: [MessageHandler(Filters.regex(r'^(.)+'), reiherbergActions["timeout"])],
        },

        fallbacks=[TypeHandler(Update, generalActions["log_update"])]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error_handler)

    print("webhook_url: ", os.environ.get("APP_URL") + TOKEN)
    print("PORT", PORT)

    updater.start_webhook(listen="0.0.0.0",
                          port=8080,
                          url_path=TOKEN,
                          webhook_url = "naunhofbot-szuep.ondigitalocean.app/" + TOKEN)

    updater.idle()
