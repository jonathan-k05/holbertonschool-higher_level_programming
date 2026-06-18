#!/usr/bin/python3
"""
Module de génération d'invitations personnalisées à partir d'un template.
Vérifie les types de données, gère les cas vides et remplace les placeholders manquants par 'N/A'.
"""

import os


def generate_invitations(template, attendees):
    """
    function pour la generation
    """

    if not isinstance(template, str):
        print("Error: Template must be a string.")
        return

    if not isinstance(attendees, list) or not all(isinstance(a, dict) for a in attendees):
        print("Error: Attendees must be a list of dictionaries.")
        return

    if not template.strip():
        print("Template is empty, no output files generated.")
        return

    if not attendees:
        print("No data provided, no output files generated.")
        return

    placeholders = ["name", "event_title", "event_date", "event_location"]

    for idx, attendee in enumerate(attendees, start=1):
        content = template

        for key in placeholders:
            val = attendee.get(key)
            if val is None:
                val = "N/A"
            content = content.replace(f"{{{key}}}", str(val))

        filename = f"output_{idx}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Error writing to {filename}: {e}")
