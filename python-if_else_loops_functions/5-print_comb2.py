#!/usr/bin/python3
for i in range(100):
    print(f'{i:02d}' + (", " if i < 98 else "\n"), end="")
