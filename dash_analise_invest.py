pip install yfinance pymannkendall dash pyngrok

import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pymannkendall as mk
import dash
from dash import dcc, html, Input, Output
from dash import jupyter_dash
jupyter_dash.default_mode="external"

# Função para baixar dados
def get_stock_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

# Função para plotar o gráfico
def plot_stock_chart(data, local_max, local_min, trend_lines):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Preço de Fechamento', line=dict(color='royalblue')))
    fig.add_trace(go.Scatter(x=data.index, y=local_max, mode='markers', name='Topos', marker=dict(color='green', symbol='triangle-up', size=10)))
    fig.add_trace(go.Scatter(x=data.index, y=local_min, mode='markers', name='Fundos', marker=dict(color='red', symbol='triangle-down', size=10)))
    fig.add_trace(go.Scatter(x=[''], y=[''], mode='lines', name='Mann Kendall e Sen’s slope', line=dict(color='orange')))

    # Adiciona uma legenda apenas para a primeira regressão
    #fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='Regressões', line=dict(color='orange')))

    for i, trend_line in enumerate(trend_lines):
        fig.add_trace(go.Scatter(x=trend_line['subset_index'], y=trend_line['y_pred'], mode='lines', showlegend=False, line=dict(color='orange')))

    fig.update_layout(
        xaxis=dict(title='Data'),
        yaxis=dict(title='Preço'),
        title=f'Gráfico\n\n',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        title_x=0.5,
        xaxis_linecolor='black',
        yaxis_linecolor='black',
        template='plotly_white',
        margin=dict(l=0, r=0, t=50, b=50),
    )


    return fig

# Instância do Dash
app = dash.Dash(__name__)
server - app.server
# Layout do aplicativo Dash com navbar
app.layout = html.Div(style={'textAlign': 'center'}, children=[
        html.Nav(style={'backgroundColor': '#000000', 'padding': '10px', 'display': 'flex', 'justify-content': 'space-between','border-radius': '12px','text-align': 'center'}, children=[
        html.Div(style={'display': 'flex', 'align-items': 'center'}, children=[
        #html.Img(src='', alt='Logo do App Pedal', style={'height': '50px', 'width': '50px'}),
        html.H3(style={'color': 'white', 'margin-left': '30px','text-align': 'center'}, children="PEDAL ANALISE INVEST"),
        ]),
        html.Div(style={'display': 'flex'}, children=[
            dcc.Link('Sobre o Smorg', href='https://callou.pythonanywhere.com/index', style={'color': 'white', 'padding': '20px'}, target='_blank')
        ]),
    ]),
    html.Br(),
    html.Br(),
    html.Label([html.B("Digite o Código da Ação: ")]),
    dcc.Input(id='stock-input', type='text', value='BBAS3.SA', style={'width': '90px','font-size': '16px'}),
    html.Br(),
    html.Br(),
    html.Label([html.B("   Selecione o Intervalo de Datas: ")]),
    dcc.DatePickerRange(
        minimum_nights=5,
        clearable=True,
        with_portal=True,
        id='date-range-picker',
        start_date='2023-01-02',
        end_date='2023-10-30',
        display_format='DD-MM-YYYY',
        style={'font-size': '16px'}
    ),
    html.Br(),
    html.Br(),
    html.Label([html.B("Número de Dias para Aplicação Mann Kendall e Sen’s slope: ")]),
    dcc.Input(id='regression-days', type='number', value=10, style={'width': '50px','font-size': '16px'}),
    html.Br(),
    html.Br(),
    html.Label([html.B("  Digite o Aporte Inicial: ")]),
    dcc.Input(id='initial-investment', type='number', value=100, style={'width': '80px','font-size': '16px'}),
    html.Br(),
    html.Br(),
    html.Button(
        'Atualizar Gráfico e Calcular Resultados',
        id='update-button',
        style={'background-color': '#5dd55d', 'color': 'black', 'font-size': '17px', 'border-radius': '10px', 'margin-top': '9px',
               'width': '250px', 'height': '60px', 'padding': '10px', 'opacity': '0.8'}
    ),
 dcc.Graph(id='stock-chart'),
    html.Br(),
    html.Div(id='strategy-results', style={'font-size': '18px','border': '2px solid #000000', 'padding': '20px', 'border-radius': '10px','width':'55%', 'margin': 'auto'}),html.Br(),
    html.Br(),
    html.Br(),
    html.Footer(style={'padding-bottom': '40px','background-color': 'white', 'color': 'black',  'bottom': '0', 'border': '1px solid #000000', 'height': '10px', 'border-radius': '10px',}, children=[
        html.P("Copyright © 2023 - PEDAL. Todos os direitos reservados.")
    ])
])


