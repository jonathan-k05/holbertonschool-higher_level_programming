#!/usr/bin/python3
"""
Task 03 - Displaying Data from JSON or CSV Files in Flask
Reads product data from products.json or products.csv based on
a 'source' query parameter. Supports optional filtering by 'id'.
Handles invalid source values and missing product IDs gracefully.
"""

import csv
import json
import os
from flask import Flask, render_template, request
from jinja2 import DictLoader

app = Flask(__name__)

templates = {
    'product_display.html': '''<!doctype html>
<html lang="en">
<head>
    <title>Products</title>
</head>
<body>
    {% if error %}
        <p>{{ error }}</p>
    {% else %}
        <table border="1">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Category</th>
                    <th>Price</th>
                </tr>
            </thead>
            <tbody>
                {% for product in products %}
                <tr>
                    <td>{{ product.name }}</td>
                    <td>{{ product.category }}</td>
                    <td>{{ product.price }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    {% endif %}
</body>
</html>'''
}

app.jinja_env.loader = DictLoader(templates)


@app.route('/products')
def products():
    """Déf product"""
    source = request.args.get('source')
    product_id = request.args.get('id')

    if source not in ['json', 'csv']:
        return render_template('product_display.html', error="Wrong source")

    products_list = []

    if source == 'json':
        if os.path.exists('products.json'):
            with open('products.json', 'r') as f:
                try:
                    products_list = json.load(f)
                except json.JSONDecodeError:
                    pass

    elif source == 'csv':
        if os.path.exists('products.csv'):
            with open('products.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        row['id'] = int(row['id'])
                    except ValueError:
                        pass
                    try:
                        row['price'] = float(row['price'])
                    except ValueError:
                        pass
                    products_list.append(row)

    if product_id is not None:
        try:
            target_id = int(product_id)
            products_list = [
                p for p in products_list if p.get('id') == target_id]
            if not products_list:
                return render_template('product_display.html', error="Product not found")
        except ValueError:
            return render_template('product_display.html', error="Product not found")

    return render_template('product_display.html', products=products_list)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
