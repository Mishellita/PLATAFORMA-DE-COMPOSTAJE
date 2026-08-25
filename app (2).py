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
from datetime import date

# ---------------------------------------------------------------
# 1. CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Gestión de Compostaje",
    page_icon="🌱",
    layout="wide",
)

# Colores de marca (Anglo American)
COLOR_AZUL = "#031795"
COLOR_AZUL_CLARO = "#ABCBFA"
COLOR_ROJO = "#FE0000"

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

# Lista de operadores para el selector (edítala aquí con los nombres reales
# de tu equipo; "Otro" siempre queda disponible por si falta alguien).
OPERADORES = ["Adrian Carpio", "Fernando Valdivia", "Mishel Ruiz", "Otro"]

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
    """
    ref = INSUMOS_REF[codigo_estructurante]
    fraccion_seca = 1 - ref["humedad"] / 100
    c_insumo = fraccion_seca * (ref["carbono"] / 100)   # kg carbono por kg insumo
    n_insumo = fraccion_seca * (ref["nitrogeno"] / 100)  # kg nitrógeno por kg insumo

    denominador = (cn_target * n_insumo) - c_insumo
    if denominador <= 0:
        # El insumo no tiene suficiente carbono relativo para mover la
        # relación C/N hacia el objetivo con esta fórmula (caso raro).
        return 0.0

    x_kg = (fixed_carbono_kg - cn_target * fixed_nitrogeno_kg) / denominador
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
tab_m1, tab_m2 = st.tabs([
    "🌾 Módulo 1 — Formulación de Lotes",
    "🪵 Módulo 2 — Capacidad de Estructurante",
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
    encabezado("🪵 Módulo 2 — Capacidad de Material Estructurante")
    st.caption("Planifica cuánto aserrín o cartón necesitas según los residuos disponibles, y compara escenarios")

    st.subheader("1. Cantidades de residuos disponibles (toneladas)")
    col1, col2 = st.columns(2)
    with col1:
        operador2_sel = st.selectbox("Operador", OPERADORES, key="m2_operador_sel")
        if operador2_sel == "Otro":
            operador2 = st.text_input("Nombre del operador (nuevo)", key="m2_operador_otro")
        else:
            operador2 = operador2_sel
    with col2:
        fecha2 = st.date_input("Fecha de planificación", value=date.today(), key="m2_fecha")

    cols_base = st.columns(len(INSUMOS_BASE))
    disponibles_ton = {}
    for col, codigo in zip(cols_base, INSUMOS_BASE):
        ref = INSUMOS_REF[codigo]
        with col:
            disponibles_ton[codigo] = st.number_input(
                f"{ref['nombre']} ({codigo})", min_value=0.0, step=0.5, format="%.2f", key=f"m2_disp_{codigo}"
            )

    cartón_disponible_ton = st.number_input(
        "Cartón (CA) ya disponible (opcional, si ya tienen algo aparte del que se calcule)",
        min_value=0.0, step=0.5, format="%.2f", key="m2_disp_CA"
    )

    total_base_ton = sum(disponibles_ton.values())

    if total_base_ton > 0:
        st.subheader("2. Proporción declarada vs. proporción real ingresada")
        st.caption("Los operadores declaran trabajar con 60% orgánico / 20% lodo / 20% cartón")

        pct_ro_real = (disponibles_ton.get("RO", 0) / total_base_ton) * 100
        pct_ld_real = (disponibles_ton.get("LD", 0) / total_base_ton) * 100
        # CA no está en INSUMOS_BASE porque se calcula; usamos lo disponible como referencia si lo hay
        pct_ca_real = (cartón_disponible_ton / (total_base_ton + cartón_disponible_ton) * 100) if cartón_disponible_ton > 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Residuos orgánicos", f"{pct_ro_real:.0f}%", f"declarado {PROPORCION_DECLARADA['RO']:.0f}%")
        c2.metric("Lodo PTAR", f"{pct_ld_real:.0f}%", f"declarado {PROPORCION_DECLARADA['LD']:.0f}%")
        c3.metric("Cartón", f"{pct_ca_real:.0f}%", f"declarado {PROPORCION_DECLARADA['CA']:.0f}%")

        desvio_ro = abs(pct_ro_real - PROPORCION_DECLARADA["RO"])
        desvio_ld = abs(pct_ld_real - PROPORCION_DECLARADA["LD"])
        if desvio_ro > 10 or desvio_ld > 10:
            alerta_txt = (
                f"La proporción ingresada (RO {pct_ro_real:.0f}% / LD {pct_ld_real:.0f}%) "
                f"se aleja más de 10 puntos de lo declarado (60/20/20). Fecha: {fecha2}."
            )
            st.warning(f"⚠️ Desviación de proporción declarada. {alerta_txt}")
            st.session_state["consultas_aserrin"].append({
                "fecha": fecha2, "tipo": "alerta_proporcion", "detalle": alerta_txt
            })
        else:
            st.success("La proporción ingresada está razonablemente cerca de lo declarado (60/20/20).")

        # --- Cálculo de escenarios ---------------------------------
        st.subheader("3. Comparación de escenarios")

        cantidades_base_kg = {c: disponibles_ton.get(c, 0) * 1000 for c in INSUMOS_BASE}
        masa_base, hum_base, c_base, n_base, cn_base = calcular_mezcla(cantidades_base_kg)

        # Escenario A: CON ASERRÍN (se calcula cuánto AS agregar)
        as_kg_necesario = kg_requeridos_estructurante(c_base, n_base, "AS", cn_target)
        mezcla_con_as = dict(cantidades_base_kg)
        mezcla_con_as["AS"] = as_kg_necesario
        masa_as, hum_as, _, _, cn_as = calcular_mezcla(mezcla_con_as)

        # Escenario B: SIN ASERRÍN (mezcla base tal cual, sin ajuste)
        masa_sin, hum_sin, _, _, cn_sin = masa_base, hum_base, None, None, cn_base

        # Escenario C: SOLO CARTÓN (se calcula cuánto CA agregar en vez de AS)
        ca_kg_necesario = kg_requeridos_estructurante(c_base, n_base, "CA", cn_target)
        mezcla_con_ca = dict(cantidades_base_kg)
        mezcla_con_ca["CA"] = ca_kg_necesario
        masa_ca, hum_ca, _, _, cn_ca = calcular_mezcla(mezcla_con_ca)

        tabla_comparativa = pd.DataFrame([
            {
                "Escenario": "Con aserrín",
                "Aserrín a solicitar (t)": round(as_kg_necesario / 1000, 2),
                "Cartón a solicitar (t)": 0,
                "Masa total (t)": round(masa_as / 1000, 2),
                "Humedad (%)": round(hum_as, 1),
                "Relación C/N": round(cn_as, 1) if cn_as != float("inf") else None,
            },
            {
                "Escenario": "Sin aserrín (mezcla base)",
                "Aserrín a solicitar (t)": 0,
                "Cartón a solicitar (t)": 0,
                "Masa total (t)": round(masa_sin / 1000, 2),
                "Humedad (%)": round(hum_sin, 1),
                "Relación C/N": round(cn_sin, 1) if cn_sin != float("inf") else None,
            },
            {
                "Escenario": "Solo cartón",
                "Aserrín a solicitar (t)": 0,
                "Cartón a solicitar (t)": round(ca_kg_necesario / 1000, 2),
                "Masa total (t)": round(masa_ca / 1000, 2),
                "Humedad (%)": round(hum_ca, 1),
                "Relación C/N": round(cn_ca, 1) if cn_ca != float("inf") else None,
            },
        ])

        st.dataframe(tabla_comparativa, use_container_width=True, hide_index=True)
        st.caption(
            f"Cálculo hecho para alcanzar una relación C/N objetivo de {cn_target:.0f}:1 "
            f"(punto medio del rango {cn_min:.0f}-{cn_max:.0f} configurado en la barra lateral)."
        )

        csv_comp = tabla_comparativa.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Descargar tabla comparativa (CSV)",
            data=csv_comp,
            file_name=f"comparativo_estructurante_{fecha2}.csv",
            mime="text/csv",
        )

        # --- Selección y generación de reporte -----------------------
        st.subheader("4. Elegir escenario y generar solicitud")
        escenario_elegido = st.radio(
            "¿Qué escenario vas a solicitar?",
            tabla_comparativa["Escenario"].tolist(),
            key="m2_escenario_radio",
        )

        if st.button("📄 Generar reporte de solicitud", type="primary"):
            fila = tabla_comparativa[tabla_comparativa["Escenario"] == escenario_elegido].iloc[0]

            reporte = f"""SOLICITUD DE MATERIAL ESTRUCTURANTE - PLANTA DE COMPOSTAJE
