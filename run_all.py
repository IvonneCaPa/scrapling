import subprocess
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

# ========== CONFIGURACIÓN ==========
NOMBRE_HOJA = 'Eventos Barcelona'  # ⚠️ CAMBIA ESTO por el nombre exacto de tu hoja
ARCHIVO_CSV = 'eventos_todos.csv'
CREDENCIALES = 'credenciales.json'

# ========== 1. EJECUTAR SCRAPERS ==========
print("🚀 1. Ejecutando scrapers...")
comandos = [
    "python scraper_entradium.py la-sastreria",
    "python fase2_detalles.py la-sastreria",
    "python scraper_entradium.py believe-club",
    "python fase2_detalles.py believe-club",
    "python scraper_entradium.py la-taska-show-bar-barcelona",
    "python fase2_detalles.py la-taska-show-bar-barcelona",
    "python scraper_tinta.py",
    "python scraper_brilli.py",
    "python scraper_churros.py",
]
for cmd in comandos:
    print(f"   -> {cmd}")
    # check=False para que si un scraper falla (ej. Cloudflare), no detenga todo
    subprocess.run(cmd, shell=True, check=False)

# ========== 2. LIMPIAR ==========
print("\n🧹 2. Limpiando CSVs...")
subprocess.run("python limpiar_csvs.py", shell=True, check=False)

# ========== 3. UNIR ==========
print("\n🔗 3. Uniendo CSVs...")
subprocess.run("python unir_csvs.py", shell=True, check=False)

# ========== 4. ORDENAR POR FECHA ==========
print("\n📅 4. Ordenando por fecha...")
df = pd.read_csv(ARCHIVO_CSV)

MESES = {'ene':1,'feb':2,'mar':3,'abr':4,'may':5,'jun':6,
         'jul':7,'ago':8,'sep':9,'oct':10,'nov':11,'dic':12}

def parsear_fecha(f):
    try:
        partes = f.strip().split()
        dia = int(partes[0])
        mes = MESES[partes[1].lower()]
        return datetime(datetime.now().year, mes, dia)
    except:
        return pd.NaT

df['_fecha_orden'] = df['Fecha'].apply(parsear_fecha)
df = df.sort_values('_fecha_orden').drop(columns=['_fecha_orden'])
df.to_csv(ARCHIVO_CSV, index=False)
print(f"   Total de eventos en el CSV: {len(df)}")

# ========== 5. SUBIR A GOOGLE SHEETS (SIN DUPLICADOS) ==========
print("\n📤 5. Subiendo a Google Sheets...")

try:
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENCIALES, scope)
    client = gspread.authorize(creds)
    sheet = client.open(NOMBRE_HOJA).sheet1
    print(f"   Conectado a la hoja: '{NOMBRE_HOJA}'")
except Exception as e:
    print(f"❌ ERROR al conectar con Google Sheets: {e}")
    print("   Revisa que el nombre de la hoja sea correcto y que la hayas compartido con el 'client_email'.")
    exit(1)

# Leer los links que ya existen en la columna 9 (Link compra entrada)
try:
    links_existentes = set(sheet.col_values(9))
    # Quitar la cabecera si existe
    if 'Link compra entrada' in links_existentes:
        links_existentes.remove('Link compra entrada')
except Exception:
    links_existentes = set()

# Filtrar el DataFrame: solo eventos cuyo link NO esté en la hoja
df_nuevos = df[~df['Link compra entrada'].isin(links_existentes)]
df_nuevos = df_nuevos.fillna('') # Rellenar vacíos para evitar errores con pandas

if len(df_nuevos) > 0:
    # Si la hoja está vacía, escribir cabeceras primero
    if len(links_existentes) == 0:
        sheet.update([df.columns.values.tolist()])
        print("   Cabeceras escritas en la hoja.")
    
    # Añadir solo los nuevos al final
    sheet.append_rows(df_nuevos.values.tolist())
    print(f"✅ Añadidos {len(df_nuevos)} eventos nuevos a la hoja.")
else:
    print("ℹ️ No hay eventos nuevos para añadir (todos ya estaban en la hoja).")

print("\n🎉 Proceso completado con éxito.")