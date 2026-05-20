#!/usr/bin/python3
def common_elements(set_1, set_2):
    val_final = []
    val_final += [val for val in set_1 for val2 in set_2 if val == val2]
    return val_final
