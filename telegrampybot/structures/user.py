from typing import Dict

from telegrampybot.constants.text_constants import TEXT_TASK_S, TEXT_CHAT_ID, TEXT_ALL, TEXT_ADMIN
from telegrampybot.structures.task import Task


class User:

    def __init__(self, user_json: Dict, tasks: Dict[str, Task]):
        self._chat_id: int = int(user_json[TEXT_CHAT_ID])
        self._tasks: Dict[str, Task] = {}
        if user_json[TEXT_TASK_S] == TEXT_ALL:
            for k, v in tasks.items():
                self._tasks[v.common_name] = v
        else:
            self._tasks: Dict[str, Task]
            for task_name in user_json[TEXT_TASK_S]:
                for k, v in tasks.items():
                    if task_name.strip() == k:
                        self._tasks[v.common_name] = v
                        break

        self._is_admin: bool = user_json[TEXT_ADMIN] if TEXT_ADMIN in user_json else False

    @property
    def chat_id(self) -> int:
        return self._chat_id

    @property
    def common_name_tasks(self) -> Dict[str, Task]:
        return self._tasks

    @property
    def is_admin(self) -> bool:
        return self._is_admin
