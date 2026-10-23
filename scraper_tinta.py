import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import random

# --- CONFIGURACIÓN ---
BASE_URL = "https://www.tinta-roja.cat"
LISTADO_URL = BASE_URL  # La home ya tiene el listado
ARCHIVO_SALIDA = "eventos_tinta_roja.csv"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Lugar constante de Tinta Roja
LUGAR = "C/ Creu dels Molers, 17, 08004 Barcelona"

# --- FASE 1: Obtener enlaces de eventos desde la home ---
print("🔍 Fase 1: Obteniendo enlaces de la home...")
resp = requests.get(LISTADO_URL, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

enlaces = soup.find_all('a', href=True)
urls_eventos = []
vistos = set()

for a in enlaces:
    href = a['href']
    # Filtro: enlaces de espectáculos
    if '/es/espectaculos/' in href or '/ca/espectaculos/' in href:
        # Quitar el query string (?event_session_id=...) para no duplicar
        url_limpia = BASE_URL + href.split('?')[0]
        if url_limpia not in vistos:
            vistos.add(url_limpia)
            urls_eventos.append(url_limpia)

print(f"   Encontrados {len(urls_eventos)} eventos únicos en la home.")

# --- FASE 2: Entrar en cada evento y extraer datos ---
print("\n🔍 Fase 2: Extrayendo detalles de cada evento...")
resultados = []

for i, url in enumerate(urls_eventos, start=1):
    print(f"[{i}/{len(urls_eventos)}] {url}")

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')

             # 1. Nombre: el primer <h1>
        nombre = ""
        h1 = soup.find('h1')
        if h1:
            nombre = h1.get_text(strip=True)

        # 2. Recoger todos los <p> en orden
        parrafos = [p.get_text(" ", strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]

        # 3. Fecha y hora: buscamos el primer párrafo que contenga un día de la semana
        RE_FECHA = re.compile(r'(Lun|Mar|Mié|Jue|Vie|Sáb|Dom)', re.IGNORECASE)
        fecha_hora = ""
        idx_fecha = -1
        for i, p in enumerate(parrafos):
            if RE_FECHA.search(p) and ('-' in p or ':' in p) and not re.search(r'\d{2}\s+\w+\s+\d{2}', p):
                # Evitar las fechas cortas tipo "Vie 23 oct 26 - 20:30"
                fecha_hora = p
                idx_fecha = i
                break

        fecha = ""
        hora = ""
        if fecha_hora:
            match_hora = re.search(r'(\d{1,2}:\d{2})', fecha_hora)
            if match_hora:
                hora = match_hora.group(1)
            fecha = re.split(r'\s*-\s*|\s+\d{1,2}:\d{2}', fecha_hora)[0].strip()

        # 4. Precio: buscamos el primer párrafo con "€"
        precio = ""
        idx_precio = -1
        RE_PRECIO = re.compile(r'\d+\s*€')
        for i, p in enumerate(parrafos):
            if RE_PRECIO.search(p) and any(x in p.lower() for x in ['reserva', 'taquilla', 'anticipada', 'tarifa', 'desde', 'a partir']):
                precio = re.sub(r'\s+', ' ', p).strip()
                idx_precio = i
                break
        # Si no encontramos con palabras clave, cogemos el primero con €
        if not precio:
            for i, p in enumerate(parrafos):
                if RE_PRECIO.search(p):
                    precio = re.sub(r'\s+', ' ', p).strip()
                    idx_precio = i
                    break

        # 5. Hosts: el párrafo justo antes de la fecha (suele ser el artista)
        hosts = ""
        if idx_fecha > 0:
            hosts = parrafos[idx_fecha - 1]

        # 6. Descripción: párrafos a partir del precio, saltando fechas, nombres sueltos y basura
        descripcion_partes = []
        RE_FECHA_CORTA = re.compile(r'(Lun|Mar|Mié|Jue|Vie|Sáb|Dom)\s+\d{1,2}\s+\w+\s+\d{2}', re.IGNORECASE)
        BASURA = ['apertura de puertas', 'quedan', 'queda ', 'entradas', 'otras fechas',
                  'cómo llegar', 'metro:', 'facebook', 'política de cookies', 'reserva',
                  'recibir el programa', '¿quieres actuar', 'cuéntanos tu proyecto',
                  'paciencia, estamos buscando']

        inicio_desc = max(idx_precio + 1, 0) if idx_precio >= 0 else 0
        for p in parrafos[inicio_desc:]:
            pl = p.lower()
            # Saltar basura conocida
            if any(x in pl for x in BASURA):
                continue
            # Saltar fechas cortas
            if RE_FECHA_CORTA.search(p):
                continue
            # Saltar nombres sueltos: párrafos cortos que no acaban en puntuación de frase
            if len(p) < 50 and not re.search(r'[.!?…]$', p.strip()):
                continue
            # Saltar párrafos muy cortos
            if len(p) < 30:
                continue
            descripcion_partes.append(p)

        descripcion = " ".join(descripcion_partes).strip()
        descripcion = re.sub(r'\s+', ' ', descripcion)
        # Cortar en cuanto aparezca el footer de la web (por si acaso)
        descripcion = re.split(r'Recibir el programa por email', descripcion, flags=re.IGNORECASE)[0].strip()
        # Cortar el bloque de comida/tapeo
        descripcion = re.split(r'La comida incluye|1 Empanada Argentinas', descripcion)[0].strip()

        # 7. Imagen: excluir banderas, logos, iconos, facebook
        imagen = ""
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src and not any(x in src.lower() for x in [
                'logo', 'icon', 'facebook.com/tr', 'noscript', 'pixel',
                '/assets/flags/', 'flags/'
            ]):
                if src.startswith('/'):
                    imagen = BASE_URL + src
                elif src.startswith('http'):
                    imagen = src
                else:
                    imagen = BASE_URL + '/' + src
                break

        resultados.append({
            'Fecha': fecha,
            'Hora': hora,
            'Nombre': nombre,
            'Fiesta': '',
            'Hosts': hosts,
            'Descripción': descripcion,
            'Lugar': LUGAR,
            'Precio': precio,
            'Link compra entrada': url,
            'Link de la imagen': imagen,
        })

    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        resultados.append({
            'Fecha': '', 'Hora': '', 'Nombre': '', 'Fiesta': '', 'Hosts': '',
            'Descripción': '', 'Lugar': LUGAR, 'Precio': '',
            'Link compra entrada': url, 'Link de la imagen': '',
        })

    time.sleep(random.uniform(1, 2))

# --- Guardar CSV ---
with open(ARCHIVO_SALIDA, 'w', newline='', encoding='utf-8') as f:
    campos = ['Fecha', 'Hora', 'Nombre', 'Fiesta', 'Hosts', 'Descripción',
              'Lugar', 'Precio', 'Link compra entrada', 'Link de la imagen']
    escritor = csv.DictWriter(f, fieldnames=campos)
    escritor.writeheader()
    escritor.writerows(resultados)

print(f"\n✅ Guardado en '{ARCHIVO_SALIDA}'")