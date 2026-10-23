from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

URL = "https://tickets.grupoarena.com/es/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, wait_until="networkidle", timeout=60000)

    # Esperar un poco por si carga contenido dinámico
    page.wait_for_timeout(3000)

    html = page.content()
    browser.close()

soup = BeautifulSoup(html, 'html.parser')

# 1. Buscar todos los enlaces que parezcan de eventos
enlaces = soup.find_all('a', href=True)
eventos = []
for a in enlaces:
    href = a['href']
    if '/arena-experience/' in href:
        # Limpiar y completar URL
        if href.startswith('/'):
            url = "https://tickets.grupoarena.com" + href
        elif href.startswith('http'):
            url = href
        else:
            url = "https://tickets.grupoarena.com/" + href
        if url not in eventos:
            eventos.append(url)

print(f"Enlaces de eventos encontrados: {len(eventos)}")
for e in eventos[:15]:
    print(f"  {e}")

# 2. Si no hay enlaces, mostrar un trozo del HTML para depurar
if not eventos:
    print("\n⚠️ No se encontraron enlaces. Primeros 2000 caracteres del HTML:")
    print(html[:2000])