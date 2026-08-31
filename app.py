"""
Plataforma de Gestión de Compostaje - Planta Minera
=====================================================
MÓDULO 1: Formulación de lotes
MÓDULO 2: Capacidad de material estructurante (aserrín / cartón)
"""

import streamlit as st
import pandas as pd
import os
from datetime import date

# ---------------------------------------------------------------
# 1. CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------------

st.set_page_config(
    page_title="Gestión de Compostaje",
    page_icon="🌱",
    layout="wide"
)


# ===============================================================
# PALETA DE COLORES
# ===============================================================

COLOR_AZUL = "#031795"          # Azul corporativo
COLOR_SMART_BLUE = "#347FF6"    # Smart Blue para encabezados de módulos
COLOR_AZUL_CLARO = "#ABCBFA"

COLOR_ROJO = "#FE0000"          # Reservado para alertas críticas únicamente
COLOR_ROJO_HOVER = "#D90000"

COLOR_NARANJA = "#FE8C00"
COLOR_AMARILLO = "#F5D700"
COLOR_VERDE = "#64B246"
COLOR_TURQUESA = "#19EBDC"

COLOR_TEXTO = "#252525"
COLOR_TEXTO_SECUNDARIO = "#666666"

COLOR_BORDE = "#E3E6EA"
COLOR_FONDO_SUAVE = "#F8F9FB"
COLOR_BLANCO = "#FFFFFF"


def buscar_archivo_logo():
    
    extensiones_validas = (".png", ".jpg", ".jpeg", ".webp")
    try:
        for nombre_archivo in os.listdir("."):
            if nombre_archivo.lower().startswith("logo") and nombre_archivo.lower().endswith(extensiones_validas):
                return nombre_archivo
    except Exception:
        pass
    return None


# ===============================================================
# ESTILO GLOBAL DE LA APLICACIÓN — estilo dashboard ejecutivo
# (bordes redondeados, sombras suaves, minimalista)
# ===============================================================

