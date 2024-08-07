import asyncio
import logging
from http import HTTPStatus
from typing import Callable

import uvicorn
from asgiref.wsgi import WsgiToAsgi
from flask import Flask, request, jsonify

from telegrampybot.configuration import Configuration
from telegrampybot.constants.text_constants import TEXT_STATUS, TEXT_MSG, TEXT_POST_CAP, TEXT_SLASH_UPDATE, \
    TEXT_SLASH_UPDATE_SLASH
from telegrampybot.structures.flask_message import FlaskMessage
from telegrampybot.structures.meta_data import MetaData
from telegrampybot.util.log_util import getlogger
from telegrampybot.util.util import get_ip

logger = getlogger(__name__, logging.DEBUG)


class FlaskServer:
    def __init__(self, configuration: Configuration, callback: Callable):
        self._configuration = configuration
        self._callback = callback
        self._flask_app = Flask(__name__)
        self._register()
        pass

    def _register(self):

        @self._flask_app.route(TEXT_SLASH_UPDATE, methods=[TEXT_POST_CAP])
        @self._flask_app.route(TEXT_SLASH_UPDATE_SLASH, methods=[TEXT_POST_CAP])
        async def custom_updates():
            if request.is_json:
                try:
                    self._callback(FlaskMessage(request.get_json()))
                    return jsonify({TEXT_STATUS: True}), HTTPStatus.OK
                except Exception as e:
                    return jsonify(
                        {TEXT_STATUS: False, TEXT_MSG: f"{e.__class__.__name__}: {str(e)}"}
                    ), HTTPStatus.BAD_REQUEST
            else:
                return jsonify({TEXT_STATUS: False, TEXT_MSG: f"got a non json data"}), HTTPStatus.BAD_REQUEST

    def serve(self):
        webserver = uvicorn.Server(
            config=uvicorn.Config(
                app=WsgiToAsgi(self._flask_app),
                host=self._configuration.flask_ip_port.ip,
                port=self._configuration.flask_ip_port.port,
                use_colors=False,
                log_level="warning"
            )
        )
        update_addr=f"http://{get_ip(self._configuration.flask_ip_port.ip)}:{self._configuration.flask_ip_port.port}{TEXT_SLASH_UPDATE}"
        MetaData.update_addr=update_addr
        logger.info(
            f"Flask is accepting request at: {update_addr}"
        )
        asyncio.get_event_loop().create_task(webserver.serve())
