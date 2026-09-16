#!/usr/bin/env python3
import sqlite3
import os

def check_flashcard_schema():
    db_path = 'HackerLabAcademy.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get current columns
    cursor.execute('PRAGMA table_info(flashcards)')
    columns = cursor.fetchall()
    
    print("Current flashcards table columns:")
    current_columns = []
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
        current_columns.append(col[1])
    
    # Expected columns from the model
    expected_columns = [
        'id', 'user_id', 'topic_slug', 'cve_id', 'front', 'back', 'example',
        'ease_factor', 'interval_days', 'repetitions', 'next_review_date',
        'stability', 'difficulty', 'state', 'step', 'last_review', 'card_id',
        'is_active', 'created_at'
    ]
    
    print("\nMissing columns:")
    missing_columns = []
    for col in expected_columns:
        if col not in current_columns:
            print(f"  - {col}")
            missing_columns.append(col)
    
    print(f"\nTotal missing columns: {len(missing_columns)}")
    
    # Check if there are any records
    cursor.execute('SELECT COUNT(*) FROM flashcards')
    count = cursor.fetchone()[0]
    print(f"Total flashcard records: {count}")
    
    # Check affected users
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM flashcards')
    user_count = cursor.fetchone()[0]
    print(f"Users with flashcards: {user_count}")
    
    conn.close()
    
    return missing_columns, count, user_count

if __name__ == "__main__":
    check_flashcard_schema()