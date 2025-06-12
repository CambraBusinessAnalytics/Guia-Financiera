import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd
import plotly.express as px
from dash import dash_table

# =====================
# CARGA Y PROCESAMIENTO DE DATOS
# =====================

# Ruta del archivo
file_path = "C:\\Users\\Ruth Rolón Aranda\\Documents\\Cambra\\Analisis para la consultoria\\ejemplo dash\\finanzas\\guaranies.xlsx"
df = pd.read_excel(file_path)
df['Riesgo'] = df['Riesgo'].fillna('Sin datos')

 # Reemplazar NaN con 'Sin Datos'
# Mapeo de calificaciones a valores numéricos (más seguros = menor número)
riesgo_map = {
    'AAA+py': 1, 'AAApy': 2, 'AAA-py': 3,
    'AA+py': 4, 'AApy': 5, 'AA-py': 6,
    'A+py': 7, 'Apy': 8, 'A-py': 9,
    'BBB+py': 10, 'BBBpy': 11, 'BBB-py': 12,
    'BB+py': 13, 'BBpy': 14, 'BB-py': 15,
    'B+py': 16, 'Bpy': 17, 'B-py': 18, 'Sin datos': 19,
}
df['Riesgo_Num'] = df['Riesgo'].map(riesgo_map)

# Plazo como número y clasificación
df['Plazo'] = pd.to_numeric(df['Plazo'], errors='coerce')

def clasificar_tipo_plazo(valor):
    # Primero normalizamos si es string (y quitamos espacios si los hay)
    if isinstance(valor, str):
        valor = valor.strip().lower()
        if valor == 'largo plazo':
            return 'Largo plazo'
        elif valor == 'mediano plazo':
            return 'Mediano plazo'
        elif valor == 'corto plazo':
            return 'Corto plazo'
        elif valor == 'muy corto plazo':
            return 'Muy corto plazo'
        elif valor == 'vista':
            return 'Vista'
        else:
            return 'Desconocido'

    # Luego evaluamos si es un número (los valores ya están controlados)
    elif isinstance(valor, (int, float)):
        if valor <= 7:
            return 'Vista'
        elif valor <= 90:
            return 'Muy corto plazo'
        elif valor <= 365:
            return 'Corto plazo'
        elif valor <= 900:
            return 'Mediano plazo'
        else:
            return 'Largo plazo'
    
    return 'Desconocido'
df['Plazo_Tipo'] = df['Plazo'].apply(clasificar_tipo_plazo)


# Reemplazo de "na" por 1.000.000 y valores nulos
df['Capital Minimo'] = df['Capital Minimo'].replace("na", 1_000_000)
df['Capital Minimo'] = pd.to_numeric(df['Capital Minimo'], errors='coerce').fillna(1_000_000)

# Crear campo combinado para el hover
df['Entidad+Producto'] = df['Entidad'] + " – " + df['Producto']

# =====================
# GRÁFICO
# =====================
riesgo_order = list(riesgo_map.keys())  # Lista en orden del menos al más riesgoso
df['Riesgo'] = pd.Categorical(df['Riesgo'], categories=riesgo_order, ordered=True)
fig = px.scatter(
    df,
    x="Riesgo",
    y="Tasa MAX",
    color="Categoria",
    symbol="Plazo_Tipo",
    category_orders={"Riesgo": riesgo_order},
    hover_name="Entidad+Producto",
    hover_data={
        "Riesgo_Num": False,
        "Tasa MAX": True,
        "Categoria": True,
        "Plazo_Tipo": True,
        "Riesgo": True,
        "Capital Minimo": True,
    },
    title="Relación entre riesgo, rentabilidad y tipo de producto financiero",
    labels={
        "Riesgo": "Riesgo",
        "Tasa MAX": "Tasa de interés máxima (%)"
    },
    #size="Capital Minimo",
    size_max=60,
    template="plotly_white"
)

fig.update_layout(
    legend=dict(
        orientation="h",       # Leyenda horizontal
        yanchor="top",         # Ancla la leyenda en la parte superior (para que quede justo debajo del gráfico)
        y=-0.2,                # La bajamos un poco para que quede debajo
        xanchor="center",      # Centrar horizontalmente
        x=0.3,
        font=dict(size=11),
        bgcolor="rgba(0,0,0,0)",  # Fondo transparente
        borderwidth=0
    ),
    margin=dict(t=40, b=80, l=40, r=40)  # Espacio extra abajo para que no quede cortada la leyenda
)

