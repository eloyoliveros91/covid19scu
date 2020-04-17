import dash
import pandas as pd
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pathlib
import plotly.graph_objs as go
import datetime as dt
import numpy as np
import plotly.express as px
import dash_auth
from flask import Flask, send_from_directory


PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
descarga = DATA_PATH.joinpath("COVID-19.xlsx")

VALID_USERNAME_PASSWORD_PAIRS = [
    ('hello', 'world'), ('foo', 'bar')
]


#external_stylesheets =['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
np.seterr(divide='ignore', invalid='ignore')


# reading data
casosConfirmados = pd.read_excel(DATA_PATH.joinpath("COVID-19.xlsx"), sheet_name = 'Casos SCU')
muestras = pd.read_excel(DATA_PATH.joinpath("muestras.xlsx"), index_col=0)
confirmadosOriente = pd.read_excel(DATA_PATH.joinpath("COVID-19.xlsx"), sheet_name = 'Oriente', skiprows=[0], usecols="A:G")
ingresosDF = pd.read_excel(DATA_PATH.joinpath("COVID-19.xlsx"), sheet_name = 'Ingresos SCU')
data = pd.read_excel(DATA_PATH.joinpath("COVID-19.xlsx"), sheet_name = 'Casos SCU')
ultimoDia = data.iloc[len(data)-1]
survey = pd.read_excel(DATA_PATH.joinpath("COVID-19.xlsx"), sheet_name = 'Survey')
pais = pd.read_excel(DATA_PATH.joinpath('COVID-19.xlsx'), sheet_name = 'Evolucion', index_col=1)
poblacionMunicipios = pd.read_excel(DATA_PATH.joinpath('municipiosCuba.xlsx'))

def riesgoSantiago():
    mun = pd.read_excel(DATA_PATH.joinpath('COVID-19.xlsx'), sheet_name = 'CasosMunicipios', index_col=0)
    xaxis = np.datetime_as_string( mun.index.values, unit='D')
    fig = go.Figure()
    ymax = 0
    for val in mun.columns: 
        value = np.round((mun[val].values*10000) / poblacionMunicipios[poblacionMunicipios.Municipios == val]['Poblacion'].values,decimals=2)
        ymax = np.max([np.max(value), ymax])
        fig.add_trace(go.Scatter(x = xaxis, 
                                y = value,
                                mode='lines+markers',
                                name=val,          
                                hoverinfo = 'y',
                                textposition = "top center",
                                line=dict(width = 3),
                                marker=dict(size=8)),                            
                    )
    fig.update_layout(
        legend_orientation = 'h', 
        legend=dict(x=0.1, y=1.1),
        xaxis = dict(
            tickvals=xaxis,
            tickformat = '%m-%d',
            ),
        yaxis = dict(
            title = 'Tasa por cada 10000 habitantes',
            tickvals = np.arange(0, ymax+1, 0.05)
        ),
        plot_bgcolor = 'rgb(235,235,235)',
        margin={'b': 0, 't': 0, 'r': 10, 'l' : 0},
        height = 350,
    )
    return fig

def riesgoCuba():
    tabla = pais.set_index('Provincia').drop(['Prueba', 'Fecha', 'Total'])
    pobProv = poblacionMunicipios.drop('Municipios', axis=1).groupby('Provincia').sum().reset_index()
    pobProv.at[11, 'Provincia'] = 'Isla de la Juventud'

    provincias = tabla.index
    fig = go.Figure()
    provincias = tabla.index
    dias = tabla.columns.values
    for i in provincias:    
        value = np.round((tabla.loc[i].values.astype('float64')*100000)/pobProv[pobProv.Provincia == i]['Poblacion'].values,decimals=2)
        fig.add_trace(go.Scatter(x=dias, y=value,
                            mode='lines+markers',
                            name=i,
                            line=dict(width = 4),
                            marker=dict(size=10),
                            hoverinfo = 'name+y'
                            ))


    fig.update_layout(xaxis=dict(
            title = 'Días desde el Pimer caso confirmado en Cuba',
            showline=True,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            ),        
            yaxis_title='Tasa de confirmados por cada 100000 habitantes',    
            plot_bgcolor = 'rgb(235,235,235)',
            margin={'t': 0, 'r': 10, 'l' : 0},
            
            )
    return fig

