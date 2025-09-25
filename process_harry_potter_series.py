"""
Process Complete Harry Potter Series (All 7 Books)
================================================

This script processes all 7 Harry Potter books and creates a unified knowledge graph
with character deduplication across the entire series.
"""

import os
import sys
import time
from typing import List, Dict, Any
from generic_book_kg_chat import GenericBookKGSystem

# Harry Potter series information
HARRY_POTTER_SERIES = [
    {
        "title": "Harry Potter and the Philosopher's Stone",
        "author": "J.K. Rowling",
        "year": "1997",
        "book_number": 1,
        "filename": "J. K. Rowling - Harry Potter - 1 - Harry Potter and the Philosopher's Stone.pdf"
    },
    {
        "title": "Harry Potter and the Chamber of Secrets",
        "author": "J.K. Rowling", 
        "year": "1998",
        "book_number": 2,
        "filename": "J. K. Rowling - Harry Potter - 2 - Harry Potter and the Chamber of Secrets.pdf"
    },
    {
        "title": "Harry Potter and the Prisoner of Azkaban",
        "author": "J.K. Rowling",
        "year": "1999", 
        "book_number": 3,
        "filename": "J. K. Rowling - Harry Potter - 3 - Harry Potter and the Prisoner of Azkaban.pdf"
    },
    {
        "title": "Harry Potter and the Goblet of Fire",
        "author": "J.K. Rowling",
        "year": "2000",
        "book_number": 4,
        "filename": "J. K. Rowling - Harry Potter - 4 - Harry Potter and the Goblet of Fire.pdf"
    },
    {
        "title": "Harry Potter and the Order of the Phoenix",
        "author": "J.K. Rowling",
        "year": "2003",
        "book_number": 5,
        "filename": "J. K. Rowling - Harry Potter - 5 - Harry Potter and the Order of the Phoenix.pdf"
    },
    {
        "title": "Harry Potter and the Half-Blood Prince",
        "author": "J.K. Rowling",
        "year": "2005",
        "book_number": 6,
        "filename": "J. K. Rowling - Harry Potter - 6 - Harry Potter and the Half-Blood Prince.pdf"
    },
    {
        "title": "Harry Potter and the Deathly Hallows",
        "author": "J.K. Rowling",
        "year": "2007",
        "book_number": 7,
        "filename": "J. K. Rowling - Harry Potter - 7 - Harry Potter and the Deathly Hallows.pdf"
    }
]

def check_pdf_files() -> List[Dict[str, Any]]:
    """Check which PDF files are available"""
    available_books = []
    missing_books = []
    
    print("🔍 Checking for Harry Potter PDF files...")
    print("=" * 50)
    
    for book in HARRY_POTTER_SERIES:
        if os.path.exists(book["filename"]):
            available_books.append(book)
            print(f"✅ Found: {book['title']}")
        else:
            missing_books.append(book)
            print(f"❌ Missing: {book['title']}")
    
    print(f"\n📊 Summary:")
    print(f"  Available: {len(available_books)} books")
    print(f"  Missing: {len(missing_books)} books")
    
    if missing_books:
        print(f"\n⚠️  Missing books:")
        for book in missing_books:
            print(f"  - {book['filename']}")
        print(f"\n💡 Please add the missing PDF files to continue with the complete series.")
        print(f"   You can still process the available books.")
    
    return available_books

def process_single_book(system: GenericBookKGSystem, book_info: Dict[str, Any], book_index: int, total_books: int) -> bool:
    """Process a single book and add it to the knowledge graph"""
    print(f"\n📚 Processing Book {book_index}/{total_books}: {book_info['title']}")
    print("=" * 60)
    
    try:
        # Process the book
        success = system.setup_book_kg(
            pdf_path=book_info["filename"],
            book_title=book_info["title"],
            book_author=book_info["author"]
        )
        
        if success:
            print(f"✅ Successfully processed: {book_info['title']}")
            
            # Get book-specific statistics
            characters = system.list_available_characters()
            print(f"👥 Characters found so far: {len(characters)}")
            
            return True
        else:
            print(f"❌ Failed to process: {book_info['title']}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {book_info['title']}: {e}")
        return False

