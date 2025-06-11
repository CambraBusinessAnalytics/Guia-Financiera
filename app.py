import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd
import plotly.express as px

# =====================
# CARGA Y PROCESAMIENTO DE DATOS
# =====================

# Ruta del archivo

df = pd.read_excel('guaranies.xlsx')

# Mapeo de calificaciones a valores numéricos (más seguros = menor número)
riesgo_map = {
    'AAA+py': 1, 'AAApy': 2, 'AAA-py': 3,
    'AA+py': 4, 'AApy': 5, 'AA-py': 6,
    'A+py': 7, 'Apy': 8, 'A-py': 9,
    'BBB+py': 10, 'BBBpy': 11, 'BBB-py': 12,
    'BB+py': 13, 'BBpy': 14, 'BB-py': 15,
    'B+py': 16, 'Bpy': 17, 'B-py': 18
}
df['Riesgo_Num'] = df['Riesgo'].map(riesgo_map)

# Plazo como número y clasificación
df['Plazo'] = pd.to_numeric(df['Plazo'], errors='coerce')

def clasificar_plazo(dias):
    if dias <= 7:
        return 'Vista'
    elif dias <= 90:
        return 'Muy corto plazo'
    elif dias <= 365:
        return 'Corto plazo'
    elif dias <= 900:
        return 'Mediano plazo'
    else:
        return 'Largo plazo'

df['Plazo_Tipo'] = df['Plazo'].apply(clasificar_plazo)

# Reemplazo de "na" por 1.000.000 y valores nulos
df['Capital Minimo'] = df['Capital Minimo'].replace("na", 1_000_000)
df['Capital Minimo'] = pd.to_numeric(df['Capital Minimo'], errors='coerce').fillna(1_000_000)

# Crear campo combinado para el hover
df['Entidad+Producto'] = df['Entidad'] + " – " + df['Producto']

# =====================
# GRÁFICO
# =====================

fig = px.scatter(
    df,
    x="Riesgo_Num",
    y="Tasa MAX",
    color="Categoria",
    symbol="Plazo_Tipo",
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
        "Riesgo_Num": "Riesgo",
        "Tasa MAX": "Tasa de interés máxima (%)"
    },
    #size="Capital Minimo",
    size_max=60,
    template="plotly_white"
)

fig.update_layout(
    # Si querés mostrar a los activos más seguros a la derecha, activá esta línea:
    # xaxis=dict(autorange="reversed"),
    legend_title_text="Producto financiero",
    title_font=dict(size=20)
)
#---------------------------------------------------------------
import plotly.express as px

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

# Boxplot por plazo
fig_plazo = px.box(
    df,
    x="Plazo_Tipo",
    y="Tasa MAX",
    points="all",
    title="Distribución de tasas por tipo de plazo",
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
                    width=10
                )
            ], justify="center", className="py-3")
        ]),
        style={'backgroundColor': 'white'},
    ),

    html.Hr(),

    # Contenido principal centrado en ancho de 10 columnas
    dbc.Container(
        dbc.Row(
            dbc.Col([
                dcc.Graph(figure=fig),
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
                    ], xs=12, sm=6, md=5),

                    dbc.Col([
                        html.Label("Tasa de interés anual (%):"),
                        dcc.Input(id='input-tasa', type='number', value=8, step=0.1)
                    ], xs=12, sm=6, md=5)
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col([
                        html.Label("Inflación anual esperada (%):"),
                        dcc.Input(id='input-inflacion', type='number', value=4, step=0.1)
                    ], xs=12, sm=6, md=5),

                    dbc.Col([
                        html.Label("Tasa de proyecto alternativo (%):"),
                        dcc.Input(id='input-alternativa', type='number', step=0.1)
                    ], xs=12, sm=6, md=5)
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col([
                        html.Label("Plazo (días):"),
                        dcc.Slider(
                            id='input-plazo',
                            min=30,
                            max=3650,
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
                    ], xs=12)
                ], className="mb-4"),

                html.Div(id='output-calculadora'),

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
                            'line-height': '1.5',
                            'font-size': '14px'
                        }
                    )
                ])
            ], width=10),
            justify="center"
        ),
        fluid=True
    )
])

from dash import Input, Output

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
