import json
from typing import Dict, List

from telegrampybot.constants.file_constants import DEFAULT_CONFIG_JSON
from telegrampybot.constants.text_constants import TEXT_TASK_S, TEXT_USER_S, TEXT_FLASK_API_ADDRESS, TEXT_BOT_TOKEN, \
    TEXT_GREETING_S, TEXT_CHAT_STYLE, TEXT_RKM, TEXT_IKM
from telegrampybot.structures.ip_port import IpPort
from telegrampybot.structures.task import Task
from telegrampybot.structures.user import User


class Configuration:
    def __init__(self, config_file: str = None):
        if config_file is None:
            config_file = DEFAULT_CONFIG_JSON
        with open(config_file, "r") as reader:
            config_json = json.loads(reader.read())
            # TODO Check config json is a valid config json
        # lets parse what tasks are there
        _task_dict: Dict[str, Task] = {}
        for name, task_detail in config_json[TEXT_TASK_S].items():
            _task_dict[name] = Task(name, task_detail)
        # lets parse users
        self._users: Dict[int, User] = {}
        self._admin_users: Dict[int, User] = {}
        for user in config_json[TEXT_USER_S]:
            user_obj = User(user, _task_dict)
            self._users[user_obj.chat_id] = user_obj
            if user_obj.is_admin:
                self._admin_users[user_obj.chat_id] = user_obj
        # lets parse other fields
        self._flask_ip_port: IpPort = IpPort(config_json[TEXT_FLASK_API_ADDRESS])
        self._bot_token: str = config_json[TEXT_BOT_TOKEN]
        self._greetings = config_json[TEXT_GREETING_S]
        self._chat_style: str = config_json[TEXT_CHAT_STYLE].lower()
        if not (self._chat_style == TEXT_RKM or self._chat_style == TEXT_IKM):
            raise Exception(f"chat_style should be \"{TEXT_RKM}\" or \"{TEXT_IKM}\"")

    @property
    def users(self) -> Dict[int, User]:
        return self._users

    @property
    def admin_users(self) -> Dict[int, User]:
        return self._admin_users

    @property
    def flask_ip_port(self) -> IpPort:
        return self._flask_ip_port

    @property
    def bot_token(self) -> str:
        return self._bot_token

    @property
    def greetings(self) -> List[str]:
        return self._greetings

    @property
    def chat_style(self) -> str:
        return self._chat_style
