#!/usr/bin/python3
"""
code 
"""
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    """
    home
    """

    return render_template('index.html')


@app.route('/about')
def about():
    """
    about
    """

    return render_template('about.html')


@app.route('/contact')
def contact():
    """
    contact
    """
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
