#!/usr/bin/python3
"""
Task 04 - Extending Dynamic Data Display to Include SQLite in Flask
Extends task_03_files.py by adding 'sql' as a valid source parameter.
Reads product data from products.json, products.csv, or products.db
depending on the 'source' query parameter. Supports optional 'id' filtering.
"""

import json
import csv
import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)


def read_json(filepath):
    """Reads and returns a list of products from a JSON file."""

    with open(filepath, 'r') as f:
        return json.load(f)


def read_csv(filepath):
    """
    Reads a CSV file and returns a list of product dicts.
    Converts 'id' to int and 'price' to float for consistency.
    """

    products = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['id'] = int(row['id'])
            row['price'] = float(row['price'])
            products.append(row)
    return products


def read_sql(db_path):
    """
    Connects to the SQLite database and returns all rows from Products
    as a list of dicts with keys: id, name, category, price.
    """

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, category, price FROM Products')
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


@app.route('/products')
def products():
    """
    Route: /products?source=json|csv|sql&id=<optional>
    - source: determines the data source (json, csv, or sql)
    - id: optional filter; returns only the matching product
    Returns error messages for invalid source or missing product.
    """

    source = request.args.get('source')
    product_id = request.args.get('id')

    if source == 'json':
        data = read_json('products.json')
    elif source == 'csv':
        data = read_csv('products.csv')
    elif source == 'sql':
        data = read_sql('products.db')
    else:
        return render_template('product_display.html', error="Wrong source")

    if product_id is not None:
        data = [p for p in data if p['id'] == int(product_id)]
        if not data:
            return render_template('product_display.html', error="Product not found")

    return render_template('product_display.html', products=data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
