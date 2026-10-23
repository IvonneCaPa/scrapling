import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURACIÓN DE LA PÁGINA (Favicon y título) ---
st.set_page_config(page_title="QueerParty Scraper", page_icon="logo.png", layout="wide")

# --- INYECCIÓN DE CSS PERSONALIZADO (ESTILO QUEERPARTY) ---
st.markdown("""
<style>
    /* Importar fuentes de Google */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

    /* Aplicar fuentes */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 900 !important;
    }

    /* Título principal con degradado */
    h1 {
        background: linear-gradient(to right, #ec4899, #d946ef, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        letter-spacing: -0.05em;
    }

    /* Estilo de la tabla (Dataframe) */
    .stDataFrame {
        border-radius: 16px !important;
        overflow: hidden !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGO Y TÍTULO ---
# Nota: Si el logo no carga en Wasmer, asegúrate de que el archivo "logo.png" esté en la raíz del repo.
try:
    st.image("logo.png", width=150)
except:
    pass # Si no hay logo, no rompemos la app

st.markdown("""
<h1 style="
    font-family: 'Outfit', sans-serif;
    font-weight: 900;
    font-size: 3.5rem;
    line-height: 1.1;
    letter-spacing: -0.05em;
    background: linear-gradient(to right, #ec4899, #d946ef, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
">
    🪩 Agenda de Eventos
</h1>
""", unsafe_allow_html=True)
st.write("Explora los próximos eventos de la escena queer en Barcelona.")

# --- LEER EL CSV ---
# Intentamos leer el archivo directamente
try:
    df = pd.read_csv('eventos_todos.csv')
    
    # Ordenar por fecha (por si no lo están ya)
    MESES = {'ene':1,'feb':2,'mar':3,'abr':4,'may':5,'jun':6,
             'jul':7,'ago':8,'sep':9,'oct':10,'nov':11,'dic':12}

    def parsear_fecha(f):
        try:
            partes = str(f).strip().split()
            dia = int(partes[0])
            mes = MESES[partes[1].lower()]
            return datetime(datetime.now().year, mes, dia)
        except:
            return pd.NaT

    df['_fecha_orden'] = df['Fecha'].apply(parsear_fecha)
    df = df.sort_values('_fecha_orden').drop(columns=['_fecha_orden'])

    # Mostrar el número de eventos
    st.success(f"✅ Se han encontrado **{len(df)} eventos**.")
    st.divider()

    # --- TABLA MEJORADA ---
    st.subheader("Resultados")
    
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "Link compra entrada": st.column_config.LinkColumn(
                "Link compra entrada",
                help="Haz clic para comprar la entrada",
                validate="^https://.*",
                display_text="Comprar 🎟️",
                width="small"
            ),
            "Link de la imagen": st.column_config.ImageColumn(
                "Imagen",
                help="Previsualización de la imagen",
                width="small"
            ),
            "Descripción": st.column_config.TextColumn(
                "Descripción",
                width="large"
            ),
            "Nombre": st.column_config.TextColumn(
                "Nombre",
                width="medium"
            ),
            "Lugar": st.column_config.TextColumn(
                "Lugar",
                width="medium"
            )
        }
    )

    # --- BOTÓN DE DESCARGA ---
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar estos resultados en CSV",
        data=csv,
        file_name='eventos_queerparty.csv',
        mime='text/csv',
    )

except FileNotFoundError:
    st.error("❌ Error: No se encontró el archivo 'eventos_todos.csv'. Asegúrate de que está en el repositorio.")
except Exception as e:
    st.error(f"❌ Ocurrió un error al leer los datos: {e}")