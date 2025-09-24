"""
Interactive Book Chat Interface
==============================

This script provides an interactive interface for chatting with book characters
using all the advanced L4/L5 approaches from the notebooks.
"""

import os
import sys
from generic_book_kg_chat import GenericBookKGSystem

def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("📚 INTERACTIVE BOOK CHARACTER CHAT")
    print("Using Advanced L4/L5 Knowledge Graph Approaches")
    print("=" * 60)

def print_help():
    """Print help information"""
    print("\n🔧 Available Commands:")
    print("  /help          - Show this help")
    print("  /characters    - List available characters")
    print("  /book          - Show book information")
    print("  /character <name> - Get character details")
    print("  /basic         - Use basic retrieval (L4)")
    print("  /advanced      - Use advanced retrieval (L5)")
    print("  /langchain     - Use LangChain chains")
    print("  /quit          - Exit the chat")
    print("\n💬 Just type a message to chat with the current character!")

def main():
    """Main interactive chat loop"""
    print_banner()
    
    # Initialize the system
    print("🔧 Initializing Book Knowledge Graph System...")
    try:
        system = GenericBookKGSystem()
        print("✅ System initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        return
    
    # Check if we have any characters
    characters = system.list_available_characters()
    if not characters:
        print("\n📖 No characters found in the knowledge graph.")
        print("Please run the setup first:")
        print("python setup_book_kg.py")
        return
    
    # Get book info
    book_info = system.get_book_info()
    if book_info:
        print(f"\n📚 Book: {book_info.get('title', 'Unknown')}")
        print(f"👤 Author: {book_info.get('author', 'Unknown')}")
    
    print(f"\n👥 Found {len(characters)} characters available for chat!")
    print_help()
    
    # Chat state
    current_character = None
    retrieval_mode = "advanced"  # Default to advanced L5 approach
    
    print(f"\n🎯 Current retrieval mode: {retrieval_mode}")
    print("💡 Type a character name to start chatting, or use /help for commands")
    
    while True:
        try:
            # Get user input
            user_input = input(f"\n{'👤 ' + current_character + ': ' if current_character else '📚 You'}: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith('/'):
                command = user_input[1:].lower()
                
                if command == 'help':
                    print_help()
                    continue
                elif command == 'quit':
                    print("👋 Goodbye! Thanks for chatting!")
                    break
                elif command == 'characters':
                    print(f"\n👥 Available characters ({len(characters)}):")
                    for i, char in enumerate(characters, 1):
                        print(f"  {i}. {char}")
                    continue
                elif command == 'book':
                    if book_info:
                        print(f"\n📚 Book Information:")
                        print(f"  Title: {book_info.get('title', 'Unknown')}")
                        print(f"  Author: {book_info.get('author', 'Unknown')}")
                    else:
                        print("📚 No book information available")
                    continue
                elif command == 'basic':
                    retrieval_mode = "basic"
                    print("🔧 Switched to basic retrieval mode (L4 approach)")
                    continue
                elif command == 'advanced':
                    retrieval_mode = "advanced"
                    print("🔧 Switched to advanced retrieval mode (L5 approach)")
                    continue
                elif command == 'langchain':
                    retrieval_mode = "langchain"
                    print("🔧 Switched to LangChain mode (L4/L5 integration)")
                    continue
                elif command.startswith('character '):
                    char_name = command[10:].strip()
                    if char_name in characters:
                        current_character = char_name
                        char_info = system.get_character_info(char_name)
                        print(f"\n👤 Now chatting with: {char_name}")
                        if char_info:
                            print(f"  Personality: {char_info.get('personality', 'Unknown')}")
                            print(f"  Speech Pattern: {char_info.get('speechPattern', 'Unknown')}")
                    else:
                        print(f"❌ Character '{char_name}' not found. Use /characters to see available characters.")
                    continue
                else:
                    print(f"❌ Unknown command: {command}. Use /help for available commands.")
                    continue
            
            # Handle character selection
            if not current_character:
                # Check if user typed a character name
                if user_input in characters:
                    current_character = user_input
                    char_info = system.get_character_info(current_character)
                    print(f"\n👤 Now chatting with: {current_character}")
                    if char_info:
                        print(f"  Personality: {char_info.get('personality', 'Unknown')}")
                        print(f"  Speech Pattern: {char_info.get('speechPattern', 'Unknown')}")
                    print("💬 You can now chat with this character!")
                    continue
                else:
                    print("❌ Please select a character first. Available characters:")
                    for char in characters[:5]:  # Show first 5
                        print(f"  - {char}")
                    if len(characters) > 5:
                        print(f"  ... and {len(characters) - 5} more. Use /characters to see all.")
                    continue
            
            # Chat with character
            print(f"\n🤔 Thinking... (using {retrieval_mode} retrieval)")
            
            try:
                if retrieval_mode == "basic":
                    response = system.chat_with_character(current_character, user_input, use_advanced_retrieval=False)
                elif retrieval_mode == "advanced":
                    response = system.chat_with_character(current_character, user_input, use_advanced_retrieval=True)
                elif retrieval_mode == "langchain":
                    response = system.chat_with_character_using_langchain(current_character, user_input)
                else:
                    response = system.chat_with_character(current_character, user_input)
                
                print(f"\n💬 {current_character}: {response}")
                
            except Exception as e:
                print(f"❌ Error generating response: {e}")
                print("💡 Try switching retrieval modes with /basic, /advanced, or /langchain")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for chatting!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("💡 Try restarting the chat or check your setup")

if __name__ == "__main__":
    main()
