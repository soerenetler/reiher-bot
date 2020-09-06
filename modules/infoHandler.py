from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from states import INFO_STATES, GENERAL_STATES
from modules import infoActions

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('info', infoActions.get_info)],

    states={},
    fallbacks=[],
    
    map_to_parent={
            INFO_STATES["INFO"]: GENERAL_STATES["INFO_END"]
        }
    )