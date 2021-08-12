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
        "actions/en_reiherberg.yml", action_functions=en_reiherbergActions.action_functions)
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
            "NAME": prechecks+[MessageHandler(Filters.regex('^(Nein, nenn mich lieber anders! 👻|Nein|Ups, verschrieben 🙈)$'), generalActions["name_frage"]),
                               CommandHandler(
                                   "Nein", generalActions["name_frage"]),
                               CommandHandler(
                                   "Ja", generalActions["datenschutz"]),
                               MessageHandler(Filters.regex(
                                   '^(Ja, gerne! 😎|Das klingt besser 😊|Ja)$'), generalActions["datenschutz"]),
                               TypeHandler(Update, generalActions["datenschutz_tipp"])],

            "NAME_AENDERN": prechecks+[MessageHandler(Filters.text & ~Filters.command, generalActions["name_aendern"]),
                                       TypeHandler(Update, generalActions["name_aendern_tipp"])],

            "DATENSCHUTZ": prechecks+[MessageHandler(Filters.regex('^(Nein|Ja|Ja, klar 🌻|Lieber nicht ⚔️)$'), generalActions["name_startpunkt"]),
                                      CommandHandler(
                "Nein", generalActions["name_startpunkt"]),
                CommandHandler(
                "Ja", generalActions["name_startpunkt"]),
                TypeHandler(Update, generalActions["datenschutz_tipp"])],

            "STARTPUNKT": prechecks+[MessageHandler(Filters.regex('^(schon da ⚓|Ja)$'), generalActions["welche_route"]),
                                     CommandHandler(
                "Ja", generalActions["welche_route"]),
                CommandHandler(
                                         'weiter', generalActions["welche_route"]),
                MessageHandler(Filters.regex(
                    '^(noch auf dem Weg 😱|Nein)$'), generalActions["weg_zum_bahnhof"]),
                CommandHandler(
                "Nein", generalActions["weg_zum_bahnhof"]),
                TypeHandler(Update, generalActions["startpunkt_tipp"])],

            "ROUTE_AUSWAEHLEN": prechecks+[CommandHandler("reiherbergaufstieg", generalActions["start_reiherberg_route"]),
                                           MessageHandler(Filters.regex(
                                               '^(Reiherbergaufstieg ⛰️|Reiherberg|Reiherbergaufstieg|Berg)$'), generalActions["start_reiherberg_route"]),
                                           CommandHandler(
                                               "seeroute", generalActions["start_see_route"]),
                                           MessageHandler(Filters.regex(
                                               '^(Seeroute 🌊|Seeroute|Zernsee|See)$'), generalActions["start_see_route"]),
                                           CommandHandler(
                                               "reiherbergaufstieg_en", generalActions["en_start_reiherberg_route"]),
                                           MessageHandler(Filters.regex(
                                               '^(Heron Hill Climb 🇬🇧|English|Heron Hill|Hill)$'), generalActions["en_start_reiherberg_route"]),
                                           TypeHandler(Update, generalActions["welche_route_tipp"])],

            "REIHERBERGROUTE_BESTAETIGEN": prechecks+[CommandHandler('weiter', reiherbergActions["frage_bahnhof_gif"]),
                                                      MessageHandler(Filters.regex(
                                                          '^(Ja, ich bin bereit 🏁|Ja)$'), reiherbergActions["frage_bahnhof_gif"]),
                                                      CommandHandler(
                "Ja", reiherbergActions["frage_bahnhof_gif"]),
                MessageHandler(Filters.regex(
                    '^(Ich würde doch lieber eine andere Route gehen 🤔|Nein)$'), generalActions["welche_route"]),
                CommandHandler(
                "Nein", generalActions["welche_route"]),
                TypeHandler(Update, generalActions["start_reiherberg_route_tipp"])],

            "EN_REIHERBERGROUTE_BESTAETIGEN": prechecks+[CommandHandler('weiter', en_reiherbergActions["en_frage_bahnhof_gif"]),
                                                         MessageHandler(Filters.regex(
                                                             '^(Yes, I am ready 🏁|Ja|yes|Yes)$'), en_reiherbergActions["en_frage_bahnhof_gif"]),
                                                        CommandHandler("yes", reiherbergActions["en_frage_bahnhof_gif"]),
                                                         MessageHandler(Filters.regex(
                                                             '^(I would rather choose another route 🤔|Nein|no|No)$'), generalActions["welche_route"]),
                                                             CommandHandler("no", reiherbergActions["welche_route"]),
                                                         TypeHandler(Update, generalActions["en_start_reiherberg_route_tipp"])],

            #######REIHERBERG-ROUTE#######
            "BAHNHOF_FRAGE_GIF": prechecks+[MessageHandler(Filters.photo, reiherbergActions["frage_bahnhof_gif_aufloesung"]),
                                            TypeHandler(Update, reiherbergActions["frage_bahnhof_gif_tipp"])],

            "BAHNHOF_FRAGE_GIF_AUFLOESUNG": prechecks+[CommandHandler('weiter', reiherbergActions["frage_bahnhof"]),
                                                       TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "BAHNHOF_FRAGE": prechecks+[CommandHandler('weiter', reiherbergActions["frage_bahnhof_aufloesung"]),
                                        MessageHandler(Filters.regex(
                                            r'^(\d)+'), reiherbergActions["frage_bahnhof_aufloesung"]),
                                        TypeHandler(Update, reiherbergActions["frage_bahnhof_tipp"])],

            "BAHNHOF_FRAGE_AUFLOESUNG": prechecks+[CommandHandler('weiter', reiherbergActions["weg01"]),
                                                   TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "WEG01": prechecks+[CommandHandler('weiter', reiherbergActions["frage_quiz"]),
                                TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "FRAGE_QUIZ": prechecks+[PollAnswerHandler(reiherbergActions["frage_quiz_aufloesung"]),
                                     TypeHandler(Update, reiherbergActions["frage_quiz_tipp"])],

            "FRAGE_QUIZ_AUFLOESUNG": prechecks+[CommandHandler('weiter', reiherbergActions["weg_01a"]),
                                                TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "WEG01A": prechecks+[CommandHandler('weiter', reiherbergActions["frage_ubahn"]),
                                 TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "FRAGE_UBAHN": prechecks+[PollAnswerHandler(reiherbergActions["frage_ubahn_aufloesung"]),
                                      TypeHandler(Update, reiherbergActions["frage_ubahn_tipp"])],

            "FRAGE_UBAHN_AUFLOESUNG": prechecks+[CommandHandler('weiter', reiherbergActions["weg02"]),
                                                 TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "WEG02": prechecks+[CommandHandler('weiter', reiherbergActions["frage_weinmeisterstrasse"]),
                                TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "FRAGE_WEINMEISTERATRASSE": prechecks+[PollAnswerHandler(reiherbergActions["frage_weinmeisterstrasse_aufloesung"]),
                                                   TypeHandler(Update, reiherbergActions["frage_weinmeisterstrasse_tipp"])],

            "FRAGE_WEINMEISTERATRASSE_AUFLOESUNG": prechecks+[CommandHandler('weiter', reiherbergActions["fehlerbild_reiherberg_bank"]),
                                                              TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "FEHLERBILD_REIHERBERG": prechecks+[PollAnswerHandler(reiherbergActions["fehlerbild_reiherberg_aufloesung"]),
                                                TypeHandler(Update, reiherbergActions["fehlerbild_reiherberg_tipp"])],

            "FEHLERBILD_REIHERBERG_AUFLOESUNG": prechecks+[CommandHandler('weiter', reiherbergActions["aufstieg_reiherberg"]),
                                                           TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "AUFSTIEG_REIHERBERG": prechecks+[CommandHandler('weiter', reiherbergActions["schaetzfrage_reiherberg"]),
                                              TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "SCHAETZFRAGE_REIHERBERG": prechecks+[MessageHandler(Filters.regex(r'^(\d)+'), reiherbergActions["schaetzfrage_reiherberg_aufloesung"]),
                                                  TypeHandler(Update, reiherbergActions["schaetzfrage_reiherberg_tipp"])],

            "SCHAETZFRAGE_REIHERBERG_AUFLOESUNG": prechecks+[CommandHandler('weiter', reiherbergActions["foto_reiherberg"]),
                                                             TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "FOTO_REIHERBERG": prechecks+[CommandHandler('weiter', reiherbergActions["foto_reiherberg_aufloesung"]),
                                          MessageHandler(
                                              Filters.photo, reiherbergActions["foto_reiherberg_aufloesung"]),
                                          TypeHandler(Update, reiherbergActions["foto_reiherberg_tipp"])],

            "FOTO_REIHERBERG_AUFLOESUNG": prechecks+[CommandHandler('weiter', reiherbergActions["weg_kirche_1"]),
                                                     TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "WEG_KIRCHE_1": prechecks+[CommandHandler('weiter', reiherbergActions["weg_kirche_2"]),
                                       TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "WEG_KIRCHE_2": prechecks+[CommandHandler('weiter', reiherbergActions["kirche_wortraetsel"]),
                                       TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "KIRCHE_WORTRAETSEL": prechecks+[MessageHandler(Filters.regex(r'^(.)+'), reiherbergActions["kirche_frage"]),
                                             TypeHandler(Update, reiherbergActions["kirche_wortraetsel_tipp"])],

            "FRAGE_KIRCHE": prechecks+[PollAnswerHandler(reiherbergActions["kirche_aufloesung"]),
                                       TypeHandler(Update, reiherbergActions["kirche_frage_tipp"])],

            "KIRCHE_AUFLOESEUNG": prechecks+[CommandHandler('weiter', reiherbergActions["weg_storchenbank"]),
                                             TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "WEG_STORCHENBANK": prechecks+[CommandHandler('weiter', reiherbergActions["frage_storchenbank"]),
                                           TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "FRAGE_STORCHENBANK": prechecks+[MessageHandler(Filters.regex(r'^(\d)+'), reiherbergActions["frage_storchenbank_aufloesung"]),
                                             TypeHandler(Update, reiherbergActions["frage_storchenbank_tipp"])],

            "KAPELLE": prechecks+[CommandHandler('weiter', reiherbergActions["weg_schule"]),
                                  TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "WEG_SCHULE": prechecks+[CommandHandler('weiter', reiherbergActions["schule"]),
                                     TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "SCHULE": prechecks+[CommandHandler('weiter', reiherbergActions["weg_landhotel"]),
                                 TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "WEG_LANDHOTEL": prechecks+[CommandHandler('weiter', reiherbergActions["weg_feuerwehr"]),
                                        TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "FEUERWEHR": prechecks+[CommandHandler('weiter', reiherbergActions["frage_feuerwehr"]),
                                    TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "FRAGE_FEUERWEHR": prechecks+[PollAnswerHandler(reiherbergActions["frage_feuerwehr_aufloesung"]),
                                          TypeHandler(Update, reiherbergActions["frage_feuerwehr_tipp"])],

            "FRAGE_FEUERWEHR_AUFLOESUNG": prechecks+[CommandHandler('weiter', reiherbergActions["rueckweg_bahnhof_2"]),
                                                     TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            # "WEG_VIERSEITENHOF": [CommandHandler('weiter', reiherbergActions["vierseitenhof"])],

            # "VIERSEITENHOF": [CommandHandler('weiter', reiherbergActions["rueckweg_bahnhof_1"])],

            "RUECKWEG_BAHNHOF_1": prechecks+[CommandHandler('weiter', reiherbergActions["rueckweg_bahnhof_2"]),
                                             TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "RUECKWEG_BAHNHOF_2": prechecks+[CommandHandler('weiter', reiherbergActions["bahnhof_ueberfuehrung"]),
                                             TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "BAHNHOF_UEBERFUERUNG": prechecks+[CommandHandler('weiter', reiherbergActions["weg_science_park"]),
                                               TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "WEG_SCIENCE_PARK": prechecks+[CommandHandler('weiter', reiherbergActions["blick_science_park"]),
                                           TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "BLICK_SCIENCE_PARK": prechecks+[CommandHandler('weiter', reiherbergActions["ende_bahnhof"]),
                                             TypeHandler(Update, reiherbergActions["weiter_tipp"])],

            "FEEDBACK": prechecks+[MessageHandler(Filters.voice, reiherbergActions["ende_feedback"]),
                                   MessageHandler(
                                       Filters.text, reiherbergActions["ende_feedback"]),
                                   CommandHandler(
                                       'weiter', reiherbergActions["ende_feedback"]),
                                   TypeHandler(Update, reiherbergActions["feedback_tipp"])],

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

            "EN_FEEDBACK": prechecks+[MessageHandler(Filters.voice, en_reiherbergActions["en_kontakt_rueckfragen"]),
                                      MessageHandler(
                                          Filters.text, en_reiherbergActions["en_kontakt_rueckfragen"]),
                                      CommandHandler('weiter', en_reiherbergActions["en_ende_feedback"]),
                                      CommandHandler('continue', en_reiherbergActions["en_ende_feedback"]),
                                      TypeHandler(Update, en_reiherbergActions["en_feedback_tipp"])],
            "EN_RUECKFRAGEN": prechecks+[MessageHandler(Filters.regex('^(Ja|Ja, gerne! 😎|Nein)$'), en_reiherbergActions["en_ende_feedback"]),
            TypeHandler(Update, en_reiherbergActions["en_rueckfragen_tipp"])],


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
