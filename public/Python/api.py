from quart import Quart, request, jsonify
from motor.motor_asyncio import AsyncIOMotorClient
import subprocess
import json
import os
from quart_cors import cors
import asyncio
import random
import string

app = Quart(__name__)
app = cors(app, allow_origin="http://localhost:3000")

# MongoDB setup
uri = 'mongodb+srv://Payment:payment123@cluster0.enjvvgg.mongodb.net/Payment?retryWrites=true&w=majority&appName=Cluster0'
client = AsyncIOMotorClient(uri)
db = client['mydatabase']
users_collection = db['users']
transactions_collection = db['transactions']


# Helper function to generate a random transaction ID
def generate_transaction_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

@app.route('/signup', methods=['POST'])
async def signup():
    data = await request.get_json()

    user_id = data.get('user_id')
    username = data.get('username')
    password = data.get('password')
    # account_number = data.get('account_number', None)
    balance = data.get('balance', 0)

    if not user_id or not username or not password:
        return jsonify({'error': 'User ID, username, and password are required'}), 400

    if await users_collection.find_one({'$or': [{'username': username}, {'id': user_id}]}):
        return jsonify({'error': 'Username or User ID already exists'}), 400

    users_collection.insert_one({
        'id': user_id,
        'username': username,
        'password': password,
        'account_number': account_number,
        'balance': balance,
    })

    # Call the Selenium script asynchronously
    # try:
    #     script_path = os.path.join(os.path.dirname(__file__), 'selenium_user_add.py')
    #     result = await asyncio.create_subprocess_exec(
    #         'python3', script_path, json.dumps(data),
    #         stdout=subprocess.PIPE, stderr=subprocess.PIPE
    #     )
    #     stdout, stderr = await result.communicate()
    #     if result.returncode != 0:
    #         return jsonify({'error': f'Failed to run Selenium script: {stderr.decode()}'}), 500
    # except Exception as e:
    #     return jsonify({'error': f'Failed to run Selenium script: {str(e)}'}), 500

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/user/<user_id>', methods=['GET'])
async def get_user_by_id(user_id):
    user = await users_collection.find_one({'id': user_id})
    if user:
        return jsonify({
            'username': user['username'],
            'id': user['id'],
            'account_number': user['account_number'],
            'balance': user['balance'],
            'password': user['password']
        }), 200

    return jsonify({'error': 'User not found'}), 404

@app.route('/users', methods=['GET'])
async def get_users():
    users = await users_collection.find({}, {'_id': 0}).to_list(length=None)  # Fetch all users asynchronously
    return jsonify(users), 200

# Modified handle_deposit function to add a transaction entry
@app.route('/deposit', methods=['POST'])
async def handle_deposit():
    data = await request.get_json()

    user_id = data.get('user_id')
    deposit = data.get('deposit')
    transaction_image = data.get('transaction_image')

    if not user_id or not deposit or not transaction_image:
        return jsonify({'error': 'User ID, deposit amount, and transaction image are required'}), 400

    user = await users_collection.find_one({'id': user_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Generate a new transaction entry
    transaction_id = generate_transaction_id()
    transaction_entry = {
        'transaction_id': transaction_id,
        'user_id': user_id,
        'type': 'deposit',
        'amount': deposit,
        'status': 'pending',
        'transaction_image': transaction_image
    }
    await transactions_collection.insert_one(transaction_entry)

    return jsonify({'message': 'Deposit recorded, pending approval', 'transaction_id': transaction_id}), 200

# Modified handle_withdraw function to add a transaction entry
@app.route('/withdraw', methods=['POST'])
async def handle_withdraw():
    data = await request.get_json()

    user_id = data.get('user_id')
    withdraw = data.get('withdraw')
    account_number = data.get('account_number')

    if not user_id or not withdraw or not account_number:
        return jsonify({'error': 'User ID, withdraw amount, and account number are required'}), 400

    user = await users_collection.find_one({'id': user_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user['balance'] < withdraw:
        return jsonify({'error': 'Insufficient balance'}), 400

    # Generate a new transaction entry
    transaction_id = generate_transaction_id()
    transaction_entry = {
        'transaction_id': transaction_id,
        'user_id': user_id,
        'type': 'withdraw',
        'amount': withdraw,
        'status': 'pending',
        'account_number': account_number
    }
    await transactions_collection.insert_one(transaction_entry)

    return jsonify({'message': 'Withdrawal recorded, pending approval', 'transaction_id': transaction_id}), 200

# Update depositConfirm to update the transaction status
@app.route('/depositConfirm', methods=['POST'])
async def confirm_deposit():
    data = await request.get_json()
    user_id = data.get('user_id')
    amount = data.get('amount')
    transaction_id = data.get('transaction_id')  # Now require transaction ID

    user = await users_collection.find_one({'id': user_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Update user's balance and deposit status
    await users_collection.update_one(
        {'id': user_id},
        {'$inc': {'balance': amount}}
    )

    # Update transaction status to 'approved'
    await transactions_collection.update_one(
        {'transaction_id': transaction_id},
        {'$set': {'status': 'approved'}}
    )

    updated_user = await users_collection.find_one({'id': user_id})
    return jsonify({'message': 'Deposit successful', 'balance': updated_user['balance']}), 200

# Update depositDecline to update the transaction status
@app.route('/depositDecline', methods=['POST'])
async def decline_deposit():
    data = await request.get_json()
    user_id = data.get('user_id')
    transaction_id = data.get('transaction_id')  # Now require transaction ID

    user = await users_collection.find_one({'id': user_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Update transaction status to 'declined'
    await transactions_collection.update_one(
        {'transaction_id': transaction_id},
        {'$set': {'status': 'declined'}}
    )

    return jsonify({'message': 'Deposit declined'}), 200

# Similar changes for withdrawConfirm and withdrawDecline
@app.route('/withdrawConfirm', methods=['POST'])
async def confirm_withdraw():
    data = await request.get_json()
    user_id = data.get('user_id')
    amount = data.get('amount')
    transaction_id = data.get('transaction_id')  # Now require transaction ID

    user = await users_collection.find_one({'id': user_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user['balance'] < amount:
        return jsonify({'error': 'Insufficient balance'}), 400

    # Update user's balance and withdraw status
    await users_collection.update_one(
        {'id': user_id},
        {'$inc': {'balance': -amount}}
    )

    # Update transaction status to 'approved'
    await transactions_collection.update_one(
        {'transaction_id': transaction_id},
        {'$set': {'status': 'approved'}}
    )

    updated_user = await users_collection.find_one({'id': user_id})
    return jsonify({'message': 'Withdrawal successful', 'balance': updated_user['balance']}), 200

@app.route('/withdrawDecline', methods=['POST'])
async def decline_withdraw():
    data = await request.get_json()
    user_id = data.get('user_id')
    transaction_id = data.get('transaction_id')  # Now require transaction ID

    user = await users_collection.find_one({'id': user_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Update transaction status to 'declined'
    await transactions_collection.update_one(
        {'transaction_id': transaction_id},
        {'$set': {'status': 'declined'}}
    )

    return jsonify({'message': 'Withdrawal declined'}), 200

@app.route('/transactions', methods=['GET'])
async def get_transactions():
    transactions = await transactions_collection.find({}, {'_id': 0}).to_list(length=None)  # Fetch all transactions asynchronously
    return jsonify(transactions), 200

if __name__ == '__main__':
    app.run(port=5000)