st.markdown(
    f"""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', 'Source Sans Pro', sans-serif !important;
    }}

    .stApp {{
        background-color: {COLOR_BLANCO};
    }}

    [data-testid="stSidebar"] {{
        background-color: {COLOR_AZUL};
        border-right: 1px solid {COLOR_BORDE};
    }}

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {{
        color: white !important;
    }}
    /* Excepción: el texto DENTRO de los recuadros de los campos
       (donde se escriben los números) debe quedar oscuro, porque
       esos recuadros tienen fondo blanco. */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] div[data-baseweb="input"] {{
        color: {COLOR_TEXTO} !important;
    }}
    /* El contenido de los desplegables (expanders) en la barra lateral
       tiene fondo claro, así que su texto debe quedar oscuro, no blanco. */
    [data-testid="stSidebar"] [data-testid="stExpander"] * {{
        color: {COLOR_TEXTO} !important;
    }}

    /* Jerarquía tipográfica: títulos más grandes, texto de cuerpo más pequeño */
    h1 {{ font-size: 26px !important; font-weight: 700 !important; }}
    h2 {{ font-size: 20px !important; font-weight: 600 !important; }}
    h3 {{ font-size: 16px !important; font-weight: 600 !important; }}
    p, span, label, div {{ font-size: 14px; }}
    .stCaption, small {{ font-size: 12px !important; }}

    /* ---------------- NAVEGACIÓN ENTRE MÓDULOS ---------------- */

    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background-color: transparent;
        border-bottom: 1px solid {COLOR_BORDE};
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: transparent !important;
        color: #555555 !important;
        border: none !important;
        border-radius: 8px 8px 0 0;
        padding: 10px 18px;
        font-weight: 500;
        font-size: 14px;
    }}

    .stTabs [data-baseweb="tab"]:hover {{
        background-color: #EFF2F7 !important;
        color: #111111 !important;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: rgba(171, 203, 250, 0.25) !important;
        color: {COLOR_AZUL} !important;
        font-weight: 700 !important;
        border-bottom: 3px solid {COLOR_AZUL} !important;
        box-shadow: 0 -2px 8px rgba(3, 23, 149, 0.06);
    }}

    /* Streamlit dibuja una barra indicadora aparte (por defecto roja);
       la forzamos a azul y anulamos cualquier borde rojo residual. */
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {{
        background-color: {COLOR_AZUL} !important;
        border-color: {COLOR_AZUL} !important;
    }}
    .stTabs [data-baseweb="tab"]:focus,
    .stTabs [data-baseweb="tab"]:focus-visible {{
        color: {COLOR_AZUL} !important;
        outline-color: {COLOR_AZUL} !important;
        box-shadow: none !important;
    }}

    /* Todo lo relacionado a la barra indicadora queda azul, nunca roja */
    .stTabs [data-baseweb="tab-highlight"] {{
        background-color: {COLOR_AZUL} !important;
    }}

    /* ---------------- BOTONES PRINCIPALES ---------------- */
    /* Un solo color de marca: azul. El rojo queda reservado para errores. */

    .stButton > button[kind="primary"] {{
        background-color: {COLOR_AZUL} !important;
        color: white !important;
        border: none !important;
        border-radius: 10px;
        font-weight: 600;
        min-height: 42px;
        box-shadow: 0 2px 6px rgba(3, 23, 149, 0.18);
        transition: background-color 0.15s ease, transform 0.05s ease;
    }}

    .stButton > button[kind="primary"]:hover {{
        background-color: {COLOR_AZUL} !important;
        color: white !important;
    }}

    .stButton > button[kind="primary"]:active {{
        transform: translateY(1px);
    }}

    .stButton > button[kind="secondary"] {{
        background-color: {COLOR_BLANCO} !important;
        color: #333333 !important;
        border: 1px solid #CDD1D6 !important;
        border-radius: 10px;
        font-weight: 500;
    }}

    .stButton > button[kind="secondary"]:hover {{
        background-color: #F7F8FA !important;
        border-color: {COLOR_AZUL} !important;
        color: {COLOR_AZUL} !important;
    }}

    .stDownloadButton > button {{
        background-color: {COLOR_BLANCO} !important;
        color: {COLOR_AZUL} !important;
        border: 1px solid {COLOR_AZUL} !important;
        border-radius: 10px;
        font-weight: 600;
    }}

    .stDownloadButton > button:hover {{
        background-color: #F3F6FF !important;
    }}

    /* ---------------- TARJETAS DE MÉTRICAS (estilo KPI) ---------------- */

    div[data-testid="stMetric"] {{
        background-color: rgba(171, 203, 250, 0.18);
        border: 1.5px solid {COLOR_AZUL_CLARO};
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 2px 10px rgba(3, 23, 149, 0.05);
    }}

    div[data-testid="stMetricLabel"] {{
        color: #555555;
        font-weight: 500;
    }}

    div[data-testid="stMetricValue"] {{
        color: {COLOR_AZUL};
        font-weight: 700;
    }}

    /* ---------------- INPUTS ---------------- */

    div[data-baseweb="input"], div[data-baseweb="select"] > div, textarea {{
        border-radius: 10px !important;
        border: 1.5px solid {COLOR_AZUL_CLARO} !important;
    }}

    /* ---------------- TABLAS Y EXPANDERS ---------------- */

    div[data-testid="stDataFrame"] {{
        border: 1px solid {COLOR_BORDE};
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(3, 23, 149, 0.04);
    }}

    div[data-testid="stExpander"] {{
        border: 1px solid {COLOR_BORDE};
        border-radius: 14px;
        background-color: {COLOR_BLANCO};
        box-shadow: 0 2px 8px rgba(3, 23, 149, 0.04);
    }}

    h1, h2, h3 {{ color: {COLOR_TEXTO}; }}
    .stCaption {{ color: {COLOR_TEXTO_SECUNDARIO}; }}
    hr {{ border-color: #ECEDEF !important; }}

    div[data-testid="stAlert"] {{
        border-radius: 12px;
    }}

    @media (max-width: 768px) {{
        .stTabs [data-baseweb="tab"] {{ padding: 8px 10px; font-size: 13px; }}
        div[data-testid="stMetric"] {{ padding: 10px 12px; }}
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# ===============================================================
# ENCABEZADO PRINCIPAL (con logo si existe en el repositorio)
# ===============================================================

def mostrar_encabezado_app():
    st.markdown(
        f"""
        <div style="padding-top:4px; padding-bottom:4px; text-align:center;">
            <div style="color:{COLOR_AZUL}; font-size:34px; font-weight:700; line-height:1.15; margin:0;">
                PLATAFORMA PARA LA GESTIÓN DEL COMPOSTAJE (Versión 01)
            </div>
            <div style="color:{COLOR_TEXTO_SECUNDARIO}; font-size:17px; font-weight:400; margin-top:8px;">
                Sistema de apoyo para formulaciones y gestión de compostaje
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

def encabezado(texto):
    """Barra de título de cada módulo, sin íconos ni subtítulo — solo el nombre."""
    st.markdown(
        f"""
        <div style="background-color:{COLOR_AZUL}; padding:14px 20px; border-radius:14px;
                    margin-bottom:14px; box-shadow:0 3px 10px rgba(3,23,149,0.15);">
            <span style="color:white; font-size:22px; font-weight:700;">{texto}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ===============================================================
# PANTALLA DE BIENVENIDA (antes de entrar a los módulos)
# ===============================================================

if "ingreso_plataforma" not in st.session_state:
    st.session_state["ingreso_plataforma"] = False

if not st.session_state["ingreso_plataforma"]:
    ruta_logo = buscar_archivo_logo()

    st.markdown("<div style='height:8vh'></div>", unsafe_allow_html=True)
    col_izq, col_centro, col_der = st.columns([1, 2, 1])
    with col_centro:
        if ruta_logo:
            st.image(ruta_logo, width=180)
        else:
            st.markdown(
                f"""
                <div style="width:80px; height:80px; border-radius:50%; background:{COLOR_AZUL};
                            display:flex; align-items:center; justify-content:center; margin:0 auto 1rem;
                            box-shadow:0 4px 14px rgba(3,23,149,0.3);">
                    <span style="color:white; font-size:20px; font-weight:700;">AA</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown(
            f"""
            <div style="text-align:center; padding:0 1rem;">
                <div style="color:{COLOR_AZUL}; font-size:26px; font-weight:700; line-height:1.3;">
                    Plataforma para la gestión del compostaje
                </div>
                <div style="color:{COLOR_TEXTO_SECUNDARIO}; font-size:15px; margin-top:4px;">
                    Primera edición
                </div>
                <div style="color:{COLOR_TEXTO_SECUNDARIO}; font-size:14px; margin-top:14px;">
                    Sistema de apoyo para formulaciones y gestión de compostaje
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
        _, col_boton, _ = st.columns([1, 1, 1])
        with col_boton:
            if st.button("Ingresar", type="primary", use_container_width=True):
                st.session_state["ingreso_plataforma"] = True
                st.rerun()
    st.stop()


# ---------------------------------------------------------------
# 2. DATOS DE REFERENCIA DE INSUMOS
#    (tabla que enviaste - humedad validada con supervisor,
#    carbono/nitrógeno/C-N de literatura)
# ---------------------------------------------------------------
INSUMOS_REF = {
    "RO":  {"nombre": "Residuos orgánicos",              "humedad": 70.0, "carbono": 48.0, "nitrogeno": 3.20, "cn": 15},
    "LD":  {"nombre": "Lodo deshidratado de PTAR",        "humedad": 55.0, "carbono": 32.0, "nitrogeno": 3.50, "cn": 9},
    "AS":  {"nombre": "Aserrín",                          "humedad": 20.0, "carbono": 50.0, "nitrogeno": 0.10, "cn": 500},
    "CA":  {"nombre": "Cartón",                           "humedad": 5.0,  "carbono": 45.0, "nitrogeno": 0.11, "cn": 400},
    "ROD": {"nombre": "Residuos orgánicos deshidratados", "humedad": 6.52, "carbono": 48.3, "nitrogeno": 3.26, "cn": 15},
}

# Insumos que forman parte de la mezcla "base" (lo que llega a diario);
# AS y CA son los estructurantes que se calculan/ajustan en el Módulo 2.
INSUMOS_BASE = ["RO", "LD", "ROD"]

# Rango recomendado por literatura para iniciar la etapa mesófila.
# Parámetro editable (no fijo) por el tema de altitud (3000 msnm).
HUMEDAD_MIN_DEFAULT = 50.0
HUMEDAD_MAX_DEFAULT = 60.0
CN_MIN_DEFAULT = 25.0
CN_MAX_DEFAULT = 35.0

# Proporción declarada históricamente por los operadores (60/20/20)
PROPORCION_DECLARADA = {"RO": 60.0, "LD": 20.0, "CA": 20.0}

# Destinos posibles para la salida de compost terminado
DESTINOS_COMPOST = ["Donación a comunidad", "Vegetación / revegetación", "Otro"]

# ---------------------------------------------------------------
# Referencia de fases del proceso de compostaje (literatura general:
# Rynk et al., "The Composting Handbook"; guías FAO de compostaje).
# Rangos aproximados — deben validarse con las condiciones reales de
# la planta (altitud 3000 msnm), tal como se ajusta en la barra lateral
# para la formulación inicial.
# ---------------------------------------------------------------
FASES_COMPOSTAJE = {
    "Mesófila I": {
        "temp": (10, 40),
        "ph": (6.0, 7.5),
        "humedad": (50, 60),
        "microorganismos": "Bacterias y hongos mesófilos, en rápida multiplicación al inicio del proceso.",
        "duracion": "2 a 5 días",
        "descripcion": "Arranque del proceso: la pila empieza a calentarse por la actividad microbiana inicial.",
    },
    "Termófila": {
        "temp": (45, 70),
        "ph": (7.5, 9.0),
        "humedad": (45, 60),
        "microorganismos": "Bacterias y actinomicetos termófilos; esta fase es clave para eliminar patógenos y semillas de maleza.",
        "duracion": "1 a 4 semanas (según manejo y frecuencia de volteos)",
        "descripcion": "Fase de mayor actividad y temperatura; se recomienda mantener oxigenación con volteos frecuentes.",
    },
    "Mesófila II (enfriamiento)": {
        "temp": (20, 45),
        "ph": (7.0, 8.5),
        "humedad": (40, 55),
        "microorganismos": "Reaparecen bacterias y hongos mesófilos que continúan degradando material más resistente.",
        "duracion": "1 a 2 semanas",
        "descripcion": "La temperatura desciende gradualmente conforme se agota el material fácilmente degradable.",
    },
    "Maduración": {
        "temp": (15, 35),
        "ph": (6.5, 8.5),
        "humedad": (30, 45),
        "microorganismos": "Comunidad microbiana estabilizada; en pilas abiertas puede aparecer macrofauna (lombrices, insectos).",
        "duracion": "4 a 12 semanas",
        "descripcion": "Etapa de estabilización final; el compost pierde temperatura y se acerca a la temperatura ambiente.",
    },
}

# ---------------------------------------------------------------
# "MEMORIA" de la app (mientras está abierta en el navegador)
# ---------------------------------------------------------------
if "seguimiento" not in st.session_state:
    st.session_state["seguimiento"] = {}
if "lotes" not in st.session_state:
    st.session_state.lotes = {}
if "consultas_aserrin" not in st.session_state:
    st.session_state["consultas_aserrin"] = []
if "salidas_compost" not in st.session_state:
    st.session_state["salidas_compost"] = {}
if "laboratorio" not in st.session_state:
    st.session_state["laboratorio"] = {}

# Límites según NTP 201.207:2020 (FERTILIZANTES. Compost para uso agrícola.
# Requisitos, 1ª Edición). Se usa como referencia técnica, aunque tu compost
# no sea exactamente para ese uso — es la norma peruana disponible.
LIMITES_NTP = {
    "humedad":            {"nombre": "Humedad (%)",                          "min": 15,  "max": 35},
    "conductividad":      {"nombre": "Conductividad eléctrica (dS/m, dil. 1:5)", "min": None, "max": 5},
    "relacion_cn":        {"nombre": "Relación C/N (compost maduro)",        "min": 10,  "max": 25},
    "ph":                 {"nombre": "pH (dilución 1:5)",                    "min": 5.0, "max": 8.5},
    "materia_organica":   {"nombre": "Materia orgánica (%)",                 "min": 20,  "max": None},
    "nitrogeno":          {"nombre": "Nitrógeno (%)",                        "min": 0.3, "max": 1.5},
    "fosforo":            {"nombre": "Fósforo (%)",                         "min": 0.1, "max": 1.0},
    "potasio":            {"nombre": "Potasio (%)",                         "min": 0.3, "max": 1.0},
    "arsenico":           {"nombre": "Arsénico (mg/kg, base seca)",         "min": None, "max": 20},
    "cadmio":             {"nombre": "Cadmio (mg/kg, base seca)",           "min": None, "max": 1},
    "cromo":              {"nombre": "Cromo (mg/kg, base seca)",            "min": None, "max": 100},
    "mercurio":           {"nombre": "Mercurio (mg/kg, base seca)",         "min": None, "max": 1},
    "niquel":             {"nombre": "Níquel (mg/kg, base seca)",           "min": None, "max": 60},
    "plomo":              {"nombre": "Plomo (mg/kg, base seca)",            "min": None, "max": 150},
    "coliformes_fecales": {"nombre": "Coliformes fecales (NMP/g, base seca)", "min": None, "max": 1000},
    "salmonella":         {"nombre": "Salmonella spp (NMP en 4g, base seca)", "min": None, "max": 3},
    "huevos_helmintos":   {"nombre": "Huevos de helmintos viables (en 4g, base seca)", "min": None, "max": 1},
}
if "zarandeo" not in st.session_state:
    st.session_state["zarandeo"] = {}
# Lista de operadores para el selector.
OPERADORES = ["Adrián Carpio", "Fernando Valdivia", "Mishel Ruiz", "Otro"]

# Prefijo para los códigos de lote autogenerados, ej: CMP-2026-001
PREFIJO_LOTE = "CMP"

# ---------------------------------------------------------------
# 3. FUNCIONES DE CÁLCULO (compartidas entre módulos)
# ---------------------------------------------------------------

def calcular_mezcla(cantidades_kg: dict):
    """
    Calcula humedad ponderada y relación C/N de una mezcla.
    cantidades_kg: diccionario {codigo_insumo: kg_ingresados}
    Devuelve: (masa_total, humedad_%, carbono_total_kg, nitrogeno_total_kg, relacion_cn)
    """
    masa_total = 0.0
    humedad_ponderada = 0.0
    carbono_total = 0.0
    nitrogeno_total = 0.0

    for codigo, kg in cantidades_kg.items():
        if kg <= 0:
            continue
        ref = INSUMOS_REF[codigo]
        masa_seca = kg * (1 - ref["humedad"] / 100)
        carbono_total += masa_seca * (ref["carbono"] / 100)
        nitrogeno_total += masa_seca * (ref["nitrogeno"] / 100)
        humedad_ponderada += kg * ref["humedad"]
        masa_total += kg

    if masa_total == 0:
        return 0, 0, 0, 0, 0

    humedad_pct = humedad_ponderada / masa_total
    relacion_cn = carbono_total / nitrogeno_total if nitrogeno_total > 0 else float("inf")
    return masa_total, humedad_pct, carbono_total, nitrogeno_total, relacion_cn


def recalcular_acumulados_lote(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recalcula masa_acumulada_ton, humedad_acumulada_% y cn_acumulado
    de un lote completo, en orden de fecha, fila por fila.
    Debe llamarse siempre que se agregue, edite o elimine un ingreso,
    porque cada fila depende del acumulado de las filas anteriores.
    """
    df = df.sort_values("fecha").reset_index(drop=True)

    masa_acum_kg = 0.0
    carbono_acum_kg = 0.0
    nitrogeno_acum_kg = 0.0
    humedad_ponderada_acum = 0.0

    for i in range(len(df)):
        masa_kg = df.loc[i, "masa_total_ton"] * 1000
        carbono_acum_kg += df.loc[i, "carbono_total_kg"]
        nitrogeno_acum_kg += df.loc[i, "nitrogeno_total_kg"]
        humedad_ponderada_acum += df.loc[i, "humedad_%"] * masa_kg
        masa_acum_kg += masa_kg

        humedad_acum_pct = humedad_ponderada_acum / masa_acum_kg if masa_acum_kg else 0
        cn_acum = carbono_acum_kg / nitrogeno_acum_kg if nitrogeno_acum_kg else 0

        df.loc[i, "masa_acumulada_ton"] = round(masa_acum_kg / 1000, 2)
        df.loc[i, "humedad_acumulada_%"] = round(humedad_acum_pct, 1)
        df.loc[i, "cn_acumulado"] = round(cn_acum, 1)

    return df


def generar_recomendacion(humedad_pct, relacion_cn, hum_min, hum_max, cn_min, cn_max):
    """Devuelve lista de mensajes (texto, tipo) 'success'/'warning'/'error'."""
    mensajes = []

    if hum_min <= humedad_pct <= hum_max:
        mensajes.append((f"Humedad dentro del rango ({humedad_pct:.1f}%).", "success"))
    elif humedad_pct < hum_min:
        mensajes.append((f"Humedad baja ({humedad_pct:.1f}%). Considera agregar un insumo más húmedo o reducir estructurante seco.", "warning"))
    else:
        mensajes.append((f"Humedad alta ({humedad_pct:.1f}%). Considera agregar más material estructurante seco (cartón/aserrín).", "warning"))

    if cn_min <= relacion_cn <= cn_max:
        mensajes.append((f"Relación C/N dentro del rango ({relacion_cn:.1f}:1).", "success"))
    elif relacion_cn < cn_min:
        mensajes.append((f"Relación C/N baja ({relacion_cn:.1f}:1). Falta material rico en carbono (aserrín/cartón).", "warning"))
    else:
        mensajes.append((f"Relación C/N alta ({relacion_cn:.1f}:1). Falta material rico en nitrógeno (residuos orgánicos/lodo).", "warning"))

    return mensajes


def kg_requeridos_estructurante(fixed_carbono_kg, fixed_nitrogeno_kg, codigo_estructurante, cn_target):
    """
    Calcula cuántos KG del insumo estructurante (AS o CA) se necesitan
    agregar a una mezcla base para alcanzar la relación C/N objetivo.
    Despeje: x = (cn_target * N_fijo - C_fijo) / (c_insumo - cn_target * n_insumo)
    Si x resulta negativo, no hace falta agregar nada (se devuelve 0).
    """
    ref = INSUMOS_REF[codigo_estructurante]
    fraccion_seca = 1 - ref["humedad"] / 100
    c_insumo = fraccion_seca * (ref["carbono"] / 100)
    n_insumo = fraccion_seca * (ref["nitrogeno"] / 100)

    denominador = c_insumo - (cn_target * n_insumo)
    if denominador == 0:
        return 0.0

    x_kg = (cn_target * fixed_nitrogeno_kg - fixed_carbono_kg) / denominador
    return max(0.0, x_kg)


# ---------------------------------------------------------------
# 4. BARRA LATERAL: parámetros ajustables
# ---------------------------------------------------------------
st.sidebar.header("Parámetros de referencia")
st.sidebar.caption("Ajustables por observación de campo (ej. altitud 3000 msnm)")

hum_min = st.sidebar.number_input("Humedad mínima (%)", value=HUMEDAD_MIN_DEFAULT, step=1.0)
hum_max = st.sidebar.number_input("Humedad máxima (%)", value=HUMEDAD_MAX_DEFAULT, step=1.0)
cn_min = st.sidebar.number_input("Relación C/N mínima", value=CN_MIN_DEFAULT, step=1.0)
cn_max = st.sidebar.number_input("Relación C/N máxima", value=CN_MAX_DEFAULT, step=1.0)
cn_target = (cn_min + cn_max) / 2

st.sidebar.divider()
st.sidebar.caption(
    "Rango base de literatura: 50-60% humedad para iniciar etapa mesófila. "
    "El ajuste aquí queda registrado como adaptación en observación, no como error."
)
st.sidebar.divider()
with st.sidebar.expander("Parámetros de insumos (actualizar con caracterización real)"):
    st.caption(
        "Si el laboratorio entrega una nueva caracterización, ajusta aquí los valores base "
        "para que todos los módulos recalculen automáticamente con los datos nuevos."
    )
    for codigo_insumo_sb in INSUMOS_REF:
        st.markdown(f"*{INSUMOS_REF[codigo_insumo_sb]['nombre']} ({codigo_insumo_sb})*")
        col_h, col_c, col_n = st.columns(3)
        INSUMOS_REF[codigo_insumo_sb]["humedad"] = col_h.number_input(
            "Humedad %", value=float(INSUMOS_REF[codigo_insumo_sb]["humedad"]),
            min_value=0.0, max_value=100.0, step=1.0, key=f"param_hum_{codigo_insumo_sb}"
        )
        INSUMOS_REF[codigo_insumo_sb]["carbono"] = col_c.number_input(
            "Carbono %", value=float(INSUMOS_REF[codigo_insumo_sb]["carbono"]),
            min_value=0.0, max_value=100.0, step=1.0, key=f"param_c_{codigo_insumo_sb}"
        )
        INSUMOS_REF[codigo_insumo_sb]["nitrogeno"] = col_n.number_input(
            "Nitrógeno %", value=float(INSUMOS_REF[codigo_insumo_sb]["nitrogeno"]),
            min_value=0.0, max_value=100.0, step=0.01, format="%.2f", key=f"param_n_{codigo_insumo_sb}"
        )
# ---------------------------------------------------------------
# 5. NAVEGACIÓN ENTRE MÓDULOS
# ---------------------------------------------------------------
mostrar_encabezado_app()

if st.session_state.lotes:
    _totales_insumo_top = {codigo: 0.0 for codigo in INSUMOS_REF}
    for _df_lote_top in st.session_state.lotes.values():
        for _codigo_top in INSUMOS_REF:
            _col_ton_top = f"{_codigo_top}_ton"
            if _col_ton_top in _df_lote_top.columns:
                _totales_insumo_top[_codigo_top] += _df_lote_top[_col_ton_top].sum()
    _masa_total_top = sum(_totales_insumo_top.values())

    _total_alertas_top = 0
    for _df_seg_top in st.session_state["seguimiento"].values():
        for _col_eval_top in ["eval_temp", "eval_ph", "eval_humedad"]:
            if _col_eval_top in _df_seg_top.columns:
                _total_alertas_top += (_df_seg_top[_col_eval_top] != "normal").sum()

    if "factor_emision_top" not in st.session_state:
        st.session_state["factor_emision_top"] = 0.5

    fila_titulo_ancho, fila_titulo_factor = st.columns([4, 1])
    with fila_titulo_ancho:
        st.markdown(
            f"""
            <div style="border:1.5px solid {COLOR_AZUL_CLARO}; border-radius:10px;
                        padding:10px 16px; background-color: rgba(171, 203, 250, 0.18);">
                <span style="color:{COLOR_AZUL}; font-weight:600; font-size:14px; display:block; text-align:center;">INDICADORES DE SEGUIMIENTO</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with fila_titulo_factor:
        with st.expander("Ajustar factor"):
            st.session_state["factor_emision_top"] = st.number_input(
                "Factor CO2e (t/t)", min_value=0.0, value=st.session_state["factor_emision_top"], step=0.05, format="%.2f", key="factor_emision_input"
            )

    _compost_obtenido_top = sum(
        d["cantidad_final_ton"] for d in st.session_state.get("zarandeo", {}).values()
        if d["estado"] == "terminado"
    )

    bloque_ancho, bloque_factor = st.columns([4, 1])
    with bloque_ancho:
        ind1, ind2, ind3, ind4, ind5 = st.columns(5)
        ind1.metric("Lotes activos", len(st.session_state.lotes))
        ind2.metric("Lotes con seguimiento", len(st.session_state["seguimiento"]))
        ind3.metric("Total ingresado a compostaje", f"{_masa_total_top:.2f} t")
        ind4.metric("Alertas acumuladas", int(_total_alertas_top))
        ind5.metric("Compost obtenido (zarandeado)", f"{_compost_obtenido_top:.2f} t")
    with bloque_factor:
        _factor_emision_top = st.session_state["factor_emision_top"]
        st.metric("CO2e evitado", f"{_masa_total_top * _factor_emision_top:.2f} t")
    st.divider()

tab_m1, tab_m2, tab_m3, tab_m4, tab_m5 = st.tabs([
    "Módulo 1 — Formulación de Lotes",
    "Módulo 2 — Capacidad de Estructurante",
    "Módulo 3 — Seguimiento de Pilas",
    "Módulo 4 — Stock de Compost",
    "Módulo 5 — Análisis de laboratorio",
])
# =================================================================
# MÓDULO 1 — FORMULACIÓN DE LOTES
# =================================================================
with tab_m1:
    encabezado("Módulo 1 — Formulación de Lotes")
    st.caption(
        "Registra los residuos que ingresan a cada lote y calcula automáticamente su humedad y relación "
        "carbono/nitrógeno, con historial acumulado día a día."
    )

    tab_nuevo, tab_historial = st.tabs(["Nuevo ingreso a un lote", "Historial de lotes"])

    # ---- PESTAÑA: NUEVO INGRESO ---------------------------------------
    with tab_nuevo:
        col1, col2, col3 = st.columns(3)

        with col1:
            operador_sel = st.selectbox("Operador", OPERADORES, key="m1_operador_sel")
            if operador_sel == "Otro":
                operador = st.text_input("Nombre del operador (nuevo)", key="m1_operador_otro")
            else:
                operador = operador_sel

        with col2:
            fecha_ingreso = st.date_input("Fecha", value=date.today(), key="m1_fecha")

        with col3:
            nums_existentes = [
                int(c.split("-")[-1]) for c in st.session_state.lotes.keys()
                if c.startswith(PREFIJO_LOTE) and c.split("-")[-1].isdigit()
            ]
            siguiente_num = max(nums_existentes) + 1 if nums_existentes else 1

            numero_lote = st.number_input("Número de lote", min_value=1, step=1, value=siguiente_num, key="m1_numero_lote")
            codigo_lote = f"{PREFIJO_LOTE}-{fecha_ingreso.year}-{int(numero_lote):03d}"

            if codigo_lote in st.session_state.lotes:
                st.caption(f"Código: **{codigo_lote}** (lote existente, se agregará este ingreso a su historial)")
            else:
                st.caption(f"Código: **{codigo_lote}** (lote nuevo)")

        st.subheader("Cantidades ingresadas hoy (toneladas)")
        st.caption("1 tonelada = 1000 kg. Los cálculos internos son los mismos, solo cambia la unidad de ingreso.")
        cols = st.columns(len(INSUMOS_REF))
        cantidades_ton = {}
        for col, (codigo, ref) in zip(cols, INSUMOS_REF.items()):
            with col:
                cantidades_ton[codigo] = st.number_input(
                    f"{ref['nombre']} ({codigo})", min_value=0.0, step=0.1, format="%.2f", key=f"nuevo_{codigo}"
                )
                if cantidades_ton[codigo] > 0:
                    st.caption(f"= {cantidades_ton[codigo] * 1000:.0f} kg")

        total_ton_preview = sum(cantidades_ton.values())
        if total_ton_preview > 0:
            st.caption("Proporción de esta mezcla (según lo ingresado arriba):")
            prop_cols = st.columns(len(INSUMOS_REF))
            for col, (codigo, ref) in zip(prop_cols, INSUMOS_REF.items()):
                pct = (cantidades_ton[codigo] / total_ton_preview) * 100 if cantidades_ton[codigo] > 0 else 0
                col.caption(f"{ref['nombre']}: **{pct:.0f}%**")

        st.subheader("Microorganismos benéficos (aditivo)")
        st.caption(
            "Inoculante microbiano aplicado a esta mezcla. Se registra para trazabilidad y costo, "
            "pero no entra en el cálculo de humedad ni de la relación C/N."
        )
        microorganismos_L = st.number_input(
            "Cantidad aplicada (litros)", min_value=0.0, step=0.1, format="%.2f", key="nuevo_microorganismos_L"
        )

        fecha_duplicada = (
            codigo_lote in st.session_state.lotes
            and (st.session_state.lotes[codigo_lote]["fecha"] == fecha_ingreso).any()
        )

        if st.button("Calcular y registrar ingreso", type="primary"):
            if not operador:
                st.error("Ingresa el nombre del operador.")
            elif sum(cantidades_ton.values()) == 0:
                st.error(
                    "No se registró ninguna cantidad. Ingresa al menos un valor mayor a 0 "
                    "en algún insumo y confirma que el número quedó escrito en el recuadro "
                    "antes de presionar el botón (en el celular, a veces hay que tocar fuera "
                    "del recuadro para que el número quede guardado)."
                )
            elif fecha_duplicada:
                st.error(
                    f"Ya existe un ingreso registrado para el lote **{codigo_lote}** en la fecha "
                    f"**{fecha_ingreso.strftime('%d/%m/%Y')}**. Solo se permite un registro por lote "
                    "y por día. Si te equivocaste en algún dato, ve a la pestaña **Historial de lotes** "
                    "→ **Corregir o eliminar un ingreso** para editarlo o borrarlo antes de volver a intentar."
                )
            else:
                cantidades = {codigo: ton * 1000 for codigo, ton in cantidades_ton.items()}
                masa, humedad_pct, c_total, n_total, cn = calcular_mezcla(cantidades)

                nueva_fila = pd.DataFrame([{
                    "fecha": fecha_ingreso,
                    "operador": operador,
                    **{f"{c}_ton": round(cantidades_ton[c], 2) for c in INSUMOS_REF},
                    **{f"{c}_%mezcla": round((cantidades_ton[c] / total_ton_preview) * 100, 1) if total_ton_preview else 0 for c in INSUMOS_REF},
                    "microorganismos_L": round(microorganismos_L, 2),
                    "masa_total_ton": round(masa / 1000, 2),
                    "humedad_%": round(humedad_pct, 1),
                    "relacion_cn": round(cn, 1) if cn != float("inf") else None,
                    "masa_acumulada_ton": None,       # se completa abajo con recalcular_acumulados_lote
                    "humedad_acumulada_%": None,
                    "cn_acumulado": None,
                    "carbono_total_kg": round(c_total, 2),
                    "nitrogeno_total_kg": round(n_total, 2),
                }])

                if codigo_lote in st.session_state.lotes:
                    df_actualizado = pd.concat(
                        [st.session_state.lotes[codigo_lote], nueva_fila], ignore_index=True
                    )
                else:
                    df_actualizado = nueva_fila

                # Lotes creados antes de agregar este campo no tienen la columna: se rellenan en 0.
                if "microorganismos_L" not in df_actualizado.columns:
                    df_actualizado["microorganismos_L"] = 0.0
                df_actualizado["microorganismos_L"] = df_actualizado["microorganismos_L"].fillna(0.0)

                st.session_state.lotes[codigo_lote] = recalcular_acumulados_lote(df_actualizado)

                # Valores acumulados ya recalculados, para mostrarlos abajo
                fila_actual = st.session_state.lotes[codigo_lote][
                    st.session_state.lotes[codigo_lote]["fecha"] == fecha_ingreso
                ].iloc[-1]
                masa_acum = fila_actual["masa_acumulada_ton"] * 1000
                humedad_acum_pct = fila_actual["humedad_acumulada_%"]
                cn_acum = fila_actual["cn_acumulado"]

                st.success(f"Ingreso registrado en el lote {codigo_lote}.")

                st.subheader("Resultado de este ingreso")
                m1, m2, m3 = st.columns(3)
                m1.metric("Masa ingresada", f"{masa / 1000:.2f} t")
                m2.metric("Humedad", f"{humedad_pct:.1f} %")
                m3.metric("Relación C/N", f"{cn:.1f} : 1")

                with st.expander("Ver balance de masa de este ingreso"):
                    agua_estimada = masa * (humedad_pct / 100)
                    masa_seca_estimada = masa - agua_estimada
                    b1, b2, b3 = st.columns(3)
                    b1.metric("Masa húmeda (total ingresado)", f"{masa / 1000:.2f} t")
                    b2.metric("Agua estimada", f"{agua_estimada / 1000:.2f} t")
                    b3.metric("Masa seca estimada", f"{masa_seca_estimada / 1000:.2f} t")
                    st.caption(
                        "Agua estimada = masa húmeda × humedad (%). "
                        "Masa seca estimada = masa húmeda − agua estimada. "
                        "El carbono y nitrógeno se calculan sobre la masa seca."
                    )

                st.subheader("Acumulado del lote (todo lo ingresado hasta hoy)")
                m4, m5, m6 = st.columns(3)
                m4.metric("Masa total del lote", f"{masa_acum / 1000:.2f} t")
                m5.metric("Humedad acumulada", f"{humedad_acum_pct:.1f} %")
                m6.metric("C/N acumulado", f"{cn_acum:.1f} : 1")

                st.subheader("Recomendaciones (según acumulado del lote)")
                for texto, tipo in generar_recomendacion(humedad_acum_pct, cn_acum, hum_min, hum_max, cn_min, cn_max):
                    if tipo == "success":
                        st.success(texto)
                    elif tipo == "warning":
                        st.warning(texto)
                    else:
                        st.error(texto)

    # ---- PESTAÑA: HISTORIAL --------------------------------------------
    with tab_historial:
        if not st.session_state.lotes:
            st.info("Aún no hay lotes registrados. Ve a la pestaña 'Nuevo ingreso' para comenzar.")
        else:
            lote_seleccionado = st.selectbox("Selecciona un lote", list(st.session_state.lotes.keys()), key="m1_hist_sel")
            df_lote = st.session_state.lotes[lote_seleccionado]
            st.dataframe(df_lote, use_container_width=True)

            csv = df_lote.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Descargar historial de este lote (CSV)",
                data=csv,
                file_name=f"{lote_seleccionado}_historial.csv",
                mime="text/csv",
            )
            st.caption(
                "Este historial no se sobrescribe: cada ingreso agrega una fila nueva, "
                "para mostrar la evolución completa del lote desde el día 1."
            )

            st.divider()
            with st.expander("Corregir o eliminar un ingreso"):
                st.caption(
                    "Selecciona la fecha del ingreso que quieres corregir. Al guardar o eliminar, "
                    "los acumulados del lote se recalculan automáticamente."
                )
                fechas_disponibles = df_lote["fecha"].tolist()
                fecha_a_editar = st.selectbox(
                    "Fecha del ingreso",
                    fechas_disponibles,
                    format_func=lambda f: f.strftime("%d/%m/%Y") if hasattr(f, "strftime") else str(f),
                    key="m1_fecha_editar",
                )

                fila_original = df_lote[df_lote["fecha"] == fecha_a_editar].iloc[0]
                idx_original = df_lote[df_lote["fecha"] == fecha_a_editar].index[0]

                st.write("Valores actuales de este ingreso:")
                columnas_vista = ["operador"] + [f"{c}_ton" for c in INSUMOS_REF]
                if "microorganismos_L" in fila_original.index:
                    columnas_vista.append("microorganismos_L")
                st.dataframe(
                    fila_original[columnas_vista].to_frame().T,
                    use_container_width=True,
                    hide_index=True,
                )

                st.write("Nuevos valores (déjalos igual si solo vas a eliminar):")
                col_op_e, col_resto_e = st.columns([1, 2])
                with col_op_e:
                    operador_edit = st.text_input(
                        "Operador", value=str(fila_original["operador"]), key="m1_editar_operador"
                    )

                cols_edit = st.columns(len(INSUMOS_REF))
                cantidades_edit_ton = {}
                for col, (codigo, ref) in zip(cols_edit, INSUMOS_REF.items()):
                    with col:
                        cantidades_edit_ton[codigo] = st.number_input(
                            f"{ref['nombre']} ({codigo})",
                            min_value=0.0,
                            step=0.1,
                            format="%.2f",
                            value=float(fila_original[f"{codigo}_ton"]),
                            key=f"m1_editar_{codigo}",
                        )

                microorganismos_edit_L = st.number_input(
                    "Microorganismos benéficos aplicados (litros)",
                    min_value=0.0,
                    step=0.1,
                    format="%.2f",
                    value=float(fila_original.get("microorganismos_L", 0.0) or 0.0),
                    key="m1_editar_microorganismos_L",
                )

                col_guardar, col_eliminar = st.columns(2)

                with col_guardar:
                    if st.button("Guardar cambios", type="primary", key="m1_btn_guardar_edicion"):
                        total_edit = sum(cantidades_edit_ton.values())
                        if not operador_edit:
                            st.error("Ingresa el nombre del operador.")
                        elif total_edit == 0:
                            st.error("Ingresa al menos una cantidad mayor a 0.")
                        else:
                            cantidades_kg_edit = {c: t * 1000 for c, t in cantidades_edit_ton.items()}
                            masa_e, humedad_e, c_e, n_e, cn_e = calcular_mezcla(cantidades_kg_edit)

                            df_lote.loc[idx_original, "operador"] = operador_edit
                            for c in INSUMOS_REF:
                                df_lote.loc[idx_original, f"{c}_ton"] = round(cantidades_edit_ton[c], 2)
                                df_lote.loc[idx_original, f"{c}_%mezcla"] = (
                                    round((cantidades_edit_ton[c] / total_edit) * 100, 1) if total_edit else 0
                                )
                            df_lote.loc[idx_original, "microorganismos_L"] = round(microorganismos_edit_L, 2)
                            df_lote.loc[idx_original, "masa_total_ton"] = round(masa_e / 1000, 2)
                            df_lote.loc[idx_original, "humedad_%"] = round(humedad_e, 1)
                            df_lote.loc[idx_original, "relacion_cn"] = round(cn_e, 1) if cn_e != float("inf") else None
                            df_lote.loc[idx_original, "carbono_total_kg"] = round(c_e, 2)
                            df_lote.loc[idx_original, "nitrogeno_total_kg"] = round(n_e, 2)

                            st.session_state.lotes[lote_seleccionado] = recalcular_acumulados_lote(df_lote)
                            st.success(
                                f"Ingreso del {fecha_a_editar.strftime('%d/%m/%Y')} actualizado. "
                                "Los acumulados del lote se recalcularon."
                            )
                            st.rerun()

                with col_eliminar:
                    if st.button("Eliminar este ingreso", key="m1_btn_eliminar_ingreso"):
                        df_restante = df_lote.drop(index=idx_original).reset_index(drop=True)
                        if df_restante.empty:
                            del st.session_state.lotes[lote_seleccionado]
                            st.success(
                                f"Se eliminó el único ingreso del lote {lote_seleccionado}. "
                                "El lote ya no aparece en la lista."
                            )
                        else:
                            st.session_state.lotes[lote_seleccionado] = recalcular_acumulados_lote(df_restante)
                            st.success(
                                f"Ingreso del {fecha_a_editar.strftime('%d/%m/%Y')} eliminado. "
                                "Los acumulados del lote se recalcularon."
                            )
                        st.rerun()

# =================================================================
# MÓDULO 2 — CAPACIDAD DE MATERIAL ESTRUCTURANTE
# =================================================================
with tab_m2:
    encabezado("Módulo 2 — Capacidad de Material Estructurante")

    with st.expander("¿Qué hace este módulo? (léelo antes de calcular)"):
        st.write(
            "Este módulo estima cuánto material estructurante (aserrín y/o cartón adicional) "
            "se necesita para que la mezcla llegue a una humedad y relación C/N adecuadas, "
            "considerando que va a ingresar más lodo deshidratado de PTAR a la planta."
        )
        st.write(
            "**Sobre la referencia 60/20/20:** los operadores han declarado trabajar históricamente "
            "con 60% residuos orgánicos, 20% lodo y 20% cartón. Esa referencia se muestra aquí "
            "**solo como comparación histórica**, no como una regla obligatoria — la mezcla real "
            "puede y debe ajustarse según lo que arrojen los cálculos de humedad y C/N."
        )

    st.subheader("1. Datos de la planificación")
    col1, col2 = st.columns(2)
    with col1:
        operador2_sel = st.selectbox("Operador", OPERADORES, key="m2_operador_sel")
        if operador2_sel == "Otro":
            operador2 = st.text_input("Nombre del operador (nuevo)", key="m2_operador_otro")
        else:
            operador2 = operador2_sel
    with col2:
        fecha2 = st.date_input("Fecha de planificación", value=date.today(), key="m2_fecha")

    st.caption("Residuos que ingresan siempre a la mezcla:")
    col_ro, col_ca, col_ld = st.columns(3)
    with col_ro:
        ro_ton = st.number_input("Residuos orgánicos (RO, t)", min_value=0.0, step=0.5, format="%.2f", key="m2_ro")
    with col_ca:
        ca_ton = st.number_input("Cartón ya considerado (CA, t)", min_value=0.0, step=0.5, format="%.2f", key="m2_ca")
    with col_ld:
        lodo_ton = st.number_input("Lodo deshidratado a procesar (LD, t)", min_value=0.0, step=0.5, format="%.2f", key="m2_ld")

    rod_ton = st.number_input(
        "Residuos orgánicos deshidratados (ROD, t) — material complementario, ingresa en poca cantidad",
        min_value=0.0, step=0.1, format="%.2f", key="m2_rod"
    )

    total_base_ton = ro_ton + ca_ton + lodo_ton

    if total_base_ton > 0:

        def mezcla_ton(cant_ton: dict):
            cant_kg = {k: v * 1000 for k, v in cant_ton.items()}
            masa_kg, hum, c_kg, n_kg, cn = calcular_mezcla(cant_kg)
            return {"masa_ton": masa_kg / 1000, "humedad": hum, "cn": cn, "carbono_kg": c_kg, "nitrogeno_kg": n_kg}

        insumos_planificados = {"RO": ro_ton, "ROD": rod_ton, "CA": ca_ton, "LD": lodo_ton}
        mezcla_base = mezcla_ton(insumos_planificados)

        if lodo_ton > 0:
            total_hist = lodo_ton / (PROPORCION_DECLARADA["LD"] / 100)
        else:
            total_hist = 0.0
        ro_hist = total_hist * (PROPORCION_DECLARADA["RO"] / 100)
        ca_hist = total_hist * (PROPORCION_DECLARADA["CA"] / 100)
        ld_hist = lodo_ton

        pct_ro_real = (ro_ton / total_base_ton) * 100
        pct_ca_real = (ca_ton / total_base_ton) * 100
        pct_ld_real = (lodo_ton / total_base_ton) * 100

        st.subheader("2. Referencia histórica vs. mezcla real ingresada")
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("Residuos orgánicos", f"{pct_ro_real:.0f}%", f"histórico {PROPORCION_DECLARADA['RO']:.0f}%")
        rc2.metric("Cartón", f"{pct_ca_real:.0f}%", f"histórico {PROPORCION_DECLARADA['CA']:.0f}%")
        rc3.metric("Lodo", f"{pct_ld_real:.0f}%", f"histórico {PROPORCION_DECLARADA['LD']:.0f}%")
        st.caption(
            "Esta comparación es solo informativa: muestra qué tan parecida es la mezcla real "
            "a la práctica histórica 60/20/20, sin que eso implique que deba corregirse."
        )
        if rod_ton > 0:
            st.caption(f"Se incluyen además {rod_ton:.2f} t de ROD, que no forma parte de la referencia 60/20/20.")

        if lodo_ton > 0:
            st.markdown("**Diferencia respecto a la referencia histórica** (tomando el lodo como base fija):")
            diferencia_ro = ro_ton - ro_hist
            diferencia_ca = ca_ton - ca_hist
            dc1, dc2 = st.columns(2)
            with dc1:
                if diferencia_ro >= 0:
                    st.write(f"RO: **{diferencia_ro:.2f} t por encima** de la referencia ({ro_hist:.2f} t). No implica que deba retirarse.")
                else:
                    st.write(f"RO: **{abs(diferencia_ro):.2f} t por debajo** de la referencia ({ro_hist:.2f} t).")
            with dc2:
                if diferencia_ca >= 0:
                    st.write(f"Cartón: **{diferencia_ca:.2f} t por encima** de la referencia ({ca_hist:.2f} t).")
                else:
                    st.write(f"Cartón: **{abs(diferencia_ca):.2f} t por debajo** de la referencia ({ca_hist:.2f} t). Esto es lo que se busca cerrar en la Alternativa C.")

        st.subheader("3. Alternativas de material estructurante")

        as_solo_ton = kg_requeridos_estructurante(mezcla_base["carbono_kg"], mezcla_base["nitrogeno_kg"], "AS", cn_target) / 1000
        mezcla_a = mezcla_ton({**insumos_planificados, "AS": as_solo_ton})

        ca_adicional_ton = kg_requeridos_estructurante(mezcla_base["carbono_kg"], mezcla_base["nitrogeno_kg"], "CA", cn_target) / 1000
        mezcla_b = mezcla_ton({**insumos_planificados, "CA": ca_ton + ca_adicional_ton})

        ca_combinado_ton = max(0.0, ca_hist - ca_ton)
        mezcla_con_ca_ref = mezcla_ton({**insumos_planificados, "CA": ca_ton + ca_combinado_ton})
        as_combinado_ton = kg_requeridos_estructurante(mezcla_con_ca_ref["carbono_kg"], mezcla_con_ca_ref["nitrogeno_kg"], "AS", cn_target) / 1000
        mezcla_c = mezcla_ton({**insumos_planificados, "CA": ca_ton + ca_combinado_ton, "AS": as_combinado_ton})

        alt1, alt2, alt3 = st.columns(3)
        with alt1:
            st.metric("Alternativa A — Aserrín", f"{as_solo_ton:.2f} t")
            st.caption("Ajuste exclusivamente con aserrín.")
        with alt2:
            st.metric("Alternativa B — Cartón adicional", f"{ca_adicional_ton:.2f} t")
            st.caption("Ajuste exclusivamente con cartón.")
        with alt3:
            st.metric("Alternativa C — Cartón + aserrín", f"{ca_combinado_ton:.2f} t CA + {as_combinado_ton:.2f} t AS")
            st.caption("Primero acerca el cartón a la referencia histórica, luego completa con aserrín.")

        if lodo_ton > 0:
            ind_a = as_solo_ton / lodo_ton
            ind_b = ca_adicional_ton / lodo_ton
            ind_c = (ca_combinado_ton + as_combinado_ton) / lodo_ton
        else:
            ind_a = ind_b = ind_c = 0

        st.subheader("4. Comparación técnica de escenarios")

        # Mezcla resultante si se siguiera exactamente la referencia histórica 60/20/20
        mezcla_hist = mezcla_ton({"RO": ro_hist, "CA": ca_hist, "LD": ld_hist})

        tabla_comparativa = pd.DataFrame([
            {
                "Escenario": "Mezcla sin ajuste",
                "RO (t)": round(ro_ton, 2), "ROD (t)": round(rod_ton, 2),
                "Cartón total (t)": round(ca_ton, 2), "Lodo (t)": round(lodo_ton, 2),
                "Aserrín (t)": 0.0, "Estructurante / t lodo": 0.0,
                "Masa total (t)": round(mezcla_base["masa_ton"], 2),
                "Humedad (%)": round(mezcla_base["humedad"], 1),
                "Relación C/N": round(mezcla_base["cn"], 1) if mezcla_base["cn"] != float("inf") else None,
            },
            {
                "Escenario": "Solo aserrín",
                "RO (t)": round(ro_ton, 2), "ROD (t)": round(rod_ton, 2),
                "Cartón total (t)": round(ca_ton, 2), "Lodo (t)": round(lodo_ton, 2),
                "Aserrín (t)": round(as_solo_ton, 2), "Estructurante / t lodo": round(ind_a, 2),
                "Masa total (t)": round(mezcla_a["masa_ton"], 2),
                "Humedad (%)": round(mezcla_a["humedad"], 1),
                "Relación C/N": round(mezcla_a["cn"], 1) if mezcla_a["cn"] != float("inf") else None,
            },
            {
                "Escenario": "Solo cartón adicional",
                "RO (t)": round(ro_ton, 2), "ROD (t)": round(rod_ton, 2),
                "Cartón total (t)": round(ca_ton + ca_adicional_ton, 2), "Lodo (t)": round(lodo_ton, 2),
                "Aserrín (t)": 0.0, "Estructurante / t lodo": round(ind_b, 2),
                "Masa total (t)": round(mezcla_b["masa_ton"], 2),
                "Humedad (%)": round(mezcla_b["humedad"], 1),
                "Relación C/N": round(mezcla_b["cn"], 1) if mezcla_b["cn"] != float("inf") else None,
            },
            {
                "Escenario": "Cartón + aserrín",
                "RO (t)": round(ro_ton, 2), "ROD (t)": round(rod_ton, 2),
                "Cartón total (t)": round(ca_ton + ca_combinado_ton, 2), "Lodo (t)": round(lodo_ton, 2),
                "Aserrín (t)": round(as_combinado_ton, 2), "Estructurante / t lodo": round(ind_c, 2),
                "Masa total (t)": round(mezcla_c["masa_ton"], 2),
                "Humedad (%)": round(mezcla_c["humedad"], 1),
                "Relación C/N": round(mezcla_c["cn"], 1) if mezcla_c["cn"] != float("inf") else None,
            },
            {
                "Escenario": "Referencia histórica 60/20/20",
                "RO (t)": round(ro_hist, 2), "ROD (t)": 0.0,
                "Cartón total (t)": round(ca_hist, 2), "Lodo (t)": round(ld_hist, 2),
                "Aserrín (t)": 0.0, "Estructurante / t lodo": 0.0,
                "Masa total (t)": round(mezcla_hist["masa_ton"], 2),
                "Humedad (%)": round(mezcla_hist["humedad"], 1),
                "Relación C/N": round(mezcla_hist["cn"], 1) if mezcla_hist["cn"] != float("inf") else None,
            },
        ])

        st.dataframe(tabla_comparativa, use_container_width=True, hide_index=True)
        st.caption(
            f"Cálculo hecho para una relación C/N objetivo de {cn_target:.0f}:1 "
            f"(punto medio del rango {cn_min:.0f}-{cn_max:.0f} configurado en la barra lateral)."
        )
        csv_comp = tabla_comparativa.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Descargar tabla comparativa (CSV)", data=csv_comp,
            file_name=f"comparativo_estructurante_{fecha2}.csv", mime="text/csv",
        )

        def evaluar_estado(mezcla):
            if not (cn_min <= mezcla["cn"] <= cn_max):
                return "REFORMULAR"
            if mezcla["humedad"] < hum_min:
                return "HUMEDAD BAJA"
            elif mezcla["humedad"] <= hum_min + 2:
                return "VIABLE (cerca del límite mínimo)"
            elif mezcla["humedad"] > hum_max:
                return "HUMEDAD ALTA"
            elif mezcla["humedad"] >= hum_max - 2:
                return "VIABLE (cerca del límite máximo)"
            else:
                return "VIABLE"

        estado_a, estado_b, estado_c = evaluar_estado(mezcla_a), evaluar_estado(mezcla_b), evaluar_estado(mezcla_c)

        st.subheader("5. Lectura para la toma de decisión")
        viables = ("VIABLE", "VIABLE (cerca del límite mínimo)", "VIABLE (cerca del límite máximo)")
        if estado_c == "VIABLE":
            st.success("La alternativa combinada (cartón + aserrín) mantiene humedad y C/N dentro de rango, con margen operativo.")
        elif estado_a == "VIABLE":
            st.success("La alternativa con aserrín mantiene humedad y C/N dentro de rango, con margen operativo.")
        elif estado_b == "VIABLE":
            st.success("La alternativa con cartón adicional mantiene humedad y C/N dentro de rango, con margen operativo.")
        elif estado_c in viables:
            st.warning(f"La alternativa combinada es admisible, pero su estado es: {estado_c}.")
        elif estado_a in viables:
            st.warning(f"La alternativa con aserrín es admisible, pero su estado es: {estado_a}.")
        elif estado_b in viables:
            st.warning(f"La alternativa con cartón es admisible, pero su estado es: {estado_b}.")
        else:
            todas_cn_ok = all(
                cn_min <= m["cn"] <= cn_max for m in (mezcla_a, mezcla_b, mezcla_c)
            )
            if todas_cn_ok and all(e == "HUMEDAD BAJA" for e in (estado_a, estado_b, estado_c)):
                st.warning(
                    "La relación C/N se logra en las tres alternativas, pero la humedad resulta baja en todas "
                    "(por debajo del mínimo configurado en la barra lateral). Esto ocurre porque el estructurante "
                    "necesario para corregir el C/N seca demasiado la mezcla. Considera aumentar la proporción de "
                    "residuo orgánico o lodo (más húmedos), o bajar el mínimo de humedad si tu experiencia de campo "
                    "indica que ese rango es viable a esta altitud."
                )
            elif todas_cn_ok and all(e == "HUMEDAD ALTA" for e in (estado_a, estado_b, estado_c)):
                st.warning(
                    "La relación C/N se logra en las tres alternativas, pero la humedad resulta alta en todas. "
                    "Considera aumentar la cantidad de estructurante seco (cartón o aserrín) más allá de lo "
                    "estrictamente necesario para el C/N, solo para bajar humedad."
                )
            else:
                st.warning("Ninguna alternativa alcanza a la vez humedad y C/N adecuados. Revisa la combinación de materiales.")

        st.markdown("**Resumen por alternativa** (si eliges esta opción, así quedaría la mezcla):")

        def fila_resumen(nombre, mezcla, estructurante_ton_lodo, estado):
            color_estado = COLOR_VERDE if estado.startswith("VIABLE") else (COLOR_NARANJA if estado in ("HUMEDAD BAJA", "HUMEDAD ALTA") else COLOR_ROJO)
            st.markdown(
                f"<div style='font-size:14px; padding:6px 0; border-left:3px solid {color_estado}; padding-left:10px;'>"
                f"<b>{nombre}</b> — C/N: {mezcla['cn']:.1f}:1 · "
                f"Humedad: {mezcla['humedad']:.1f}% · "
                f"Estructurante/t lodo: {estructurante_ton_lodo:.2f} t · "
                f"Estado: {estado}"
                f"</div>",
                unsafe_allow_html=True,
            )

        fila_resumen("Solo aserrín", mezcla_a, ind_a, estado_a)
        fila_resumen("Solo cartón adicional", mezcla_b, ind_b, estado_b)
        fila_resumen("Cartón + aserrín", mezcla_c, ind_c, estado_c)

        with st.expander("¿Cómo interpretar las alternativas?"):
            st.write("**Solo aserrín:** cuánto aserrín sería necesario si se usa como único material corrector del C/N.")
            st.write("**Solo cartón:** cuánto cartón adicional se necesitaría si se usa únicamente este material.")
            st.write("**Cartón + aserrín:** primero aprovecha el cartón hasta acercarse a la referencia histórica, y luego usa aserrín como complemento.")
            st.write("Una cantidad elevada de estructurante no significa que el cálculo esté mal: puede indicar que los materiales base están lejos de las condiciones objetivo.")
            st.write(f"Rango de humedad usado: {hum_min:.0f}%–{hum_max:.0f}%. Rango C/N usado: {cn_min:.0f}–{cn_max:.0f}.")

        st.subheader("6. Elegir alternativa y generar solicitud")
        alternativa_map = {
            "Solo aserrín": (as_solo_ton, 0.0, mezcla_a),
            "Solo cartón adicional": (0.0, ca_adicional_ton, mezcla_b),
            "Cartón + aserrín": (as_combinado_ton, ca_combinado_ton, mezcla_c),
        }
        alternativa_elegida = st.radio("¿Qué alternativa vas a solicitar?", list(alternativa_map.keys()), key="m2_alt_radio")

        if st.button("Generar reporte de solicitud", type="primary"):
            if not operador2:
                st.error("Ingresa el nombre del operador antes de generar el reporte.")
                st.stop()
            as_sol, ca_sol, mezcla_sel = alternativa_map[alternativa_elegida]
            reporte = f"""SOLICITUD DE MATERIAL ESTRUCTURANTE - PLANTA DE COMPOSTAJE
Fecha de planificación: {fecha2}
Operador: {operador2}
Alternativa elegida: {alternativa_elegida}

Residuos considerados:
  - Residuos orgánicos: {ro_ton:.2f} t
  - Residuos orgánicos deshidratados: {rod_ton:.2f} t
  - Cartón (ya considerado): {ca_ton:.2f} t
  - Lodo deshidratado a procesar: {lodo_ton:.2f} t

Material adicional a solicitar:
  - Aserrín: {as_sol:.2f} t
  - Cartón adicional: {ca_sol:.2f} t

Resultado estimado de la mezcla:
  - Masa total: {mezcla_sel['masa_ton']:.2f} t
  - Humedad estimada: {mezcla_sel['humedad']:.1f} %
  - Relación C/N estimada: {mezcla_sel['cn']:.1f}:1

Referencia histórica de planta (60/20/20, solo informativa):
  - RO: {ro_hist:.2f} t | Cartón: {ca_hist:.2f} t | Lodo: {ld_hist:.2f} t

(Reporte generado automáticamente por la plataforma de gestión de compostaje.
Valores estimados según formulación de referencia; el aserrín usa propiedades
referenciales de literatura y debe recalibrarse cuando exista caracterización real.)
"""
            st.text_area("Vista previa del reporte (puedes copiarlo a un correo)", reporte, height=320)
            st.download_button(
                "Descargar reporte (TXT)", data=reporte.encode("utf-8"),
                file_name=f"solicitud_estructurante_{fecha2}.txt", mime="text/plain",
            )
            st.session_state["consultas_aserrin"].append({
                "fecha": fecha2, "tipo": "solicitud_generada",
                "detalle": f"{alternativa_elegida}: aserrín {as_sol:.2f} t, cartón {ca_sol:.2f} t",
            })
    else:
        st.info("Ingresa al menos residuos orgánicos, cartón o lodo para ver las alternativas.")

    st.divider()
    st.subheader("Historial de consultas y alertas de este módulo")
    st.caption(
        "Aquí queda registrado cada reporte de solicitud que generas en la sección 6 "
        "(qué alternativa elegiste y cuánto aserrín/cartón pediste), como bitácora "
        "de las decisiones tomadas durante la sesión."
    )
    if st.session_state["consultas_aserrin"]:
        st.dataframe(pd.DataFrame(st.session_state["consultas_aserrin"]), use_container_width=True)
    else:
        st.caption("Aún no hay consultas registradas en esta sesión.")

# =================================================================
# MÓDULO 3 — SEGUIMIENTO DE PILAS
# =================================================================
with tab_m3:
    encabezado("Módulo 3 — Seguimiento de Pilas")
    st.caption(
        "Registra la temperatura, pH y humedad de cada lote a lo largo del tiempo, y recibe recomendaciones "
        "automáticas según la fase del proceso en la que se encuentra."
    )

    with st.expander("Fases del proceso de compostaje (referencia educativa)", expanded=False):
        st.caption(
            "Rangos de literatura general de compostaje. Son un punto de partida — "
            "deben ajustarse con la experiencia real de la planta (altitud 3000 msnm)."
        )
        tabla_fases = pd.DataFrame([
            {
                "Fase": nombre,
                "Temperatura (°C)": f"{d['temp'][0]}–{d['temp'][1]}",
                "pH": f"{d['ph'][0]}–{d['ph'][1]}",
                "Humedad (%)": f"{d['humedad'][0]}–{d['humedad'][1]}",
                "Duración típica": d["duracion"],
                "Microorganismos / notas": d["microorganismos"],
            }
            for nombre, d in FASES_COMPOSTAJE.items()
        ])
        st.dataframe(tabla_fases, use_container_width=True, hide_index=True)

    if not st.session_state.lotes:
        st.info("Aún no hay lotes creados. Ve al Módulo 1 y registra al menos un lote antes de hacer seguimiento.")
    else:
        st.subheader("1. Registrar mediciones de hoy")
        col1, col2, col3 = st.columns(3)
        with col1:
            lote_seg = st.selectbox("Código de lote", list(st.session_state.lotes.keys()), key="m3_lote")
        with col2:
            fecha_seg = st.date_input("Fecha de seguimiento", value=date.today(), key="m3_fecha")
        with col3:
            fase_seg = st.selectbox("Fase actual de la pila", list(FASES_COMPOSTAJE.keys()), key="m3_fase")

        operadores_seg = st.multiselect(
            "Operador(es) que realizan la medición",
            [op for op in OPERADORES if op != "Otro"] + ["Otro"],
            key="m3_operadores",
        )
        if "Otro" in operadores_seg:
            operador_otro_seg = st.text_input("Nombre del operador adicional", key="m3_operador_otro")

        st.markdown("**Temperatura** — 3 puntos de medición de la pila (°C)")
        t1, t2, t3 = st.columns(3)
        temp1 = t1.number_input("Punto 1", key="m3_t1", step=0.5, format="%.1f")
        temp2 = t2.number_input("Punto 2", key="m3_t2", step=0.5, format="%.1f")
        temp3 = t3.number_input("Punto 3", key="m3_t3", step=0.5, format="%.1f")
        temp_prom = (temp1 + temp2 + temp3) / 3
        st.caption(f"Temperatura promedio: **{temp_prom:.1f} °C**")

        st.markdown("**pH** — 3 puntos de medición de la pila")
        p1, p2, p3 = st.columns(3)
        ph1 = p1.number_input("Punto 1", key="m3_ph1", step=0.1, format="%.1f")
        ph2 = p2.number_input("Punto 2", key="m3_ph2", step=0.1, format="%.1f")
        ph3 = p3.number_input("Punto 3", key="m3_ph3", step=0.1, format="%.1f")
        ph_prom = (ph1 + ph2 + ph3) / 3
        st.caption(f"pH promedio: **{ph_prom:.2f}**")

        col_h, col_v = st.columns(2)
        with col_h:
            humedad_seg = st.number_input("Humedad medida de la pila (%)", min_value=0.0, max_value=100.0, step=1.0, key="m3_hum")
        with col_v:
            se_volteo = st.checkbox("¿Se realizó volteo en esta fecha?", key="m3_volteo_check")
            if se_volteo:
                num_volteos_dia = st.number_input("¿Cuántos volteos se hicieron?", min_value=1, step=1, value=1, key="m3_num_volteos")
            else:
                num_volteos_dia = 0

        if st.button("Registrar seguimiento", type="primary"):
            campos_faltantes = []
            if not operadores_seg:
                campos_faltantes.append("operador(es)")
            if temp1 == 0 or temp2 == 0 or temp3 == 0:
                campos_faltantes.append("los 3 puntos de temperatura")
            if ph1 == 0 or ph2 == 0 or ph3 == 0:
                campos_faltantes.append("los 3 puntos de pH")
            if humedad_seg == 0:
                campos_faltantes.append("humedad")

            if campos_faltantes:
                st.error(f"Faltan datos por completar: {', '.join(campos_faltantes)}. No se puede registrar con celdas en 0 o vacías.")
                st.stop()

            ref_fase = FASES_COMPOSTAJE[fase_seg]
            lista_operadores = [op for op in operadores_seg if op != "Otro"]
            if "Otro" in operadores_seg and operador_otro_seg:
                lista_operadores.append(operador_otro_seg)
            operadores_txt = ", ".join(lista_operadores) if lista_operadores else "(sin especificar)"

            def evaluar_parametro(valor, rango):
                if valor < rango[0]:
                    return "bajo"
                elif valor > rango[1]:
                    return "alto"
                else:
                    return "normal"

            eval_temp = evaluar_parametro(temp_prom, ref_fase["temp"])
            eval_ph = evaluar_parametro(ph_prom, ref_fase["ph"])
            eval_hum = evaluar_parametro(humedad_seg, ref_fase["humedad"])

            nueva_fila_seg = pd.DataFrame([{
                "fecha": fecha_seg, "fase": fase_seg, "operadores": operadores_txt,
                "T1": temp1, "T2": temp2, "T3": temp3, "T_prom": round(temp_prom, 1),
                "pH1": ph1, "pH2": ph2, "pH3": ph3, "pH_prom": round(ph_prom, 2),
                "humedad_%": humedad_seg, "volteo": se_volteo, "n_volteos": num_volteos_dia,
                "eval_temp": eval_temp, "eval_ph": eval_ph, "eval_humedad": eval_hum,
            }])

            if lote_seg in st.session_state["seguimiento"]:
                st.session_state["seguimiento"][lote_seg] = pd.concat(
                    [st.session_state["seguimiento"][lote_seg], nueva_fila_seg], ignore_index=True
                )
            else:
                st.session_state["seguimiento"][lote_seg] = nueva_fila_seg

            st.success(f"Seguimiento registrado para el lote {lote_seg}.")

            st.subheader("2. Resultado de este registro")
            r1, r2, r3 = st.columns(3)
            r1.metric("Temperatura promedio", f"{temp_prom:.1f} °C", eval_temp)
            r2.metric("pH promedio", f"{ph_prom:.2f}", eval_ph)
            r3.metric("Humedad", f"{humedad_seg:.0f} %", eval_hum)

            st.subheader("Recomendaciones")
            if eval_temp == "normal":
                st.success(f"Temperatura dentro del rango esperado para {fase_seg} ({ref_fase['temp'][0]}-{ref_fase['temp'][1]} °C).")
            elif eval_temp == "bajo":
                st.warning(
                    f"Temperatura baja para {fase_seg} (esperado {ref_fase['temp'][0]}-{ref_fase['temp'][1]} °C). "
                    "Puede indicar falta de oxígeno, humedad insuficiente, o que la pila perdió calor; considera voltear."
                )
            else:
                st.warning(
                    f"Temperatura alta para {fase_seg} (esperado {ref_fase['temp'][0]}-{ref_fase['temp'][1]} °C). "
                    "Verifica que no falte oxigenación; un volteo ayuda a liberar calor excesivo."
                )

            if eval_ph == "normal":
                st.success(f"pH dentro del rango esperado ({ref_fase['ph'][0]}-{ref_fase['ph'][1]}).")
            elif eval_ph == "bajo":
                st.warning(f"pH bajo (esperado {ref_fase['ph'][0]}-{ref_fase['ph'][1]}). Puede indicar exceso de material fácilmente fermentable o falta de aireación.")
            else:
                st.warning(f"pH alto (esperado {ref_fase['ph'][0]}-{ref_fase['ph'][1]}). Revisa si hay exceso de material nitrogenado (lodo).")

            if eval_hum == "normal":
                st.success(f"Humedad dentro del rango esperado ({ref_fase['humedad'][0]}-{ref_fase['humedad'][1]}%).")
            elif eval_hum == "bajo":
                st.warning(f"Humedad baja (esperado {ref_fase['humedad'][0]}-{ref_fase['humedad'][1]}%). Considera regar la pila.")
            else:
                st.warning(f"Humedad alta (esperado {ref_fase['humedad'][0]}-{ref_fase['humedad'][1]}%). Considera voltear y agregar estructurante seco.")

        if lote_seg in st.session_state["seguimiento"]:
            df_seg = st.session_state["seguimiento"][lote_seg]

            st.subheader("3. Duración por fase (según lo registrado)")
            resumen_fases = (
                df_seg.groupby("fase")["fecha"]
                .agg(["min", "max", "count"])
                .rename(columns={"min": "primer registro", "max": "último registro", "count": "N° mediciones"})
            )
            resumen_fases["días (rango de fechas)"] = (
                pd.to_datetime(resumen_fases["último registro"]) - pd.to_datetime(resumen_fases["primer registro"])
            ).dt.days + 1
            resumen_fases["días (según N° de mediciones)"] = resumen_fases["N° mediciones"]
            st.dataframe(resumen_fases, use_container_width=True)
            st.caption(
                "\"Días (rango de fechas)\" usa la diferencia entre el primer y el último registro de la fase. "
                "\"Días (según N° de mediciones)\" asume una medición por día."
            )
            st.bar_chart(resumen_fases["días (según N° de mediciones)"])
            dias_totales = (pd.to_datetime(df_seg["fecha"].max()) - pd.to_datetime(df_seg["fecha"].min())).days + 1
            st.caption(f"Días totales de proceso registrados para este lote: **{dias_totales}**")

            st.subheader("4. Evolución en el tiempo")
            df_chart = df_seg.copy()
            df_chart["fecha"] = pd.to_datetime(df_chart["fecha"])
            df_chart = df_chart.set_index("fecha").sort_index()

            cg1, cg2, cg3 = st.columns(3)
            with cg1:
                st.caption("Temperatura promedio (°C)")
                st.line_chart(df_chart["T_prom"])
            with cg2:
                st.caption("pH promedio")
                st.line_chart(df_chart["pH_prom"])
            with cg3:
                st.caption("Humedad (%)")
                st.line_chart(df_chart["humedad_%"])

            st.subheader("5. Registro completo del lote")
            st.dataframe(df_seg, use_container_width=True)
            total_volteos = int(df_seg["n_volteos"].sum()) if "n_volteos" in df_seg.columns else (
                int(df_seg["volteo"].sum()) if "volteo" in df_seg.columns else 0
            )
            st.caption(f"Volteos registrados en total para este lote: **{total_volteos}**")

            csv_seg = df_seg.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Descargar seguimiento de este lote (CSV)",
                data=csv_seg, file_name=f"{lote_seg}_seguimiento.csv", mime="text/csv",
            )
        else:
            st.info("Aún no hay registros de seguimiento para este lote.")

# =================================================================
# MÓDULO 4 — STOCK DE COMPOST
# =================================================================
with tab_m4:
    encabezado("Módulo 4 — Stock de Compost")
    st.caption(
        "Registra los ingresos y salidas de compost terminado por lote (donación, vegetación u otro destino), "
        "y consulta cuánto stock disponible queda en cada uno."
    )

    if not st.session_state.lotes:
        st.info("Aún no hay lotes registrados. El stock se irá llenando a medida que uses el Módulo 1.")
    else:
        st.subheader("1. Lotes culminados y proceso de zarandeo")
        st.caption("Cuando un lote termina maduración, márcalo aquí para iniciar el zarandeo antes de pasar a stock.")

        lotes_sin_zarandeo = [l for l in st.session_state.lotes if l not in st.session_state["zarandeo"]]
        if lotes_sin_zarandeo:
            col_z1, col_z2 = st.columns([3, 1])
            with col_z1:
                lote_culminar = st.selectbox("Lote culminado", lotes_sin_zarandeo, key="m4_lote_culminar")
            with col_z2:
                st.write("")
                if st.button("Iniciar zarandeo", key="m4_btn_iniciar_zarandeo"):
                    cantidad_inicial = st.session_state.lotes[lote_culminar]["masa_acumulada_ton"].iloc[-1]
                    st.session_state["zarandeo"][lote_culminar] = {
                        "estado": "en_zarandeo", "fecha_inicio": date.today(),
                        "cantidad_inicial_ton": cantidad_inicial,
                        "fecha_fin": None, "cantidad_final_ton": None, "ficha_pesaje": None,
                    }
                    st.rerun()

        lotes_en_zarandeo = [l for l, d in st.session_state["zarandeo"].items() if d["estado"] == "en_zarandeo"]
        if lotes_en_zarandeo:
            st.markdown("*Lotes actualmente en zarandeo:*")
            for lote_z in lotes_en_zarandeo:
                datos_z = st.session_state["zarandeo"][lote_z]
                dias_zarandeo = (date.today() - datos_z["fecha_inicio"]).days
                st.write(f"{lote_z} — inició zarandeo el {datos_z['fecha_inicio']} ({dias_zarandeo} días en proceso), cantidad ingresada al zarandeo: {datos_z['cantidad_inicial_ton']:.2f} t")

                col_zf1, col_zf2, col_zf3 = st.columns(3)
                with col_zf1:
                    cantidad_final = st.number_input(f"Cantidad tamizada final (t) — {lote_z}", min_value=0.0, step=0.05, format="%.2f", key=f"m4_cant_final_{lote_z}")
                with col_zf2:
                    ficha_zarandeo = st.text_input(f"N° ficha de pesaje — {lote_z}", key=f"m4_ficha_z_{lote_z}")
                with col_zf3:
                    st.write("")
                    if st.button(f"Registrar zarandeo terminado", key=f"m4_btn_fin_{lote_z}"):
                        if cantidad_final == 0 or not ficha_zarandeo:
                            st.error("Completa la cantidad final y el N° de ficha de pesaje.")
                        else:
                            datos_z["estado"] = "terminado"
                            datos_z["fecha_fin"] = date.today()
                            datos_z["cantidad_final_ton"] = cantidad_final
                            datos_z["ficha_pesaje"] = ficha_zarandeo
                            st.success(f"Zarandeo del lote {lote_z} registrado: {cantidad_final:.2f} t ({cantidad_final*1000:.0f} kg).")
                            st.rerun()

        lotes_terminados_z = {l: d for l, d in st.session_state["zarandeo"].items() if d["estado"] == "terminado"}
        if lotes_terminados_z:
            with st.expander("Ver lotes con zarandeo terminado"):
                df_zarandeo_terminado = pd.DataFrame([
                    {"Lote": l, "Cantidad inicial (t)": d["cantidad_inicial_ton"], "Cantidad final (t)": d["cantidad_final_ton"],
                     "Cantidad final (kg)": d["cantidad_final_ton"] * 1000, "Días de zarandeo": (d["fecha_fin"] - d["fecha_inicio"]).days,
                     "Ficha de pesaje": d["ficha_pesaje"]}
                    for l, d in lotes_terminados_z.items()
                ])
                st.dataframe(df_zarandeo_terminado, use_container_width=True, hide_index=True)

        st.subheader("2. Registrar salida de compost")

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            lote_salida = st.selectbox("Lote", list(st.session_state.lotes.keys()), key="m4_lote_salida")
        with col_s2:
            fecha_salida = st.date_input("Fecha de salida", value=date.today(), key="m4_fecha_salida")
        with col_s3:
            destino_salida = st.selectbox("Destino", DESTINOS_COMPOST, key="m4_destino")

        col_s4, col_s5 = st.columns(2)
        with col_s4:
            cantidad_salida_ton = st.number_input("Cantidad que sale (t)", min_value=0.0, step=0.1, format="%.2f", key="m4_cantidad_salida")
        with col_s5:
            ficha_pesaje = st.text_input("N° de ficha de pesaje", key="m4_ficha_pesaje")

        if st.button("Registrar salida de compost", type="primary"):
            campos_faltantes_salida = []
            if cantidad_salida_ton == 0:
                campos_faltantes_salida.append("cantidad que sale")
            if not ficha_pesaje:
                campos_faltantes_salida.append("N° de ficha de pesaje")

            if campos_faltantes_salida:
                st.error(f"Faltan datos por completar: {', '.join(campos_faltantes_salida)}.")
                st.stop()

            nueva_salida = pd.DataFrame([{
                "fecha": fecha_salida, "destino": destino_salida,
                "cantidad_ton": cantidad_salida_ton, "ficha_pesaje": ficha_pesaje,
            }])
            if lote_salida in st.session_state["salidas_compost"]:
                st.session_state["salidas_compost"][lote_salida] = pd.concat(
                    [st.session_state["salidas_compost"][lote_salida], nueva_salida], ignore_index=True
                )
            else:
                st.session_state["salidas_compost"][lote_salida] = nueva_salida
            st.success(f"Salida registrada para el lote {lote_salida}.")

        st.subheader("3. Stock por lote (solo lotes con zarandeo terminado)")
        filas_stock = []
        for codigo_lote_ind in lotes_terminados_z:
            ingresado = lotes_terminados_z[codigo_lote_ind]["cantidad_final_ton"]
            if codigo_lote_ind in st.session_state["salidas_compost"]:
                salido = st.session_state["salidas_compost"][codigo_lote_ind]["cantidad_ton"].sum()
            else:
                salido = 0.0
            filas_stock.append({
                "Lote": codigo_lote_ind,
                "Ingresado (t)": round(ingresado, 2),
                "Salido (t)": round(salido, 2),
                "Stock disponible (t)": round(ingresado - salido, 2),
            })
        if not filas_stock:
            st.info("Aún no hay lotes con zarandeo terminado. El stock se llena una vez que un lote pasa por esa etapa.")
            df_stock = pd.DataFrame(columns=["Lote", "Ingresado (t)", "Salido (t)", "Stock disponible (t)"])
        else:
            df_stock = pd.DataFrame(filas_stock)
        st.dataframe(df_stock, use_container_width=True, hide_index=True)

        sk1, sk2, sk3 = st.columns(3)
        sk1.metric("Total ingresado (todos los lotes)", f"{df_stock['Ingresado (t)'].sum():.2f} t")
        sk2.metric("Total salido (todos los lotes)", f"{df_stock['Salido (t)'].sum():.2f} t")
        sk3.metric("Stock disponible total", f"{df_stock['Stock disponible (t)'].sum():.2f} t")

        st.subheader("3. Distribución de salidas por destino")
        todas_salidas = [df for df in st.session_state["salidas_compost"].values()]
        if todas_salidas:
            df_todas_salidas = pd.concat(todas_salidas, ignore_index=True)
            resumen_destino = df_todas_salidas.groupby("destino")["cantidad_ton"].sum()
            st.bar_chart(resumen_destino)
            st.dataframe(
                resumen_destino.reset_index().rename(columns={"destino": "Destino", "cantidad_ton": "Total (t)"}),
                use_container_width=True, hide_index=True,
            )
        else:
            st.caption("Aún no hay salidas registradas para graficar.")

        with st.expander("Ver historial completo de salidas por lote"):
            if st.session_state["salidas_compost"]:
                lote_hist_salida = st.selectbox(
                    "Selecciona un lote", list(st.session_state["salidas_compost"].keys()), key="m4_hist_salida_sel"
                )
                st.dataframe(st.session_state["salidas_compost"][lote_hist_salida], use_container_width=True, hide_index=True)
            else:
                st.caption("Aún no hay salidas registradas.")
# =================================================================
# MÓDULO 5 — ANÁLISIS DE LABORATORIO
# =================================================================
with tab_m5:
    encabezado("Módulo 5 — Análisis de Laboratorio")
    st.caption(
        "Registra el envío de muestras a laboratorio, el conteo de días de espera, y compara "
        "los resultados contra la NTP 201.207:2020 (referencia peruana disponible para compost)."
    )

    if not st.session_state.lotes:
        st.info("Aún no hay lotes registrados.")
    else:
        st.subheader("1. Enviar lote a laboratorio")
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            lote_lab = st.selectbox("Lote", list(st.session_state.lotes.keys()), key="m5_lote")
        with col_l2:
            fecha_envio_lab = st.date_input("Fecha de envío a laboratorio", value=date.today(), key="m5_fecha_envio")

        if st.button("Registrar envío a laboratorio", type="primary"):
            st.session_state["laboratorio"][lote_lab] = {
                "fecha_envio": fecha_envio_lab, "fecha_resultado": None, "resultados": None,
            }
            st.success(f"Envío registrado para el lote {lote_lab}.")
            st.rerun()

        st.subheader("2. Lotes esperando resultados")
        lotes_esperando = {l: d for l, d in st.session_state["laboratorio"].items() if d["resultados"] is None}
        if lotes_esperando:
            for l_espera, d_espera in lotes_esperando.items():
                dias_espera = (date.today() - d_espera["fecha_envio"]).days
                st.write(f"{l_espera} — enviado el {d_espera['fecha_envio']} ({dias_espera} días esperando resultados)")
        else:
            st.caption("No hay lotes esperando resultados en este momento.")

        st.subheader("3. Cargar resultados de laboratorio")
        if lotes_esperando:
            lote_resultado = st.selectbox("Lote a registrar", list(lotes_esperando.keys()), key="m5_lote_resultado")

            st.markdown("*Físico-químicos*")
            c1, c2, c3 = st.columns(3)
            r_humedad = c1.number_input("Humedad (%)", min_value=0.0, step=0.1, key="m5_r_humedad")
            r_ce = c2.number_input("Conductividad eléctrica (dS/m)", min_value=0.0, step=0.1, key="m5_r_ce")
            r_cn = c3.number_input("Relación C/N", min_value=0.0, step=0.1, key="m5_r_cn")
            c4, c5 = st.columns(2)
            r_ph = c4.number_input("pH", min_value=0.0, max_value=14.0, step=0.1, key="m5_r_ph")
            r_mo = c5.number_input("Materia orgánica (%)", min_value=0.0, step=0.1, key="m5_r_mo")

            st.markdown("*Nutrientes*")
            c6, c7, c8 = st.columns(3)
            r_n = c6.number_input("Nitrógeno (%)", min_value=0.0, step=0.01, format="%.2f", key="m5_r_n")
            r_p = c7.number_input("Fósforo (%)", min_value=0.0, step=0.01, format="%.2f", key="m5_r_p")
            r_k = c8.number_input("Potasio (%)", min_value=0.0, step=0.01, format="%.2f", key="m5_r_k")

            st.markdown("*Metales pesados (mg/kg, base seca)*")
            c9, c10, c11 = st.columns(3)
            r_as = c9.number_input("Arsénico", min_value=0.0, step=0.1, key="m5_r_as")
            r_cd = c10.number_input("Cadmio", min_value=0.0, step=0.1, key="m5_r_cd")
            r_cr = c11.number_input("Cromo", min_value=0.0, step=0.1, key="m5_r_cr")
            c12, c13 = st.columns(2)
            r_hg = c12.number_input("Mercurio", min_value=0.0, step=0.1, key="m5_r_hg")
            r_ni = c13.number_input("Níquel", min_value=0.0, step=0.1, key="m5_r_ni")
            r_pb = st.number_input("Plomo", min_value=0.0, step=0.1, key="m5_r_pb")

            st.markdown("*Microbiológicos (base seca)*")
            c14, c15, c16 = st.columns(3)
            r_colif = c14.number_input("Coliformes fecales (NMP/g)", min_value=0.0, step=1.0, key="m5_r_colif")
            r_salm = c15.number_input("Salmonella spp (NMP en 4g)", min_value=0.0, step=1.0, key="m5_r_salm")
            r_helm = c16.number_input("Huevos de helmintos viables (en 4g)", min_value=0.0, step=1.0, key="m5_r_helm")

            if st.button("Registrar resultados y comparar con la norma", type="primary"):
                resultados = {
                    "humedad": r_humedad, "conductividad": r_ce, "relacion_cn": r_cn, "ph": r_ph,
                    "materia_organica": r_mo, "nitrogeno": r_n, "fosforo": r_p, "potasio": r_k,
                    "arsenico": r_as, "cadmio": r_cd, "cromo": r_cr, "mercurio": r_hg,
                    "niquel": r_ni, "plomo": r_pb, "coliformes_fecales": r_colif,
                    "salmonella": r_salm, "huevos_helmintos": r_helm,
                }
                st.session_state["laboratorio"][lote_resultado]["resultados"] = resultados
                st.session_state["laboratorio"][lote_resultado]["fecha_resultado"] = date.today()
                st.success(f"Resultados registrados para el lote {lote_resultado}.")
                st.rerun()
        else:
            st.caption("No hay lotes pendientes de resultados.")

        st.subheader("4. Reporte de cumplimiento (NTP 201.207:2020)")
        lotes_con_resultado = {l: d for l, d in st.session_state["laboratorio"].items() if d["resultados"] is not None}
        if lotes_con_resultado:
            lote_reporte = st.selectbox("Ver reporte del lote", list(lotes_con_resultado.keys()), key="m5_lote_reporte")
            datos_reporte = lotes_con_resultado[lote_reporte]

            filas_reporte = []
            for clave, limite in LIMITES_NTP.items():
                valor = datos_reporte["resultados"][clave]
                cumple = True
                if limite["min"] is not None and valor < limite["min"]:
                    cumple = False
                if limite["max"] is not None and valor > limite["max"]:
                    cumple = False
                if limite["min"] is not None and limite["max"] is not None:
                    rango_txt = f"{limite['min']} – {limite['max']}"
                elif limite["min"] is not None:
                    rango_txt = f"≥ {limite['min']}"
                elif limite["max"] is not None:
                    rango_txt = f"≤ {limite['max']}"
                else:
                    rango_txt = "-"
                filas_reporte.append({
                    "Parámetro": limite["nombre"], "Resultado": valor,
                    "Rango NTP 201.207:2020": rango_txt, "Estado": "Cumple" if cumple else "No cumple",
                })

            df_reporte = pd.DataFrame(filas_reporte)

            filas_html = ""
            for _, fila in df_reporte.iterrows():
                if fila["Estado"] == "Cumple":
                    bg_estado, color_estado = "#E8F5E9", COLOR_VERDE
                else:
                    bg_estado, color_estado = "#FDECEA", COLOR_ROJO
                filas_html += (
                    "<tr>"
                    f"<td style='padding:8px 12px; border-bottom:1px solid {COLOR_BORDE};'>{fila['Parámetro']}</td>"
                    f"<td style='padding:8px 12px; border-bottom:1px solid {COLOR_BORDE};'>{fila['Resultado']}</td>"
                    f"<td style='padding:8px 12px; border-bottom:1px solid {COLOR_BORDE};'>{fila['Rango NTP 201.207:2020']}</td>"
                    f"<td style='padding:8px 12px; border-bottom:1px solid {COLOR_BORDE}; background-color:{bg_estado}; color:{color_estado}; font-weight:600;'>{fila['Estado']}</td>"
                    "</tr>"
                )
            tabla_html = (
                "<table style='width:100%; border-collapse:collapse; font-size:14px;'>"
                f"<thead><tr style='background-color:{COLOR_AZUL};'>"
                "<th style='padding:8px 12px; text-align:left; color:white;'>Parámetro</th>"
                "<th style='padding:8px 12px; text-align:left; color:white;'>Resultado</th>"
                "<th style='padding:8px 12px; text-align:left; color:white;'>Rango NTP 201.207:2020</th>"
                "<th style='padding:8px 12px; text-align:left; color:white;'>Estado</th>"
                "</tr></thead>"
                f"<tbody>{filas_html}</tbody>"
                "</table>"
            )
            st.markdown(tabla_html, unsafe_allow_html=True)

            n_no_cumple = (df_reporte["Estado"] == "No cumple").sum()
            if n_no_cumple == 0:
                st.success(f"El lote {lote_reporte} cumple con todos los parámetros evaluados de la NTP 201.207:2020.")
            else:
                st.warning(f"El lote {lote_reporte} tiene {n_no_cumple} parámetro(s) fuera del rango de la NTP 201.207:2020.")

            dias_espera_total = (datos_reporte["fecha_resultado"] - datos_reporte["fecha_envio"]).days
            st.caption(f"Enviado a laboratorio: {datos_reporte['fecha_envio']} · Resultado recibido: {datos_reporte['fecha_resultado']} ({dias_espera_total} días de espera)")

            csv_reporte = df_reporte.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Descargar reporte (CSV)", data=csv_reporte,
                file_name=f"reporte_laboratorio_{lote_reporte}.csv", mime="text/csv",
            )
        else:
            st.caption("Aún no hay resultados de laboratorio registrados.")