def confirmadosStgo():
    fig = go.Figure()
    x = casosConfirmados['Día']
    y = casosConfirmados['Casos Confirmados Acumulados']
    cols = ['Casos Confirmados Acumulados', 'Nuevos Casos Confirmados']
    for col in cols:
        fig.add_trace(go.Scatter(x=x, y=casosConfirmados[col],
                            mode='lines+markers+text',
                            name=col,
                            text = casosConfirmados[col],
                            textposition = "bottom center",
                            textfont = dict(color='rgb(0,0,0)'),
                            hoverinfo='x+y',
                            line=dict(width = 4),
                            marker=dict(size=12)))    
    fig.update_layout(
        xaxis=dict(
            title = 'Días desde el Primer caso confirmado en Santiago de Cuba',
            showline=True,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            #gridcolor = 'rgb(0,0,0)'
            ), 
        autosize  = True,       
        yaxis_title='Total de casos',   
        legend_orientation="h", 
        plot_bgcolor = 'rgb(235,235,235)',
        margin={'t': 0, 'r': 10, 'l' : 0, 'b':0},
        legend=dict(x=-.1, y=1.15),
        height = 350,
        yaxis=dict(
            linecolor ='rgb(220,220,220)', 
            linewidth=1.5,
            tickmode = 'array',
            tickvals = np.arange(0, np.max(y)+7, 4)
            )    
    )    
    return fig

def casosMcpios(chartType):
    mcpios = survey.groupby('Municipio').size()
    labels = mcpios.index
    values = mcpios.values
    
    if chartType == 'Pie':    
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0.1, 0.1, 0.1, 0.1], 
                                    )])
        fig.update_traces(hoverinfo='label+percent+value', textinfo='label',
                        marker=dict(line=dict(color='#000000', width=2)))
        fig.update_layout(showlegend=False, margin={'t': 0}, height = 350)
    else:
        fig = go.Figure()
        fig.add_bar(
            x=labels, y=values,
            name='Casos confirmados por muncipios',
            text = values,
        )
        fig.update_layout(margin={'t': 4},height = 350,plot_bgcolor = 'rgb(255,255,255)',
        yaxis=dict(linecolor ='rgb(170,170,170)', linewidth=2))
        
    return fig

def mcpiosAreaSalud():
    mcpios = survey.groupby(['Municipio', 'Área de Salud']).size().to_frame(name='Total').reset_index()
    mcpios.loc[:, 'Provincia'] = 'PROVINCIA'
    mcpios
    import plotly.express as px

    fig = px.sunburst(mcpios, path=['Provincia', 'Municipio', 'Área de Salud'], values='Total',
                    hover_data=['Total'])
    fig.update_layout(
        height = 350,
        margin = dict(t=0, l=0, r=0, b=0)
    )
    return fig

def confirmadosOte():
    conf = confirmadosOriente.dropna().set_index('Fecha').drop('Días', 1)
    x = conf.index
    fig = go.Figure()
    for i in conf.columns:
        fig.add_trace(go.Scatter(x=x, y=conf[i],
                            mode='lines+markers',
                            name=i,
                            line=dict(width = 4),
                            marker=dict(size=8)))    
    fig.update_layout(
        xaxis=dict(
            title = 'Fechas desde el Primer caso confirmado en el Oriente',
            showline=True,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickvals=x,
            tickformat = '%m-%d'
            ),
        yaxis=dict(
            linecolor ='rgb(220,220,220)', 
            linewidth=1.5,
            tickmode = 'array',
            tickvals = np.arange(0, confirmadosOriente[confirmadosOriente.columns[2:7]].max().max(), 4),
            title='Total de casos'
            ),
        legend_orientation="h",     
        legend=dict(x=-.1, y=1.1),
        margin={'t': 0, 'r':15},
        plot_bgcolor = 'rgb(235,235,235)',
        height = 350,        
    )
    return fig

