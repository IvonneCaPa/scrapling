import requests
from bs4 import BeautifulSoup
import re

URL = "https://churros-conchocolate.com/tickets/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

resp = requests.get(URL, headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, 'html.parser')

# 1. Enlaces que parezcan de eventos o compra
print("--- Enlaces con 'event', 'ticket', 'entrada', 'barcelona', 'madrid' ---")
for a in soup.find_all('a', href=True):
    href = a['href'].lower()
    txt = a.get_text(strip=True)
    if any(x in href for x in ['event', 'ticket', 'entrada', 'barcelona', 'madrid', 'compra']) or any(x in txt.lower() for x in ['comprar', 'entrada', 'ticket']):
        print(f"  '{txt[:50]}' -> {a['href']}")

# 2. Buscar textos con fechas
print("\n--- Textos con posibles fechas ---")
for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'div', 'span']):
    txt = tag.get_text(" ", strip=True)
    if txt and re.search(r'\d{1,2}\s+(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)', txt, re.IGNORECASE):
        if len(txt) < 200:
            print(f"  <{tag.name}> {txt[:150]}")

# 3. Buscar precios
print("\n--- Textos con € ---")
for tag in soup.find_all(['p', 'div', 'span', 'h2', 'h3', 'a']):
    txt = tag.get_text(" ", strip=True)
    if txt and '€' in txt and len(txt) < 150:
        print(f"  <{tag.name}> {txt}")

# 4. Buscar secciones con id 'barcelona' o 'madrid'
print("\n--- Elementos con id que contenga ciudad ---")
for tag in soup.find_all(id=True):
    if any(x in tag['id'].lower() for x in ['barcelona', 'madrid', 'valencia', 'sevilla']):
        print(f"  <{tag.name} id='{tag['id']}'> {tag.get_text(' ', strip=True)[:150]}")

# 5. og:image
print("\n--- og:image ---")
og = soup.find('meta', {'property': 'og:image'})
print(og.get('content') if og else "NO HAY")

# 6. Iframes
print("\n--- Iframes ---")
for iframe in soup.find_all('iframe'):
    print(f"  src={iframe.get('src')}")

# 7. Primeros 2000 caracteres del body (texto limpio)
print("\n--- Primeros 2000 caracteres del body (texto) ---")
body = soup.find('body')
if body:
    print(body.get_text(" ", strip=True)[:2000])