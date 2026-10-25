import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.title("Monitoramento de Ativos B3")
ticker = st.text_input("Digite o Ticker (ex: MXRF11, PETR4)", value="MXRF11")
token = st.secrets["BRAPI_TOKEN"]

if st.button("Analisar Ativo"):
    url = f"https://brapi.dev/api/quote/{ticker}?range=1mo&interval=1d&token={token}"
    response = requests.get(url).json()
    
    if 'results' in response:
        dados = response['results'][0]
        st.metric(label=f"Cotação Atual ({ticker})", value=f"R$ {dados['regularMarketPrice']}")
        
        df = pd.DataFrame(dados['historicalDataPrice'])
        df['date'] = pd.to_datetime(df['date'], unit='s')
        
        fig = px.line(df, x='date', y='close', title='Variação de Preço (30 Dias)')
        st.plotly_chart(fig)
    else:
        st.error("Ativo não encontrado ou erro na API.")
