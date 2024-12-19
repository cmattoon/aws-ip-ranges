#!/usr/bin/env python3
import formatters

data = [
    ['ID', 'Name', 'Value'],
    [1, 'One', '1'],
    [2, 'Two', '2'],
    [3, 'Three', '3']
]

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