#---------------------------------------------------------------

# Boxplot por categoría
fig_categoria = px.box(
    df,
    x="Categoria",
    y="Tasa MAX",
    points="all",  # Mostrar puntos individuales
    hover_name="Entidad+Producto",
    hover_data={
        "Riesgo_Num": False,
        "Tasa MAX": True,
        "Categoria": True,
        "Plazo_Tipo": True,
        "Riesgo": True,
        "Capital Minimo": True
    },
    title="Distribución de tasas por categoría de producto",
    template="plotly_white"
)
orden_plazos = ['Vista', 'Muy corto plazo', 'Corto plazo', 'Mediano plazo', 'Largo plazo']
df['Plazo_Tipo'] = pd.Categorical(df['Plazo_Tipo'], categories=orden_plazos, ordered=True)



# Boxplot por plazo
fig_plazo = px.box(
    df,
    x="Plazo_Tipo",
    y="Tasa MAX",
    points="all",
    title="Distribución de tasas por tipo de plazo",
    category_orders={"Plazo_Tipo": orden_plazos},
    template="plotly_white",
    hover_name="Entidad+Producto",
    hover_data={
        "Riesgo_Num": False,
        "Tasa MAX": True,
        "Categoria": True,
        "Plazo_Tipo": True,
        "Riesgo": True,
        "Capital Minimo": True
    },
)

# Boxplot por riesgo original
fig_riesgo = px.box(
    df,
    x="Riesgo",
    y="Tasa MAX",
    points="all",
    category_orders={"Riesgo": riesgo_order},
    title="Distribución de tasas por calificación de riesgo",
    template="plotly_white",
    hover_name="Entidad+Producto",
    hover_data={
        "Riesgo_Num": False,
        "Tasa MAX": True,
        "Categoria": True,
        "Plazo_Tipo": True,
        "Riesgo": True,
        "Capital Minimo": True
    },
)
df2 = df[['Categoria', 'Entidad', 'Producto', 'Tasa MIN', 'Tasa MAX', 'Capital Minimo', 'Riesgo', 'Plazo_Tipo']]
tabla_df2 = dash_table.DataTable(
    columns=[{"name": col, "id": col} for col in df2.columns],
    filter_action="native",
    sort_action="native",
    data=df2.to_dict("records"),
    style_table={"overflowX": "auto"},
    style_cell={
        "textAlign": "left",
        "padding": "5px",
        "fontFamily": "Arial",
        "fontSize": "13px",
    },
    style_header={
        "backgroundColor": "black",
        "color": "white",
        "fontWeight": "bold"
    },
    page_size=15  # Ajustable según necesidad
)
# =====================
# APP DASH
# =====================

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    # Encabezado
    html.Header(
        dbc.Container([
            dbc.Row([
                dbc.Col(
                    dbc.Row([
                        dbc.Col(html.Img(src='/assets/CAMBRA.png', style={'height': '80px'}), width="auto"),
                        dbc.Col(html.H1(
                            "Guía de Productos Financieros",
                            className="m-0",
                            style={
                                'font-family': 'Avenir, sans-serif',
                                'font-weight': '700',
                                'font-size': '2rem',
                                'text-align': 'center',
                                'color': '#333'
                            }
                        ), align="center")
                    ], align="center"),
                    width=8
                )
            ], justify="center", className="py-3")
        ]),
        style={'backgroundColor': 'white'},
    ),
