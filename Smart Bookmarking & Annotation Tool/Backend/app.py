from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from bson.objectid import ObjectId
import bcrypt

# Flask Setup
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend
app.config['MONGO_URI'] = 'mongodb://localhost:27017/bookmark-tool'
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to a more secure key
mongo = PyMongo(app)
jwt = JWTManager(app)

# MongoDB Collections
users_collection = mongo.db.users
bookmarks_collection = mongo.db.bookmarks

# Register a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if users_collection.find_one({'username': username}):
        return jsonify({'message': 'Username already exists'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    users_collection.insert_one({
        'username': username,
        'password': hashed_password
    })

    return jsonify({'message': 'User created'}), 201

# User Login (authentication)
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = users_collection.find_one({'username': username})
    if not user:
        return jsonify({'message': 'Invalid username or password'}), 400

    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify({'token': access_token, 'userId': str(user['_id'])})

    return jsonify({'message': 'Invalid username or password'}), 400

# Add a new bookmark (user must be authenticated)
@app.route('/bookmarks', methods=['POST'])
@jwt_required()
def add_bookmark():
    current_user = get_jwt_identity()
    data = request.json
    url = data.get('url')
    title = data.get('title')
    tags = data.get('tags')
    notes = data.get('notes')

    bookmarks_collection.insert_one({
        'user': ObjectId(current_user),
        'url': url,
        'title': title,
        'tags': tags,
        'notes': notes
    })

    return jsonify({'message': 'Bookmark added successfully'}), 201

# Get all bookmarks for the authenticated user
@app.route('/bookmarks', methods=['GET'])
@jwt_required()
def get_bookmarks():
    current_user = get_jwt_identity()
    bookmarks = bookmarks_collection.find({'user': ObjectId(current_user)})
    
    bookmarks_list = []
    for bookmark in bookmarks:
        bookmark_data = {
            'id': str(bookmark['_id']),
            'url': bookmark['url'],
            'title': bookmark['title'],
            'tags': bookmark['tags'],
            'notes': bookmark['notes']
        }
        bookmarks_list.append(bookmark_data)

    return jsonify(bookmarks_list), 200

# Search bookmarks by tag (for authenticated users)
@app.route('/search', methods=['GET'])
@jwt_required()
def search_bookmarks():
    current_user = get_jwt_identity()
    query = request.args.get('query')
    
    bookmarks = bookmarks_collection.find({
        'user': ObjectId(current_user),
        'tags': {'$in': [query]}
    })

    bookmarks_list = []
    for bookmark in bookmarks:
        bookmark_data = {
            'id': str(bookmark['_id']),
            'url': bookmark['url'],
            'title': bookmark['title'],
            'tags': bookmark['tags'],
            'notes': bookmark['notes']
        }
        bookmarks_list.append(bookmark_data)

    return jsonify(bookmarks_list), 200

if __name__ == '__main__':
    app.run(debug=True)