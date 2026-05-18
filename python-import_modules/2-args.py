#!/usr/bin/python3
from sys import argv

if __name__ == "__main__":
    args = argv[1:]
    n = len(args)

    if n == 0:
        print("0 arguments.")
    elif n == 1:
        print("1 argument:")
    else:
        print("{} arguments:".format(n))

    for i in range(n):
        print("{}: {}".format(i + 1, args[i]))
