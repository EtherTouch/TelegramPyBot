import logging

from telegram.ext import Application, MessageHandler, filters, CallbackQueryHandler

from telegrampybot.configuration import Configuration
from telegrampybot.constants.text_constants import TEXT_IKM, TEXT_RKM
from telegrampybot.flask_server import FlaskServer
from telegrampybot.telegram_msg_manager import TelegramMsgManager
from telegrampybot.util.log_util import getlogger

logger = getlogger(__name__, logging.DEBUG)

if __name__ == '__main__':
    # lets parse the configuration
    configuration: Configuration = Configuration()
    # Lets make telegram bot application
    application = Application.builder().token(configuration.bot_token).build()
    # lets make flask server app
    telegram_bot_wrapper = TelegramMsgManager(application, configuration)

    # lets attached the handler according to the chat style
    if configuration.chat_style == TEXT_IKM:
        application.add_handler(MessageHandler(filters.TEXT, telegram_bot_wrapper.unauth_handle_telegram_update_msg))
        application.add_handler(CallbackQueryHandler(telegram_bot_wrapper.unauth_handle_telegram_update_msg))
    elif configuration.chat_style == TEXT_RKM:
        # Dont register CallbackQueryHandler if style is TEXT_CMD
        application.add_handler(MessageHandler(filters.TEXT, telegram_bot_wrapper.unauth_handle_telegram_update_msg))

    # make callback as "update_from_flask"
    flask_server = FlaskServer(configuration, telegram_bot_wrapper.update_from_flask)
    # Now serve the flask server
    flask_server.serve()
    # Now run polling
    application.run_polling(
        drop_pending_updates=True, # we dont want to take message which were already sent before bot started
        timeout=30
    )
