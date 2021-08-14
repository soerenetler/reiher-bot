from telegram import Update
import yaml

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PicklePersistence,
                          ConversationHandler, CallbackQueryHandler, PollAnswerHandler, PollHandler, TypeHandler)

def read_state_yml(filename, actions={}):
    with open(filename) as file:
        yaml_dict = yaml.load(file)

    actions_dict = {}

    for state, handlers in yaml_dict.items():
        handler_list = []
        for handler in handlers:
            if handler["handler"] == "MessageHandler":
                newHandler = MessageHandler(Filters.regex(handler["regex"]), handler["action"])
            elif handler["handler"] == "CommandHandler":
                newHandler = CommandHandler(handler["command"], handler["action"])
            elif handler["handler"] == "TypeHandler":
                if handler["type"] == "Update":
                    type_ = Update
                newHandler = TypeHandler(type_, handler["action"])
                
            handler_list.append(newHandler)

        actions_dict[state]= handler_list

    return actions_dict