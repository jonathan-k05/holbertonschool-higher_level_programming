#!/usr/bin/python3
"""
Task 02 - Dynamic Template with Loops and Conditions in Flask
Reads items from a JSON file and passes them to a Jinja template
that uses {% for %} and {% if %} to render content dynamically.
"""
import json
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/items')
def items():
    """
    Reads items.json and passes the list to items.html.
    If the file is missing or malformed, an empty list is used
    so the template's 'No items found' condition is triggered.
    """
    try:
        with open('items.json', 'r') as f:
            data = json.load(f)
        items_list = data.get('items', [])
    except (FileNotFoundError, json.JSONDecodeError):
        items_list = []

    return render_template('items.html', items=items_list)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
