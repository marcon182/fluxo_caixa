from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from src.models.user import User, db
import re

auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    """Valida se o email tem um formato válido."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validação dos dados
        if not data.get('username'):
            return jsonify({'error': 'Nome de usuário é obrigatório'}), 400
        
        if not data.get('email'):
            return jsonify({'error': 'Email é obrigatório'}), 400
        
        if not data.get('password'):
            return jsonify({'error': 'Senha é obrigatória'}), 400
        
        if len(data['username']) < 3:
            return jsonify({'error': 'Nome de usuário deve ter pelo menos 3 caracteres'}), 400
        
        if len(data['password']) < 6:
            return jsonify({'error': 'Senha deve ter pelo menos 6 caracteres'}), 400
        
        if not is_valid_email(data['email']):
            return jsonify({'error': 'Email inválido'}), 400
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Nome de usuário já existe'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já está em uso'}), 400
        
        # Criar novo usuário
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário registrado com sucesso',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('username'):
            return jsonify({'error': 'Nome de usuário é obrigatório'}), 400
        
        if not data.get('password'):
            return jsonify({'error': 'Senha é obrigatória'}), 400
        
        # Buscar usuário
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Nome de usuário ou senha incorretos'}), 401
        
        # Fazer login do usuário
        login_user(user)
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        logout_user()
        return jsonify({'message': 'Logout realizado com sucesso'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/current_user', methods=['GET'])
@login_required
def get_current_user():
    try:
        return jsonify({
            'user': current_user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/check_auth', methods=['GET'])
def check_auth():
    """Verifica se o usuário está autenticado."""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict()
        }), 200
    else:
        return jsonify({
            'authenticated': False
        }), 200

