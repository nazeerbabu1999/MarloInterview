from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from flask_jwt_extended import get_jwt
from app.models import User, GroupData

data_blueprint = Blueprint('data', __name__)

@data_blueprint.route('/login', methods=['POST'])
def login():
    """
    Login endpoint to authenticate the user and issue a JWT.
    """
    data = request.form
    username = data.get('username')
    password = data.get('password')
    print(username,password,"user data")
    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({"msg": "Invalid username or password"}), 401

    # Create JWT token with user ID and role
    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify(access_token=access_token)

@data_blueprint.route('/group-data', methods=['GET'])
@jwt_required()
def fetch_group_data():
    """
    Fetch group data based on the role in the JWT token.
    """
    # Get user identity from JWT token
    identity = get_jwt_identity()  # This will now return a string (e.g., user ID)
    user_role = get_jwt().get("role") 
    user_id = get_jwt().get("id") 
    

    # Filter data based on role
    if user_role == 'admin':
        data = GroupData.query.all()
    elif user_role in ['bulk', 'tanker']:
        data = GroupData.query.filter_by(group_type=user_role).all()
    else:
        return jsonify({"msg": "Unauthorized access"}), 403

    # Serialize and return data
    return jsonify({
        "success": True,
        "data": [entry.data for entry in data]
    })
