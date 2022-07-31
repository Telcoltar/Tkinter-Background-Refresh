import random
import time
from datetime import datetime


class DummyDataInOut:
    def get_data(self):
        time.sleep(0.2)
        return f'{datetime.now():%H:%M:%S.%f} {" ".join([str(random.randint(0, 10)) for _ in range(10)])}'

    def accept_command(self, command: str):
        return f"{datetime.now():%H:%M:%S.%f} Got command {command}."
