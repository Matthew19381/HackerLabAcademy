"""CTF challenges solvable from their own description, in the browser or a terminal (2026-11-03).

Every flag below was generated from the data in the description and checked:
base64 / ROT13 / base64url (JWT) / MD5 of a common password / URL encoding / hex / a log line.
"""

CHALLENGES: list[dict] = [
    {
        "title": "Ciasteczko w Base64",
        "category": "web", "difficulty": 1, "points": 50,
        "description": (
            "Po zalogowaniu aplikacja ustawia ciasteczko:\n\n"
            "`Set-Cookie: debug=RkxBR3tDSUFTVEVDWktPX09ES09ET1dBTkV9; Path=/`\n\n"
            "Co naprawdę jest w środku? Podaj flagę."
        ),
        "flag": "FLAG{CIASTECZKO_ODKODOWANE}",
        "hint": "Znak `=` na końcu bywa, tu go nie ma — ale alfabet wskazuje na Base64. `echo ... | base64 -d`",
        "solution": "Base64 to kodowanie, nie szyfrowanie: każdy może je odwrócić. Nie trzymaj w ciasteczkach danych, które mają być tajne.",
    },
    {
        "title": "Komentarz w HTML",
        "category": "web", "difficulty": 1, "points": 50,
        "description": (
            "W źródle strony logowania (Ctrl+U) jest zapomniany komentarz:\n\n"
            "`<!-- TODO usunac przed wdrozeniem: SYNT{XBZRAGNEMR_FN_CHOYVPMAR} -->`\n\n"
            "Podaj flagę."
        ),
        "flag": "FLAG{KOMENTARZE_SA_PUBLICZNE}",
        "hint": "Każda litera przesunięta o 13 pozycji w alfabecie (ROT13). `tr 'A-Za-z' 'N-ZA-Mn-za-m'`",
        "solution": "Komentarze HTML trafiają do przeglądarki każdego użytkownika — przegląd źródła strony to pierwszy krok rekonesansu.",
    },
    {
        "title": "Token bez podpisu",
        "category": "web", "difficulty": 2, "points": 100,
        "description": (
            "API zwraca token sesji:\n\n"
            "`eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyIjoiamFuIiwicm9sZSI6InVzZXIiLCJmbGFnIjoiRkxBR3tKV1RfVE9fTklFX1NaWUZSfSJ9.`\n\n"
            "Co zawiera i czemu `alg: none` to problem? Podaj flagę z treści tokena."
        ),
        "flag": "FLAG{JWT_TO_NIE_SZYFR}",
        "hint": "JWT to trzy części base64url oddzielone kropkami: nagłówek, dane, podpis. Odkoduj środkową.",
        "solution": "Dane w JWT są jawne. Przy `alg: none` serwer, który akceptuje taki token, pozwala każdemu zmienić np. `role` na `admin`.",
    },
    {
        "title": "Wyciek hasha",
        "category": "crypto", "difficulty": 2, "points": 100,
        "description": (
            "Z bazy wyciekł wiersz:\n\n"
            "`admin:5f4dcc3b5aa765d61d8327deb882cf99`\n\n"
            "Jaki to algorytm i jakie hasło? Flaga to `FLAG{hasło}`."
        ),
        "flag": "FLAG{password}",
        "hint": "32 znaki hex to typowo MD5. Popularne hasła mają gotowe hashe w słownikach (rockyou.txt, crackstation).",
        "solution": "MD5 bez soli dla popularnego hasła łamie się w sekundę słownikiem. Do haseł: bcrypt/argon2 z solą.",
    },
    {
        "title": "Zakodowany parametr",
        "category": "web", "difficulty": 1, "points": 50,
        "description": (
            "W logach proxy widzisz żądanie:\n\n"
            "`GET /search?q=%46%4C%41%47%7B%55%52%4C%5F%45%4E%43%4F%44%49%4E%47%7D`\n\n"
            "Podaj flagę."
        ),
        "flag": "FLAG{URL_ENCODING}",
        "hint": "`%41` to bajt 0x41 w ASCII. Burp Decoder albo `python3 -c \"import urllib.parse; print(urllib.parse.unquote('...'))\"`.",
        "solution": "Kodowanie URL ukrywa payloady przed prostymi filtrami — WAF i walidacja muszą działać na zdekodowanej wartości.",
    },
    {
        "title": "Zrzut pamięci",
        "category": "forensics", "difficulty": 2, "points": 100,
        "description": (
            "Fragment zrzutu w hex:\n\n"
            "`464c41477b4845585f544f5f54454b53547d`\n\n"
            "Podaj flagę."
        ),
        "flag": "FLAG{HEX_TO_TEKST}",
        "hint": "Każde dwie cyfry hex to jeden bajt. `echo ... | xxd -r -p`",
        "solution": "Hex to tylko zapis bajtów — narzędzia jak xxd i CyberChef odczytują go natychmiast.",
    },
    {
        "title": "Kto próbował SQL Injection?",
        "category": "forensics", "difficulty": 2, "points": 100,
        "description": (
            "Fragment access.log:\n\n"
            "```\n"
            "10.0.0.12 - - [02/Nov/2026:10:01:13] \"GET /products?id=4 HTTP/1.1\" 200\n"
            "10.0.0.47 - - [02/Nov/2026:10:01:20] \"GET /products?id=4%27%20OR%201%3D1--%20 HTTP/1.1\" 500\n"
            "10.0.0.12 - - [02/Nov/2026:10:01:31] \"GET /cart HTTP/1.1\" 200\n"
            "10.0.0.88 - - [02/Nov/2026:10:02:02] \"GET /products?id=5 HTTP/1.1\" 200\n"
            "```\n\n"
            "Flaga to `FLAG{adres IP atakującego}`."
        ),
        "flag": "FLAG{10.0.0.47}",
        "hint": "Odkoduj parametry z `%27`, `%20`, `%3D`. Który wygląda jak `' OR 1=1-- `? Kod 500 też coś mówi.",
        "solution": "`' OR 1=1-- ` to klasyczny test SQLi; błąd 500 po apostrofie sugeruje, że zapytanie jest sklejane z wejścia.",
    },
]
