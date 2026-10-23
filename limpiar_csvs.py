import csv
import os
import re

# Archivos a limpiar
ARCHIVOS = {
    'eventos_la-sastreria_completo.csv': 'sastreria',
    'eventos_believe-club_completo.csv': 'believe',
    'eventos_la-taska-show-bar-barcelona_completo.csv': 'taska',
    'eventos_tinta_roja.csv': 'tinta',
    'eventos_brilli_brilli.csv': 'brilli',
    'eventos_churros.csv': 'churros',
}

CAMPOS = [
    'Fecha', 'Hora', 'Nombre', 'Fiesta', 'Hosts', 'Descripción',
    'Lugar', 'Precio', 'Link compra entrada', 'Link de la imagen'
]

# Meses en español → abreviatura
MESES = {
    'enero': 'ene', 'febrero': 'feb', 'marzo': 'mar', 'abril': 'abr',
    'mayo': 'may', 'junio': 'jun', 'julio': 'jul', 'agosto': 'ago',
    'septiembre': 'sep', 'setiembre': 'sep', 'octubre': 'oct',
    'noviembre': 'nov', 'diciembre': 'dic',
    'ene': 'ene', 'feb': 'feb', 'mar': 'mar', 'abr': 'abr',
    'may': 'may', 'jun': 'jun', 'jul': 'jul', 'ago': 'ago',
    'sep': 'sep', 'oct': 'oct', 'nov': 'nov', 'dic': 'dic',
}


def normalizar_fecha(fecha):
    """Convierte '25 de octubre' o '6 NOV' a '25 oct' / '06 nov'."""
    if not fecha:
        return ''
    f = fecha.lower().strip()

    # Patrón: "25 de octubre" o "25 octubre"
    match = re.search(r'(\d{1,2})\s*(?:de\s+)?([a-záéíóúñ]+)', f)
    if match:
        dia = match.group(1).zfill(2)
        mes = match.group(2)
        mes_abrev = MESES.get(mes, mes[:3])
        return f"{dia} {mes_abrev}"

    return fecha  # Si no encaja, dejarla tal cual


def limpiar_fila(fila, origen):
    """Aplica las limpiezas específicas según el origen."""
    # 1. Quitar "+Fiestas" del lugar (Churros)
    if origen == 'churros':
        fila['Lugar'] = fila.get('Lugar', '').replace('+Fiestas', '').strip()

    # 2. Precio vacío → "Ver enlace"
    if not fila.get('Precio', '').strip():
        fila['Precio'] = 'Ver enlace'

    # 3. Limpiar descripción de Brilli Brilli
    if origen == 'brilli':
        desc = fila.get('Descripción', '')
        # Cortar en el listado de fotos
        desc = re.split(r'BRILLI BRILLI XXL ·', desc)[0].strip()
        desc = re.split(r'¡MÁS FOTOS!', desc)[0].strip()
        desc = re.sub(r'\s+', ' ', desc).strip()
        fila['Descripción'] = desc

    # 4. Normalizar fecha
    fila['Fecha'] = normalizar_fecha(fila.get('Fecha', ''))

    # 5. Limpiar espacios múltiples en todos los campos de texto
    for campo in CAMPOS:
        if campo in fila and isinstance(fila[campo], str):
            fila[campo] = re.sub(r'\s+', ' ', fila[campo]).strip()

    return fila


# Procesar cada archivo
for archivo, origen in ARCHIVOS.items():
    if not os.path.exists(archivo):
        print(f"⚠️ No existe: {archivo} (se omite)")
        continue

    with open(archivo, 'r', encoding='utf-8') as f:
        lector = csv.DictReader(f)
        filas = list(lector)

    filas_limpias = [limpiar_fila(fila, origen) for fila in filas]

    # Guardar versión limpia
    salida = archivo.replace('.csv', '_limpio.csv')
    with open(salida, 'w', newline='', encoding='utf-8') as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS)
        escritor.writeheader()
        # Solo escribimos los campos que nos interesan
        for fila in filas_limpias:
            escritor.writerow({campo: fila.get(campo, '') for campo in CAMPOS})

    print(f"✅ {archivo} → {salida} ({len(filas_limpias)} eventos)")

print("\n🧹 Limpieza completada.")