def muestrasStgo():
    fig4 = go.Figure()

    names = ['Muestras Negativas','Muestras Confirmadas','Muestras Confirmadas-Evolutivas']
    cols = ['NEG-COVID-19', 'POS-COVID-19', 'POS-COVID-19/EVOLUTIVO DE CONFIRMADO']
    color = ['#1d6996', '#73af48', '#edad08']

    x = np.datetime_as_string( muestras['FR'].unique(), unit='D')
    y = muestras.groupby('FR').sum()

    for num, name in enumerate(names):
        fig4.add_bar(
            x=x, y=y[cols[num]],
            name=name,
            marker_color=color[num]            
        )
    fig4.update_layout(barmode='stack', legend=dict(
                x=0,
                y=1.0,
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)'
            ),
            xaxis=dict(
                title = 'Fecha de análisis de muestras',
                showline=True,
                showticklabels=True,
                linecolor='rgb(204, 204, 204)',
                linewidth=2,
                ticks='outside',
                tickvals=x,
                tickformat = '%m-%d',
            ),        
            yaxis = dict(
                title='Número de muestras analizadas',        
                tickvals = np.arange(0, y.sum(1).max()+10, 20).tolist()
            ),
            uniformtext_minsize=8, 
            uniformtext_mode='hide',
            margin={'t': 0, 'r':20},
            plot_bgcolor = 'rgb(235,235,235)',
            height = 350
            )
    fig4.update_xaxes(automargin=True)
    return fig4

def ingresos(barra1, barra2, nombre1, nombre2):
    fig3 = go.Figure()
    x = ingresosDF['Fecha']

    fig3.add_bar(x = x, y = ingresosDF[barra1], name=nombre1, text=ingresosDF[barra1], marker_color='#1d6996')
    fig3.add_bar(x = x, y = ingresosDF[barra2], name=nombre2, text=ingresosDF[barra2], marker_color='#73af48')

    fig3.update_layout(barmode='stack')

    fig3.update_layout(legend_orientation="h")
    fig3.update_layout(legend=dict(x=-.1, y=1.1))
    fig3.update_layout(xaxis=dict(
            tickformat = '%m-%d',
            title = 'Fechas de ingresos',
            showline=True,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickvals=x,
            ),        
            yaxis_title='Total de personas ingresadas',        
            margin={'t': 0, 'r':20},
            plot_bgcolor = 'rgb(235,235,235)',
        height = 350
            )
    fig3.update_xaxes(automargin=True)

    return fig3

def generoEdad():
    grupos_etareos_tx = ['0-18', '19-40', '41-60', '+60']
    survey['GE'] = pd.cut(survey.Edad, [0,18,40,60,120], 
                        labels = grupos_etareos_tx, right=True, include_lowest=True)
    gr = survey.groupby(['GE', 'Género'])
    mujeres = [gr.size()[ge]['F'] for ge in grupos_etareos_tx]
    hombres = [gr.size()[ge]['M'] for ge in grupos_etareos_tx]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=grupos_etareos_tx,
        y=hombres,
        name='Hombres',        
        marker=dict(
            color='rgba(58, 71, 80)',
            #line=dict(color='rgba(58, 71, 80, 1.0)', width=3)
        ),
        hoverinfo = 'y',
        base = 0,
        width = 0.4
    ))

    fig.add_trace(go.Bar(
        x=grupos_etareos_tx,
        y=mujeres,
        name='Mujeres',
        hoverinfo = 'y',
        marker=dict(
            color='rgba(246, 78, 139)',
            #line=dict(color='rgba(246, 78, 139, 1.0)', width=3)
            opacity = 0.85
        ),
        base=0,
        width = 0.4
    ))

    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = grupos_etareos_tx ,
            zeroline=True,
        ),
        legend_orientation="h",
        legend=dict(x=-.1, y=1.2),
        xaxis_title="Grupos etáreos",
        yaxis_title="Total de Casos Confirmados",
        barmode='group',
        bargap=0.6,
        bargroupgap = 1,    
        margin={'t': 20, 'r':20, 'b':0},
        plot_bgcolor = 'rgb(235,235,235)',
        height = 335
    )
    return fig

def create_top(title, content):
    card = html.Div([
                html.Div([
                html.Div([
                    html.Div(children=title, className='h6 font-weight-bold text-primary text-uppercase'),
                    html.Div([                        
                    html.Div([                        
                        html.Div(children=content, className='h2 mb-0 font-weight-bold text-gray-800')
                        ], className='col mr-2'),                    
                    ], className='row no-gutters align-items-center'),
                ], className='card-body'),
                ], className='card border-bottom-danger shadow h-45'),
            ], className='mb-1 mr-1')
    return(card)

