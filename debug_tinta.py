import requests
from bs4 import BeautifulSoup
import re

url = "https://www.tinta-roja.cat/es/espectaculos/concierto-de-bossa-samba-221"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

resp = requests.get(url, headers=headers)
print("Status:", resp.status_code)

soup = BeautifulSoup(resp.text, 'html.parser')

# 1. ¿Hay h1?
h1 = soup.find('h1')
print("\nH1:", h1.get_text(strip=True) if h1 else "NO ENCONTRADO")

# 2. ¿Cuántos párrafos hay y qué contienen?
print("\n--- PRIMEROS 15 <p> ---")
parrafos = soup.find_all('p')
print(f"Total de <p>: {len(parrafos)}")
for i, p in enumerate(parrafos[:15]):
    txt = p.get_text(" ", strip=True)
    if txt:
        print(f"[{i}] {txt[:120]}")