def selecionar_valores_por_indices(lista, indices):
    valores_indice_proximotopo = [lista[indice] for indice in indices]
    return valores_indice_proximotopo

def selecionar_proximo_fundo(indices, indice_anterior):
    indice_fundo_proximoTopoAnterior = None

    for indice in indices:
        if indice > indice_anterior:
            indice_fundo_proximoTopoAnterior = indice
            break

    return indice_fundo_proximoTopoAnterior

def aux_function(data, posicoes_topos_tendencia_alta):
    # CELL 1
    listaFundos = data['local_min'].tolist()
    indiceDataFundos=[]
    indice=0
    valoresFundo=[]
    for i in listaFundos:
        if (not(np.isnan(i))):
            #print(i)
            valoresFundo.append(i)
            indiceDataFundos.append(indice)
        indice+=1

    # CELL 2
    lista_indices = indiceDataFundos
    indices_referencia = posicoes_topos_tendencia_alta
    indice_fundo_proximoTopoAnterior_lista = []
    for indice_referencia in indices_referencia:
        indice_fundo_proximoTopoAnterior = selecionar_proximo_fundo(lista_indices, indice_referencia)
        indice_fundo_proximoTopoAnterior_lista.append(indice_fundo_proximoTopoAnterior)
        indice_fundo_proximoTopoAnterior_lista = list(filter(lambda x: x is not None, indice_fundo_proximoTopoAnterior_lista))

    # CELL 3
    listaTodosValores = data['Close'].tolist()
    minha_lista = listaTodosValores
    meus_indices = indice_fundo_proximoTopoAnterior_lista
    valores_indice_proximotopo = selecionar_valores_por_indices(minha_lista, meus_indices)
    return valores_indice_proximotopo

# Callback para atualizar o gráfico e calcular resultados quando o botão é clicado
@app.callback(
    [Output('stock-chart', 'figure'),
     Output('strategy-results', 'children')],
    [Input('update-button', 'n_clicks')],
    [dash.dependencies.State('stock-input', 'value'),
     dash.dependencies.State('date-range-picker', 'start_date'),
     dash.dependencies.State('date-range-picker', 'end_date'),
     dash.dependencies.State('regression-days', 'value'),
     dash.dependencies.State('initial-investment', 'value')]
)
def update_chart_and_calculate_results(n_clicks, stock_input, start_date, end_date, regression_days, initial_investment):

    # Obter os dados da ação utilizando o ticker fornecido pelo usuário e as datas selecionadas
    data = get_stock_data(stock_input, start_date, end_date)

    # Encontrar os topos (máximos) e fundos (mínimos)
    data['local_max'] = data['Close'][(data['Close'].shift(1) < data['Close']) & (data['Close'].shift(-1) < data['Close'])]
    data['local_min'] = data['Close'][(data['Close'].shift(1) > data['Close']) & (data['Close'].shift(-1) > data['Close'])]

    # Lista para armazenar as regressões
    trend_lines = []


    data['data'] = data.index
    listaTodosValores = data['Close'].tolist()
    listaTodosValoresData = data['data'].tolist()
    listaTopos = data['local_max'].tolist()
    valores_topos_tendencia_alta = []
    posicoes_topos_tendencia_alta = []


    # Calcular e plotar a regressão para os N dias anteriores a cada topo, onde N é o número de dias especificado pelo usuário
    for i, top_date in enumerate(data['local_max'].dropna().index):
        if top_date - pd.DateOffset(days=regression_days) >= data.index[0]:
            start_date = top_date - pd.DateOffset(days=regression_days)
            end_date = top_date
            subset = data[start_date:end_date]
            x = np.arange(len(subset))
            trend, h, p, z, Tau, s, var_s, slope, intercept = mk.original_test(subset['Close'])
            y_pred = intercept + slope * x

            if trend == 'increasing' and p < 0.05 and s >= 0:
                trend_lines.append({'subset_index': subset.index, 'y_pred': y_pred})
                posicoes_topos_tendencia_alta.append(listaTopos.index(subset['local_max'].iloc[-1]))  # Armazena a posição do topo em tendência de alta
                valores_topos_tendencia_alta.append(subset['Close'].iloc[-1])  # Armazena o valor do topo em tendência de alta


    # Plotar o gráfico
    fig = plot_stock_chart(data, data['local_max'], data['local_min'], trend_lines)

    valores_indice_proximotopo = aux_function(data, posicoes_topos_tendencia_alta)

    # Calcular resultados das estratégias
    resultado_buy_sell = stock_buy_sell(
        data,
        regression_days,
        initial_investment,
        posicoes_topos_tendencia_alta,
        valores_topos_tendencia_alta,
        valores_indice_proximotopo,
        listaTodosValoresData,
        listaTodosValores)


    resultado_buy_hold = buy_and_hold(data, initial_investment)

    # Calcular porcentagem de ganho ou perda
    ganho_perda_percentual_buy_sell = ((resultado_buy_sell - initial_investment) / initial_investment) * 100
    ganho_perda_percentual_buy_hold = ((resultado_buy_hold - initial_investment) / initial_investment) * 100

    # Exibir resultados
    results_text = [
        html.B(f"- Resultado Estratégia Mann Kendall: R$ {resultado_buy_sell:.2f} | "),
        html.B(f"Porcentagem Referente ao Aporte Inicial: {ganho_perda_percentual_buy_sell:.2f}%"), html.Br(),
         html.B(f"-----------------------------------------------------------------"), html.Br(),
        html.B(f"- Resultado Buy and Hold: R$ {resultado_buy_hold:.2f} | "),
        html.B(f"Porcentagem Referente ao Aporte Inicial: {ganho_perda_percentual_buy_hold:.2f}%",), html.Br(), html.Br(),


    ]


    return fig, results_text

