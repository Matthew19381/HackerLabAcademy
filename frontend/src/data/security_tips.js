export const SECURITY_TIPS = [
  "Zawsze używaj silnych haseł i menedżera haseł.",
  "Włącz uwierzytelnianie dwuskładnikowe (2FA) wszędzie gdzie to możliwe.",
  "Regularnie aktualizuj oprogramowanie i systemy operacyjne.",
  "Nie klikaj w podejrzane linki w e-mailach, nawet jeśli wyglądają na legalne.",
  "Używaj VPN w publicznych sieciach Wi-Fi.",
  "Regularnie rób kopie zapasowe ważnych danych.",
  "Nie udostępniaj haseł nikomu, nawet jeśli twierdzi, że jest z supportu technicznego.",
  "Zawsze sprawdzaj adres URL przed wprowadzeniem danych logowania.",
  "Używaj unikalnych haseł do każdego konta.",
  "Zainstaluj antywirus i utrzymuj jego bazy wirusów aktualne.",
  "Nie instaluj nieznanego oprogramowania z nieoficjalnych źródeł.",
  "Używaj szyfrowania dysku (BitLocker, FileVault) na laptopach.",
  "Regularnie przeglądaj logi aktywności kont (loginy, urządzenia).",
  "Wyłącz automatyczne łączenie się z publicznymi sieciami Wi-Fi.",
  "Używaj HTTPS w każdej stronie, gdzie wprowadzasz dane.",
  "Nie loguj się na ważne konta z komputera publicznego.",
  "Szkol pracowników w zakresie phishingowych ataków.",
  "Stosuj zasadę najmniejszych uprawnień w systemach.",
  "Zaimplementuj politykę harmonogramu rotate kluczy i haseł.",
  "Regularnie przeprowadzaj audyty bezpieczeństwa i testy penetracyjne.",
  "Szyfruj komunikację wewnętrzna (TLS, SSH).",
  "Nie przechowuj haseł w tekście jawnym w kodzie źródłowym.",
  "Używaj prepared statements i ORM do zapobiegania SQL injection.",
  "Waliduj i sanitizuj wszystkie dane wejściowe od użytkowników.",
  "Zapętl należyte zabezpieczanie sesji (secure cookies, HttpOnly, SameSite).",
  "Ogranicz liczbę prób logowania, aby zapobiec brute force.",
  "Monitoruj podejrzane aktywności (wiele logowań z różnych lokalizacji).",
  "Nie udostępniaj informacji o infrastrukturze w publicznych forach.",
  "Stosuj Content Security Policy (CSP) aby ograniczyć XSS.",
  "Regularnie aktualizuj biblioteki i zależności projektu.",
]

export const getTipOfTheDay = () => {
  const today = new Date().toISOString().split('T')[0] // YYYY-MM-DD
  const seed = today.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  const index = seed % SECURITY_TIPS.length
  return SECURITY_TIPS[index]
}
