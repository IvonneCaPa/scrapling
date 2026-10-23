import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# 1. Inspeccionar la HOME
print("=" * 50)
print("HOME: https://www.tinta-roja.cat")
print("=" * 50)
resp = requests.get("https://www.tinta-roja.cat", headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

enlaces = soup.find_all('a', href=True)
eventos = [a for a in enlaces if '/es/espectaculos/' in a['href'] or '/ca/espectaculos/' in a['href']]
print(f"Enlaces de eventos encontrados: {len(eventos)}")
for a in eventos[:10]:
    print(f"  {a.get_text(strip=True)[:60]} -> {a['href']}")

# 2. Inspeccionar una página de DETALLE
print("\n" + "=" * 50)
print("DETALLE: https://www.tinta-roja.cat/es/espectaculos/dramas-de-honor-2198")
print("=" * 50)
resp2 = requests.get("https://www.tinta-roja.cat/es/espectaculos/dramas-de-honor-2198", headers=headers)
soup2 = BeautifulSoup(resp2.text, 'html.parser')

# Ver los encabezados y párrafos principales
for tag in soup2.find_all(['h1', 'h2', 'h3', 'p'], limit=20):
    texto = tag.get_text(strip=True)
    if texto and len(texto) > 5:
        print(f"<{tag.name}> {texto[:150]}")

# Buscar og:image
og_img = soup2.find('meta', {'property': 'og:image'})
if og_img:
    print(f"\nog:image -> {og_img.get('content')}")
else:
    print("\nNo hay og:image")