#!/usr/bin/python3
"""
Task 02 - Dynamic Template with Loops and Conditions in Flask
Reads items from a JSON file and passes them to a Jinja template
that uses {% for %} and {% if %} to render content dynamically.
"""

import json
from flask import Flask, render_template
from jinja2 import DictLoader

app = Flask(__name__)

json_data = '''{
    "items": ["Python Book", "Flask Mug", "Jinja Sticker"]
}'''

templates = {
    'header.html': '''<header>
    <h1>My Flask App</h1>
    <nav>
        <a href="/">Home</a> | 
        <a href="/about">About</a> | 
        <a href="/contact">Contact</a> | 
        <a href="/items">Items</a>
    </nav>
</header>''',

    'footer.html': '''<footer>
    <p>&copy; 2024 My Flask App</p>
</footer>''',

    'items.html': '''<!doctype html>
<html lang="en">
<head>
    <title>Items List</title>
</head>
<body>
    {% include 'header.html' %}
    
    <h1>Items List</h1>
    
    {% if items %}
        <ul>
        {% for item in items %}
            <li>{{ item }}</li>
        {% endfor %}
        </ul>
    {% else %}
        <p>No items found</p>
    {% endif %}
    
    {% include 'footer.html' %}
</body>
</html>'''
}

app.jinja_env.loader = DictLoader(templates)


@app.route('/items')
def items():
    """
    def items
    """
    data = json.loads(json_data)
    items_list = data.get("items", [])
    return render_template('items.html', items=items_list)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
