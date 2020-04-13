
def confirmadosStgo():
    fig = go.Figure()
    x = casosConfirmados['Fecha']
    y = casosConfirmados['Casos Confirmados Acumulados']
    fig.add_trace(go.Scatter(x=x, y=y,
                        mode='lines+markers',
                        name='Casos Confirmados Acumulados',
                        line=dict(width = 4),
                        marker=dict(size=12)))
    fig.add_trace(go.Scatter(x=x, y=casosConfirmados['Nuevos Casos Confirmados'],
                        mode='lines+markers',
                        name='Nuevos Casos Confirmados',
                        line=dict(width = 4),
                        marker=dict(size=12)))

    fig.update_layout(
        xaxis=dict(
            title = 'Fecha desde el Pimer caso confirmado',
            showline=True,

            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            ),        
        yaxis_title='Total de casos',   
        legend_orientation="h", 
        margin={'t': 0},
        legend=dict(x=-.1, y=1.1)    
    )    
    return fig

def casosMcpios():
    mcpios = survey.groupby('Municipio').size()
    labels = mcpios.index
    values = mcpios.values
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0.1, 0.1, 0.1, 0.1], 
                                )])
    fig.update_traces(hoverinfo='label+percent+value', textinfo='label',
                    marker=dict(line=dict(color='#000000', width=2)))
    fig.update_layout(showlegend=False, margin={'t': 0},)
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
                            marker=dict(size=12)))    
    fig.update_layout(xaxis=dict(
            title = 'Fechas desde el Pimer caso confirmado en el Oriente',
            showline=True,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            ),        
            yaxis_title='Total de casos', 
            legend_orientation="h",     
            legend=dict(x=-.1, y=1.1),
            margin={'t': 0}  
            )
    return fig

def muestrasStgo():
    fig4 = go.Figure()

    x = muestras['Fecha']
    muest = muestras.set_index('Fecha')
    colors = ['#1d6996', '#edad08', '#73af48']
    for num, col in enumerate([muest.columns[2],muest.columns[1], muest.columns[3]]):
        fig4.add_bar(
            x=x, y=muest[col],
            name=col,
            marker_color=colors[num]            
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
            ),        
            yaxis = dict(
                title='Número de muestras analizadas',        
                tickvals = np.arange(0, muestras['Muestras Estudiadas'].max()+20, 20).tolist()
            ),
            uniformtext_minsize=8, 
            uniformtext_mode='hide',
            margin={'t': 1}
            )
    fig4.update_xaxes(automargin=True)
    return fig4
