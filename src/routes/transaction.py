from flask import Blueprint, request, jsonify
from src.models.transaction import Transaction
from src.models.user import db
from datetime import datetime

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/transactions', methods=['GET'])
def get_transactions():
    try:
        transactions = Transaction.query.order_by(Transaction.date.desc()).all()
        return jsonify([transaction.to_dict() for transaction in transactions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('/transactions', methods=['POST'])
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
        
        # Criar nova transação
        transaction = Transaction(
            description=data['description'],
            amount=float(data['amount']),
            type=data['type'],
            date=datetime.strptime(data.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify(transaction.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    try:
        transaction = Transaction.query.get_or_404(transaction_id)
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({'message': 'Transação excluída com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('/balance', methods=['GET'])
def get_balance():
    try:
        income = db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.type == 'income').scalar() or 0
        expense = db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.type == 'expense').scalar() or 0
        balance = income - expense
        
        return jsonify({
            'income': income,
            'expense': expense,
            'balance': balance
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

