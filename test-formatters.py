#!/usr/bin/env python3
import formatters

from dataclasses import dataclass


@dataclass
class TestData:
    name: str
    temp: int
    rh: float


datasets = []
datasets.append([
    TestData('Sensor 1', 90, 0.9),
    TestData('Sensor 2', 89, 0.8),
    TestData('Sensor 3', 0, 0)
])
datasets.append([
    ['ID', 'Name', 'Value'],
    [1, 'One', '1'],
    [2, 'Two', '2'],
    [3, 'Three', '3']
])

for data in datasets:

    for fmt in formatters.List():
        print(f"----")
        print(f"Format: {fmt}")
        fmr = formatters.Get(fmt, data)
        value = fmr.string()
        print(f"\033[32m{value}\033[0m")
        print("")

        if fmt == 'text':
            print("text/table:")
            fmr._as_table = True
            print(f"\033[33m{fmr.string()}\033[0m")
