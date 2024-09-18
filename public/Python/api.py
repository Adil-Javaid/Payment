from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
# MongoDB connection URI
uri = 'mongodb+srv://Payment:payment123@cluster0.enjvvgg.mongodb.net/Payment?retryWrites=true&w=majority'

# MongoDB setup
client = MongoClient(uri)
db = client['Payment']  # Database name
users_collection = db['users']  # Collection name

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    # Retrieve data from the request
    user_id = data.get('user_id')
    username = data.get('username')
    password = data.get('password')
    balance = data.get('balance', 0)  # Default value is 0 if not provided
    withdraw = data.get('withdraw', 0)  # Default value is 0 if not provided
    deposit = data.get('deposit', 0)  # Default value is 0 if not provided
    deposit_status = data.get('deposit_status', 'pending')  # Default is 'pending'
    withdraw_status = data.get('withdraw_status', 'pending')  # Default is 'pending'
    transaction_image = data.get('transaction_image', None)  # Default is None (if not provided)

    # Validate the required fields
    if not user_id or not username or not password:
        return jsonify({'error': 'User ID, username, and password are required'}), 400

    # Check for existing username or user ID
    if users_collection.find_one({'$or': [{'username': username}, {'id': user_id}]}):
        return jsonify({'error': 'Username or User ID already exists'}), 400

    # Save the user in MongoDB
    users_collection.insert_one({
        'id': user_id,
        'username': username,
        'password': password,
        'balance': balance,
        'withdraw': withdraw,
        'deposit': deposit,
        'deposit_status': deposit_status,
        'withdraw_status': withdraw_status,
        'transaction_image': transaction_image
    })

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
            '$inc': {'balance': -amount, 'withdraw': amount}  # Decrease balance and increase withdraw
        }
    )

    # Fetch updated balance
    updated_user = users_collection.find_one({'id': user_id})

    return jsonify({'message': 'Withdrawal successful', 'balance': updated_user['balance']}), 200

@app.route('/depositConfirm', methods=['POST'])
def confirm_deposit():
    data = request.get_json()
    user_id = data.get('user_id')
    amount = data.get('amount')

    # Find user in MongoDB
    user = users_collection.find_one({'id': user_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Update the balance and deposit status in MongoDB
    users_collection.update_one(
        {'id': user_id},
        {
            '$set': {'deposit_status': 'approved'},
            '$inc': {'balance': amount, 'deposit': amount}  # Increase balance and deposit
        }
    )

    # Fetch updated balance
    updated_user = users_collection.find_one({'id': user_id})

    return jsonify({'message': 'Deposit successful', 'balance': updated_user['balance']}), 200

@app.route('/user/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    # Fetch user from MongoDB
    user = users_collection.find_one({'id': user_id})
    if user:
        return jsonify({
            'username': user['username'],
            'id': user['id'],
            'balance': user['balance'],
            'password': user['password']
        }), 200

    return jsonify({'error': 'User not found'}), 404

@app.route('/users', methods=['GET'])
def get_users():
    # Fetch all users from MongoDB
    users = list(users_collection.find({}, {'_id': 0}))  # Omit the MongoDB internal _id field
    return jsonify(users), 200

@app.route('/deposit', methods=['POST'])
def handle_deposit():
    data = request.get_json()

    # Retrieve data from the request
    user_id = data.get('user_id')
    deposit = data.get('deposit')
    transaction_image = data.get('transaction_image')  # URL or path to the image

    # Validate the required fields
    if not user_id or not deposit or not transaction_image:
        return jsonify({'error': 'User ID, deposit amount, and transaction image are required'}), 400

    # Find the user in the database
    user = users_collection.find_one({'id': user_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Update user's deposit info
    users_collection.update_one(
        {'id': user_id},
        {
            '$set': {
                'deposit_status': 'pending',
                'transaction_image': transaction_image
            },
            '$inc': {
                'deposit': deposit  # Increment deposit amount
            }
        }
    )

    return jsonify({'message': 'Deposit recorded, pending approval'}), 200

@app.route('/withdraw', methods=['POST'])
def handle_withdraw():
    data = request.get_json()

    # Retrieve data from the request
    user_id = data.get('user_id')
    withdraw = data.get('withdraw')

    # Validate the required fields
    if not user_id or not withdraw:
        return jsonify({'error': 'User ID and withdraw amount are required'}), 400

    # Find the user in the database
    user = users_collection.find_one({'id': user_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Check if the user has enough balance
    if user['balance'] < withdraw:
        return jsonify({'error': 'Insufficient balance'}), 400

    # Update user's withdrawal info
    users_collection.update_one(
        {'id': user_id},
        {
            '$set': {'withdraw_status': 'pending'},
            '$inc': {'withdraw': withdraw}  # Increment withdraw amount
        }
    )

    return jsonify({'message': 'Withdrawal recorded, pending approval'}), 200

@app.route('/test_connection', methods=['GET'])
def test_connection():
    try:
        # Try to retrieve the server status
        client.admin.command('ping')
        return jsonify({'message': 'MongoDB connection successful'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
