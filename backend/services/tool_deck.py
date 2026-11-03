"""Tool syntax deck (plan C6, ACTION_PLAN F6.5): the commands TryHackMe rooms use all the time.

Fronts are recall questions ("which flag ..."), backs the exact syntax. Added on demand per user,
idempotent (cards whose front the user already has are skipped).
"""

TOOL_DECK: list[tuple[str, str, str | None]] = [
    # (front, back, example)
    ("nmap: która flaga wykrywa wersje usług na portach?", "-sV", "nmap -sV 10.10.10.10"),
    ("nmap: jak przeskanować wszystkie 65535 portów TCP?", "-p-", "nmap -p- 10.10.10.10"),
    ("nmap: która flaga to skan SYN (półotwarty)?", "-sS (wymaga uprawnień roota)", "sudo nmap -sS 10.10.10.10"),
    ("nmap: jak uruchomić domyślne skrypty NSE?", "-sC", "nmap -sC -sV 10.10.10.10"),
    ("nmap: która flaga wykrywa system operacyjny?", "-O", "sudo nmap -O 10.10.10.10"),
    ("nmap: jak pominąć wykrywanie hosta (ping), gdy cel nie odpowiada na ICMP?", "-Pn", "nmap -Pn 10.10.10.10"),
    ("nmap: jak zapisać wynik we wszystkich formatach naraz?", "-oA <nazwa>", "nmap -sV -oA skan 10.10.10.10"),
    ("nmap: która flaga to skan UDP?", "-sU", "sudo nmap -sU --top-ports 100 10.10.10.10"),
    ("gobuster: jak szukać katalogów na stronie?", "gobuster dir -u <URL> -w <lista>",
     "gobuster dir -u http://10.10.10.10 -w /usr/share/wordlists/dirb/common.txt"),
    ("gobuster: jak dodać rozszerzenia plików do szukania?", "-x <rozszerzenia>", "gobuster dir -u http://cel -w lista.txt -x php,txt,html"),
    ("gobuster: jak szukać subdomen w DNS?", "gobuster dns -d <domena> -w <lista>", "gobuster dns -d example.com -w subdomains.txt"),
    ("hydra: jak łamać hasło jednego użytkownika SSH listą haseł?", "hydra -l <login> -P <lista> ssh://<IP>",
     "hydra -l admin -P rockyou.txt ssh://10.10.10.10"),
    ("hydra: która flaga podaje listę loginów zamiast jednego?", "-L <plik>", "hydra -L users.txt -P rockyou.txt ftp://10.10.10.10"),
    ("hydra: jaki moduł atakuje formularz logowania wysyłany POST-em?", "http-post-form \"<ścieżka>:<parametry z ^USER^ i ^PASS^>:F=<tekst błędu>\"",
     "hydra -l admin -P rockyou.txt 10.10.10.10 http-post-form \"/login:user=^USER^&pass=^PASS^:F=incorrect\""),
    ("msfconsole: jak znaleźć moduł?", "search <fraza>", "search eternalblue"),
    ("msfconsole: jak wybrać moduł?", "use <ścieżka modułu lub numer z search>", "use exploit/windows/smb/ms17_010_eternalblue"),
    ("msfconsole: jak ustawić adres celu?", "set RHOSTS <IP>", "set RHOSTS 10.10.10.10"),
    ("msfconsole: jak ustawić swój adres dla reverse shella?", "set LHOST <twój IP>", "set LHOST tun0"),
    ("msfconsole: jak zobaczyć wymagane opcje modułu?", "show options", None),
    ("msfconsole: jak uruchomić moduł?", "run (albo exploit)", None),
    ("Burp Suite: które narzędzie służy do ręcznego ponawiania i zmieniania żądań?", "Repeater", None),
    ("Burp Suite: które narzędzie automatycznie podstawia listę payloadów w żądanie?", "Intruder", None),
    ("Burp Suite: gdzie zdekodujesz Base64 albo kodowanie URL?", "Decoder", None),
    ("netcat: jak nasłuchiwać na porcie, czekając na reverse shell?", "nc -lvnp <port>", "nc -lvnp 4444"),
]