# Função para estratégia de compra e venda de ações
def stock_buy_sell(
        data,
        regression_days,
        initial_investment,
        posicoes_topos_tendencia_alta,
        valores_topos_tendencia_alta,
        valores_indice_proximotopo,
        listaTodosValoresData,
        listaTodosValores):

    valor_especulado = initial_investment
    resultado_final = 0

    # for indice, valor_topo, valor_fundo in zip(
    #     data['local_max'].dropna().index,
    #     data['local_max'].dropna().values,
    #     data['local_min'].dropna().values):

    for indice, valor_topo, valor_fundo in zip(
        posicoes_topos_tendencia_alta,
        valores_topos_tendencia_alta,
        valores_indice_proximotopo
    ):
        comprou = False
        vendeu = False
        valor_compra = 0
        valor_venda = 0
        retorno = 0
        qtd_ações = 0

        zip_lists = zip(listaTodosValoresData, listaTodosValores)

        for _, valor_atual in list(zip_lists)[indice+1:]:
            # Ato de comprar
            if not comprou and valor_atual > valor_topo:
                comprou = True
                valor_compra = valor_topo
                distancia = valor_atual - valor_fundo
                porcentagem = (distancia / valor_fundo)
                # Especulação compra
                qtd_ações = valor_especulado / valor_compra
                valor_especulado = qtd_ações * valor_compra

            # Ato de vender
            # Se o valor subiu acima 3x a porcentagem do fundo ou abaixou abaixo 1x a porcentagem do fundo anterior, venda ação
            if comprou and (valor_atual >= valor_compra + (valor_compra * porcentagem * 3) or valor_atual < valor_fundo * (1 - porcentagem)):
                valor_venda = valor_atual
                # Especulação venda
                valor_especulado = qtd_ações * valor_venda
                resultado_final = valor_especulado
                vendeu = True
                # Interrompendo iteração atual, pois venda e compra da referência atual foram realizadas
                break

        # if not comprou:
        #     resultado_final += valor_especulado
        # if not vendeu:
        #     # Se a venda não foi realizada, manter as ações até o final do período
        #     resultado_final += qtd_ações * data['Close'].iloc[-1]

    return resultado_final

# Função para estratégia Buy and Hold
def buy_and_hold(data, initial_investment):
    primeiro_valor = data['Close'].iloc[0]
    ultimo_valor = data['Close'].iloc[-1]
    qtd_ações = initial_investment / primeiro_valor
    resultado_final = qtd_ações * ultimo_valor
    return resultado_final

# Rodar o servidor Dash externamente
if __name__ == '__main__':
    app.run_server(mode='external')
