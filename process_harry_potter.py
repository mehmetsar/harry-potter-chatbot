"""
Process Harry Potter and the Philosopher's Stone
==============================================

This script processes the Harry Potter PDF using our advanced knowledge graph system.
"""

import os
import sys
from generic_book_kg_chat import GenericBookKGSystem

def main():
    """Process the Harry Potter book"""
    print("🏰 Processing Harry Potter and the Philosopher's Stone")
    print("=" * 60)
    
    # Check if PDF exists
    pdf_path = "J. K. Rowling - Harry Potter - 1 - Harry Potter and the Philosopher's Stone.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        print("Please make sure the PDF file is in the current directory")
        return False
    
    print(f"✅ Found PDF: {pdf_path}")
    
    # Initialize the system
    print("\n🔧 Initializing Knowledge Graph System...")
    try:
        system = GenericBookKGSystem()
        print("✅ System initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        print("Please check your .env file and API keys")
        return False
    
    # Process the book
    print(f"\n📚 Processing: Harry Potter and the Philosopher's Stone")
    print("This will use all L4/L5 approaches:")
    print("  - L4: Text chunking, vector embeddings, basic RAG")
    print("  - L5: Advanced relationships, windowed retrieval, LangChain integration")
    print("  - Character analysis with LLM-powered style extraction")
    
    try:
        success = system.setup_book_kg(
            pdf_path=pdf_path,
            book_title="Harry Potter and the Philosopher's Stone",
            book_author="J.K. Rowling"
        )
        
        if success:
            print(f"\n🎉 Successfully processed Harry Potter!")
            
            # Show statistics
            characters = system.list_available_characters()
            print(f"👥 Found {len(characters)} characters")
            
            if characters:
                print("📋 Characters discovered:")
                for i, char in enumerate(characters[:15], 1):  # Show first 15
                    print(f"  {i:2d}. {char}")
                if len(characters) > 15:
                    print(f"  ... and {len(characters) - 15} more characters")
            
            # Show book info
            book_info = system.get_book_info()
            if book_info:
                print(f"\n📚 Book Information:")
                print(f"  Title: {book_info.get('title', 'Unknown')}")
                print(f"  Author: {book_info.get('author', 'Unknown')}")
            
            print(f"\n🚀 Ready to chat! Run: python interactive_book_chat.py")
            return True
        else:
            print("❌ Failed to process the book")
            return False
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Harry Potter Knowledge Graph is ready!")
        print("\nNext steps:")
        print("1. Add your OpenAI API key to the .env file if you haven't already")
        print("2. Run: python interactive_book_chat.py")
        print("3. Start chatting with Harry, Hermione, Ron, and other characters!")
    else:
        print("\n❌ Processing failed. Please check the error messages above.")
