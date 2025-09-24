"""
Harry Potter Knowledge Graph Chatbot Web App
============================================

A Flask web application for chatting with Harry Potter characters
using the advanced knowledge graph system.
"""

from flask import Flask, render_template, request, jsonify, session
import os
import json
from generic_book_kg_chat import GenericBookKGSystem

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Initialize the system
try:
    kg_system = GenericBookKGSystem()
    characters = kg_system.list_available_characters()
    book_info = kg_system.get_book_info()
    print(f"✅ System initialized with {len(characters)} characters")
except Exception as e:
    print(f"❌ Error initializing system: {e}")
    kg_system = None
    characters = []
    book_info = {}

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', 
                         characters=characters[:20],  # Show first 20
                         book_info=book_info,
                         total_characters=len(characters))

@app.route('/api/characters')
def get_characters():
    """Get all available characters"""
    return jsonify({
        'characters': characters,
        'total': len(characters)
    })

@app.route('/api/character/<character_name>')
def get_character_info(character_name):
    """Get character information"""
    if not kg_system:
        return jsonify({'error': 'System not initialized'}), 500
    
    try:
        char_info = kg_system.get_character_info(character_name)
        return jsonify(char_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    if not kg_system:
        return jsonify({'error': 'System not initialized'}), 500
    
    data = request.get_json()
    character = data.get('character')
    message = data.get('message')
    retrieval_mode = data.get('mode', 'advanced')
    
    if not character or not message:
        return jsonify({'error': 'Character and message required'}), 400
    
    try:
        if retrieval_mode == 'basic':
            response = kg_system.chat_with_character(character, message, use_advanced_retrieval=False)
        elif retrieval_mode == 'langchain':
            response = kg_system.chat_with_character_using_langchain(character, message)
        else:  # advanced
            response = kg_system.chat_with_character(character, message, use_advanced_retrieval=True)
        
        return jsonify({
            'response': response,
            'character': character,
            'mode': retrieval_mode
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/book')
def get_book_info():
    """Get book information"""
    return jsonify(book_info)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
