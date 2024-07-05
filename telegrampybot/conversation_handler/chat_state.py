class ChatState:

    def __init__(self, message: str):
        self._message: str = message.strip()
        pass

    @property
    def message(self) -> str:
        return self._message

    def is_message_empty(self):
        return self._message == ""


class WaitingPyClass(ChatState):

    def __init__(self, message: str = ""):
        super().__init__(message)

    pass


class WaitingFunction(ChatState):
    def __init__(self, message: str = ""):
        super().__init__(message)

    pass


class WaitingArgument(ChatState):
    def __init__(self, message: str = ""):
        super().__init__(message)

    pass


class TaskDoneWithError(ChatState):
    def __init__(self, message: str = ""):
        super().__init__(message)

    pass


class TaskDone(ChatState):
    def __init__(self, message: str = ""):
        super().__init__(message)

    pass


class TaskCompletelyDone(ChatState):
    def __init__(self, message: str = ""):
        super().__init__(message)

    pass


class TaskNotDoneWithTaskNameError(ChatState):
    def __init__(self, message: str = ""):
        super().__init__(message)

    pass
class TaskNotDoneWithFuncNameError(ChatState):
    def __init__(self, message: str = ""):
        super().__init__(message)

    pass