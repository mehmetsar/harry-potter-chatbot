"""
Check Harry Potter PDF Files
===========================

This script checks which Harry Potter PDF files you have and helps organize them.
"""

import os
import glob
from typing import List, Dict

# Expected Harry Potter filenames
EXPECTED_FILES = [
    "J. K. Rowling - Harry Potter - 1 - Harry Potter and the Philosopher's Stone.pdf",
    "J. K. Rowling - Harry Potter - 2 - Harry Potter and the Chamber of Secrets.pdf", 
    "J. K. Rowling - Harry Potter - 3 - Harry Potter and the Prisoner of Azkaban.pdf",
    "J. K. Rowling - Harry Potter - 4 - Harry Potter and the Goblet of Fire.pdf",
    "J. K. Rowling - Harry Potter - 5 - Harry Potter and the Order of the Phoenix.pdf",
    "J. K. Rowling - Harry Potter - 6 - Harry Potter and the Half-Blood Prince.pdf",
    "J. K. Rowling - Harry Potter - 7 - Harry Potter and the Deathly Hallows.pdf"
]

def find_harry_potter_files() -> List[str]:
    """Find all Harry Potter PDF files in the current directory"""
    # Look for files with "Harry Potter" in the name
    pattern = "*Harry Potter*.pdf"
    found_files = glob.glob(pattern)
    return found_files

def check_expected_files() -> Dict[str, bool]:
    """Check which expected files are present"""
    status = {}
    for filename in EXPECTED_FILES:
        status[filename] = os.path.exists(filename)
    return status

def suggest_renaming(found_files: List[str]) -> List[Dict[str, str]]:
    """Suggest renaming for found files to match expected format"""
    suggestions = []
    
    # Common patterns and their suggested names
    patterns = {
        "philosopher": "1 - Harry Potter and the Philosopher's Stone.pdf",
        "chamber": "2 - Harry Potter and the Chamber of Secrets.pdf",
        "prisoner": "3 - Harry Potter and the Prisoner of Azkaban.pdf", 
        "goblet": "4 - Harry Potter and the Goblet of Fire.pdf",
        "order": "5 - Harry Potter and the Order of the Phoenix.pdf",
        "half-blood": "6 - Harry Potter and the Half-Blood Prince.pdf",
        "deathly": "7 - Harry Potter and the Deathly Hallows.pdf"
    }
    
    for file in found_files:
        file_lower = file.lower()
        for pattern, suggested in patterns.items():
            if pattern in file_lower:
                suggestions.append({
                    "current": file,
                    "suggested": f"J. K. Rowling - Harry Potter - {suggested}"
                })
                break
    
    return suggestions

def main():
    """Check Harry Potter files and provide recommendations"""
    print("🔍 Harry Potter PDF File Checker")
    print("=" * 50)
    
    # Find all Harry Potter files
    found_files = find_harry_potter_files()
    print(f"📁 Found {len(found_files)} Harry Potter PDF files:")
    for i, file in enumerate(found_files, 1):
        print(f"  {i}. {file}")
    
    print(f"\n📋 Checking expected files...")
    expected_status = check_expected_files()
    
    available_count = 0
    missing_files = []
    
    for filename, exists in expected_status.items():
        if exists:
            print(f"  ✅ {filename}")
            available_count += 1
        else:
            print(f"  ❌ {filename}")
            missing_files.append(filename)
    
    print(f"\n📊 Summary:")
    print(f"  Available: {available_count}/7 books")
    print(f"  Missing: {len(missing_files)} books")
    
    if found_files and missing_files:
        print(f"\n💡 Renaming Suggestions:")
        suggestions = suggest_renaming(found_files)
        for suggestion in suggestions:
            print(f"  📝 Rename: '{suggestion['current']}'")
            print(f"      To: '{suggestion['suggested']}'")
            print()
    
    if available_count == 7:
        print(f"\n🎉 Perfect! All 7 Harry Potter books are ready!")
        print(f"Run: python process_harry_potter_series.py")
    elif available_count > 0:
        print(f"\n✅ You can process the available books!")
        print(f"Run: python process_harry_potter_series.py")
        print(f"The script will process {available_count} available books.")
    else:
        print(f"\n❌ No Harry Potter PDF files found!")
        print(f"Please add the PDF files to the current directory.")
        print(f"Expected filenames:")
        for filename in EXPECTED_FILES:
            print(f"  - {filename}")

if __name__ == "__main__":
    main()
