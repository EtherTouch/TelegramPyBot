import logging
from typing import Dict

from telegram import Update

from telegrampybot.configuration import Configuration
from telegrampybot.constants.text_constants import TEXT_BACK, TEXT_SLASH_START
from telegrampybot.conversation_handler.chat import Chat
from telegrampybot.conversation_handler.chat_state import WaitingArgument
from telegrampybot.structures.user import User
from telegrampybot.util.log_util import getlogger

logger = getlogger(__name__, logging.DEBUG)


class ChatProgress:

    def __init__(self, configuration: Configuration):
        self._chat_progress: Dict[int, Chat] = {}
        self._configuration: Configuration = configuration
        pass

    def add_chat_progress(self,update: Update, chat_id: int, message: str):
        message = message.strip()

        if chat_id not in self._chat_progress:
            self._chat_progress[chat_id] = Chat(chat_id)
            return
        chat = self._chat_progress[chat_id]
        # if message == TEXT_SLASH_START and not isinstance(chat.chat_state(), WaitingArgument):
        if message == TEXT_SLASH_START:
            self.reset_chat_progress(chat_id)
            return
        elif message == TEXT_BACK and not isinstance(chat.chat_state(), WaitingArgument):
            if chat_id in self._chat_progress:
                self._chat_progress[chat_id]._go_back()
                return
        else:
            user: User = self._configuration.users[chat_id]
            # add message and execute function
            self._chat_progress[chat_id].add_message(update,user, message)

    def reset_chat_progress(self, chat_id: int):
        self._chat_progress[chat_id]._reset()

    def get_chat(self, chat_id: int) -> Chat:
        if chat_id not in self._chat_progress:
            self._chat_progress[chat_id] = Chat(chat_id)
        return self._chat_progress[chat_id]
