from flask import Flask, request, jsonify
from pymongo import MongoClient
import subprocess
import json
import os
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
uri = 'mongodb+srv://Payment:payment123@cluster0.enjvvgg.mongodb.net/Payment?retryWrites=true&w=majority&appName=Cluster0'

# MongoDB setup
client = MongoClient(uri)
db = client['mydatabase']
users_collection = db['users']

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    user_id = data.get('user_id')
    username = data.get('username')
    password = data.get('password')
    account_number = data.get(None)  # New field
    balance = data.get('balance', 0)
    withdraw = data.get('withdraw', 0)
    deposit = data.get('deposit', 0)
    deposit_status = data.get('deposit_status', 'pending')  # Default is 'pending'
    withdraw_status = data.get('withdraw_status', 'pending')  # Default is 'pending'
    transaction_image = data.get('transaction_image', None)

    # Validate required fields
    if not user_id or not username or not password:
        return jsonify({'error': 'User ID, username and password are required'}), 400

    # Check for existing username or user ID
    if users_collection.find_one({'$or': [{'username': username}, {'id': user_id}]}):
        return jsonify({'error': 'Username or User ID already exists'}), 400

    # Save the user in MongoDB
    users_collection.insert_one({
        'id': user_id,
        'username': username,
        'password': password,
        'account_number': account_number,  # Save account number
        'balance': balance,
        'withdraw': withdraw,
        'deposit': deposit,
        'deposit_status': deposit_status,
        'withdraw_status': withdraw_status,
        'transaction_image': transaction_image
    })

    # Call the Selenium script
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'selenium_user_add.py')
        result = subprocess.run(['py', script_path, json.dumps(data)], capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        return jsonify({'error': f'Failed to run Selenium script: {str(e)}'}), 500

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/withdrawConfirm', methods=['POST'])
def confirm_withdraw():
    data = request.get_json()
    user_id = data.get('user_id')
    amount = data.get('amount')

    # Find user in MongoDB
    user = users_collection.find_one({'id': user_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Ensure sufficient balance
    if user['balance'] < amount:
        return jsonify({'error': 'Insufficient balance'}), 400

    # Update the balance and withdraw status in MongoDB
    users_collection.update_one(
        {'id': user_id},
        {
            '$set': {'withdraw_status': 'approved'},
            '$inc': {'balance': -amount, 'withdraw': amount}
        }
    )

    updated_user = users_collection.find_one({'id': user_id})
    return jsonify({'message': 'Withdrawal successful', 'balance': updated_user['balance']}), 200

@app.route('/withdrawDecline', methods=['POST'])
def decline_withdraw():
    data = request.get_json()
    user_id = data.get('user_id')

    # Find user in MongoDB
    user = users_collection.find_one({'id': user_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Update the withdraw status to declined
    users_collection.update_one(
        {'id': user_id},
        {'$set': {'withdraw_status': 'declined'}}
    )

    return jsonify({'message': 'Withdrawal declined'}), 200

@app.route('/depositConfirm', methods=['POST'])
def confirm_deposit():
    data = request.get_json()
    user_id = data.get('user_id')
    amount = data.get('amount')

    user = users_collection.find_one({'id': user_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    users_collection.update_one(
        {'id': user_id},
        {
            '$set': {'deposit_status': 'approved'},
            '$inc': {'balance': amount, 'deposit': amount}
        }
    )

    updated_user = users_collection.find_one({'id': user_id})
    return jsonify({'message': 'Deposit successful', 'balance': updated_user['balance']}), 200

@app.route('/depositDecline', methods=['POST'])
def decline_deposit():
    data = request.get_json()
    user_id = data.get('user_id')

    user = users_collection.find_one({'id': user_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    users_collection.update_one(
        {'id': user_id},
        {'$set': {'deposit_status': 'declined'}}
    )

    return jsonify({'message': 'Deposit declined'}), 200

@app.route('/user/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    user = users_collection.find_one({'id': user_id})
    if user:
        return jsonify({
            'username': user['username'],
            'id': user['id'],
            'account_number': user['account_number'],  # Include account number
            'balance': user['balance'],
            'password': user['password']
        }), 200

    return jsonify({'error': 'User not found'}), 404

@app.route('/users', methods=['GET'])
def get_users():
    users = list(users_collection.find({}, {'_id': 0}))  # Omit MongoDB internal _id field
    return jsonify(users), 200

@app.route('/deposit', methods=['POST'])
def handle_deposit():
    data = request.get_json()

    user_id = data.get('user_id')
    deposit = data.get('deposit')
    transaction_image = data.get('transaction_image')

    if not user_id or not deposit or not transaction_image:
        return jsonify({'error': 'User ID, deposit amount, and transaction image are required'}), 400

    user = users_collection.find_one({'id': user_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    users_collection.update_one(
        {'id': user_id},
        {
            '$set': {
                'deposit_status': 'pending',
                'transaction_image': transaction_image
            },
            '$inc': {
                'deposit': deposit
            }
        }
    )

    return jsonify({'message': 'Deposit recorded, pending approval'}), 200

@app.route('/withdraw', methods=['POST'])
def handle_withdraw():
    data = request.get_json()

    user_id = data.get('user_id')
    withdraw = data.get('withdraw')
    account_number = data.get('account_number')

    if not user_id or not withdraw or not account_number:
        return jsonify({'error': 'User ID, withdraw amount, and account number are required'}), 400

    user = users_collection.find_one({'id': user_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user['balance'] < withdraw:
        return jsonify({'error': 'Insufficient balance'}), 400

    # Update user's withdrawal info and account number
    users_collection.update_one(
        {'id': user_id},
        {
            '$set': {
                'withdraw_status': 'pending',
                'account_number': account_number  # Update account number
            },
            '$inc': {'withdraw': withdraw}  # Increment withdraw amount
        }
    )

    return jsonify({'message': 'Withdrawal recorded, pending approval'}), 200


if __name__ == '__main__':
    app.run(debug=True)
