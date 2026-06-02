from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
from flask_jwt_extended import jwt_required
from services.db import get_db

blog_bp = Blueprint('blog', __name__)

def to_json(doc):
  if isinstance(doc, list):
    return [to_json(d) for d in doc]
  if doc is None:
    return None
  if isinstance(doc, dict):
    doc = dict(doc)
    doc['_id'] = str(doc.get('_id', ''))
  return doc

@blog_bp.route('/', methods=['GET'])
@jwt_required()
def list_posts():
  db = get_db()
  domain = request.args.get('domain', '')
  query = {'domain_key': domain} if domain else {}
  posts = list(db.blog_posts.find(query).sort('created_at', -1))
  return jsonify(to_json(posts)), 200

@blog_bp.route('/', methods=['POST'])
@jwt_required()
def create_post():
  db = get_db()
  data = request.json or {}

  doc = {
    'domain_key': data.get('domain_key', ''),
    'title': data.get('title', 'Untitled'),
    'slug': data.get('slug', data.get('title', 'untitled').lower().replace(' ', '-')),
    'content': data.get('content', ''),
    'excerpt': data.get('excerpt', ''),
    'author': data.get('author', ''),
    'category': data.get('category', ''),
    'tags': data.get('tags', []),
    'image': data.get('image', ''),
    'published': data.get('published', False),
    'created_at': datetime.utcnow(),
    'updated_at': datetime.utcnow()
  }

  result = db.blog_posts.insert_one(doc)
  doc['_id'] = str(result.inserted_id)
  return jsonify(to_json(doc)), 201

@blog_bp.route('/<post_id>', methods=['GET'])
@jwt_required()
def get_post(post_id):
  db = get_db()
  try:
    post = db.blog_posts.find_one({'_id': ObjectId(post_id)})
    if not post:
      return jsonify({'error': 'Post not found'}), 404
    return jsonify(to_json(post)), 200
  except:
    return jsonify({'error': 'Invalid post ID'}), 400

@blog_bp.route('/<post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
  db = get_db()
  try:
    data = request.json or {}
    update = {}

    if 'title' in data:
      update['title'] = data['title']
    if 'slug' in data:
      update['slug'] = data['slug']
    if 'content' in data:
      update['content'] = data['content']
    if 'excerpt' in data:
      update['excerpt'] = data['excerpt']
    if 'author' in data:
      update['author'] = data['author']
    if 'category' in data:
      update['category'] = data['category']
    if 'tags' in data:
      update['tags'] = data['tags']
    if 'image' in data:
      update['image'] = data['image']
    if 'published' in data:
      update['published'] = data['published']

    update['updated_at'] = datetime.utcnow()

    result = db.blog_posts.update_one(
      {'_id': ObjectId(post_id)},
      {'$set': update}
    )

    if result.matched_count == 0:
      return jsonify({'error': 'Post not found'}), 404

    post = db.blog_posts.find_one({'_id': ObjectId(post_id)})
    return jsonify(to_json(post)), 200
  except:
    return jsonify({'error': 'Invalid post ID'}), 400

@blog_bp.route('/<post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
  db = get_db()
  try:
    result = db.blog_posts.delete_one({'_id': ObjectId(post_id)})
    if result.deleted_count == 0:
      return jsonify({'error': 'Post not found'}), 404
    return jsonify({'success': True}), 200
  except:
    return jsonify({'error': 'Invalid post ID'}), 400

@blog_bp.route('/<post_id>/toggle', methods=['PATCH'])
@jwt_required()
def toggle_post(post_id):
  db = get_db()
  try:
    post = db.blog_posts.find_one({'_id': ObjectId(post_id)})
    if not post:
      return jsonify({'error': 'Post not found'}), 404

    new_status = not post.get('published', False)
    db.blog_posts.update_one(
      {'_id': ObjectId(post_id)},
      {'$set': {'published': new_status, 'updated_at': datetime.utcnow()}}
    )

    post = db.blog_posts.find_one({'_id': ObjectId(post_id)})
    return jsonify(to_json(post)), 200
  except:
    return jsonify({'error': 'Invalid post ID'}), 400

@blog_bp.route('/public', methods=['GET'])
def get_public_posts():
  db = get_db()
  domain = request.args.get('domain', '')
  posts = list(db.blog_posts.find({
    'domain_key': domain,
    'published': True
  }).sort('created_at', -1))
  return jsonify(to_json(posts)), 200
