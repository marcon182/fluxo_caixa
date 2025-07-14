from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from src.models.transaction import Transaction
from src.models.user import db
from datetime import datetime

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/transactions', methods=['GET'])
@login_required
def get_transactions():
    try:
        # Buscar apenas transações do usuário logado
        transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
        return jsonify([transaction.to_dict() for transaction in transactions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('/transactions', methods=['POST'])
@login_required
def add_transaction():
    try:
        data = request.get_json()
        
        # Validação dos dados
        if not data.get('description'):
            return jsonify({'error': 'Descrição é obrigatória'}), 400
        
        if not data.get('amount'):
            return jsonify({'error': 'Valor é obrigatório'}), 400
        
        if data.get('type') not in ['income', 'expense']:
            return jsonify({'error': 'Tipo deve ser "income" ou "expense"'}), 400
        
        # Criar nova transação associada ao usuário logado
        transaction = Transaction(
            description=data['description'],
            amount=float(data['amount']),
            type=data['type'],
            date=datetime.strptime(data.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date(),
            user_id=current_user.id
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify(transaction.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('/transactions/<int:transaction_id>', methods=['DELETE'])
@login_required
def delete_transaction(transaction_id):
    try:
        # Buscar transação apenas do usuário logado
        transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
        
        if not transaction:
            return jsonify({'error': 'Transação não encontrada'}), 404
        
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({'message': 'Transação excluída com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('/balance', methods=['GET'])
@login_required
def get_balance():
    try:
        # Calcular saldo apenas das transações do usuário logado
        income = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.type == 'income', 
            Transaction.user_id == current_user.id
        ).scalar() or 0
        
        expense = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.type == 'expense', 
            Transaction.user_id == current_user.id
        ).scalar() or 0
        
        balance = income - expense
        
        return jsonify({
            'income': income,
            'expense': expense,
            'balance': balance
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

