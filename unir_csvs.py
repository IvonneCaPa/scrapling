import csv
import os

ARCHIVOS = [
    'eventos_la-sastreria_completo_limpio.csv',
    'eventos_believe-club_completo_limpio.csv',
    'eventos_la-taska-show-bar-barcelona_completo_limpio.csv',
    'eventos_tinta_roja_limpio.csv',
    'eventos_brilli_brilli_limpio.csv',
    'eventos_churros_limpio.csv',
]

CAMPOS = [
    'Fecha', 'Hora', 'Nombre', 'Fiesta', 'Hosts', 'Descripción',
    'Lugar', 'Precio', 'Link compra entrada', 'Link de la imagen'
]

todos = []

for archivo in ARCHIVOS:
    if not os.path.exists(archivo):
        print(f"⚠️ No existe: {archivo} (se omite)")
        continue
    with open(archivo, 'r', encoding='utf-8') as f:
        filas = list(csv.DictReader(f))
        print(f"✅ {archivo}: {len(filas)} eventos")
        for fila in filas:
            todos.append({campo: fila.get(campo, '').strip() for campo in CAMPOS})

with open('eventos_todos.csv', 'w', newline='', encoding='utf-8') as f:
    escritor = csv.DictWriter(f, fieldnames=CAMPOS)
    escritor.writeheader()
    escritor.writerows(todos)

print(f"\n🎉 Total: {len(todos)} eventos en 'eventos_todos.csv'")