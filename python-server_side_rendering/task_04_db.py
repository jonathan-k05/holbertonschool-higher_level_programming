#!/usr/bin/python3
"""
Task 04 - Extending Dynamic Data Display to Include SQLite in Flask
Extends task_03_files.py by adding 'sql' as a valid source parameter.
Reads product data from products.json, products.csv, or products.db
depending on the 'source' query parameter. Supports optional 'id' filtering.
"""
import csv
import json
import os
import sqlite3
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
    """Définition des items"""

    source = request.args.get('source')
    product_id = request.args.get('id')

    if source not in ['json', 'csv', 'sql']:
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

    elif source == 'sql':
        if os.path.exists('products.db'):
            try:
                conn = sqlite3.connect('products.db')
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                if product_id is not None:
                    cursor.execute(
                        'SELECT id, name, category, price FROM Products WHERE id = ?', (product_id,))
                else:
                    cursor.execute(
                        'SELECT id, name, category, price FROM Products')

                rows = cursor.fetchall()
                conn.close()

                products_list = [dict(row) for row in rows]

                if product_id is not None and not products_list:
                    return render_template('product_display.html', error="Product not found")

            except sqlite3.Error:
                return render_template('product_display.html', error="Database error")
        else:
            return render_template('product_display.html', error="Database error")

    if source in ['json', 'csv'] and product_id is not None:
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
