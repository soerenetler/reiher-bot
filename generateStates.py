from telegram import Update
import yaml

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PicklePersistence,
                          ConversationHandler, CallbackQueryHandler, PollAnswerHandler, PollHandler, TypeHandler)

def read_state_yml(filename, actions={}, prechecks=[]):
    with open(filename) as file:
        yaml_dict = yaml.load(file)

    actions_dict = {}

    for state, handlers in yaml_dict.items():
        handler_list = prechecks
        for handler in handlers:
            if handler["handler"] == "MessageHandler":
                if handler["filter"] == "regex":
                    newHandler = MessageHandler(Filters.regex(handler["regex"]), actions[handler["action"]])
                elif handler["filter"] == "text":
                    newHandler = MessageHandler(Filters.text, actions[handler["action"]])
            elif handler["handler"] == "CommandHandler":
                newHandler = CommandHandler(handler["command"], actions[handler["action"]])
            elif handler["handler"] == "TypeHandler":
                if handler["type"] == "Update":
                    type_ = Update
                newHandler = TypeHandler(type_, actions[handler["action"]])
                
            handler_list.append(newHandler)

        actions_dict[state]= handler_list

    return actions_dict