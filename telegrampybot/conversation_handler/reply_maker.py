import random
from typing import List, Dict, Callable

from telegrampybot.configuration import Configuration
from telegrampybot.constants.text_constants import TEXT_BACK, TEXT_REPLY_MARKUP, TEXT_TEXT, TEXT_RKM, TEXT_IKM
from telegrampybot.conversation_handler.chat_progress import ChatProgress
from telegrampybot.conversation_handler.chat_state import WaitingPyClass, WaitingFunction, WaitingArgument
from telegrampybot.structures.task import Task
from telegrampybot.structures.task_function import TaskFunction
from telegrampybot.util.util import make_inline_keyboard_markup, make_reply_keyboard_markup, \
    do_nothing_message_wrapper, query_message_wrapper


class ReplyMaker:
    def __init__(self, configuration: Configuration, chat_progress: ChatProgress):
        self._configuration = configuration
        self._chat_progresss = chat_progress
        # choose type of keyboard maker acordung to the style
        if self._configuration.chat_style == TEXT_RKM:
            self._keyboard_maker: Callable = make_reply_keyboard_markup
            self._message_wrapper: Callable = do_nothing_message_wrapper
        elif self._configuration.chat_style == TEXT_IKM:
            self._keyboard_maker: Callable = make_inline_keyboard_markup
            self._message_wrapper: Callable = query_message_wrapper
        pass

    def get_reply(self, chat_id: int):
        chat = self._chat_progresss.get_chat(chat_id)
        message: str = ""
        options: List[str] = []
        common_name_task_dict: Dict[str, Task] = self._configuration.users[chat_id].common_name_tasks
        if isinstance(chat.chat_state(), WaitingPyClass):
            # lets check if any message stored in the chat state
            if chat.chat_state().is_message_empty():
                message = random.choice(self._configuration.greetings)
            else:
                message = chat.chat_state().message
            options = list(common_name_task_dict.keys())
        elif isinstance(chat.chat_state(), WaitingFunction):
            task_name = chat.get_last_message()
            if task_name is None:
                # this must not be called
                raise Exception("There was no last messsage")
            task: Task = common_name_task_dict[task_name]
            # lets check if any message stored in the chat state
            if chat.chat_state().is_message_empty():
                message = task.task_description
            else:
                message = chat.chat_state().message
            task_functions: Dict[str, TaskFunction] = task.common_name_functions
            options = list(task_functions.keys())
            options.append(TEXT_BACK)
        elif isinstance(chat.chat_state(), WaitingArgument):
            message = chat.chat_state().message

        reply_markup = self._keyboard_maker(options)
        message = self._message_wrapper(message)
        return {
            TEXT_TEXT: message,
            TEXT_REPLY_MARKUP: reply_markup
        }
