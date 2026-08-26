"""
Plataforma de Gestión de Compostaje - Planta Minera
=====================================================
MÓDULO 1: Formulación de lotes
MÓDULO 2: Capacidad de material estructurante (aserrín / cartón)

Cómo funciona este archivo (guía rápida para quien no programa):
- Streamlit lee este archivo de arriba a abajo cada vez que alguien
  interactúa con la app (por ejemplo, al apretar un botón).
- "st.session_state" es la "memoria" de la app mientras está abierta:
  ahí guardamos los lotes y su historial para que no se borren
  cada vez que se actualiza la pantalla. OJO: esto se pierde si la
  app se reinicia o "duerme" (ver aviso en el pie de página) — eso
  se resuelve más adelante conectando a una hoja de cálculo en línea.
- Los datos de insumos (humedad, carbono, nitrógeno) están en el
  diccionario INSUMOS_REF más abajo.
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

COLOR_ROJO = "#FE0000"          # Botones principales
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


# ===============================================================
# ESTILO GLOBAL DE LA APLICACIÓN
# ===============================================================

st.markdown(
    f"""
    <style>

    /* ==========================================================
       FONDO GENERAL
       ========================================================== */

    .stApp {{
        background-color: {COLOR_BLANCO};
    }}


    /* ==========================================================
       NAVEGACIÓN ENTRE MÓDULOS

       Módulo 1
       Módulo 2
       Módulo 3

       Se mantienen blancos.
       ========================================================== */

    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background-color: {COLOR_BLANCO};
        border-bottom: 1px solid {COLOR_BORDE};
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: {COLOR_BLANCO} !important;
        color: #444444 !important;
        border: none !important;
        border-radius: 6px 6px 0 0;
        padding: 10px 16px;
        font-weight: 500;
    }}

    .stTabs [data-baseweb="tab"]:hover {{
        background-color: #F7F8FA !important;
        color: #111111 !important;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {COLOR_BLANCO} !important;
        color: #111111 !important;
        font-weight: 700 !important;
        border-bottom: 3px solid {COLOR_AZUL} !important;
    }}


    /* ==========================================================
       ELIMINAR FONDOS COLOREADOS EN PESTAÑAS INTERNAS

       Ejemplo:
       Nuevo ingreso a un lote
       Historial de lotes
       ========================================================== */

    button[data-baseweb="tab"] {{
        background-color: {COLOR_BLANCO} !important;
    }}


    /* ==========================================================
       BOTONES PRINCIPALES

       Calcular
       Registrar
       Generar reporte
       ========================================================== */

    .stButton > button[kind="primary"] {{
        background-color: {COLOR_ROJO} !important;
        color: white !important;
        border: 1px solid {COLOR_ROJO} !important;

        border-radius: 8px;

        font-weight: 600;

        min-height: 42px;

        transition:
            background-color 0.15s ease,
            border-color 0.15s ease,
            transform 0.05s ease;
    }}

    .stButton > button[kind="primary"]:hover {{
        background-color: {COLOR_ROJO_HOVER} !important;
        border-color: {COLOR_ROJO_HOVER} !important;
        color: white !important;
    }}

    .stButton > button[kind="primary"]:active {{
        transform: translateY(1px);
    }}


    /* ==========================================================
       BOTONES SECUNDARIOS

       Sin color especial.
       ========================================================== */

    .stButton > button[kind="secondary"] {{
        background-color: {COLOR_BLANCO} !important;
        color: #333333 !important;

        border: 1px solid #CDD1D6 !important;

        border-radius: 8px;

        font-weight: 500;
    }}

    .stButton > button[kind="secondary"]:hover {{
        background-color: #F7F8FA !important;
        color: #111111 !important;
        border-color: #AEB4BC !important;
    }}


    /* ==========================================================
       BOTONES DE DESCARGA
       ========================================================== */

    .stDownloadButton > button {{
        background-color: {COLOR_BLANCO} !important;

        color: {COLOR_AZUL} !important;

        border: 1px solid {COLOR_AZUL} !important;

        border-radius: 8px;

        font-weight: 600;
    }}

    .stDownloadButton > button:hover {{
        background-color: #F3F6FF !important;

        color: {COLOR_AZUL} !important;

        border-color: {COLOR_AZUL} !important;
    }}


    /* ==========================================================
       TARJETAS DE MÉTRICAS
       ========================================================== */

    div[data-testid="stMetric"] {{
        background-color: {COLOR_FONDO_SUAVE};

        border: 1px solid {COLOR_BORDE};

        border-radius: 10px;

        padding: 14px 16px;
    }}


    /* Nombre de la métrica */
    div[data-testid="stMetricLabel"] {{
        color: #555555;
        font-weight: 500;
    }}


    /* Valor principal */
    div[data-testid="stMetricValue"] {{
        color: {COLOR_TEXTO};
        font-weight: 600;
    }}


    /* ==========================================================
       INPUTS
       ========================================================== */

    div[data-baseweb="input"] {{
        border-radius: 8px;
    }}

    div[data-baseweb="select"] > div {{
        border-radius: 8px;
    }}

    textarea {{
        border-radius: 8px !important;
    }}


    /* ==========================================================
       DATAFRAMES
       ========================================================== */

    div[data-testid="stDataFrame"] {{
        border: 1px solid {COLOR_BORDE};
        border-radius: 9px;
        overflow: hidden;
    }}


    /* ==========================================================
       EXPANDERS
       ========================================================== */

    div[data-testid="stExpander"] {{
        border: 1px solid {COLOR_BORDE};
        border-radius: 9px;
        background-color: {COLOR_BLANCO};
    }}


    /* ==========================================================
       SUBHEADERS NORMALES DE STREAMLIT
       ========================================================== */

    h1 {{
        color: {COLOR_TEXTO};
    }}

    h2 {{
        color: {COLOR_TEXTO};
    }}

    h3 {{
        color: {COLOR_TEXTO};
    }}


    /* ==========================================================
       TEXTOS SECUNDARIOS
       ========================================================== */

    .stCaption {{
        color: {COLOR_TEXTO_SECUNDARIO};
    }}


    /* ==========================================================
       DIVISORES
       ========================================================== */

    hr {{
        border-color: #ECEDEF !important;
    }}


    /* ==========================================================
       ALERTAS

       Streamlit mantiene sus colores semánticos:
       verde = correcto
       amarillo = advertencia
       rojo = error
       azul = información
       ========================================================== */

    div[data-testid="stAlert"] {{
        border-radius: 9px;
    }}


    /* ==========================================================
       AJUSTE PARA PANTALLAS PEQUEÑAS
       ========================================================== */

    @media (max-width: 768px) {{

        .stTabs [data-baseweb="tab"] {{
            padding: 8px 10px;
            font-size: 13px;
        }}

        div[data-testid="stMetric"] {{
            padding: 10px 12px;
        }}

    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# ===============================================================
# ENCABEZADO PRINCIPAL DE SAFCO
# ===============================================================

def mostrar_encabezado_app():

    # -----------------------------------------------------------
    # Buscar logo
    #
    # Si en GitHub lo guardaste como logo.png, lo encuentra.
    # También revisa formatos habituales por seguridad.
    # -----------------------------------------------------------

    candidatos_logo = [
        "logo.png",
        "logo.jpg",
        "logo.jpeg",
        "logo.webp",
        "logo"
    ]

    ruta_logo = None

    for archivo_logo in candidatos_logo:

        if os.path.exists(archivo_logo):

            ruta_logo = archivo_logo
            break


    # -----------------------------------------------------------
    # Distribución encabezado
    # -----------------------------------------------------------

    col_logo, col_texto = st.columns(
        [2.3, 7.7],
        vertical_alignment="center"
    )


    # -----------------------------------------------------------
    # LOGO
    # -----------------------------------------------------------

    with col_logo:

        if ruta_logo:

            st.image(
                ruta_logo,
                width=230
            )

        else:

            # Reserva visual si el archivo no está disponible

            st.markdown(
                f"""
                <div style="
                    width:58px;
                    height:58px;

                    border-radius:50%;

                    background:{COLOR_AZUL};

                    display:flex;
                    align-items:center;
                    justify-content:center;

                    border:3px solid {COLOR_ROJO};
                ">

                    <span style="
                        color:white;
                        font-size:14px;
                        font-weight:700;
                    ">
                        AA
                    </span>

                </div>
                """,
                unsafe_allow_html=True,
            )


    # -----------------------------------------------------------
    # TÍTULO
    # -----------------------------------------------------------

    with col_texto:

        st.markdown(
            f"""
            <div style="
                padding-top:4px;
                padding-bottom:4px;
            ">

                <div style="
                    color:{COLOR_AZUL};

                    font-size:27px;
                    font-weight:700;

                    line-height:1.15;

                    margin:0;
                ">
                    Plataforma de Gestión de Compostaje
                </div>


                <div style="
                    color:{COLOR_TEXTO_SECUNDARIO};

                    font-size:14px;
                    font-weight:400;

                    margin-top:6px;
                ">
                    SAFCO · Planta de compostaje
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    st.divider()

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
# "MEMORIA" del Módulo 3 (mientras la app está abierta)
# ---------------------------------------------------------------
if "seguimiento" not in st.session_state:
    st.session_state["seguimiento"] = {}

# Lista de operadores para el selector.
OPERADORES = ["Adrián Carpio", "Fernando Valdivia", "Michelle Rubiz", "Otro"]

# Prefijo para los códigos de lote autogenerados, ej: CMP-2026-001
PREFIJO_LOTE = "CMP"

# ---------------------------------------------------------------
# 3. "MEMORIA" DE LA APP (mientras está abierta en el navegador)
# ---------------------------------------------------------------
if "lotes" not in st.session_state:
    st.session_state.lotes = {}
if "consultas_aserrin" not in st.session_state:
    st.session_state["consultas_aserrin"] = []

# ---------------------------------------------------------------
# 4. FUNCIONES DE CÁLCULO (compartidas entre módulos)
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

    Despeje matemático a partir de:
        cn_target = (C_fijo + x * c_insumo) / (N_fijo + x * n_insumo)
    donde x son los kg del estructurante a agregar, y c_insumo/n_insumo
    son el carbono y nitrógeno (en base seca) por kg de ese insumo.
    Resolviendo para x:
        x = (cn_target * N_fijo - C_fijo) / (c_insumo - cn_target * n_insumo)
    Si x resulta negativo, significa que la mezcla ya está en o por
    encima del C/N objetivo y no hace falta agregar nada (se devuelve 0).
    """
    ref = INSUMOS_REF[codigo_estructurante]
    fraccion_seca = 1 - ref["humedad"] / 100
    c_insumo = fraccion_seca * (ref["carbono"] / 100)   # kg carbono por kg insumo
    n_insumo = fraccion_seca * (ref["nitrogeno"] / 100)  # kg nitrógeno por kg insumo

    denominador = c_insumo - (cn_target * n_insumo)
    if denominador == 0:
        return 0.0

    x_kg = (cn_target * fixed_nitrogeno_kg - fixed_carbono_kg) / denominador
    return max(0.0, x_kg)


# ---------------------------------------------------------------
# 5. BARRA LATERAL: parámetros ajustables (aplican a ambos módulos)
# ---------------------------------------------------------------
st.sidebar.header("⚙️ Parámetros de referencia")
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
st.sidebar.warning(
    "⚠️ Prototipo: los datos ingresados viven solo en esta sesión del "
    "navegador. Si se recarga la página o la app se reinicia, se pierden. "
    "El guardado permanente (Google Sheets) queda pendiente como siguiente fase."
)


def encabezado(texto):
    st.markdown(
        f"""
        <div style="background-color:{COLOR_AZUL}; padding:14px 18px; border-radius:8px; margin-bottom:10px;">
            <span style="color:white; font-size:26px; font-weight:700;">{texto}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------
# 6. NAVEGACIÓN ENTRE MÓDULOS
# ---------------------------------------------------------------
mostrar_encabezado_app()

tab_m1, tab_m2, tab_m3 = st.tabs([
    "Módulo 1 — Formulación de Lotes",
    "Módulo 2 — Capacidad de Estructurante",
    "Módulo 3 — Seguimiento de Pilas",
])

# =================================================================
# MÓDULO 1 — FORMULACIÓN DE LOTES
# =================================================================
with tab_m1:
    encabezado("Módulo 1 — Formulación de Lotes")
    st.caption("Registro de ingresos de residuos por lote, con cálculo automático de humedad y relación C/N")

    tab_nuevo, tab_historial = st.tabs(["➕ Nuevo ingreso a un lote", "📋 Historial de lotes"])

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
            else:
                cantidades = {codigo: ton * 1000 for codigo, ton in cantidades_ton.items()}
                masa, humedad_pct, c_total, n_total, cn = calcular_mezcla(cantidades)

                if codigo_lote in st.session_state.lotes:
                    hist_previo = st.session_state.lotes[codigo_lote]
                    carbono_acum = hist_previo["carbono_total_kg"].sum() + c_total
                    nitrogeno_acum = hist_previo["nitrogeno_total_kg"].sum() + n_total
                    masa_acum_ton_previa = hist_previo["masa_total_ton"].sum()
                    masa_acum = (masa_acum_ton_previa * 1000) + masa
                    humedad_prev_ponderada = (hist_previo["humedad_%"] * hist_previo["masa_total_ton"] * 1000).sum()
                    humedad_acum_pct = (humedad_prev_ponderada + humedad_pct * masa) / masa_acum if masa_acum else 0
                    cn_acum = carbono_acum / nitrogeno_acum if nitrogeno_acum else 0
                else:
                    carbono_acum, nitrogeno_acum, masa_acum = c_total, n_total, masa
                    humedad_acum_pct, cn_acum = humedad_pct, cn

                nueva_fila = pd.DataFrame([{
                    "fecha": fecha_ingreso,
                    "operador": operador,
                    **{f"{c}_ton": round(cantidades_ton[c], 2) for c in INSUMOS_REF},
                    **{f"{c}_%mezcla": round((cantidades_ton[c] / total_ton_preview) * 100, 1) if total_ton_preview else 0 for c in INSUMOS_REF},
                    "masa_total_ton": round(masa / 1000, 2),
                    "humedad_%": round(humedad_pct, 1),
                    "relacion_cn": round(cn, 1) if cn != float("inf") else None,
                    "masa_acumulada_ton": round(masa_acum / 1000, 2),
                    "humedad_acumulada_%": round(humedad_acum_pct, 1),
                    "cn_acumulado": round(cn_acum, 1),
                    "carbono_total_kg": round(c_total, 2),
                    "nitrogeno_total_kg": round(n_total, 2),
                }])

                if codigo_lote in st.session_state.lotes:
                    st.session_state.lotes[codigo_lote] = pd.concat(
                        [st.session_state.lotes[codigo_lote], nueva_fila], ignore_index=True
                    )
                else:
                    st.session_state.lotes[codigo_lote] = nueva_fila

                st.success(f"Ingreso registrado en el lote {codigo_lote}.")

                st.subheader("Resultado de este ingreso")
                m1, m2, m3 = st.columns(3)
                m1.metric("Masa ingresada", f"{masa / 1000:.2f} t")
                m2.metric("Humedad", f"{humedad_pct:.1f} %")
                m3.metric("Relación C/N", f"{cn:.1f} : 1")

                with st.expander("🔍 Ver balance de masa de este ingreso"):
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
                "⬇️ Descargar historial de este lote (CSV)",
                data=csv,
                file_name=f"{lote_seleccionado}_historial.csv",
                mime="text/csv",
            )
            st.caption(
                "Este historial no se sobrescribe: cada ingreso agrega una fila nueva, "
                "para mostrar la evolución completa del lote desde el día 1."
            )

# =================================================================
# MÓDULO 2 — CAPACIDAD DE MATERIAL ESTRUCTURANTE
# =================================================================
with tab_m2:
    encabezado("Módulo 2 — Capacidad de Material Estructurante")
    st.caption("Planifica cuánto aserrín o cartón adicional necesitas para una cantidad de lodo a procesar")

    with st.expander("ℹ️ ¿Qué hace este módulo? (léelo antes de calcular)"):
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

    # ---- Entradas -------------------------------------------------
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

        # --- Referencia histórica 60/20/20 (solo informativa) -------
        # OJO: se ancla en el LODO, porque es la cantidad que se está
        # planificando procesar (el "cuello de botella" real de la
        # planta); RO y CA de referencia se calculan a partir de él.
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
                    st.write(f"🟢 RO: **{diferencia_ro:.2f} t por encima** de la referencia ({ro_hist:.2f} t). No implica que deba retirarse.")
                else:
                    st.write(f"🟡 RO: **{abs(diferencia_ro):.2f} t por debajo** de la referencia ({ro_hist:.2f} t).")
            with dc2:
                if diferencia_ca >= 0:
                    st.write(f"🟢 Cartón: **{diferencia_ca:.2f} t por encima** de la referencia ({ca_hist:.2f} t).")
                else:
                    st.write(f"🟡 Cartón: **{abs(diferencia_ca):.2f} t por debajo** de la referencia ({ca_hist:.2f} t). Esto es lo que se busca cerrar en la Alternativa C.")

        # --- Alternativas --------------------------------------------
        st.subheader("3. Alternativas de material estructurante")

        # Alternativa A: solo aserrín
        as_solo_ton = kg_requeridos_estructurante(mezcla_base["carbono_kg"], mezcla_base["nitrogeno_kg"], "AS", cn_target) / 1000
        mezcla_a = mezcla_ton({**insumos_planificados, "AS": as_solo_ton})

        # Alternativa B: solo cartón adicional
        ca_adicional_ton = kg_requeridos_estructurante(mezcla_base["carbono_kg"], mezcla_base["nitrogeno_kg"], "CA", cn_target) / 1000
        mezcla_b = mezcla_ton({**insumos_planificados, "CA": ca_ton + ca_adicional_ton})

        # Alternativa C: primero cierra la brecha de cartón hasta la referencia histórica,
        # y con lo que falte para el C/N objetivo, completa con aserrín.
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

        # --- Tabla comparativa técnica ---------------------------------
        st.subheader("4. Comparación técnica de escenarios")

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
                "Masa total (t)": round(total_base_ton, 2),
                "Humedad (%)": None, "Relación C/N": None,
            },
        ])

        st.dataframe(tabla_comparativa, use_container_width=True, hide_index=True)
        st.caption(
            f"Cálculo hecho para una relación C/N objetivo de {cn_target:.0f}:1 "
            f"(punto medio del rango {cn_min:.0f}-{cn_max:.0f} configurado en la barra lateral)."
        )
        csv_comp = tabla_comparativa.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Descargar tabla comparativa (CSV)", data=csv_comp,
            file_name=f"comparativo_estructurante_{fecha2}.csv", mime="text/csv",
        )

        # --- Evaluación de viabilidad -----------------------------------
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
            st.success("🟢 La alternativa combinada (cartón + aserrín) mantiene humedad y C/N dentro de rango, con margen operativo.")
        elif estado_a == "VIABLE":
            st.success("🟢 La alternativa con aserrín mantiene humedad y C/N dentro de rango, con margen operativo.")
        elif estado_b == "VIABLE":
            st.success("🟢 La alternativa con cartón adicional mantiene humedad y C/N dentro de rango, con margen operativo.")
        elif estado_c in viables:
            st.warning(f"🟡 La alternativa combinada es admisible, pero su estado es: {estado_c}.")
        elif estado_a in viables:
            st.warning(f"🟡 La alternativa con aserrín es admisible, pero su estado es: {estado_a}.")
        elif estado_b in viables:
            st.warning(f"🟡 La alternativa con cartón es admisible, pero su estado es: {estado_b}.")
        else:
            st.warning("⚠️ Ninguna alternativa alcanza a la vez humedad y C/N adecuados. Revisa la combinación de materiales.")

        st.markdown("**Resumen por alternativa** (si eliges esta opción, así quedaría la mezcla):")

        def fila_resumen(nombre, mezcla, estructurante_ton_lodo, estado):
            emoji = "🟢" if estado.startswith("VIABLE") else ("🟡" if estado in ("HUMEDAD BAJA", "HUMEDAD ALTA") else "🔴")
            st.markdown(
                f"<div style='font-size:14px; padding:4px 0;'>"
                f"{emoji} <b>{nombre}</b> — C/N: {mezcla['cn']:.1f}:1 · "
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

        # --- Selección y generación de reporte -----------------------
        st.subheader("6. Elegir alternativa y generar solicitud")
        alternativa_map = {
            "Solo aserrín": (as_solo_ton, 0.0, mezcla_a),
            "Solo cartón adicional": (0.0, ca_adicional_ton, mezcla_b),
            "Cartón + aserrín": (as_combinado_ton, ca_combinado_ton, mezcla_c),
        }
        alternativa_elegida = st.radio("¿Qué alternativa vas a solicitar?", list(alternativa_map.keys()), key="m2_alt_radio")

        if st.button("📄 Generar reporte de solicitud", type="primary"):
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
                "⬇️ Descargar reporte (TXT)", data=reporte.encode("utf-8"),
                file_name=f"solicitud_estructurante_{fecha2}.txt", mime="text/plain",
            )
            st.session_state["consultas_aserrin"].append({
                "fecha": fecha2, "tipo": "solicitud_generada",
                "detalle": f"{alternativa_elegida}: aserrín {as_sol:.2f} t, cartón {ca_sol:.2f} t",
            })
    else:
        st.info("Ingresa al menos residuos orgánicos, cartón o lodo para ver las alternativas.")

    # --- Historial de consultas de este módulo ---------------------------
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
    st.caption("Registro diario de temperatura, pH y humedad por lote, con recomendaciones según la fase del proceso")

    with st.expander("📚 Fases del proceso de compostaje (referencia educativa)", expanded=False):
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

        if st.button("✅ Registrar seguimiento", type="primary"):
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
                st.success(f"🟢 Temperatura dentro del rango esperado para {fase_seg} ({ref_fase['temp'][0]}-{ref_fase['temp'][1]} °C).")
            elif eval_temp == "bajo":
                st.warning(
                    f"🟡 Temperatura baja para {fase_seg} (esperado {ref_fase['temp'][0]}-{ref_fase['temp'][1]} °C). "
                    "Puede indicar falta de oxígeno, humedad insuficiente, o que la pila perdió calor; considera voltear."
                )
            else:
                st.warning(
                    f"🟡 Temperatura alta para {fase_seg} (esperado {ref_fase['temp'][0]}-{ref_fase['temp'][1]} °C). "
                    "Verifica que no falte oxigenación; un volteo ayuda a liberar calor excesivo."
                )

            if eval_ph == "normal":
                st.success(f"🟢 pH dentro del rango esperado ({ref_fase['ph'][0]}-{ref_fase['ph'][1]}).")
            elif eval_ph == "bajo":
                st.warning(f"🟡 pH bajo (esperado {ref_fase['ph'][0]}-{ref_fase['ph'][1]}). Puede indicar exceso de material fácilmente fermentable o falta de aireación.")
            else:
                st.warning(f"🟡 pH alto (esperado {ref_fase['ph'][0]}-{ref_fase['ph'][1]}). Revisa si hay exceso de material nitrogenado (lodo).")

            if eval_hum == "normal":
                st.success(f"🟢 Humedad dentro del rango esperado ({ref_fase['humedad'][0]}-{ref_fase['humedad'][1]}%).")
            elif eval_hum == "bajo":
                st.warning(f"🟡 Humedad baja (esperado {ref_fase['humedad'][0]}-{ref_fase['humedad'][1]}%). Considera regar la pila.")
            else:
                st.warning(f"🟡 Humedad alta (esperado {ref_fase['humedad'][0]}-{ref_fase['humedad'][1]}%). Considera voltear y agregar estructurante seco.")

        # ---- Historial, duración por fase y mini-dashboard -----------
        if lote_seg in st.session_state["seguimiento"]:
            df_seg = st.session_state["seguimiento"][lote_seg]

            st.subheader("3. Duración por fase (según lo registrado)")
            resumen_fases = (
                df_seg.groupby("fase")["fecha"]
                .agg(["min", "max", "count"])
                .rename(columns={"min": "primer registro", "max": "último registro", "count": "N° mediciones"})
            )
            resumen_fases["días observados"] = (
                pd.to_datetime(resumen_fases["último registro"]) - pd.to_datetime(resumen_fases["primer registro"])
            ).dt.days + 1
            st.dataframe(resumen_fases, use_container_width=True)
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
                "⬇️ Descargar seguimiento de este lote (CSV)",
                data=csv_seg, file_name=f"{lote_seg}_seguimiento.csv", mime="text/csv",
            )
        else:
            st.info("Aún no hay registros de seguimiento para este lote.")
