#!/usr/bin/python3
"""
Module pour sérialiser et désérialiser un dictionnaire au format XML.
"""
import xml.etree.ElementTree as ET


def serialize_to_xml(dictionary, filename):
    """
    Sérialise un dictionnaire Python au format XML et l'enregistre dans un fichier.
    """
    root = ET.Element("data")

    for key, value in dictionary.items():
        child = ET.SubElement(root, key)
        child.text = str(value)

    tree = ET.ElementTree(root)
    tree.write(filename, encoding='utf-8', xml_declaration=True)


def deserialize_from_xml(filename):
    """
    Lit un fichier XML et reconstruit un dictionnaire Python.
    """
    try:
        tree = ET.parse(filename)
        root = tree.getroot()

        # Reconstitution du dictionnaire à partir des éléments enfants
        return {child.tag: child.text for child in root}
    except Exception:
        return {}
