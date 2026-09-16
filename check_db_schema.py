#!/usr/bin/env python3
import sqlite3
import os

# Ścieżka do bazy danych
db_path = "HackerLabAcademy.db"

if not os.path.exists(db_path):
    print(f"Baza danych nie istnieje: {db_path}")
    exit(1)

print(f"Sprawdzanie schematu bazy danych: {db_path}")
print("=" * 50)

# Połącz z bazą danych
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Sprawdź kolumny w tabeli flashcards
cursor.execute("PRAGMA table_info(flashcards)")
columns = cursor.fetchall()

print("Kolumny w tabeli flashcards:")
for col in columns:
    print(f"  {col[1]:<20} ({col[2]})")

print("\nPorównanie z obecnym modelem:")
print("Oczekiwane kolumny:")
expected_columns = [
    "id", "user_id", "topic_slug", "cve_id",
    "front", "back", "example",
    "ease_factor", "interval_days", "repetitions", "next_review_date",
    "stability", "difficulty", "state", "step", "last_review", "card_id",
    "is_active", "created_at"
]

missing_columns = []
for col in expected_columns:
    found = False
    for existing_col in columns:
        if existing_col[1] == col:
            found = True
            break
    if not found:
        missing_columns.append(col)

if missing_columns:
    print(f"\nBRAKUJĄCE KOLUMNY: {missing_columns}")
else:
    print("\nWszystkie kolumny obecne!")

# Sprawdź liczbę rekordów
cursor.execute("SELECT COUNT(*) FROM flashcards")
count = cursor.fetchone()[0]
print(f"\nLiczba rekordów w tabeli flashcards: {count}")

# Sprawdź liczbę użytkowników
cursor.execute("SELECT COUNT(DISTINCT user_id) FROM flashcards")
user_count = cursor.fetchone()[0]
print(f"Liczba użytkowników z flashcardami: {user_count}")

conn.close()
print("=" * 50)