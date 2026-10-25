import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.title("Monitoramento de Ativos B3")
ticker = st.text_input("Digite o Ticker (ex: MXRF11, PETR4)", value="MXRF11").upper()
token = st.secrets["BRAPI_TOKEN"]

if st.button("Analisar Ativo"):
    url = f"https://brapi.dev/api/quote/{ticker}?range=1mo&interval=1d&token={token}"
    response = requests.get(url).json()
    
    if 'results' in response:
        dados = response['results'][0]
        
        # Organização em colunas para os cartões de dados
        col1, col2 = st.columns(2)
        col1.metric(label="Cotação Atual", value=f"R$ {dados.get('regularMarketPrice', 0):.2f}")
        
        # Extração inteligente de dividendos da Brapi
        if 'dividendsData' in dados and 'cashDividends' in dados['dividendsData']:
            lista_div = dados['dividendsData']['cashDividends']
            if lista_div:
                ultimo_pagamento = lista_div[-1] # Pega o registo mais recente
                data_pag = pd.to_datetime(ultimo_pagamento['paymentDate']).strftime('%d/%m/%Y')
                valor_div = ultimo_pagamento['rate']
                col2.metric(label=f"Dividendo ({data_pag})", value=f"R$ {valor_div:.4f}")
        else:
            col2.metric(label="Dividendos", value="Sem dados recentes")

        # Construção do gráfico com layout avançado
        df = pd.DataFrame(dados['historicalDataPrice'])
        df['date'] = pd.to_datetime(df['date'], unit='s')
        
        fig = px.area(df, x='date', y='close', title=f'Variação de Preço - {ticker} (30 Dias)')
        
        # Estilização: Cor ciano, preenchimento suave e remoção do fundo
        fig.update_traces(line_color='#00C3DA', fillcolor='rgba(0, 195, 218, 0.15)')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="",
            yaxis_title="Preço (R$)",
            hovermode="x unified",
            margin=dict(l=0, r=0, t=40, b=0)
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)')
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Ativo não encontrado ou erro na API.")
