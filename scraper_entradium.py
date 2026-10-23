import requests
from bs4 import BeautifulSoup
import re
import csv
import sys

# --- CONFIGURACIÓN ---
# Uso: python scraper_entradium.py la-sastreria
#      python scraper_entradium.py believe-club
#      python scraper_entradium.py la-taska-show-bar-barcelona

if len(sys.argv) > 1:
    organizador = sys.argv[1]
else:
    organizador = "la-sastreria"  # por defecto

url = f"https://entradium.com/es/organizers/{organizador}"
archivo_salida = f"eventos_{organizador}.csv"

print(f"Scrapeando: {url}")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

respuesta = requests.get(url, headers=headers)
soup = BeautifulSoup(respuesta.text, 'html.parser')

todos_los_enlaces = soup.find_all('a', href=True)

RE_FECHA = re.compile(r'^\d{1,2}\s+(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)', re.IGNORECASE)
RE_PRECIO = re.compile(r'^[\d.,]+\s*€$')
CIUDADES = ('barcelona', 'madrid', 'barcekona', 'valencia', 'sevilla', 'bilbao', 'malaga', 'málaga')

eventos = []
vistos = set()

for enlace in todos_los_enlaces:
    href = enlace['href']
    if '/es/events/' not in href:
        continue

    url_evento = "https://entradium.com" + href if href.startswith('/') else href
    if url_evento in vistos:
        continue
    vistos.add(url_evento)

    trozos = []
    for hijo in enlace.find_all(string=True):
        t = hijo.strip()
        if t and t.lower() != 'desde':
            trozos.append(t)

    fecha = precio = nombre = lugar = ""

    for t in trozos:
        if not fecha and RE_FECHA.match(t):
            fecha = t
        elif not precio and RE_PRECIO.match(t):
            precio = t
        elif any(ciudad in t.lower() for ciudad in CIUDADES) and ',' in t:
            lugar = t
        elif fecha and precio and not nombre:
            nombre = t

    if not lugar and trozos:
        ultimo = trozos[-1]
        if ',' in ultimo:
            lugar = ultimo

    if not nombre:
        print(f"⚠️ Sin nombre para: {url_evento} -> trozos={trozos}")
        nombre = "NO_PARSEADO"

    eventos.append({
        "Fecha": fecha,
        "Nombre": nombre,
        "Lugar": lugar,
        "Precio": precio,
        "Link": url_evento,
    })

print(f"Eventos extraídos: {len(eventos)}")
for ev in eventos[:3]:
    print(ev)

with open(archivo_salida, 'w', newline='', encoding='utf-8') as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=["Fecha", "Nombre", "Lugar", "Precio", "Link"])
    escritor.writeheader()
    escritor.writerows(eventos)

print(f"\n✅ Guardado en '{archivo_salida}'")