html.Hr(),
    # Gráfico
    dbc.Container([
    dcc.Graph(figure=fig),  # tu gráfico principal de burbujas
    html.Hr(),
    dcc.Graph(figure=fig_categoria),
    html.Hr(),
    dcc.Graph(figure=fig_plazo),
    html.Hr(),
    dcc.Graph(figure=fig_riesgo),
    html.Hr(),
    html.H4("Calculadora de rendimiento vs inflación y alternativas"),
    dbc.Row([
        dbc.Col([
            html.Label("Monto inicial (Gs):"),
            dcc.Input(id='input-monto', type='number', value=1000000, step=10000)
        ]),
        dbc.Col([
            html.Label("Tasa de interés anual (%):"),
            dcc.Input(id='input-tasa', type='number', value=8, step=0.1)
        ]),
        dbc.Col([
            html.Label("Inflación anual esperada (%):"),
            dcc.Input(id='input-inflacion', type='number', value=4, step=0.1)
        ]),
        dbc.Col([
            html.Label("Tasa de proyecto alternativo (%):"),
            dcc.Input(id='input-alternativa', type='number', step=0.1)
        ])
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.Label("Plazo (días):"),
            dcc.Slider(
                id='input-plazo',
                min=30,
                max=3650,  # hasta 10 años
                step=15,
                value=365,
                marks={
                    30: '30 días',
                    90: '3 meses',
                    180: '6 meses',
                    365: '1 año',
                    730: '2 años',
                    1095: '3 años',
                    1460: '4 años',
                    1825: '5 años',
                    2190: '6 años',
                    2555: '7 años',
                    2920: '8 años',
                    3285: '9 años',
                    3650: '10 años'
                },
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ])
    ]),
    html.Br(),
    html.Div(id='output-calculadora'),
    html.Hr(),
    html.H4("Tabla de productos financieros"),
    tabla_df2,
    html.Div([
    html.P(
    "Realizado por Cambra Business Analytics. // Contacto: +595 0985 705586.",
    style={
        'font-family': 'Cambria, serif',
        'font-style': 'italic',
        'text-align': 'center',
        'color': 'white',
        'background-color': 'black',
        'margin-top': '20px',
        'width': '80%',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'padding': '10px',
        #'border-radius': '10px',
        'line-height': '1.5',
        'font-size': '14px'
        }
    )
]),

    ])
])
from dash import Input, Output, State

@app.callback(
    Output('output-calculadora', 'children'),
    Input('input-monto', 'value'),
    Input('input-tasa', 'value'),
    Input('input-inflacion', 'value'),
    Input('input-plazo', 'value'),
    Input('input-alternativa', 'value')
)
def calcular_rendimiento(monto, tasa, inflacion, plazo, tasa_alt):
    if None in [monto, tasa, inflacion, plazo]:
        return "Por favor, complete todos los campos obligatorios."

    tasa_efectiva = tasa / 100
    inflacion_efectiva = inflacion / 100

    # Valor final con interés compuesto (capitalización anual)
    vf = monto * (1 + tasa_efectiva) ** (plazo / 365)
    intereses_generados = vf - monto

    # Valor final ajustado por inflación (valor real del total acumulado)
    vf_real = vf / ((1 + inflacion_efectiva) ** (plazo / 365))

    # Valor del capital inicial ajustado por inflación (sin intereses)
    capital_real = monto / ((1 + inflacion_efectiva) ** (plazo / 365))

    # Pérdida de poder adquisitivo en términos del capital inicial
    perdida_inflacion = monto - capital_real

    resultado = [
        html.P(f"📈 Valor final estimado (capital + intereses): Gs. {vf:,.0f}"),
        html.P(f"➕ Intereses generados: Gs. {intereses_generados:,.0f}"),
        #html.Br(),
        html.P(f"📉 Valor ajustado por inflación (del total acumulado): Gs. {vf_real:,.0f}"),
        html.P(f"🧮 Valor actual del capital inicial erosionado por inflación: Gs. {capital_real:,.0f}"),
        html.P(f"💸 Pérdida de poder adquisitivo estimada (sin intereses): Gs. {perdida_inflacion:,.0f}")
    ]

    if tasa_alt is not None:
        tasa_alt_efectiva = tasa_alt / 100
        vf_alt = monto * (1 + tasa_alt_efectiva) ** (plazo / 365)
        diferencia_abs = vf - vf_alt
        diferencia_pct = (diferencia_abs / vf_alt) * 100

        #resultado.append(html.Br())
        resultado.append(html.P(f"⚖️ Valor final con tasa alternativa: Gs. {vf_alt:,.0f}"))
        if diferencia_abs > 0:
            resultado.append(html.P(f"✅ Tu inversión original supera al proyecto alternativo en Gs. {diferencia_abs:,.0f} ({diferencia_pct:.2f}%)"))
        elif diferencia_abs < 0:
            resultado.append(html.P(f"⚠️ Tu inversión original rinde Gs. {abs(diferencia_abs):,.0f} menos que el proyecto alternativo ({abs(diferencia_pct):.2f}%)"))
        else:
            resultado.append(html.P(f"🔍 Ambos proyectos tendrían exactamente el mismo valor final."))

    return resultado
if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=8080)