def totalCasosPais():
    tabla = pais.set_index('Provincia').dropna(1)
    last = tabla.columns[len(tabla.columns)-1]
    provincias = tabla[last]
    colors = ['#1d6996']*16
    colors[12]='crimson'
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y = provincias.index[1:16],
        x = provincias.values[1:16],
        orientation = 'h',
        marker_color = colors
    ))
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        margin={'t':20 ,'r':20},
        plot_bgcolor = 'rgb(235,235,235)',
        height = 350,
        xaxis=dict(            
                tickmode = 'array',
                tickvals = np.arange(0, np.max(provincias.values[1:16]), 20),
                title = 'Total de casos confirmados'
        )
    )
    return fig

def sintomas():
    tabla = survey.groupby(['Municipio', 'Sintomas']).size().to_frame(name = 'Total').reset_index()
    fig = go.Figure()
    cols = ['Asintomática', 'Sintomática']
    colors = ['rgba(58, 71, 80)', 'rgba(246, 78, 139)']
    nombres= ['Asintomáticos', 'Sintomático']

    for i in range(len(cols)):    
        fig.add_trace(go.Bar(
            x=tabla[tabla['Sintomas'] == cols[i]]['Municipio'].values,
            y=tabla[tabla['Sintomas'] == cols[i]]['Total'],            
            name=nombres[i],
            hoverinfo = 'y',
            marker=dict(
                color=colors[i],
                #line=dict(color='rgba(58, 71, 80, 1.0)', width=3)
                opacity = 0.85
            ),
            base = 0,
            width = 0.4
        ))

    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = tabla.Municipio.unique() ,
            zeroline=True,
        ),
        legend_orientation="h",
        legend=dict(x=-.1, y=1.2),     
        barmode='group',
        bargap=0.4,
        bargroupgap = 1,    
        margin={'t': 20, 'r':20, 'b':0, 'l':0},
        plot_bgcolor = 'rgb(235,235,235)',
        height = 350
    )
    return fig

def imagen():    
    card = html.Div([        
            html.Img(src = "./assets/uo.png",
                className='img-fluid px-3 px-sm-4 mt-3 mb-4',
                style = {'width' : '25rem'})                                  
            ], className='col-xl-2 col-md-4 mb-4')
    return(card)

def muestrasProvincias():
    
    x = np.datetime_as_string( muestras['FR'].unique(), unit='D')
    y = muestras[muestras['PROVINCIA']=='SANTIAGO'].groupby('FR').sum().sum(1).values

    provincias = ['GRANMA', 'LAS TUNAS', 'HOLGUÍN', 'GUANTÁNAMO', 'OTRO']
    names = ['Granma', 'Las Tunas', 'Holguín', 'Guantánamo', 'Otro']
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y,
                    mode='lines+markers+text',
                    name='Santiago de Cuba',
                    text = y,
                    textposition = "bottom center",
                    textfont = dict(color='rgb(0,0,0)'),
                    hoverinfo = 'x',
                    line=dict(width = 4),
                    marker=dict(size=12)),
                    )
    for num, prov in enumerate(provincias):
        y = muestras[muestras['PROVINCIA']==prov].groupby('FR').sum().sum(1).values
        fig.add_trace(go.Scatter(x=x, 
                    y=y,
                    mode='lines+markers+text',
                    name=names[num],
                    text = y,
                    textposition = "bottom center",
                    textfont = dict(color='rgb(0,0,0)'),
                    hoverinfo = 'x',
                    line=dict(width = 4),
                    marker=dict(size=12),
                    visible='legendonly'),                    
                    )
    fig.update_layout(
        margin={'t':20 ,'r':20, 'l':0},
        plot_bgcolor = 'rgb(235,235,235)',
        height = 350,
        xaxis = dict(
            title = 'Fechas de análisis de las muestras',
            tickvals=x,
            tickformat = '%m-%d',
        ),
        legend_orientation="h",     
        legend=dict(x=-.1, y=1.1),
        )

    return fig

