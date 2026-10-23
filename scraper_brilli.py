import requests
from bs4 import BeautifulSoup
import csv
import re

URL = "https://brillibrilliparty.com/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

resp = requests.get(URL, headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, 'html.parser')

# 1. Nombre: del <title> (limpiando el sufijo)
nombre = ""
if soup.title and soup.title.string:
    nombre = soup.title.string.split('...')[0].strip()

# 2. Texto completo del body para buscar fecha, hora, lugar y descripción
body_text = soup.get_text(" ", strip=True)

# 3. Fecha: patrón "DOMINGO 25 DE OCTUBRE"
fecha = ""
match_fecha = re.search(r'(LUNES|MARTES|MIÉRCOLES|JUEVES|VIERNES|SÁBADO|DOMINGO)\s+(\d{1,2})\s+DE\s+(\w+)', body_text, re.IGNORECASE)
if match_fecha:
    dia_semana = match_fecha.group(1).capitalize()
    dia = match_fecha.group(2)
    mes = match_fecha.group(3).lower()
    # Mapear mes a abreviatura
    meses = {'enero':'ene','febrero':'feb','marzo':'mar','abril':'abr','mayo':'may','junio':'jun',
             'julio':'jul','agosto':'ago','septiembre':'sep','octubre':'oct','noviembre':'nov','diciembre':'dic'}
    mes_abrev = meses.get(mes, mes[:3])
    fecha = f"{dia} {mes_abrev} ({dia_semana})"

# 4. Hora: patrón "DE 17:00 A 0:00"
hora = ""
match_hora = re.search(r'DE\s+(\d{1,2}:\d{2})\s+A\s+(\d{1,2}:\d{2})', body_text, re.IGNORECASE)
if match_hora:
    hora = f"{match_hora.group(1)} - {match_hora.group(2)}"

# 5. Lugar: patrón "Sala Plataforma (C/Nou de la Rambla, 145)"
lugar = ""
match_lugar = re.search(r'(Sala\s+\w+)\s*\(([^)]+)\)', body_text, re.IGNORECASE)
if match_lugar:
    lugar = f"{match_lugar.group(1)}, {match_lugar.group(2)}, Barcelona"
else:
    lugar = "Sala Plataforma, C/Nou de la Rambla, 145, Barcelona"

# 6. Link de compra: primer enlace a spaces.toffolo.studio
link_compra = ""
for a in soup.find_all('a', href=True):
    if 'spaces.toffolo.studio' in a['href']:
        link_compra = a['href']
        break

# 7. Imagen: og:image
imagen = ""
og = soup.find('meta', {'property': 'og:image'})
if og:
    imagen = og.get('content')

# 8. Descripción: el texto del body entre "COMPRAR ENTRADAS" y "SALA PLATAFORMA"
# Buscamos el bloque que empieza con "FIESTA" o similar
descripcion = ""
match_desc = re.search(r'(FIESTA\s*·[^©]+)', body_text, re.IGNORECASE)
if match_desc:
    descripcion = match_desc.group(1).strip()
    # Limpiar repeticiones de "¡COMPRAR ENTRADAS!"
    descripcion = re.sub(r'¡COMPRAR ENTRADAS!\s*', '', descripcion).strip()
    descripcion = re.sub(r'\s+', ' ', descripcion)
    # Limpiar la descripción: cortar en el listado de fotos o en el texto repetido
    descripcion = re.split(r'BRILLI BRILLI XXL ·', descripcion)[0].strip()
    descripcion = re.split(r'¡MÁS FOTOS!', descripcion)[0].strip()
    descripcion = re.sub(r'\s+', ' ', descripcion).strip()

# 9. Precio: no disponible en el HTML
precio = ""

# 10. Hosts y Fiesta: el nombre de la fiesta es Brilli Brilli
fiesta = "Brilli Brilli"
hosts = "Brilli Brilli"

# Guardar en CSV (una sola fila)
with open('eventos_brilli_brilli.csv', 'w', newline='', encoding='utf-8') as f:
    campos = ['Fecha', 'Hora', 'Nombre', 'Fiesta', 'Hosts', 'Descripción',
              'Lugar', 'Precio', 'Link compra entrada', 'Link de la imagen']
    escritor = csv.DictWriter(f, fieldnames=campos)
    escritor.writeheader()
    escritor.writerow({
        'Fecha': fecha,
        'Hora': hora,
        'Nombre': nombre,
        'Fiesta': fiesta,
        'Hosts': hosts,
        'Descripción': descripcion,
        'Lugar': lugar,
        'Precio': precio,
        'Link compra entrada': link_compra,
        'Link de la imagen': imagen,
    })

print("✅ Guardado en 'eventos_brilli_brilli.csv'")
print(f"\nFecha: {fecha}")
print(f"Hora: {hora}")
print(f"Nombre: {nombre}")
print(f"Lugar: {lugar}")
print(f"Link compra: {link_compra}")
print(f"Imagen: {imagen}")
print(f"Descripción: {descripcion[:200]}...")