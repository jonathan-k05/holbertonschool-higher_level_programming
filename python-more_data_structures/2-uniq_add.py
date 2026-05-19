#!/usr/bin/python3
def uniq_add(my_list=[]):
    uniques = []
    for val in my_list:
        if val not in uniques:
            uniques.append(val)
    total = sum(uniques)
    return total
