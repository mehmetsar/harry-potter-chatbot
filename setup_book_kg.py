"""
Setup Script for Generic Book Knowledge Graph
============================================

This script sets up a book knowledge graph using all L4/L5 approaches:
- L4: Text chunking, vector embeddings, basic RAG
- L5: Advanced relationships, windowed retrieval, LangChain integration
"""

import os
import sys
from generic_book_kg_chat import GenericBookKGSystem

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'cohere',
        'langchain',
        'langchain-community',
        'langchain-openai',
        'neo4j',
        'PyPDF2',
        'PyMuPDF',
        'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print(f"\nInstall with: pip install {' '.join(missing_packages)}")
        return False
    else:
        print("✅ All required packages are installed")
        return True

def create_env_file():
    """Create .env file with credentials"""
    env_content = """# Neo4j Credentials (from your existing setup)
NEO4J_URI=neo4j+s://ef78fe3e.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=NXgD8hLRCpo9Qx2_hywyvi1hFGy5e0ozmi3f5eg80tk
NEO4J_DATABASE=neo4j

# Cohere API Key (you already have this)
COHERE_API_KEY=8hBcb6YBzGqsM9gKkrkieSbhqbeBQ0UHchNpgLr4

# OpenAI API Key (for embeddings) - ADD YOUR KEY HERE
OPENAI_API_KEY=your_openai_api_key_here
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with your credentials")
    print("⚠️  Please add your OpenAI API key to the .env file")

def setup_book():
    """Setup a book in the knowledge graph"""
    print("\n📚 Book Setup")
    print("=" * 40)
    
    # Get book details
    pdf_path = input("📄 Enter path to PDF file: ").strip()
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    book_title = input("📖 Enter book title: ").strip()
    if not book_title:
        book_title = "Unknown Book"
    
    book_author = input("👤 Enter book author: ").strip()
    if not book_author:
        book_author = "Unknown Author"
    
    print(f"\n🔧 Setting up: {book_title} by {book_author}")
    print("This will use all L4/L5 approaches:")
    print("  - L4: Text chunking, vector embeddings, basic RAG")
    print("  - L5: Advanced relationships, windowed retrieval, LangChain integration")
    
    # Initialize system
    try:
        system = GenericBookKGSystem()
        print("✅ System initialized")
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        return False
    
    # Setup the knowledge graph
    try:
        success = system.setup_book_kg(pdf_path, book_title, book_author)
        if success:
            print(f"\n🎉 Successfully set up knowledge graph for: {book_title}")
            
            # Show statistics
            characters = system.list_available_characters()
            print(f"👥 Found {len(characters)} characters")
            
            if characters:
                print("📋 Characters discovered:")
                for char in characters[:10]:  # Show first 10
                    print(f"  - {char}")
                if len(characters) > 10:
                    print(f"  ... and {len(characters) - 10} more")
            
            print(f"\n🚀 Ready to chat! Run: python interactive_book_chat.py")
            return True
        else:
            print("❌ Failed to setup knowledge graph")
            return False
            
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return False

def test_system():
    """Test the system with a simple query"""
    print("\n🧪 Testing System...")
    
    try:
        system = GenericBookKGSystem()
        characters = system.list_available_characters()
        
        if not characters:
            print("❌ No characters found. Please setup a book first.")
            return False
        
        print(f"✅ System working! Found {len(characters)} characters")
        
        # Test with first character
        test_character = characters[0]
        print(f"🧪 Testing with character: {test_character}")
        
        # Test basic chat
        response = system.chat_with_character(test_character, "Hello, how are you?")
        print(f"💬 {test_character}: {response[:100]}...")
        
        print("✅ System test successful!")
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🏗️  Generic Book Knowledge Graph Setup")
    print("Using L4/L5 Advanced Approaches")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Create environment file
    create_env_file()
    
    # Setup book
    if setup_book():
        # Test the system
        test_system()
        
        print("\n🎉 Setup Complete!")
        print("\nNext steps:")
        print("1. Add your OpenAI API key to the .env file")
        print("2. Run: python interactive_book_chat.py")
        print("3. Start chatting with book characters!")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
