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
from generateStates import read_state_yml
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
    PORT = int(os.environ.get('PORT', '8080'))

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
                 CommandHandler('start', generalActions["start_name"]),
                 CallbackQueryHandler(cqh)]

    conv_handler = ConversationHandler(
        allow_reentry=True,
        per_chat=False,
        conversation_timeout=6 * 60 * 60,
        entry_points=[CommandHandler('start', generalActions["start_name"])],
        persistent=True, name='reiherbot',

        states={
            **read_state_yml("states/general.yml", actions={**reiherbergActions, **en_reiherbergActions, **generalActions}, prechecks=prechecks),
            **read_state_yml("states/reiherberg.yml", actions={**reiherbergActions, **en_reiherbergActions, **generalActions}, prechecks=prechecks),
            

            #######EN_REIHERBERG-ROUTE#######
            "EN_BAHNHOF_FRAGE_GIF": prechecks+[MessageHandler(Filters.photo, en_reiherbergActions["en_frage_bahnhof_gif_aufloesung"]),
                                         TypeHandler(Update, en_reiherbergActions["en_frage_bahnhof_gif_tipp"])],

            "EN_BAHNHOF_FRAGE_GIF_AUFLOESUNG": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_frage_bahnhof"]),
                                                        CommandHandler('continue', en_reiherbergActions["en_frage_bahnhof"]),
                                                          TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_BAHNHOF_FRAGE": prechecks+[MessageHandler(Filters.regex(r'^(\d)+'), en_reiherbergActions["en_frage_bahnhof_aufloesung"]),
                                         TypeHandler(Update, en_reiherbergActions["en_frage_bahnhof_tipp"])],

            "EN_BAHNHOF_FRAGE_AUFLOESUNG": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_weg01"]),
                                                        CommandHandler('continue', en_reiherbergActions["en_weg01"]),
                                                      TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_WEG01": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_frage_quiz"]),
                                    CommandHandler('continue', en_reiherbergActions["en_frage_quiz"]),
                                   TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_FRAGE_QUIZ": prechecks+[PollAnswerHandler(en_reiherbergActions["en_frage_quiz_aufloesung"]),
                                         TypeHandler(Update, en_reiherbergActions["en_frage_quiz_tipp"])],

            "EN_FRAGE_QUIZ_AUFLOESUNG": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_weg_01a"]),
                                                   CommandHandler('continue', en_reiherbergActions["en_weg_01a"]),
                                                   TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_WEG01A": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_frage_ubahn"]),
                                    CommandHandler('continue', en_reiherbergActions["en_frage_ubahn"]),
                                    TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_FRAGE_UBAHN": prechecks+[PollAnswerHandler(en_reiherbergActions["en_frage_ubahn_aufloesung"]),
                                         TypeHandler(Update, en_reiherbergActions["en_frage_ubahn_tipp"])],

            "EN_FRAGE_UBAHN_AUFLOESUNG": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_weg02"]),
                                                    CommandHandler('continue', en_reiherbergActions["en_weg02"]),
                                                    TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_WEG02": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_frage_weinmeisterstrasse"]),
                                   CommandHandler('continue', en_reiherbergActions["en_frage_weinmeisterstrasse"]),
                                   TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_FRAGE_WEINMEISTERATRASSE": prechecks+[PollAnswerHandler(en_reiherbergActions["en_frage_weinmeisterstrasse_aufloesung"]),
                                                      TypeHandler(Update, en_reiherbergActions["en_frage_weinmeisterstrasse_tipp"])],

            "EN_FRAGE_WEINMEISTERATRASSE_AUFLOESUNG": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_fehlerbild_reiherberg_bank"]),
                                                                 CommandHandler('continue', en_reiherbergActions["en_fehlerbild_reiherberg_bank"]),
                                                                 TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_FEHLERBILD_REIHERBERG": prechecks+[PollAnswerHandler(en_reiherbergActions["en_fehlerbild_reiherberg_aufloesung"]),
                                                   TypeHandler(Update, en_reiherbergActions["en_fehlerbild_reiherberg_tipp"])],

            "EN_FEHLERBILD_REIHERBERG_AUFLOESUNG": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_aufstieg_reiherberg"]),
                                                              CommandHandler('continue', en_reiherbergActions["en_aufstieg_reiherberg"]),
                                                              TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_AUFSTIEG_REIHERBERG": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_schaetzfrage_reiherberg"]),
                                                 CommandHandler('continue', en_reiherbergActions["en_schaetzfrage_reiherberg"]),
                                                 TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_SCHAETZFRAGE_REIHERBERG": prechecks+[MessageHandler(Filters.regex(r'^(\d)+'), en_reiherbergActions["en_schaetzfrage_reiherberg_aufloesung"]),
                                                     TypeHandler(Update, en_reiherbergActions["en_schaetzfrage_reiherberg_tipp"])],

            "EN_SCHAETZFRAGE_REIHERBERG_AUFLOESUNG": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_foto_reiherberg"]),
                                                                CommandHandler('continue', en_reiherbergActions["en_foto_reiherberg"]),
                                                                TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_FOTO_REIHERBERG": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_foto_reiherberg_aufloesung"]),
                                             CommandHandler('continue', en_reiherbergActions["en_foto_reiherberg_aufloesung"]),
                                             MessageHandler(Filters.photo, en_reiherbergActions["en_foto_reiherberg_aufloesung"]),
                                             TypeHandler(Update, en_reiherbergActions["en_foto_reiherberg_tipp"])],

            "EN_FOTO_REIHERBERG_AUFLOESUNG": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_weg_kirche_1"]),
                                                        CommandHandler('continue', en_reiherbergActions["en_weg_kirche_1"]),
                                                        TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_WEG_KIRCHE_1": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_weg_kirche_2"]),
            CommandHandler('continue', en_reiherbergActions["en_weg_kirche_2"]),
                                          TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_WEG_KIRCHE_2": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_kirche_wortraetsel"]),
                                          CommandHandler('continue', en_reiherbergActions["en_kirche_wortraetsel"]),
                                          TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_KIRCHE_WORTRAETSEL": prechecks+[MessageHandler(Filters.regex(r'^(.)+'), en_reiherbergActions["en_kirche_frage"]),
                                                TypeHandler(Update, en_reiherbergActions["en_kirche_wortraetsel_tipp"])],

            "EN_FRAGE_KIRCHE": prechecks+[PollAnswerHandler(en_reiherbergActions["en_kirche_aufloesung"]),
                                          TypeHandler(Update, en_reiherbergActions["en_frage_kirche_tipp"])],

            "EN_KIRCHE_AUFLOESEUNG": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_weg_storchenbank"]),
                                                CommandHandler('continue', en_reiherbergActions["en_weg_storchenbank"]),
                                                TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_WEG_STORCHENBANK": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_frage_storchenbank"]),
                                              CommandHandler('continue', en_reiherbergActions["en_frage_storchenbank"]),
                                              TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_FRAGE_STORCHENBANK": prechecks+[MessageHandler(Filters.regex(r'^(\d)+'), en_reiherbergActions["en_frage_storchenbank_aufloesung"]),
                                                TypeHandler(Update, en_reiherbergActions["en_frage_storchenbank_tipp"])],

            "EN_KAPELLE": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_weg_schule"]),
                                     CommandHandler('continue', en_reiherbergActions["en_weg_schule"]),
                                     TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_WEG_SCHULE": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_schule"]),
                                        CommandHandler('continue', en_reiherbergActions["en_schule"]),
                                        TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_SCHULE": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_weg_landhotel"]),
                                    CommandHandler('continue', en_reiherbergActions["en_weg_landhotel"]),
                                    TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_WEG_LANDHOTEL": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_weg_feuerwehr"]),
                                           CommandHandler('continue', en_reiherbergActions["en_weg_feuerwehr"]),
                                           TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_FEUERWEHR": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_frage_feuerwehr"]),
                                       CommandHandler('continue', en_reiherbergActions["en_frage_feuerwehr"]),
                                        TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_FRAGE_FEUERWEHR": prechecks+[PollAnswerHandler(en_reiherbergActions["en_frage_feuerwehr_aufloesung"]),
                                                TypeHandler(Update, en_reiherbergActions["en_frage_feuerwehr_tipp"])],

            "EN_FRAGE_FEUERWEHR_AUFLOESUNG": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_rueckweg_bahnhof_2"]),
                                                        CommandHandler('continue', en_reiherbergActions["en_rueckweg_bahnhof_2"]),
                                                        TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            # "EN_WEG_VIERSEITENHOF": [CommandHandler('weiter', en_reiherbergActions["vierseitenhof"])],

            # "EN_VIERSEITENHOF": [CommandHandler('weiter', en_reiherbergActions["rueckweg_bahnhof_1"])],

            "EN_RUECKWEG_BAHNHOF_1": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_rueckweg_bahnhof_2"]),
                                                CommandHandler('continue', en_reiherbergActions["en_rueckweg_bahnhof_2"]),
                                                TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_RUECKWEG_BAHNHOF_2": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_bahnhof_ueberfuehrung"]),
                                                CommandHandler('continue', en_reiherbergActions["en_bahnhof_ueberfuehrung"]),
                                                TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_BAHNHOF_UEBERFUERUNG": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_weg_science_park"]),
                                                  CommandHandler('continue', en_reiherbergActions["en_weg_science_park"]),
                                                  TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_WEG_SCIENCE_PARK": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_blick_science_park"]),
                                              CommandHandler('continue', en_reiherbergActions["en_blick_science_park"]),
                                              TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_BLICK_SCIENCE_PARK": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_ende_bahnhof"]),
                                                CommandHandler('continue', en_reiherbergActions["en_ende_bahnhof"]),
                                                TypeHandler(Update, en_reiherbergActions["en_weiter_tipp"])],

            "EN_FEEDBACK": prechecks+[MessageHandler((Filters.text | Filters.photo | Filters.voice) & ~Filters.command, en_reiherbergActions["en_ende_feedback"]),
                                      CommandHandler('weiter', en_reiherbergActions["en_ende_feedback"]),
                                      CommandHandler('continue', en_reiherbergActions["en_ende_feedback"]),
                                      TypeHandler(Update, en_reiherbergActions["en_feedback_tipp"])],

            ConversationHandler.TIMEOUT: [MessageHandler(Filters.regex(r'^(.)+'), reiherbergActions["timeout"])],
        },

        fallbacks=[TypeHandler(Update, generalActions["log_update"])]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error_handler)

    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url=os.environ.get("APP_URL") + TOKEN)
    updater.idle()
