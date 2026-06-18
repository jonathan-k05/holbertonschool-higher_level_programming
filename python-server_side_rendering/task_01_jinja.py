#!/usr/bin/python3
"""le task_01"""
from flask import Flask, render_template
from jinja2 import DictLoader


app = Flask(__name__)

"""Définition de tous les templates HTML directement en Python"""

templates = {
    'header.html': '''<header>
    <h1>My Flask App</h1>
    <nav>
        <a href="/">Home</a> | 
        <a href="/about">About</a> | 
        <a href="/contact">Contact</a>
    </nav>
</header>''',

    'footer.html': '''<footer>
    <p>&copy; 2024 My Flask App</p>
</footer>''',

    'index.html': '''<!doctype html>
<html lang="en">
<head>
    <title>My Flask App</title>
</head>
<body>
    {% include 'header.html' %}
    <h1>Welcome to My Flask App</h1>
    <p>This is a simple Flask application.</p>
    <ul>
        <li>Flask</li>
        <li>HTML</li>
        <li>Templates</li>
    </ul>
    {% include 'footer.html' %}
</body>
</html>''',

    'about.html': '''<!doctype html>
<html lang="en">
<head>
    <title>About Us</title>
</head>
<body>
    {% include 'header.html' %}
    <h1>About Us</h1>
    <p>This page describes our application.</p>
    {% include 'footer.html' %}
</body>
</html>''',

    'contact.html': '''<!doctype html>
<html lang="en">
<head>
    <title>Contact Us</title>
</head>
<body>
    {% include 'header.html' %}
    <h1>Contact Us</h1>
    <p>Contact us at contact@example.com.</p>
    {% include 'footer.html' %}
</body>
</html>'''
}

app.jinja_env.loader = DictLoader(templates)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
