#!/usr/bin/env python3
"""
Migracja schematu tabeli flashcards - dodanie brakujących kolumn
"""

import sqlite3
import os
from datetime import datetime

def migrate_flashcards():
    db_path = "HackerLabAcademy.db"
    backup_path = f"HackerLabAcademy.db.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if not os.path.exists(db_path):
        print(f"Baza danych nie istnieje: {db_path}")
        return False
    
    # Utwórz backup
    print(f"Tworzenie backupu: {backup_path}")
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print("✓ Backup utworzony pomyślnie")
    except Exception as e:
        print(f"✗ Błąd tworzenia backupu: {e}")
        return False
    
    # Połącz z bazą danych
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✓ Połączono z bazą danych")
    except Exception as e:
        print(f"✗ Błąd połączenia z bazą danych: {e}")
        return False
    
    # Sprawdź obecny schemat
    cursor.execute("PRAGMA table_info(flashcards)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Obecne kolumny: {columns}")
    
    # Definicja kolumn do dodania
    columns_to_add = [
        ("cve_id", "INTEGER", "NULL"),
        ("stability", "FLOAT", "NULL"),
        ("difficulty", "FLOAT", "NULL"), 
        ("state", "INTEGER", "DEFAULT 1"),
        ("step", "INTEGER", "NULL"),
        ("last_review", "DATETIME", "NULL"),
        ("card_id", "BIGINT", "NULL")
    ]
    
    # Dodaj brakujące kolumny
    for col_name, col_type, col_constraint in columns_to_add:
        if col_name not in columns:
            try:
                # Dodaj kolumnę z odpowiednimi constraintami
                if col_constraint.startswith("DEFAULT"):
                    constraint = f"DEFAULT {col_constraint.split(' ', 1)[1]}"
                elif col_constraint == "NULL":
                    constraint = ""
                else:
                    constraint = col_constraint
                
                alter_sql = f"ALTER TABLE flashcards ADD COLUMN {col_name} {constraint}"
                cursor.execute(alter_sql)
                print(f"✓ Dodano kolumnę: {col_name}")
            except Exception as e:
                print(f"✗ Błąd dodawania kolumny {col_name}: {e}")
                conn.rollback()
                return False
        else:
            print(f"- Kolumna {col_name} już istnieje")
    
    # Zatwierdź zmiany
    try:
        conn.commit()
        print("✓ Zmiany zapisane pomyślnie")
    except Exception as e:
        print(f"✗ Błąd zapisu zmian: {e}")
        conn.rollback()
        return False
    
    # Weryfikacja schematu po migracji
    cursor.execute("PRAGMA table_info(flashcards)")
    new_columns = cursor.fetchall()
    print(f"\nSchemat po migracji:")
    for col in new_columns:
        print(f"  {col[1]:<20} ({col[2]})")
    
    # Sprawdź czy dane nadal istnieją
    cursor.execute("SELECT COUNT(*) FROM flashcards")
    count = cursor.fetchone()[0]
    print(f"\nLiczba rekordów po migracji: {count}")
    
    conn.close()
    print("\n✓ Migracja zakończona pomyślnie!")
    return True

if __name__ == "__main__":
    migrate_flashcards()