def positividad():
    x = np.datetime_as_string( muestras['FR'].unique(), unit='D')

    y = muestras[muestras['PROVINCIA']=='SANTIAGO'].groupby('FR').sum()    
    
    positivos = np.cumsum(y[['POS-COVID-19', 'POS-COVID-19/EVOLUTIVO DE CONFIRMADO']].sum(1)).values
       
    totalesCum = np.cumsum(y.sum(1)).values    
    positividad = (positivos*100)/totalesCum

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=positividad,
                    mode='lines+markers+text',
                    name='Santiago de Cuba',
                    text = positividad,
                    textposition = "bottom center",
                    texttemplate =  '%{y:.1f}',
                    textfont = dict(color='rgb(0,0,0)'),
                    line=dict(width = 4),
                    hoverinfo = 'x',
                    marker=dict(size=12)),                  
                )
    
    provincias = ['GRANMA', 'LAS TUNAS', 'HOLGUÍN', 'GUANTÁNAMO']
    names = ['Granma', 'Las Tunas', 'Holguín', 'Guantánamo']
    
    for col, prov in enumerate(provincias):
        y = muestras[muestras['PROVINCIA']==prov].groupby('FR').sum()
        positivos = np.cumsum(y[['POS-COVID-19', 'POS-COVID-19/EVOLUTIVO DE CONFIRMADO']].sum(1)).values       
        totalesCum = np.cumsum(y.sum(1)).values    
        positividad = (positivos*100)/totalesCum

        fig.add_trace(go.Scatter(x=x, y=positividad,
            mode='lines+markers+text',
            name=names[col],
            text = positividad,
            textposition = "bottom center",
            texttemplate =  '%{y:.1f}',
            textfont = dict(color='rgb(0,0,0)'),
            line=dict(width = 4),
            hoverinfo = 'x',
            visible='legendonly',
            marker=dict(size=12)),                  
        )
    fig.update_layout(
            margin={'t':0 ,'r':20, 'l':0},
            plot_bgcolor = 'rgb(235,235,235)',
            height = 350,
            xaxis = dict(
                title = 'Fechas de análisis de las muestras',
                tickvals=x,
                tickformat = '%m-%d',
            ),
            legend_orientation="h",     
            legend=dict(x=-.1, y=1.1),
    )
    return fig

summary = html.Div([
                    #imagen(),
                    create_top('Fecha', str(ingresosDF.iloc[-1]['Fecha'].day) + "/" + str(ingresosDF.iloc[-1]['Fecha'].month
                    )),
                    create_top('Confirmados', ultimoDia[3]),
                    create_top('Ingresados', ingresosDF.dropna(1).iloc[-1]['Pacientes Ingresados']),
                    create_top('Altas Médicas', ultimoDia[4]),
                    create_top('Graves', ultimoDia[7]),                    
                    create_top('Críticos', ultimoDia[8]),
                    create_top('Fallecidos', ultimoDia[6])],
                    className = 'row', style={"justify-content":"space-around"})

app = dash.Dash(__name__)
app.title = 'COVID 19 Santiago de Cuba'
server = app.server
application = app.server
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

