#!/usr/bin/python3
"""
This script adds all command line arguments to a Python list,
and saves them to a JSON file format.
"""
import sys
import os

save_to_json_file = (
    __import__('5-save_to_json_file').save_to_json_file
)
load_from_json_file = (
    __import__('6-load_from_json_file').load_from_json_file
)

filename = "add_item.json"

# Charge la liste existante si le fichier existe, sinon initialise une liste vide
if os.path.exists(filename):
    my_list = load_from_json_file(filename)
else:
    my_list = []

# Ajoute les arguments (en excluant le nom du script sys.argv[0])
my_list.extend(sys.argv[1:])

# Sauvegarde la liste mise à jour
save_to_json_file(my_list, filename)
