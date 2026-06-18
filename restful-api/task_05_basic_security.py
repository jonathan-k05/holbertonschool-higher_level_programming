#!/usr/bin/python3
"""Truc hyper compliqué"""

from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "super-secret-key-pour-les-tests"

auth = HTTPBasicAuth()
jwt = JWTManager(app)

users = {
    "user1": {
        "username": "user1",
        "password": generate_password_hash("password"),
        "role": "user"
    },
    "admin1": {
        "username": "admin1",
        "password": generate_password_hash("password"),
        "role": "admin"
    }
}


@auth.verify_password
def verify_password(username, password):
    """Vérifie les identifiants pour la Basic Auth."""

    user = users.get(username)
    if user and check_password_hash(user["password"], password):
        return username
    return None


@auth.error_handler
def basic_auth_error(status):
    """Force un retour standardisé 401 en cas d'échec Basic Auth."""

    return jsonify({"error": "Unauthorized access"}), 401


@jwt.unauthorized_loader
def handle_unauthorized_error(err):
    return jsonify({"error": "Missing or invalid token"}), 401


@jwt.invalid_token_loader
def handle_invalid_token_error(err):
    return jsonify({"error": "Invalid token"}), 401


@jwt.expired_token_loader
def handle_expired_token_error(err, expired_data):
    return jsonify({"error": "Token has expired"}), 401


@app.route("/basic-protected", methods=["GET"])
@auth.login_required
def basic_protected():
    """Route protégée par Basic Auth."""

    return "Basic Auth: Access Granted"


@app.route("/login", methods=["POST"])
def login():
    """Génère un token JWT si les identifiants POST sont valides."""

    if not request.is_json:
        return jsonify({"error": "Invalid JSON"}), 400

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user = users.get(username)
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Bad credentials"}), 401

    additional_claims = {"role": user["role"]}
    access_token = create_access_token(
        identity=username, additional_claims=additional_claims)

    return jsonify(access_token=access_token), 200


@app.route("/jwt-protected", methods=["GET"])
@jwt_required()
def jwt_protected():
    """Route protégée basique par JWT."""

    return "JWT Auth: Access Granted"


@app.route("/admin-only", methods=["GET"])
@jwt_required()
def admin_only():
    """Route protégée par JWT + Vérification du rôle Administrateur."""

    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    return "Admin Access: Granted"


if __name__ == "__main__":
    app.run()
