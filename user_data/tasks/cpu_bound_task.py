import threading

import requests
from pathos.multiprocessing import ProcessingPool

from telegrampybot.configuration import Configuration
from telegrampybot.conversation_handler.chat_state import TaskDone
from telegrampybot.structures.meta_data import MetaData

"""
This example includes:
- Running cpu bound task.
- Update a message when task is complete through api of the running flask server.

"""


class CpuBoundTask:

    def cpu_bound_function(self, *args):
        print("Starting CPU-bound task")
        # Simulate a CPU-bound operation
        sum(range(10 ** 8))  # This is a placeholder for a CPU-bound operation
        print(f"CPU-bound task completed")
        if (len(args) < 1):
            return
        # lets post update message to the telegram via the flask server
        # we have passed the metadata as argument in *args
        meta_data: MetaData = args[0]
        meta_data_json = meta_data.to_json()

        # url = "http://localhost:4212/update"
        url = f"http://localhost:{Configuration().flask_ip_port.port}/update"
        data = {
            "meta": meta_data_json,
            "data": {
                "msg": "Cpu bound task completed \n[update through flask server]"
            }
        }

        response = requests.post(url, json=data)
        print(response.json(), f" [{response.status_code}]")
        return ":)"

    def run_in_a_thread(self):
        # Don't do this, this will still block the main thread because it is cpu bound
        # Lol this will still block the main thread. you should run such in another process
        threading.Thread(target=self.cpu_bound_function, daemon=True).start()
        return TaskDone("Cpu bound task is running in another thread")

    # Run the cpu bound function in another process
    # Using "multiprocess" library will cause some Pickling error
    def run_in_a_process(self, **kwargs):
        metadata = kwargs.get("metadata")
        with ProcessingPool() as pool:
            result = pool.apipe(self.cpu_bound_function, metadata)
            # print(result.get()) # wait the process to complete
        return TaskDone("Cpu bound task running in another process")
