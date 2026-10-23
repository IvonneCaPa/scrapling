import requests
from bs4 import BeautifulSoup
import csv
import re

URL = "https://churros-conchocolate.com/tickets/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

resp = requests.get(URL, headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, 'html.parser')

# Descripciones generales por sección
descripciones_seccion = {}
for sec_id in ['barcelona', 'madrid']:
    sec = soup.find('section', id=sec_id)
    if sec:
        # La descripción es el primer <p> o el texto tras el <h2>
        h2 = sec.find(['h1', 'h2', 'h3'])
        desc = ""
        if h2:
            siguiente = h2.find_next('p')
            if siguiente:
                desc = siguiente.get_text(" ", strip=True)
        descripciones_seccion[sec_id] = desc

resultados = []

# Recorremos todas las secciones que contengan eventos
for seccion in soup.find_all('section'):
    sec_id = seccion.get('id', '')
    if sec_id in ['barcelona', 'madrid']:
        fiesta = "Churros con Chocolate" if sec_id == 'barcelona' else "Caballero"
        desc_general = descripciones_seccion.get(sec_id, "")
    else:
        # Sección +Fiestas u otras
        texto_sec = seccion.get_text(" ", strip=True)
        if 'VARIETÉS' in texto_sec or 'BLACK PONY' in texto_sec:
            fiesta = "+Fiestas"
            desc_general = ""
        else:
            continue

    # Buscar todos los enlaces "Entradas" de esta sección
    for a in seccion.find_all('a', href=True):
        if a.get_text(strip=True).lower() != 'entradas':
            continue

        link_compra = a['href']

        # El bloque de evento es el contenedor padre del enlace
        bloque = a.find_parent()
        if not bloque:
            continue

        # Subir hasta encontrar un contenedor que tenga el título y la fecha
        # Estrategia: buscar el ancestro que contenga un <p> con el título
        contenedor = a
        for _ in range(5):
            contenedor = contenedor.find_parent()
            if not contenedor:
                break
            texto = contenedor.get_text(" ", strip=True)
            # Si el contenedor ya tiene título + fecha + "Entradas", nos vale
            if re.search(r'\d{1,2}\s+(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)', texto, re.IGNORECASE) and 'Entradas' in texto:
                break

        if not contenedor:
            continue

        texto_bloque = contenedor.get_text(" ", strip=True)

        # Nombre: el <p> que contiene el título (suele tener "–" o "CHURROS"/"CABALLERO"/"VARIETÉS")
        nombre = ""
        for p in contenedor.find_all('p'):
            t = p.get_text(" ", strip=True)
            if t and ('–' in t or 'CHURROS' in t.upper() or 'CABALLERO' in t.upper() or 'VARIETÉS' in t.upper()):
                nombre = t
                break
        if not nombre:
            # Fallback: primera línea del texto
            nombre = texto_bloque.split('Entradas')[0].strip()[:100]

                # Fecha y hora: patrón flexible (mayúsculas/minúsculas, con o sin hora)
        fecha = ""
        hora = ""
        lugar = ""

        # Intentar primero con hora: "25 oct 16:00 Sala Apolo BCN"
        match = re.search(
            r'(\d{1,2}\s+[A-Za-zÁÉÍÓÚÑáéíóúñ]{3,4})\s+(\d{1,2}:\d{2})\s*([A-Za-zÀ-ÿ\s\.\+]+?)(?:\s*Entradas|$)',
            texto_bloque, re.IGNORECASE
        )
        if match:
            fecha = match.group(1)
            hora = match.group(2)
            lugar = match.group(3).strip()
        else:
            # Intentar sin hora: "6 NOV" o "06 nov"
            match_f = re.search(r'(\d{1,2}\s+[A-Za-zÁÉÍÓÚÑáéíóúñ]{3,4})', texto_bloque, re.IGNORECASE)
            if match_f:
                fecha = match_f.group(1)
            # Intentar capturar el lugar tras la fecha (sin hora)
            match_l = re.search(
                r'\d{1,2}\s+[A-Za-zÁÉÍÓÚÑáéíóúñ]{3,4}\s+([A-Za-zÀ-ÿ\s\.\+]+?)(?:\s*Entradas|$)',
                texto_bloque, re.IGNORECASE
            )
            if match_l:
                lugar = match_l.group(1).strip()

        # Normalizar fecha: si viene como "6 NOV", dejarla como "6 nov"
        if fecha:
            partes = fecha.split()
            if len(partes) == 2:
                fecha = f"{partes[0]} {partes[1].lower()}"

        # Ajustar Fiesta según el nombre
        if 'CABALLERO' in nombre.upper():
            fiesta = "Caballero"
        elif 'VARIETÉS' in nombre.upper() or 'BLACK PONY' in nombre.upper():
            fiesta = "+Fiestas"
        elif 'CHURROS' in nombre.upper():
            fiesta = "Churros con Chocolate"

        # Limpiar el nombre de posibles prefijos repetidos
        nombre = re.sub(r'\s+', ' ', nombre).strip()
        nombre = nombre.replace('+Fiestas', '').strip()
        lugar = lugar.replace('+Fiestas', '').strip()

        resultados.append({
            'Fecha': fecha,
            'Hora': hora,
            'Nombre': nombre,
            'Fiesta': fiesta,
            'Hosts': nombre,
            'Descripción': desc_general,
            'Lugar': lugar,
            'Precio': '',
            'Link compra entrada': link_compra,
            'Link de la imagen': '',
        })

        resultados.append({
            'Fecha': fecha,
            'Hora': hora,
            'Nombre': nombre,
            'Fiesta': fiesta,
            'Hosts': nombre,
            'Descripción': desc_general,
            'Lugar': lugar,
            'Precio': '',
            'Link compra entrada': link_compra,
            'Link de la imagen': '',
        })

# Deduplicar por link de compra
vistos = set()
resultados_unicos = []
for r in resultados:
    if r['Link compra entrada'] not in vistos:
        vistos.add(r['Link compra entrada'])
        resultados_unicos.append(r)

# Guardar CSV
with open('eventos_churros.csv', 'w', newline='', encoding='utf-8') as f:
    campos = ['Fecha', 'Hora', 'Nombre', 'Fiesta', 'Hosts', 'Descripción',
              'Lugar', 'Precio', 'Link compra entrada', 'Link de la imagen']
    escritor = csv.DictWriter(f, fieldnames=campos)
    escritor.writeheader()
    escritor.writerows(resultados_unicos)

print(f"✅ Guardados {len(resultados_unicos)} eventos en 'eventos_churros.csv'")
for r in resultados_unicos[:5]:
    print(r)