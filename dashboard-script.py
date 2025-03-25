import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Proyectos",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Dashboard de Gestión de Proyectos")

# Función para cargar y procesar datos
def load_data(uploaded_file):
    # Leer el Excel manteniendo los hipervínculos
    df = pd.read_excel(
        uploaded_file,
        parse_dates=[
            'Fecha Inicio',
            'Fecha Creación',
            'Fecha Actualización'
        ],
        date_parser=lambda x: pd.to_datetime(x, format='%d/%m/%Y', errors='coerce')
    )
    return df

# Subida de archivo
uploaded_file = st.file_uploader("📁 Cargar archivo Excel de JIRA", type=['xlsx'])

if uploaded_file is not None:
    # Cargar datos
    df = load_data(uploaded_file)
    
    # Mostrar filtros en la barra lateral
    st.sidebar.header("Filtros")
    
    # Filtro de empresa
    empresas = ['Todos'] + sorted(df['Empresa'].astype(str).unique().tolist())
    empresa_seleccionada = st.sidebar.selectbox('Empresa:', empresas)
    
    # Filtro de estado
    estados = ['Todos'] + sorted(df['Estado'].unique().tolist())
    estado_seleccionado = st.sidebar.selectbox('Estado:', estados)
    
    # Filtro de período
    st.sidebar.header("Filtro de Período")
    fecha_inicio = st.sidebar.date_input(
        "Fecha Inicio",
        value=df['Fecha Inicio'].min()
    )
    fecha_fin = st.sidebar.date_input(
        "Fecha Fin",
        value=df['Fecha Inicio'].max()
    )

    #Filtro de usuarios
    usuarios = ['Todos'] + sorted(df['Asignado'].unique().tolist())
    usuario_seleccionado = st.sidebar.selectbox('Usuario Asignado:', usuarios)


    # Aplicar filtros
    df_filtrado = df.copy()
    if empresa_seleccionada != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Empresa'] == empresa_seleccionada]
    if estado_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Estado'] == estado_seleccionado]
    if usuario_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Asignado'] == usuario_seleccionado]

    df_filtrado = df_filtrado[
        (df_filtrado['Fecha Inicio'].dt.date >= fecha_inicio) &
        (df_filtrado['Fecha Inicio'].dt.date <= fecha_fin)
    ]

    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Tareas",
            value=len(df_filtrado)
        )
    
    with col2:
        horas_totales = df_filtrado['Horas Utilizadas'].sum()
        st.metric(
            label="Total Horas",
            value=f"{horas_totales:,.0f}h"
        )
    
    with col3:
        tareas_proceso = len(df_filtrado[df_filtrado['Estado'] == 'En proceso'])
        st.metric(
            label="Tareas en Proceso",
            value=tareas_proceso
        )
    
    with col4:
        personal_activo = df_filtrado['Asignado'].nunique()
        st.metric(
            label="Personal Activo",
            value=personal_activo
        )
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución de tareas por empresa
        fig_empresa = px.pie(
            df_filtrado,
            names='Empresa',
            title='Distribución de Tareas por Empresa',
            hole=0.3
        )
        st.plotly_chart(fig_empresa, use_container_width=True)
        
        # Distribución de tipos de tarea
        tipo_tarea_counts = df_filtrado['Tipo Tarea'].value_counts().reset_index()
        fig_tipo = px.bar(
            tipo_tarea_counts,
            x='Tipo Tarea',  # Usar el nombre correcto de la columna
            y='count',
            title='Distribución de Tipos de Tareas'
        )
        st.plotly_chart(fig_tipo, use_container_width=True)
    
    with col2:
        # Carga de trabajo por persona
        carga_trabajo = df_filtrado.groupby('Asignado')['Horas Utilizadas'].sum().sort_values(ascending=True)
        fig_carga = px.bar(
            carga_trabajo,
            orientation='h',
            title='Carga de Trabajo por Persona (Horas)',
            labels={'value': 'Horas', 'index': 'Persona'}
        )
        st.plotly_chart(fig_carga, use_container_width=True)
        
        # Estado de las tareas
        fig_estado = px.pie(
            df_filtrado,
            names='Estado',
            title='Estado de las Tareas',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_estado, use_container_width=True)
    
    # Tabla de detalles
    st.header("📋 Detalles de Tareas")
    
    # Columnas a mostrar
    columnas_mostrar = [
        'Fecha Inicio',  
        'Código',
        'Tipo',
        'Horas Utilizadas',
        'Empresa',
        'Tipo Tarea', 
        'Resumen', 
        'Estado',
        "Asignado"        
    ]
 
    # Formatear fechas para la tabla
    df_tabla = df_filtrado[columnas_mostrar].copy()
    for col in ['Fecha Inicio']:
        df_tabla[col] = df_tabla[col].dt.strftime('%Y-%m-%d')

    # Crear la URL en el mismo Código
    df_tabla["Código"] = df_tabla["Código"].apply(
        lambda x: f'<a href="https://summitdev.atlassian.net/browse/{x}" target="_blank">{x}</a>'
    )

    # Mostrar la tabla con HTML habilitado
    st.write(
        df_tabla.to_html(
            escape=False,
            index=False
        ),
        unsafe_allow_html=True
    )

else:
    # Mensaje cuando no hay archivo cargado
    st.info("👆 Por favor, carga un archivo Excel para visualizar el dashboard.")
    
    # Ejemplo de estructura esperada
    st.markdown("""
    ### Estructura esperada del archivo:
    El archivo Excel debe contener las siguientes columnas:
    - Código
    - Tipo
    - Empresa
    - Tipo Tarea
    - Horas Utilizadas
    - Estado
    - Asignado
    - Fecha de inicio
    - Fecha Actualización
    """)

# Pie de página
st.markdown("---")
st.markdown("Dashboard creado por BorchSolutions 📊")
