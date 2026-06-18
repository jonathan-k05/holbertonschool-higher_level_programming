#!/usr/bin/python3
"""
Task_04
"""

from flask import Flask, jsonify, request

app = Flask(__name__)
users = {}


@app.route("/")
def home():
    """Endpoint racine : message de bienvenue."""

    return "Welcome to the Flask API!"


@app.route("/data")
def get_data():
    """Endpoint /data : retourne la liste de tous les noms d'utilisateurs."""

    return jsonify(list(users.keys()))


@app.route("/status")
def status():
    """Endpoint /status : vérification de l'état de l'API."""

    return "OK"


@app.route("/users/<username>")
def get_user(username):
    """Endpoint dynamique : retourne l'objet complet d'un utilisateur spécifique."""

    user = users.get(username)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@app.route("/add_user", methods=["POST"])
def add_user():
    """Endpoint POST /add_user : ajoute un nouvel utilisateur après validations."""

    if not request.is_json:
        return jsonify({"error": "Invalid JSON"}), 400

    data = request.get_json()

    username = data.get("username")
    if not username:
        return jsonify({"error": "Username is required"}), 400

    if username in users:
        return jsonify({"error": "Username already exists"}), 409

    users[username] = data

    response_data = {
        "message": "User added",
        "user": data
    }
    return jsonify(response_data), 201


if __name__ == "__main__":
    app.run()
