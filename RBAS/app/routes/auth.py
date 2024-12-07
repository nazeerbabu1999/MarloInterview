from flask import Blueprint, request, jsonify
from app import db
from app.models import User, UserPermission

auth_bp = Blueprint('auth', __name__)



@auth_bp.route('/users', methods=['GET'])
def get_users():
    """
    Get all users
    """
    users = User.query.all()
    result = [
        {
            'id': user.id,
            'username': user.username,
            'role': user.role
        } for user in users
    ]
    return jsonify(result), 200


@auth_bp.route('users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get a single user by ID
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    result = {
        'id': user.id,
        'username': user.username,
        'role': user.role
    }
    return jsonify(result), 200


@auth_bp.route('users/', methods=['POST'])
def create_user():
    """
    Create a new user
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role_name = data.get('role')

    if not all([username, password, role_name]):
        return jsonify({'error': 'Missing fields'}), 400

    # Check if role exists
    role = UserPermission.query.filter_by(role=role_name).first()
    if not role:
        return jsonify({'error': 'Invalid role'}), 400

    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400

    # Create the user
    new_user = User(username=username, password=password, user_role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully', 'user_id': new_user.id}), 201


@auth_bp.route('users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Update a user's details
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    username = data.get('username')
    password = data.get('password')
    role_name = data.get('role')

    if username:
        user.username = username
    if password:
        user.password = password
    if role_name:
        role = UserPermission.query.filter_by(role=role_name).first()
        if not role:
            return jsonify({'error': 'Invalid role'}), 400
        user.user_role = role

    db.session.commit()
    return jsonify({'message': 'User updated successfully'}), 200


@auth_bp.route('users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Delete a user by ID
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200
