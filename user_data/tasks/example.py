import json

from telegrampybot.conversation_handler.chat_state import TaskDone, TaskCompletelyDone, WaitingArgument

"""
This example show
- simple functions
- returning values and showing the result in the user's telgram app
- How to run function after passing arguments
"""


class HelloWorld:

    def hello_world(self):
        print("hello World")
        # if nothing is return than we make it return a class of  "TaskDone"

    def hello(self):
        print("hello")
        return TaskDone("say \"hello\"")

    def hi_world(self):
        print("hi world")
        # this return value will make user to choose tasks
        return TaskCompletelyDone("We have done task completly")

    def hello_user(self, *args):
        # Simple example to pass arguments in a function
        if len(args) < 1:
            return WaitingArgument("Please input your first name")
        if len(args) < 2:
            return WaitingArgument("Please input your second name")
        print(f"Hello {args[0]} {args[1]}")
        return TaskCompletelyDone(f"We have said \"Hello {args[0]} {args[1]}\"")

    def bonjour(self):
        # this function cannot be called as it is not declared in the config.json
        print("bonjour")
        return TaskDone("say \"bonjour\"")

    def hello_extra(self, **kwargs):
        print(f"Hello from SimpleClass: {json.dumps(kwargs)}")
        return TaskDone(f"Kwarg value is:{json.dumps(kwargs)}")
