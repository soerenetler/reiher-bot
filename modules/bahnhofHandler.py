from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

from states import BAHNHOF_STATES, GENERAL_STATES
from modules import bahnhofActions, introActions

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('weiter', bahnhofActions.frage_bahnhof),
                  MessageHandler(Filters.regex('^(Ja, ich bin bereit 🏁|Ja)$'), bahnhofActions.frage_bahnhof),
                  MessageHandler(Filters.regex('^(Ich würde doch lieber eine andere Route gehen 🤔|Nein)$'), introActions.welche_route)],

    states={BAHNHOF_STATES["BAHNHOF_FRAGE"]: [CommandHandler('weiter', bahnhofActions.frage_bahnhof_aufloesung),
                                              MessageHandler(Filters.regex(r'^(\d)+'),bahnhofActions.frage_bahnhof_aufloesung)],
            BAHNHOF_STATES["BAHNHOF_FRAGE_AUFLOESUNG"]: [CommandHandler('weiter', bahnhofActions.weg01),
                                                        CallbackQueryHandler(bahnhofActions.weg01_callback_query)],
            BAHNHOF_STATES["WEG01"]: [CommandHandler('weiter', bahnhofActions.frage_ubahn),
                                      CallbackQueryHandler(bahnhofActions.frage_ubahn_callback_query)],
            BAHNHOF_STATES["FRAGE_UBAHN"]: [MessageHandler(Filters.regex('^(Kurfürstendamm|Unter den Linden|Zoologischer Garten)$'), bahnhofActions.frage_ubahn_aufloesung)],
            BAHNHOF_STATES["FRAGE_UBAHN_AUFLOESUNG"]: [CommandHandler('weiter', bahnhofActions.weg02),
                                                       CallbackQueryHandler(bahnhofActions.weg02_callback_query)],
            BAHNHOF_STATES["FEHLERBILD_REIHERBERG"]: [CommandHandler('weiter', bahnhofActions.fehlerbild_reiherberg_aufloesung),
                                                      MessageHandler(Filters.regex('^(Supermarktschild|Ahorn|Bushaltestelle|Kotbeutelspender)$'), bahnhofActions.fehlerbild_reiherberg_aufloesung)],
            BAHNHOF_STATES["FEHLERBILD_REIHERBERG_AUFLOESUNG"]: [CommandHandler('weiter', bahnhofActions.aufstieg_reiherberg),
                                                                 CallbackQueryHandler(bahnhofActions.aufstieg_reiherberg_callback_query)],
            BAHNHOF_STATES["AUFSTIEG_REIHERBERG"]: [CommandHandler('weiter', bahnhofActions.schaetzfrage_reiherberg),
                                                    CallbackQueryHandler(bahnhofActions.schaetzfrage_reiherberg_callback_query)],
            BAHNHOF_STATES["SCHAETZFRAGE_REIHERBERG"]: [CommandHandler('weiter', bahnhofActions.schaetzfrage_reiherberg_aufloesung),
                                                        MessageHandler(Filters.regex(r'^(\d)+'),bahnhofActions.schaetzfrage_reiherberg_aufloesung)],
            BAHNHOF_STATES["SCHAETZFRAGE_REIHERBERG_AUFLOESUNG"]: [CommandHandler('weiter', bahnhofActions.foto_reiherberg),
                                                                   CallbackQueryHandler(bahnhofActions.foto_reiherberg_callback_query)],
            BAHNHOF_STATES["FOTO_REIHERBERG"]: [CommandHandler('weiter', bahnhofActions.foto_reiherberg_aufloesung),
                                                MessageHandler(Filters.photo, bahnhofActions.foto_reiherberg_aufloesung),
                                                CallbackQueryHandler(bahnhofActions.foto_reiherberg_aufloesung_callback_query)]},
    fallbacks=[],
    
    map_to_parent={
                BAHNHOF_STATES["FOTO_REIHERBERG_AUFLOESUNG"]: GENERAL_STATES["ABSCHLUSS"]
        }
    )