import asyncio
import logging
from typing import List

from telegram import Update, Message, InlineKeyboardMarkup
from telegram.ext import ContextTypes, Application

from telegrampybot.configuration import Configuration
from telegrampybot.constants.text_constants import TEXT_REPLY_MARKUP, TEXT_TEXT
from telegrampybot.conversation_handler.conversation_handler import ConversationHandler
from telegrampybot.structures.flask_message import FlaskMessage
from telegrampybot.util.authorisation_util import check_authorisation
from telegrampybot.util.log_util import getlogger
from telegrampybot.util.util import query_message_wrapper

logger = getlogger(__name__, logging.DEBUG)


class TelegramMsgManager:

    def __init__(self, application: Application, configuration: Configuration):
        self._configuration = configuration
        self._application: Application = application
        self._conversation_handler: ConversationHandler = ConversationHandler(configuration)

    async def unauth_handle_telegram_update_msg(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # lets get the chat id
        if update.callback_query:
            chat_id = int(update.callback_query.message.chat.id)
        else:
            chat_id = int(update.message.chat_id)
        # check this chat_id is authorised
        if check_authorisation(chat_id, self._configuration):
            await self._handle_telegram_update_msg(update, context)
        else:
            logger.error('Rejected unauthorized message from chatid: %s', chat_id)
            self.send_message_to_admins(f'Rejected unauthorized message from chatid: {chat_id}')
        pass

    async def _handle_telegram_update_msg(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message is not None:
            logger.info(f"Received Valid message: {update.message.text} from {update.message.chat_id}")
            chat_id, reply = self._conversation_handler.receive_conversation(
                update,
                update.message.chat_id,
                update.message.text,
                context)
            result: Message = await self._application.bot.send_message(
                chat_id=chat_id, **reply
            )
            # lets store the message id if the reply markup is empty
            reply_markup: InlineKeyboardMarkup = reply[TEXT_REPLY_MARKUP]
            if isinstance(reply_markup, InlineKeyboardMarkup) and len(reply_markup.inline_keyboard) != 0:
                self._conversation_handler.latest_query_msg_ids[chat_id] = result.message_id
        elif update.callback_query is not None:
            query = update.callback_query
            chat_id = query.from_user.id
            # CallbackQueries need to be answered, even if no notification to the user is needed
            # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
            await query.answer()
            # lets check if the query is the latest query
            if chat_id not in self._conversation_handler.latest_query_msg_ids:
                self._conversation_handler.latest_query_msg_ids[chat_id] = query.message.message_id
            else:
                last_query_id = self._conversation_handler.latest_query_msg_ids[chat_id]
                if last_query_id > query.message.message_id:
                    logger.warning(f"Old query id: {query.message.message_id}")
                    # collapse the inline keyboard and do nothing
                    await query.edit_message_text(
                        **{
                            TEXT_TEXT: query.data,
                            TEXT_REPLY_MARKUP: InlineKeyboardMarkup(())
                        }
                    )
                    return

            chat_id, reply = self._conversation_handler.receive_conversation(
                update,
                query.from_user.id,
                query.data,
                context)
            # modify the query
            await query.edit_message_text(**reply)

    def eqit_query_message(self, message_id: int, chat_id: int, message: str):
        # replace some characters
        message = message.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
        # get the curent reply markup
        reply = self._conversation_handler.reply_maker.get_reply(chat_id)
        asyncio.create_task(self._application.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=reply[TEXT_REPLY_MARKUP]
        ))

    def send_message(self, chat_id: int, message: str):
        # replace some characters
        message = message.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
        asyncio.create_task(self._application.bot.send_message(
            chat_id,
            message
        ))

    def send_message_to_chat_ids(self, chat_ids: List[int], message: str):
        # replace some characters
        message = message.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
        for chat_id in chat_ids:
            asyncio.create_task(self._application.bot.send_message(
                chat_id,
                message
            ))

    def send_message_to_admins(self, message):
        admin_user_chat_ids: List[int] = list(self._configuration.admin_users.keys())
        self.send_message_to_chat_ids(admin_user_chat_ids, message)

    def update_from_flask(self, flask_msg: FlaskMessage) -> None:
        if flask_msg.meta_data is None:
            # if there is no metadata send the message to admin
            self.send_message_to_admins(flask_msg.message)
        else:
            chat_ids = flask_msg.meta_data.chat_ids if flask_msg.meta_data.chat_ids is not None else []
            if flask_msg.meta_data.query_message:
                query_chat_id = flask_msg.meta_data.query_message.chat_id
                query_msg_id = flask_msg.meta_data.query_message.message_id
                # remove from chat ids as message is send
                chat_ids.remove(query_chat_id) if query_chat_id in chat_ids else None
                # todo edit the query message
                self.eqit_query_message(
                    message_id=query_msg_id,
                    chat_id=query_chat_id,
                    message=query_message_wrapper(flask_msg.message)
                )
                pass
            if flask_msg.meta_data.simple_message:
                simple_chat_id = flask_msg.meta_data.simple_message.chat_id
                # remove from chat ids as message is send
                chat_ids.remove(simple_chat_id) if simple_chat_id in chat_ids else None
                self.send_message(chat_id=simple_chat_id, message=flask_msg.message)
            # send the mesage to the remaining chat ids
            self.send_message_to_chat_ids(chat_ids=chat_ids, message=flask_msg.message)

        pass
