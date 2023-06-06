import os
from datetime import datetime


def record_log(content: str):
    # record to a txt file and append
    with open("log.txt", "a") as f:
        f.write("-" * 50)
        f.write(os.linesep)
        f.write(str(datetime.now()) + ": " + content)
        f.write(os.linesep)
