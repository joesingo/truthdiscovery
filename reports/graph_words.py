#!/usr/bin/env python3
from datetime import datetime
import os.path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

LOG_FILE = os.path.join(os.path.dirname(__file__), "wc.csv")

def main():
    xs = []
    ys = []
    with open(LOG_FILE) as csvfile:
        for line in csvfile:
            timestamp, words = map(int, line.strip().split(","))
            dt = datetime.utcfromtimestamp(timestamp)
            xs.append(dt)
            ys.append(words)

    fig, ax = plt.subplots()
    ax.plot(xs, ys)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m-%Y %H:%M"))
    ax.grid(True)
    fig.autofmt_xdate()

    fig.suptitle("Word count of work-in-progress dissertation over time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Word count")
    plt.show()

if __name__ == "__main__":
    main()
