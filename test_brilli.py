import requests
from bs4 import BeautifulSoup

URL = "https://brillibrilliparty.com/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

resp = requests.get(URL, headers=headers, timeout=15)
print("Status:", resp.status_code)
print("Longitud HTML:", len(resp.text))

soup = BeautifulSoup(resp.text, 'html.parser')

# 1. Título
print("\nTítulo:", soup.title.string if soup.title else "NO HAY")

# 2. Enlaces que parezcan de eventos o entradas
print("\n--- Enlaces con 'event', 'ticket', 'fiesta', 'party' ---")
for a in soup.find_all('a', href=True):
    href = a['href'].lower()
    if any(x in href for x in ['event', 'ticket', 'entrada', 'fiesta', 'party']):
        print(f"  {a['href']} -> {a.get_text(strip=True)[:60]}")

# 3. ¿Hay algo que parezca una fecha?
import re
print("\n--- Textos con posibles fechas ---")
for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'div'], limit=50):
    txt = tag.get_text(" ", strip=True)
    if txt and re.search(r'\d{1,2}\s+(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)', txt, re.IGNORECASE):
        print(f"  <{tag.name}> {txt[:120]}")
        break

# 4. Primeros 1500 caracteres del body para ver estructura
print("\n--- Primeros 1500 caracteres del body ---")
body = soup.find('body')
if body:
    print(body.get_text(" ", strip=True)[:1500])