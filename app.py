import streamlit as st
import subprocess
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURACIÓN DE LA PÁGINA (Favicon y título) ---
st.set_page_config(page_title="QueerParty Scraper", page_icon="favicon.ico", layout="wide")

# --- INYECCIÓN DE CSS PERSONALIZADO (ESTILO QUEERPARTY · TEMA CLARO) ---
st.markdown("""
<style>
    /* Importar fuentes de Google */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

    /* Fondo claro y texto oscuro en toda la app */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background-color: #fdf8ff !important;
        color: #1f1633 !important;
    }

    /* Cabecera superior transparente (para que no se vea la barra oscura) */
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Aplicar fuentes */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Textos generales en oscuro */
    .stApp p,
    .stApp label,
    .stApp li,
    .stApp span,
    .stMarkdown,
    h2, h3, h4 {
        color: #1f1633;
    }

    /* Título principal con degradado */
    h1 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 900 !important;
        font-size: 3.5rem !important;
        line-height: 1.1 !important;
        letter-spacing: -0.05em !important;
        background: linear-gradient(to right, #ec4899, #d946ef, #06b6d4) !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-bottom: 0.5rem !important;
    }

    /* Estilo del botón principal (como en tu web) */
    .stButton > button,
    .stDownloadButton > button {
        background: linear-gradient(to right, #ec4899, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 700 !important;
        box-shadow: 0 8px 22px -6px rgba(236, 72, 153, 0.45) !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton > button p,
    .stDownloadButton > button p {
        color: white !important;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 28px -4px rgba(236, 72, 153, 0.6) !important;
    }

    /* Estilo de la tabla (Dataframe) */
    .stDataFrame {
        background-color: #ffffff !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        border: 1px solid rgba(31, 22, 51, 0.12) !important;
        box-shadow: 0 4px 18px -8px rgba(31, 22, 51, 0.18) !important;
    }

    /* Separadores */
    hr {
        border-color: rgba(31, 22, 51, 0.12) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGO (Sin nav, solo la imagen) ---
st.image("https://queerparty.es/img/logo.png", width=150)

# --- TÍTULO PRINCIPAL ---
st.title("Scraper de Eventos")
st.write("Pulsa el botón para buscar los eventos más recientes de nuestras webs.")

# --- ESTADO DE LA SESIÓN ---
if 'datos' not in st.session_state:
    st.session_state.datos = None

# --- BOTÓN PARA EJECUTAR EL SCRAPING ---
if st.button("🚀 Buscar Eventos Ahora"):

    with st.spinner("⏳ Ejecutando scrapers... Esto puede tardar un par de minutos. ¡No cierres la pestaña!"):

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
            subprocess.run(cmd, shell=True, check=False)

        subprocess.run("python limpiar_csvs.py", shell=True, check=False)
        subprocess.run("python unir_csvs.py", shell=True, check=False)

        try:
            df = pd.read_csv('eventos_todos.csv')

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

            st.session_state.datos = df

        except FileNotFoundError:
            st.error("❌ Error: No se encontró el archivo 'eventos_todos.csv'.")
            st.session_state.datos = None

# --- MOSTRAR LOS RESULTADOS ---
if st.session_state.datos is not None:
    df = st.session_state.datos
    st.success(f"✅ Se han encontrado **{len(df)} eventos**.")

    st.divider()

    # --- TABLA MEJORADA ---
    st.subheader("Resultados")

    st.dataframe(
        df,  # Mostramos el DataFrame completo sin filtros
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
        file_name='eventos_filtrados.csv',
        mime='text/csv',
    )
else:
    st.info("Aún no se han cargado los datos. Pulsa el botón de arriba para empezar.")