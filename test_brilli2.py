import requests
from bs4 import BeautifulSoup
import re

URL = "https://brillibrilliparty.com/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

resp = requests.get(URL, headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, 'html.parser')

# 1. og:image
print("--- og:image ---")
og = soup.find('meta', {'property': 'og:image'})
print(og.get('content') if og else "NO HAY")

# 2. Buscar precios (€)
print("\n--- Textos con € ---")
for tag in soup.find_all(['p', 'div', 'span', 'h2', 'h3', 'a']):
    txt = tag.get_text(" ", strip=True)
    if txt and '€' in txt and len(txt) < 100:
        print(f"  <{tag.name}> {txt}")

# 3. Buscar el enlace real de compra (donde apunta #tickets o botones)
print("\n--- Enlaces de compra (botones 'COMPRAR') ---")
for a in soup.find_all('a', href=True):
    txt = a.get_text(strip=True).lower()
    if 'comprar' in txt or 'entrada' in txt or 'ticket' in txt:
        print(f"  '{a.get_text(strip=True)}' -> {a['href']}")

# 4. Buscar iframes (a veces el widget de venta está embebido)
print("\n--- Iframes ---")
for iframe in soup.find_all('iframe'):
    print(f"  src={iframe.get('src')}")

# 5. Buscar scripts con URLs de venta (fourvenues, entradium, etc.)
print("\n--- Scripts con URLs de venta ---")
for script in soup.find_all('script', src=True):
    src = script['src']
    if any(x in src.lower() for x in ['fourvenues', 'entradium', 'ticket', 'checkout', 'buy']):
        print(f"  {src}")

# 6. Buscar todas las <img> del hero (para imagen)
print("\n--- Primeras 5 imágenes ---")
for img in soup.find_all('img')[:5]:
    print(f"  {img.get('src')}")