@server.route("/data/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(DATA_PATH, "COVID-19.xlsx", as_attachment=True)



app.layout = html.Div([
    html.Nav([ 
            html.H1(className='h3 mb-0 text-gray-800', children='SITUACIÓN DE LA COVID-19 EN SANTIAGO DE CUBA'),            
          ], className='navbar navbar-expand navbar-light bg-white topbar mb-2 static-top shadow d-sm-flex align-items-center justify-content-center mb-2' ),
    summary,
    
    #confirmados stgo, confirmados pais
    html.Div([
            # Area Chart -->
            html.Div([ 
              html.Div([ 
                # Card Header - Dropdown -->
                html.Div([
                  html.H6(className='text-gray-100 m-0 font-weight-bold text-primary', children='Casos confirmados en Santiago de Cuba'),                  
                ], className='card-header bg-gradient-primary py-2 d-flex flex-row align-items-center justify-content-between'),
                # Card Body -->
                    dcc.Graph(
                        id='confirmados_stg',
                        figure=confirmadosStgo(),
                        config={
                            'displayModeBar': False
                        } 
                    ),
                    
              ], className='card shadow mb-4'),
            ], className='col-xl-8 col-lg-7 px-1'),
            # Pie Chart -->
            html.Div([ 
              html.Div([                 
                html.Div([
                  html.H6(className='text-gray-100 m-0 font-weight-bold text-primary', children='Casos Confirmados por Provincias'),                  
                ], className='card-header bg-gradient-primary py-2 d-flex flex-row align-items-center justify-content-between'),
                  dcc.Graph(
                        #id='casosMcpiosPie',
                        #figure=casosMcpios('Pie'),
                        id='casosPais',
                        figure=totalCasosPais(),
                        config={
                            'displayModeBar': False
                        } 
                    ),                  
              ], className='card shadow mb-4'),
            ], className='col-xl-4 col-lg-5 px-1'),
          ], className='row'),

    # riesgo stgo, sintomas
    html.Div([
            # Area Chart -->
            html.Div([ 
              html.Div([ 
                # Card Header - Dropdown -->
                html.Div([
                  html.H6(className='text-gray-100 m-0 font-weight-bold text-primary', children='Riesgo Epidemiológico en los municipios de Santiago de Cuba (10000 hab)'),                  
                ], className='card-header bg-gradient-primary py-2 d-flex flex-row align-items-center justify-content-between'),
                # Card Body -->
                    dcc.Graph(
                        id='riesgoSantiago',
                        figure=riesgoSantiago(),
                        config={
                            'displayModeBar': False
                        } 
                    ),
              ], className='card shadow mb-4'),
            ], className='col-xl-8 col-lg-7 px-1'),
            # Pie Chart -->
            html.Div([ 
              html.Div([                 
                html.Div([
                  html.H6(className='text-gray-100 m-0 font-weight-bold text-primary', children='Relación de casos sintomáticos y asintomáticos'),                  
                ], className='card-header bg-gradient-primary py-2 d-flex flex-row align-items-center justify-content-between'),
                  dcc.Graph(
                        id='sintomas',
                        figure=sintomas(),
                        config={
                            'displayModeBar': False
                        } 
                    ),                  
              ], className='card shadow mb-4'),
            ], className='col-xl-4 col-lg-5 px-1'),
          ], className='row'),

    #riesgo Cuba
    html.Div([
            # Area Chart -->
            html.Div([ 
              html.Div([ 
                # Card Header - Dropdown -->
                html.Div([
                  html.H6(className='text-gray-100 m-0 font-weight-bold text-primary', children='Riesgo epidemiológico en las provincias de Cuba (100000 hab)'),                  
                ], className='card-header bg-gradient-primary py-2 d-flex flex-row align-items-center justify-content-between'),
                # Card Body -->
                    dcc.Graph(
                        id='riesgoCuba',
                        figure=riesgoCuba(),
                        config={
                            'displayModeBar': False
                        } 
                    ),
              ], className='card shadow mb-4'),
            ], className='col-xl-12 col-lg-12 px-1'),            
          ], className='row'),

    #muestrasProvincias y municipios
    html.Div([
        # Area Chart -->
        html.Div([ 
        html.Div([ 
            # Card Header - Dropdown -->
            html.Div([
            html.H6(className='text-gray-100 m-0 font-weight-bold text-primary', children='Relación de muestras analizadas por provincias'),                  
            ], className='card-header bg-gradient-primary py-2 d-flex flex-row align-items-center justify-content-between'),
            # Card Body -->
                dcc.Graph(
                    id='muestrasProvincias',
                    figure=muestrasProvincias(),
                    config={
                        'displayModeBar': False
                    } 
                ),
        ], className='card shadow mb-4'),
        ], className='col-xl-7 col-lg-7 px-1'),
        # Pie Chart -->
        html.Div([ 
            html.Div([                 
            html.Div([
                html.H6(className='text-gray-100 m-0 font-weight-bold text-primary', children='Relación por Municipios y Áreas de Salud'),                  
            ], className='card-header bg-gradient-primary py-2 d-flex flex-row align-items-center justify-content-between'),
                dcc.Graph(
                    id='municipioAreaSalud',
                    figure=mcpiosAreaSalud(),
                    config={
                        'displayModeBar': False
                    } 
                ),                  
            ], className='card shadow mb-4'),
        ], className='col-xl-5 col-lg-5 px-1'),                 
    ], className='row'),
    
    #positividad y muestras
    html.Div([
        # Area Chart -->
        html.Div([ 
        html.Div([ 
            # Card Header - Dropdown -->
            html.Div([
            html.H6(className='text-gray-100 m-0 font-weight-bold text-primary', children='Positividad de las muestras analizadas por provincias'),                  
            ], className='card-header bg-gradient-primary py-2 d-flex flex-row align-items-center justify-content-between'),
            # Card Body -->
                dcc.Graph(
                    id='positividad',
                    figure=positividad(),
                    config={
                        'displayModeBar': False
                    } 
                ),
        ], className='card shadow mb-4'),
        ], className='col-xl-7 col-lg-7 px-1'),
        # Pie Chart -->
        html.Div([ 
            html.Div([                 
            html.Div([
                html.H6(className='text-gray-100 m-0 font-weight-bold text-primary', children='Relación de casos confirmados por Sexo y Grupo Etáreo'),                  
            ], className='card-header bg-gradient-primary py-2 d-flex flex-row align-items-center justify-content-between'),
                dcc.Graph(
                    id='generoEdad',
                    figure=generoEdad(),
                    config={
                        'displayModeBar': False
                    } 
                ),                  
            ], className='card shadow mb-4'),
        ], className='col-xl-5 col-lg-5 px-1'),         
    ], className='row'),
    
    # 3era fila de graficos
    html.Div([
            # Area Chart -->
            html.Div([ 
                html.Div([                 
                html.Div([
                    html.H6(className='text-gray-100 m-0 font-weight-bold text-primary', children='Relación de Muestras Analizadas'),                  
                ], className='card-header bg-gradient-primary py-2 d-flex flex-row align-items-center justify-content-between'),
                    dcc.Graph(
                        id='muestrasStgo',
                        figure=muestrasStgo(),
                        config={
                            'displayModeBar': False
                        } 
                    ),                  
                ], className='card shadow mb-4'),
            ], className='col-xl-6 col-lg-6 px-1'),               
            # Pie Chart -->
            html.Div([ 
              html.Div([                 
                html.Div([
                  html.H6(className='text-gray-100 m-0 font-weight-bold text-primary', children='Relación de ingresos - Adultos/Niños'),                  
                ], className='card-header bg-gradient-primary py-2 d-flex flex-row align-items-center justify-content-between'),
                  dcc.Graph(
                        id='ingresosAdulto',
                        figure=ingresos('Adultos','Niños', 'Adultos', 'Niños'),
                        config={
                            'displayModeBar': False
                        } 
                    ),                  
              ], className='card shadow mb-4'),
            ], className='col-xl-6 col-lg-6 px-1'),
          ], className='row'),

    #cuarta fila de graficos
     
    html.Div([
                # Area Chart -->
                html.Div([ 
                html.Div([ 
                    # Card Header - Dropdown -->
                    html.Div([
                    html.H6(className='text-gray-100 m-0 font-weight-bold text-primary', children='Relación de Ingresos - Cubanos/Extranjeros'),                  
                    ], className='card-header bg-gradient-primary py-2 d-flex flex-row align-items-center justify-content-between'),
                    # Card Body -->
                        dcc.Graph(
                            id='ingresosCubanos',
                            figure=ingresos('Cubano','Extranjero', 'Cubanos', 'Extranjeros'),
                            config={
                                'displayModeBar': False
                            } 
                        ),
                ], className='card shadow mb-4'),
                ], className='col-xl-6 col-lg-6 px-1'),
                # Pie Chart -->
                html.Div([ 
                    html.Div([ 
                        # Card Header - Dropdown -->
                        html.Div([
                        html.H6(className='text-gray-100 m-0 font-weight-bold text-primary', children='Relación de Ingresos - Hombres/Mujeres'),                  
                        ], className='card-header bg-gradient-primary py-2 d-flex flex-row align-items-center justify-content-between'),
                        # Card Body -->
                            dcc.Graph(
                                id='ingresosSexo',
                                figure=ingresos('Hombres','Mujeres', 'Hombres', 'Mujeres'),
                                config={
                                    'displayModeBar': False
                                } 
                            ),
                    ], className='card shadow mb-4'),
                ], className='col-xl-6 col-lg-6 px-1'),
            ], className='row'),

    # html.Link(children = ['Puede consultar toda la información aqui: '],
    # href = "./assets/COVID-19.xlsx")
    html.P([
        'Acá puede descargar toda la información empleada: ',
        html.A(children = 'covid19SCU', href="./data/COVID-19.xlsx")
    ],),
    
    
], className='container-fluid')


if __name__ == '__main__':
    app.run_server(debug=True)
