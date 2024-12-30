# api.py
from flask import Blueprint, jsonify

# Membuat blueprint untuk API
api_bp = Blueprint('api', __name__)

# Contoh route API
@api_bp.route('/status', methods=['GET'])
def status():
    return jsonify({"message": "API is running!"}), 200

@api_bp.route('/data', methods=['GET'])
def get_data():
    # Simulasi data yang akan dikirimkan oleh API
    data = {
        "user_id": 123,
        "username": "john_doe",
        "email": "john@example.com"
    }
    return jsonify(data), 200
