import streamlit as st
import json
import pandas as pd
import plotly.express as px
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Resultados Votación - Curso 1", layout="wide")

# --- DATOS DE ESTUDIANTES (LISTA 1 - Original) ---
ESTUDIANTES = [
    {"rut": "236669998", "nombre": "JULIAN AGUILAR"},
    {"rut": "237771052", "nombre": "ELOISA AHUMADA"},
    {"rut": "235812002", "nombre": "FELIPE AMBIADO"},
    {"rut": "238080614", "nombre": "FELIPE ARRIAGADA"},
    {"rut": "237693469", "nombre": "AGUSTIN CAMUS"},
    {"rut": "236455750", "nombre": "TAREK CHAMAS"},
    {"rut": "237679520", "nombre": "PEDRO FREIRE"},
    {"rut": "236588041", "nombre": "ALONSO GALDAMES"},
    {"rut": "238560136", "nombre": "LEONOR GIACAMAN"},
    {"rut": "237505468", "nombre": "MAITE GILLET"},
    {"rut": "238188180", "nombre": "CONSUELO GUZMAN"},
    {"rut": "237165632", "nombre": "TEODORO HERNANDO"},
    {"rut": "236909026", "nombre": "SEBASTIAN IBAR"},
    {"rut": "237720474", "nombre": "AGUSTIN JELVES"},
    {"rut": "236203751", "nombre": "SOFIA LAGOS"},
    {"rut": "237052331", "nombre": "MAITE MEJIAS"},
    {"rut": "235501716", "nombre": "AGUSTÍN MONTENEGRO"},
    {"rut": "237462653", "nombre": "CATALINA ODINO"},
    {"rut": "236234088", "nombre": "EMILIA OLMOS"},
    {"rut": "236646793", "nombre": "DAMIAN PETERMANN"},
    {"rut": "235293692", "nombre": "VITTORIO PIAGGIO"},
    {"rut": "238139104", "nombre": "ANTONIO PINO"},
    {"rut": "238891191", "nombre": "MAURICIO PIZARRO"},
    {"rut": "234124293", "nombre": "HELENA SANHUEZA"},
    {"rut": "23567744K", "nombre": "ALICIA VARGAS"},
    {"rut": "236857417", "nombre": "VALENTIN VILLARROEL"}
]

# Crear diccionario para búsqueda rápida RUT -> Nombre
rut_a_nombre = {e['rut']: e['nombre'] for e in ESTUDIANTES}

# --- FUNCIÓN DE CARGA LOCAL ---
def cargar_datos_locales(uploaded_file=None):
    # Prioridad 1: Archivo subido manualmente (por si quieres analizar un backup)
    if uploaded_file is not None:
        return json.load(uploaded_file), "Archivo subido manualmente"
    
    # Prioridad 2: Archivo local generado por el programa de votación
    archivo_local = 'votos.json'
    if os.path.exists(archivo_local):
        with open(archivo_local, 'r', encoding='utf-8') as f:
            return json.load(f), f"Archivo local '{archivo_local}'"
            
    return [], None

# --- INTERFAZ PRINCIPAL ---
st.title("📊 Dashboard Curso 1 (Local)")

# Sidebar simplificado
st.sidebar.header("Fuente de Datos")
uploaded_file = st.sidebar.file_uploader("Opcional: Subir JSON externo", type=['json'])

# Cargar datos
data, fuente = cargar_datos_locales(uploaded_file)

if not data:
    st.error("❌ No se encontraron datos.")
    st.info("Asegúrate de que el archivo 'votos.json' esté en la misma carpeta que este script, o súbelo en el menú lateral.")
    st.stop()

st.success(f"✅ Datos cargados desde: {fuente} ({len(data)} votos)")

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["🏆 Valores", "🤝 Mejor Compañero", "📝 Datos Crudos"])

# --- ANÁLISIS VALORES ---
with tab1:
    st.header("Resultados por Valor")
    if len(data) > 0:
        # Extraer todos los valores posibles de los datos
        valores_encontrados = set()
        for voto in data:
            if 'valores' in voto:
                valores_encontrados.update(voto['valores'].keys())
        
        valores_disponibles = list(valores_encontrados)
        
        if valores_disponibles:
            valor_seleccionado = st.selectbox("Selecciona un Valor:", valores_disponibles)
            
            conteo_valores = {}
            for voto in data:
                elegidos = voto['valores'].get(valor_seleccionado, [])
                for rut in elegidos:
                    nombre = rut_a_nombre.get(rut, rut)
                    conteo_valores[nombre] = conteo_valores.get(nombre, 0) + 1
            
            if conteo_valores:
                df_valores = pd.DataFrame(list(conteo_valores.items()), columns=['Alumno', 'Votos'])
                df_valores = df_valores.sort_values('Votos', ascending=False)
                
                fig = px.bar(
                    df_valores, 
                    x='Alumno', y='Votos', color='Votos',
                    title=f"Votos en: {valor_seleccionado}",
                    text_auto=True, color_continuous_scale='Blues'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sin votos para este valor.")
        else:
            st.warning("El archivo JSON no parece tener estructura de 'valores'.")
    else:
        st.info("El archivo está vacío.")

# --- ANÁLISIS MEJOR COMPAÑERO ---
with tab2:
    st.header("Ranking Mejor Compañero")
    ranking = {}
    
    for voto in data:
        elegidos = voto.get('mejor_companero', [])
        puntos_por_posicion = [3, 2, 1]
        
        for i, rut in enumerate(elegidos):
            if i < 3:
                nombre = rut_a_nombre.get(rut, rut)
                puntos = puntos_por_posicion[i]
                
                if nombre not in ranking:
                    ranking[nombre] = {'Votos Totales': 0, 'Puntaje': 0}
                ranking[nombre]['Votos Totales'] += 1
                ranking[nombre]['Puntaje'] += puntos

    if ranking:
        df_ranking = pd.DataFrame.from_dict(ranking, orient='index').reset_index()
        df_ranking.columns = ['Alumno', 'Votos Totales', 'Puntaje']
        df_ranking = df_ranking.sort_values('Puntaje', ascending=False).reset_index(drop=True)
        
        # FIX: Usamos column_config de Streamlit (moderno, sin dependencias extra)
        st.dataframe(
            df_ranking,
            column_config={
                "Puntaje": st.column_config.ProgressColumn(
                    "Puntaje",
                    help="Puntaje calculado",
                    format="%d",
                    min_value=0,
                    max_value=int(df_ranking['Puntaje'].max()) if not df_ranking.empty else 10,
                ),
                "Votos Totales": st.column_config.NumberColumn(
                    "Votos Totales",
                    format="%d 🗳️"
                )
            },
            use_container_width=True
        )
        
        fig_ranking = px.bar(
            df_ranking.head(10),
            x='Alumno', y='Puntaje', color='Puntaje',
            title="Top 10 - Puntaje Mejor Compañero",
            text_auto=True, color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_ranking, use_container_width=True)
    else:
        st.info("No hay datos de Mejor Compañero.")

# --- DATOS CRUDOS ---
with tab3:
    st.write(f"Viendo datos de: {len(data)} estudiantes")
    st.json(data)
