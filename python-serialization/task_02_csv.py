#!/usr/bin/python3
"""
Module pour convertir des données CSV en format JSON.
"""
import csv
import json


def convert_csv_to_json(csv_filename):
    """
    Lit un fichier CSV et convertit son contenu en un fichier JSON nommé data.json.
    Renvoie True si la conversion réussit, False en cas d'erreur.
    """
    try:
        with open(csv_filename, mode='r', encoding='utf-8') as csv_file:
            # Utilisation de DictReader pour transformer chaque ligne en dictionnaire
            csv_reader = csv.DictReader(csv_file)
            data = list(csv_reader)

        with open('data.json', mode='w', encoding='utf-8') as json_file:
            # Sérialisation de la liste de dictionnaires en JSON
            json.dump(data, json_file, ensure_ascii=False, indent=4)

        return True

    except Exception:
        return False
