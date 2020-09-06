from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

from states import INTRO_STATES, GENERAL_STATES
from modules import introActions

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', introActions.start_name)],

    states={
            INTRO_STATES["NAME"]: [MessageHandler(Filters.regex('^(Nein, nenn mich lieber anders! 👻|Nein|Ups, verschrieben 🙈)$'), introActions.name_frage),
                                   MessageHandler(Filters.regex('^(Ja, gerne! 😎|Das klingt besser 😊|Ja)$'), introActions.name_startpunkt)],

            INTRO_STATES["NAME_AENDERN"]: [MessageHandler(Filters.text & ~Filters.command, introActions.name_aendern)],

            INTRO_STATES["STARTPUNKT"]: [MessageHandler(Filters.regex('^(schon da ⚓|Ja)$'), introActions.welche_route),
                                        CommandHandler('weiter', introActions.welche_route),
                                        CallbackQueryHandler(introActions.welche_route_callback_query),
                                        MessageHandler(Filters.regex('^(noch auf dem Weg 😱|Nein)$'), introActions.weg_zum_bahnhof)],

            INTRO_STATES["ROUTE_AUSWAEHLEN"]: [MessageHandler(Filters.regex('^(Testroute 🧪|Testroute)$'), introActions.start_test_route)]
        },
    fallbacks=[],
    
    map_to_parent={
                INTRO_STATES["TESTROUTE_BESTAETIGEN"]: GENERAL_STATES["BAHNHOF_START"]
        }
    )