Fecha de planificación: {fecha2}
Operador: {operador2}
Escenario elegido: {escenario_elegido}

Residuos disponibles considerados:
"""
            for codigo in INSUMOS_BASE:
                reporte += f"  - {INSUMOS_REF[codigo]['nombre']}: {disponibles_ton.get(codigo, 0):.2f} t\n"

            reporte += f"\nMaterial a solicitar:\n"
            reporte += f"  - Aserrín: {fila['Aserrín a solicitar (t)']:.2f} t\n"
            reporte += f"  - Cartón adicional: {fila['Cartón a solicitar (t)']:.2f} t\n"
            reporte += f"\nResultado estimado de la mezcla:\n"
            reporte += f"  - Masa total: {fila['Masa total (t)']:.2f} t\n"
            reporte += f"  - Humedad estimada: {fila['Humedad (%)']:.1f} %\n"
            reporte += f"  - Relación C/N estimada: {fila['Relación C/N']}:1\n"
            reporte += f"\n(Reporte generado automáticamente por la plataforma de gestión de compostaje. "
            reporte += f"Valores estimados según formulación de referencia, sujetos a validación en campo.)\n"

            st.text_area("Vista previa del reporte (puedes copiarlo a un correo)", reporte, height=280)
            st.download_button(
                "⬇️ Descargar reporte (TXT)",
                data=reporte.encode("utf-8"),
                file_name=f"solicitud_estructurante_{fecha2}.txt",
                mime="text/plain",
            )

            st.session_state["consultas_aserrin"].append({
                "fecha": fecha2, "tipo": "solicitud_generada",
                "detalle": f"{escenario_elegido}: aserrín {fila['Aserrín a solicitar (t)']:.2f} t, cartón {fila['Cartón a solicitar (t)']:.2f} t",
            })
    else:
        st.info("Ingresa al menos una cantidad de residuos disponibles para ver los escenarios.")

    # --- Historial de consultas de este módulo ---------------------------
    st.divider()
    st.subheader("Historial de consultas y alertas de este módulo")
    if st.session_state["consultas_aserrin"]:
        st.dataframe(pd.DataFrame(st.session_state["consultas_aserrin"]), use_container_width=True)
    else:
        st.caption("Aún no hay consultas registradas en esta sesión.")
