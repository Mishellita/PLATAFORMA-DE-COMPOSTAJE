"""
Plataforma de Gestión de Compostaje - Planta Minera
=====================================================
MÓDULO 1: Formulación de lotes

Cómo funciona este archivo (guía rápida para quien no programa):
- Streamlit lee este archivo de arriba a abajo cada vez que alguien
  interactúa con la app (por ejemplo, al apretar un botón).
- "st.session_state" es la "memoria" de la app mientras está abierta:
  ahí guardamos los lotes y su historial para que no se borren
  cada vez que se actualiza la pantalla.
- Los datos de insumos (humedad, carbono, nitrógeno) están en el
  diccionario INSUMOS_REF más abajo. Esos son los valores que nos
  diste; se pueden editar directamente desde ahí, o más adelante
  los conectamos a un módulo de caracterización editable.
"""

import streamlit as st
import pandas as pd
from datetime import date

# ---------------------------------------------------------------
# 1. CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Gestión de Compostaje",
    layout="wide",
)

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

# Rango recomendado por literatura para iniciar la etapa mesófila.
# OJO: esto queda como parámetro editable (no fijo), tal como se
# conversó, porque la altitud (3000 msnm) puede requerir un ajuste
# que todavía se está validando en campo.
HUMEDAD_MIN_DEFAULT = 50.0
HUMEDAD_MAX_DEFAULT = 60.0
CN_MIN_DEFAULT = 25.0
CN_MAX_DEFAULT = 35.0

# Lista de operadores para el selector (edítala aquí con los nombres reales
# de tu equipo; "Otro" siempre queda disponible por si falta alguien).
OPERADORES = ["Operador 1", "Operador 2", "Operador 3", "Otro"]

# Prefijo para los códigos de lote autogenerados, ej: CMP-2026-001
PREFIJO_LOTE = "CMP"

# ---------------------------------------------------------------
# 3. "MEMORIA" DE LA APP (mientras está abierta en el navegador)
#    - lotes: diccionario {codigo_lote: DataFrame con el historial}
# ---------------------------------------------------------------
if "lotes" not in st.session_state:
    st.session_state.lotes = {}

# ---------------------------------------------------------------
# 4. FUNCIONES DE CÁLCULO
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
        masa_seca = kg * (1 - ref["humedad"] / 100)  # materia seca del insumo
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
    """Devuelve una lista de mensajes (texto, tipo) donde tipo es
    'success', 'warning' o 'error', para pintar en la app."""
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


# ---------------------------------------------------------------
# 5. INTERFAZ - BARRA LATERAL: parámetros ajustables
# ---------------------------------------------------------------
st.sidebar.header("⚙️ Parámetros de referencia")
st.sidebar.caption("Ajustables por observación de campo (ej. altitud 3000 msnm)")

hum_min = st.sidebar.number_input("Humedad mínima (%)", value=HUMEDAD_MIN_DEFAULT, step=1.0)
hum_max = st.sidebar.number_input("Humedad máxima (%)", value=HUMEDAD_MAX_DEFAULT, step=1.0)
cn_min = st.sidebar.number_input("Relación C/N mínima", value=CN_MIN_DEFAULT, step=1.0)
cn_max = st.sidebar.number_input("Relación C/N máxima", value=CN_MAX_DEFAULT, step=1.0)

st.sidebar.divider()
st.sidebar.caption(
    "Rango base de literatura: 50-60% humedad para iniciar etapa mesófila. "
    "El ajuste aquí queda registrado como adaptación en observación, no como error."
)

