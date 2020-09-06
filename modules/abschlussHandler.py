from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from states import ABSCHLUSS_STATES, GENERAL_STATES
from modules import abschlussActions

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('weiter', abschlussActions.get_feedback)],

    states={


    },
    fallbacks=[],
    
    map_to_parent={
            ABSCHLUSS_STATES["ENDE"]: GENERAL_STATES["ENDE"]
        }
    )