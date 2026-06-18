#!/usr/bin/python3
"""
Task 03 - Displaying Data from JSON or CSV Files in Flask
Reads product data from products.json or products.csv based on
a 'source' query parameter. Supports optional filtering by 'id'.
Handles invalid source values and missing product IDs gracefully.
"""

import json
import csv
from flask import Flask, render_template, request

app = Flask(__name__)


def read_json(filepath):
    """Reads and returns a list of products from a JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def read_csv(filepath):
    """
    Reads a CSV file and returns a list of product dicts.
    Converts 'id' to int and 'price' to float for consistency with JSON data.
    """
    products = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['id'] = int(row['id'])
            row['price'] = float(row['price'])
            products.append(row)
    return products


@app.route('/products')
def products():
    """
    Route: /products?source=json|csv&id=<optional>
    - source: determines which file to read (json or csv)
    - id: optional filter; returns only the matching product
    Returns error messages for invalid source or missing product.
    """
    source = request.args.get('source')
    product_id = request.args.get('id')

    if source == 'json':
        data = read_json('products.json')
    elif source == 'csv':
        data = read_csv('products.csv')
    else:
        return render_template('product_display.html', error="Wrong source")

    if product_id is not None:
        data = [p for p in data if p['id'] == int(product_id)]
        if not data:
            return render_template('product_display.html', error="Product not found")

    return render_template('product_display.html', products=data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
