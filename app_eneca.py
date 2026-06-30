import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import folium
from streamlit_folium import st_folium

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Dashboard Cartográfico ENECA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos estéticos personalizados para tarjetas de alerta
st.markdown("""
    <style>
    .kpi-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #24415A;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA Y SIMULACIÓN DE DATOS (Basado en Formulario 1, 2 y 3)
@st.cache_data
def cargar_datos_completos():
    # Avance semanal
    semanas = [f"Semana {i}" for i in range(1, 9)]
    df_avance = pd.DataFrame({
        "Semana": semanas,
        "Planificado": [15, 30, 48, 65, 80, 95, 110, 120],
        "Real": [12, 28, 45, 61, 78, 92, 105, 118]
    })
    
    # Consistencia por Distrito (IDE 3 de Supervisor vs AE1/EH1 de Encuestador)
    df_consistencia = pd.DataFrame({
        "Distrito": ["San Salvador", "Soyapango", "Ilopango", "Mejicanos", "Santa Tecla"],
        "Estructuras Supervisor (IDE)": [120, 95, 84, 110, 75],
        "Estructuras Encuestador (AE/EH)": [120, 81, 84, 108, 75]
    })
    
    # Tipos de estructuras (IDE 2)
    tipos_est = ["Vivienda", "Vivienda Mesón", "Vivienda y Establecimiento", "Edificio Residencial", "Establecimiento", "Centro Educativo/Salud/Religioso"]
    df_estructuras = pd.DataFrame({
        "Tipo": tipos_est,
        "Cantidad": [450, 120, 85, 40, 65, 30]
    })
    
    # Densidad de hogares por vivienda (MH 2 / EH10)
    df_hogares = pd.DataFrame({
        "Hogares por Vivienda": ["1 Hogar", "2 Hogares", "3 o más Hogares"],
        "Total Viviendas": [380, 55, 15]
    })

    # Datos simulados de coordenadas GPS capturadas en campo (IDE 4) centrado en El Salvador
    df_coordenadas = pd.DataFrame({
        'Latitud': [13.6929, 13.7010, 13.6850, 13.7120, 13.6730],
        'Longitud': [-89.2182, -89.1420, -89.1870, -89.2030, -89.2800],
        'Municipio': ['San Salvador', 'Soyapango', 'Ilopango', 'Mejicanos', 'Santa Tecla'],
        'Estructura': ['Vivienda Particular', 'Vivienda Mesón', 'Establecimiento', 'Vivienda Particular', 'Edificio Residencial'],
        'Resultado': ['Completa', 'Ausente temporalmente', 'Completa', 'Rechazo', 'Completa'],
        'Color': ['green', 'orange', 'green', 'red', 'green']
    })
    
    return df_avance, df_consistencia, df_estructuras, df_hogares, df_coordenadas

df_avance, df_consistencia, df_estructuras, df_hogares, df_coordenadas = cargar_datos_completos()

# 3. BARRA LATERAL (FILTROS GLOBALES)
st.sidebar.title("Filtros de Control")
st.sidebar.markdown("---")
region_selected = st.sidebar.selectbox("Región de Salud", ["Metropolitana", "Occidental", "Central", "Paracentral", "Oriental"])
depto_selected = st.sidebar.selectbox("Departamento", ["San Salvador", "La Libertad"])
municipio_selected = st.sidebar.multiselect("Municipio", ["San Salvador", "Soyapango", "Ilopango", "Mejicanos", "Santa Tecla"], default=["San Salvador", "Soyapango", "Ilopango"])

# 4. ENCABEZADO PRINCIPAL
st.title("📊 ENECA: Control de Calidad y Gestión Cartográfica")
st.caption(f"Visualización en tiempo real para la Región {region_selected} | Fase: Actualización Cartográfica")
st.markdown("---")

# 5. FILA 1: TARJETAS DE INDICADORES CLAVE (KPIs)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("<div class='kpi-card'><h3>📈 Avance Global</h3><h2>98.3%</h2><p style='color:green;margin:0;'>🟢 En Meta Operativa</p></div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='kpi-card'><h3>📍 Georreferencia</h3><h2>97.8%</h2><p style='color:green;margin:0;'>🟢 Éxito GPS (IDE 4)</p></div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='kpi-card'><h3>⚠️ Tasa Rechazo</h3><h2>2.4%</h2><p style='color:green;margin:0;'>🟢 Umbral Seguro (MH11)</p></div>", unsafe_allow_html=True)
with col4:
    st.markdown("<div class='kpi-card'><h3>🏠 Vivienda Cerrada</h3><h2>11.5%</h2><p style='color:orange;margin:0;'>🟡 Reajustar Horarios (IDS 6)</p></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 6. NUEVA SECCIÓN: MAPA DE COBERTURA GEORREFERENCIADA
st.subheader("🗺️ Mapa de Cobertura y Georreferenciación en Tiempo Real (IDE 4)")
st.caption("Los puntos muestran las estructuras mapeadas en terreno. El color indica el estado de la visita (Verde: Completo, Amarillo: Ausente, Rojo: Rechazo).")

# Crear mapa centrado en el área metropolitana
m = folium.Map(location=[13.6929, -89.2182], zoom_start=12, tiles="OpenStreetMap")

# Agregar marcadores interactivos
for index, fila in df_coordenadas.iterrows():
    folium.Marker(
        location=[fila['Latitud'], fila['Longitud']],
        popup=f"<b>Muni:</b> {fila['Municipio']}<br><b>Tipo:</b> {fila['Estructura']}<br><b>Estado:</b> {fila['Resultado']}",
        tooltip=f"{fila['Municipio']} - {fila['Resultado']}",
        icon=folium.Icon(color=fila['Color'], icon='home' if 'Vivienda' in fila['Estructura'] else 'info-sign')
    ).add_to(m)

# Mostrar mapa responsivo
st_folium(m, width="100%", height=400, returned_objects=[])

st.markdown("---")

# 7. FILA 3: GRÁFICOS DE SEGUIMIENTO Y CONSISTENCIA
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("📉 Curva de Progreso: Planificado vs Real")
    fig_avance = px.line(df_avance, x="Semana", y=["Planificado", "Real"], 
                         markers=True, labels={"value": "Segmentos Completados"},
                         color_discrete_sequence=["#A0A0A0", "#24415A"])
    fig_avance.update_layout(legend=dict(title="Criterio"), margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_avance, use_container_width=True)

with col_b:
    st.subheader("🔍 Índice de Consistencia: Supervisor vs Encuestador")
    fig_consistencia = px.bar(df_consistencia, x="Distrito", 
                              y=["Estructuras Supervisor (IDE)", "Estructuras Encuestador (AE/EH)"],
                              barmode="group",
                              color_discrete_sequence=["#1f77b4", "#aec7e8"])
    fig_consistencia.update_layout(legend=dict(title="Formulario"), margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_consistencia, use_container_width=True)

# 8. FILA 4: CARACTERIZACIÓN DEMOGRÁFICA
col_c, col_d = st.columns(2)
with col_c:
    st.subheader("🏢 Distribución por Tipo de Estructura (IDE 2)")
    fig_pie = px.pie(df_estructuras, values="Cantidad", names="Tipo", 
                     color_discrete_sequence=px.colors.sequential.Blues_r, hole=0.4)
    fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_pie, use_container_width=True)

with col_d:
    st.subheader("👨‍👩‍👧‍👦 Densidad de Hogares por Vivienda (EH10)")
    fig_hogares = px.bar(df_hogares, x="Hogares por Vivienda", y="Total Viviendas",
                         color="Hogares por Vivienda", color_discrete_sequence=["#24415A", "#5A82A6", "#9CB9D9"])
    fig_hogares.update_layout(showlegend=False, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_hogares, use_container_width=True)

st.markdown("---")

# 9. PIE DE PÁGINA: TABLA DE ALERTAS (Solucionado con .map)
st.subheader("🚨 Alertas de Errores Críticos en Campo")

df_alertas = pd.DataFrame({
    "Código Segmento": ["SEG-0815", "SEG-1102", "SEG-0412", "SEG-0921"],
    "Municipio": ["Soyapango", "Ilopango", "San Salvador", "Mejicanos"],
    "Supervisor a Cargo": ["María López", "Carlos Mendoza", "Juan Pérez", "Ana Gómez"],
    "Estructuras Sin GPS (IDE 4)": [14, 0, 1, 8],
    "Tasa de Rechazo Diario": ["3.1%", "18.7%", "1.2%", "14.2%"],
    "Estado de Alerta": ["⚠️ GPS Descalibrado", "🚨 Alto Rechazo", "✅ Conforme", "🚨 Alto Rechazo"]
})

def color_alertas(val):
    if "🚨" in str(val):
        return 'background-color: #ffcccc; color: #cc0000; font-weight: bold;'
    elif "⚠️" in str(val):
        return 'background-color: #fff3cd; color: #856404;'
    elif "✅" in str(val):
        return 'background-color: #d4edda; color: #155724;'
    return ''

# Aquí aplicamos el método .map corregido para versiones modernas de Pandas
df_styled = df_alertas.style.map(color_alertas, subset=['Estado de Alerta'])
st.dataframe(df_styled, use_container_width=True, hide_index=True)