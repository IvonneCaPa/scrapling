import csv
import re
import time
import random
import requests
import sys
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN ---
# Uso: python fase2_detalles.py la-sastreria
if len(sys.argv) > 1:
    organizador = sys.argv[1]
else:
    organizador = "la-sastreria"

archivo_entrada = f'eventos_{organizador}.csv'
archivo_salida = f'eventos_{organizador}_completo.csv'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

PALABRAS_BASURA = [
    "tenemos miles de eventos",
    "política de cookies",
    "nosotros y nuestros socios",
    "almacenamiento o acceso técnico",
    "consentimiento",
    "crea un evento",
    "¿por qué vender con entradium?",
    "selecciona tus entradas",
    "precio final",
    "demasiadas butacas",
]

def es_basura(texto):
    t = texto.lower()
    return any(p in t for p in PALABRAS_BASURA)

FORMATOS_FIESTA = {
    "vermut burlesquero": "Vermut Burlesquero",
    "el taller de": "El Taller de La Sorny",
    "cupleteria": "Cupletería",
    "comediax": "COMEDIAX",
}

with open(archivo_entrada, 'r', encoding='utf-8') as f:
    eventos = list(csv.DictReader(f))

print(f"Procesando {len(eventos)} eventos de '{organizador}'...")

resultados = []

for i, evento in enumerate(eventos, start=1):
    link = evento['Link']
    print(f"[{i}/{len(eventos)}] {evento['Nombre']}")

    try:
        respuesta = requests.get(link, headers=headers, timeout=10)
        soup = BeautifulSoup(respuesta.text, 'html.parser')

        # 1. Imagen
        imagen = ""
        og_image = soup.find('meta', {'property': 'og:image'})
        if og_image and og_image.get('content'):
            imagen = og_image['content']

        # 2. Descripción
        descripcion = ""
        candidatos = []
        for bloque in soup.find_all(['p', 'div', 'section']):
            txt = bloque.get_text(" ", strip=True)
            if 80 < len(txt) < 5000 and not es_basura(txt):
                candidatos.append(txt)
        if candidatos:
            descripcion = max(candidatos, key=len)

        descripcion = re.sub(r'^Descripción del evento\s*', '', descripcion)
        descripcion = re.split(r'Política de acceso', descripcion)[0]
        descripcion = re.sub(r'\s+', ' ', descripcion).strip()

        if len(descripcion) < 40 or descripcion.lower() == evento['Nombre'].lower():
            descripcion = ""

        # 3. Hora
        hora = ""
        texto_pagina = soup.get_text(" ", strip=True)
        match_hora = re.search(r'\b(\d{1,2}:\d{2})\s*[Hh]?\b', texto_pagina)
        if match_hora:
            hora = match_hora.group(1)

        # 4. Fiesta y Hosts
        nombre_evento = evento['Nombre']
        fiesta = ""
        hosts = ""
        nombre_lower = nombre_evento.lower()

        for clave, valor in FORMATOS_FIESTA.items():
            if clave in nombre_lower:
                fiesta = valor
                break

        if " con " in nombre_lower:
            hosts = nombre_evento.split(" con ", 1)[1].strip()
        elif " de " in nombre_lower and fiesta:
            hosts = nombre_evento.split(" de ", 1)[1].strip()
        else:
            hosts = nombre_evento.strip()

        resultados.append({
            'Fecha': evento['Fecha'],
            'Hora': hora,
            'Nombre': evento['Nombre'],
            'Fiesta': fiesta,
            'Hosts': hosts,
            'Descripción': descripcion,
            'Lugar': evento['Lugar'],
            'Precio': evento['Precio'],
            'Link compra entrada': evento['Link'],
            'Link de la imagen': imagen,
        })

    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        resultados.append({
            'Fecha': evento['Fecha'],
            'Hora': '',
            'Nombre': evento['Nombre'],
            'Fiesta': '',
            'Hosts': evento['Nombre'],
            'Descripción': '',
            'Lugar': evento['Lugar'],
            'Precio': evento['Precio'],
            'Link compra entrada': evento['Link'],
            'Link de la imagen': '',
        })

    time.sleep(random.uniform(1, 2))

with open(archivo_salida, 'w', newline='', encoding='utf-8') as f:
    campos = ['Fecha', 'Hora', 'Nombre', 'Fiesta', 'Hosts', 'Descripción',
              'Lugar', 'Precio', 'Link compra entrada', 'Link de la imagen']
    escritor = csv.DictWriter(f, fieldnames=campos)
    escritor.writeheader()
    escritor.writerows(resultados)

print(f"\n✅ Guardado en '{archivo_salida}'")