def perform_series_deduplication(system: GenericBookKGSystem):
    """Perform character deduplication across the entire series"""
    print(f"\n🔄 Performing series-wide character deduplication...")
    print("=" * 60)
    
    try:
        # Get all characters from the series
        all_characters = system.list_available_characters()
        print(f"📊 Total characters before deduplication: {len(all_characters)}")
        
        if len(all_characters) > 1:
            # Find duplicates across the series
            duplicate_groups = system.find_duplicate_characters(all_characters)
            
            if duplicate_groups:
                print(f"🔍 Found {len(duplicate_groups)} groups of duplicate characters")
                for canonical, variations in duplicate_groups.items():
                    print(f"  📝 {canonical}: {variations}")
                
                # Merge duplicates
                system.merge_duplicate_characters(duplicate_groups)
                print("✅ Character deduplication completed")
            else:
                print("ℹ️  No duplicate characters found")
        
        # Get final statistics
        final_characters = system.list_available_characters()
        print(f"📊 Final character count: {len(final_characters)}")
        
        # Get merge statistics
        stats = system.get_character_merge_statistics()
        if stats:
            print(f"\n📈 Series Statistics:")
            print(f"  Total characters: {stats.get('total_characters', 0)}")
            print(f"  Mentioned characters: {stats.get('mentioned_characters', 0)}")
            print(f"  Analyzed characters: {stats.get('analyzed_characters', 0)}")
            print(f"  Deduplication applied: {stats.get('deduplication_applied', False)}")
        
    except Exception as e:
        print(f"❌ Error during series deduplication: {e}")

def main():
    """Process the complete Harry Potter series"""
    print("🏰 Harry Potter Series Knowledge Graph Builder")
    print("=" * 60)
    print("This will process all 7 Harry Potter books and create a unified knowledge graph")
    print("with character deduplication across the entire series.")
    print()
    
    # Check for available PDF files
    available_books = check_pdf_files()
    
    if not available_books:
        print("❌ No Harry Potter PDF files found!")
        print("Please add the PDF files to the current directory.")
        return False
    
    # Initialize the system
    print(f"\n🔧 Initializing Knowledge Graph System...")
    try:
        system = GenericBookKGSystem()
        print("✅ System initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        print("Please check your .env file and API keys")
        return False
    
    # Process each book
    successful_books = 0
    failed_books = []
    
    print(f"\n📚 Processing {len(available_books)} books...")
    print("This will use all L4/L5 approaches with series-wide character deduplication")
    
    start_time = time.time()
    
    for i, book in enumerate(available_books, 1):
        success = process_single_book(system, book, i, len(available_books))
        if success:
            successful_books += 1
        else:
            failed_books.append(book["title"])
        
        # Add a small delay between books to avoid overwhelming the system
        if i < len(available_books):
            print("⏳ Waiting 2 seconds before processing next book...")
            time.sleep(2)
    
    processing_time = time.time() - start_time
    
    # Perform series-wide deduplication
    if successful_books > 0:
        perform_series_deduplication(system)
    
    # Final summary
    print(f"\n🎉 Harry Potter Series Processing Complete!")
    print("=" * 60)
    print(f"📊 Processing Summary:")
    print(f"  Total books processed: {successful_books}/{len(available_books)}")
    print(f"  Processing time: {processing_time:.1f} seconds")
    
    if failed_books:
        print(f"  Failed books: {', '.join(failed_books)}")
    
    if successful_books > 0:
        # Show final statistics
        characters = system.list_available_characters()
        print(f"\n👥 Final Character Count: {len(characters)}")
        
        if characters:
            print(f"\n📋 Main Characters:")
            main_characters = ["Harry Potter", "Hermione Granger", "Ron Weasley", "Dumbledore", "Snape", "Voldemort"]
            for char in main_characters:
                if char in characters:
                    print(f"  ✅ {char}")
                else:
                    print(f"  ❌ {char}")
        
        # Show book info
        book_info = system.get_book_info()
        if book_info:
            print(f"\n📚 Series Information:")
            print(f"  Title: {book_info.get('title', 'Unknown')}")
            print(f"  Author: {book_info.get('author', 'Unknown')}")
        
        print(f"\n🚀 Ready to chat with the complete Harry Potter series!")
        print(f"Run: python interactive_book_chat.py")
        return True
    else:
        print("❌ No books were successfully processed")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Harry Potter Series Knowledge Graph is ready!")
        print("\nNext steps:")
        print("1. Make sure your API keys are set in the .env file")
        print("2. Run: python interactive_book_chat.py")
        print("3. Start chatting with characters from the entire series!")
        print("4. Characters will have knowledge from all 7 books!")
    else:
        print("\n❌ Processing failed. Please check the error messages above.")