# ---------------------------------------------------------------
# 6. INTERFAZ PRINCIPAL
# ---------------------------------------------------------------
st.markdown(
    """
    <div style="background-color:#031795; padding:14px 18px; border-radius:8px; margin-bottom:10px;">
        <span style="color:white; font-size:26px; font-weight:700;"> Módulo 1 — Formulación de Lotes</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Registro de ingresos de residuos por lote, con cálculo automático de humedad y relación C/N")

tab_nuevo, tab_historial = st.tabs(["➕ Nuevo ingreso a un lote", "📋 Historial de lotes"])

# ---- PESTAÑA: NUEVO INGRESO -------------------------------------------------
with tab_nuevo:
    col1, col2, col3 = st.columns(3)

    with col1:
        operador_sel = st.selectbox("Operador", OPERADORES)
        if operador_sel == "Otro":
            operador = st.text_input("Nombre del operador (nuevo)")
        else:
            operador = operador_sel

    with col2:
        fecha_ingreso = st.date_input("Fecha", value=date.today())

    with col3:
        # El operador solo escribe el NÚMERO de lote (1, 2, 3, 15...);
        # el código completo (CMP-2026-00X) se arma solo, para evitar
        # errores de tipeo y mantener el formato siempre igual.
        nums_existentes = [
            int(c.split("-")[-1]) for c in st.session_state.lotes.keys()
            if c.startswith(PREFIJO_LOTE) and c.split("-")[-1].isdigit()
        ]
        siguiente_num = max(nums_existentes) + 1 if nums_existentes else 1

        numero_lote = st.number_input("Número de lote", min_value=1, step=1, value=siguiente_num)
        codigo_lote = f"{PREFIJO_LOTE}-{fecha_ingreso.year}-{int(numero_lote):03d}"

        if codigo_lote in st.session_state.lotes:
            st.caption(f"Código: *{codigo_lote}* (lote existente, se agregará este ingreso a su historial)")
        else:
            st.caption(f"Código: *{codigo_lote}* (lote nuevo)")

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

    # Vista previa de la proporción de la mezcla que se está armando,
    # ANTES de presionar el botón, para que el operador vea de una vez
    # si se está acercando o no a la proporción 60/20/20 declarada.
    total_ton_preview = sum(cantidades_ton.values())
    if total_ton_preview > 0:
        st.caption("Proporción de esta mezcla (según lo ingresado arriba):")
        prop_cols = st.columns(len(INSUMOS_REF))
        for col, (codigo, ref) in zip(prop_cols, INSUMOS_REF.items()):
            pct = (cantidades_ton[codigo] / total_ton_preview) * 100 if cantidades_ton[codigo] > 0 else 0
            col.caption(f"{ref['nombre']}: *{pct:.0f}%*")

    if st.button("Calcular y registrar ingreso", type="primary"):
        if not operador:
            st.error("Ingresa el nombre del operador.")
        elif sum(cantidades_ton.values()) == 0:
            st.error(
                "No se registró ninguna cantidad. Ingresa al menos un valor mayor a 0 "
                "en algún insumo y confirma que el número quedó escrito en el recuadro "
                "antes de presionar el botón (a veces en el celular hay que tocar fuera "
                "del recuadro para que el número quede guardado)."
            )
        else:
            # Convertimos a kg solo para el cálculo interno (las fórmulas
            # y las densidades de referencia están pensadas en kg).
            cantidades = {codigo: ton * 1000 for codigo, ton in cantidades_ton.items()}
            masa, humedad_pct, c_total, n_total, cn = calcular_mezcla(cantidades)

            # Traemos el historial previo del lote (si existe) para
            # acumular con lo ya ingresado antes, tal como se conversó:
            # cada lote lleva su propia línea de tiempo.
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
                # guardamos también en kg internamente, útil si más adelante
                # se conecta con laboratorio o reportes que pidan kg
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

# ---- PESTAÑA: HISTORIAL -----------------------------------------------------
with tab_historial:
    if not st.session_state.lotes:
        st.info("Aún no hay lotes registrados. Ve a la pestaña 'Nuevo ingreso' para comenzar.")
    else:
        lote_seleccionado = st.selectbox("Selecciona un lote", list(st.session_state.lotes.keys()))
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
            "Este historial no se sobrescribe: cada botón 'Calcular y registrar ingreso' "
            "agrega una fila nueva, para poder mostrar la evolución completa del lote desde el día 1."
        )
