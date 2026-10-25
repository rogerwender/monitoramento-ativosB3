import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.title("Monitorização de Ativos - B3 e Global")
ticker = st.text_input("Digite o Ticker (ex: MXRF11, PETR4, SGOV)", value="SGOV").upper()
token = st.secrets["BRAPI_TOKEN"]

if st.button("Analisar Ativo"):
    # Adição dos parâmetros dividends=true e fundamental=true
    url = f"https://brapi.dev/api/quote/{ticker}?range=1mo&interval=1d&token={token}"
    response = requests.get(url).json()
    
    if 'results' in response:
        dados = response['results'][0]
        
        # Estrutura de três colunas para acomodar os novos indicadores
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Cotação Atual", value=f"R$ {dados.get('regularMarketPrice', 0):.2f}")
        
        # Lógica corrigida para extração de dividendos
        if 'dividendsData' in dados and 'cashDividends' in dados['dividendsData']:
            lista_div = dados['dividendsData']['cashDividends']
            if lista_div:
                ultimo_pagamento = lista_div[-1]
                data_pag = pd.to_datetime(ultimo_pagamento['paymentDate']).strftime('%d/%m/%Y')
                valor_div = ultimo_pagamento['rate']
                col2.metric(label=f"Dividendo ({data_pag})", value=f"R$ {valor_div:.4f}")
        else:
            col2.metric(label="Dividendos", value="Sem dados recentes")

        # Extração do Dividend Yield (se disponível no ativo)
        dy = dados.get('summaryDetail', {}).get('dividendYield', None)
        if dy is not None:
             col3.metric(label="Dividend Yield", value=f"{dy * 100:.2f}%")
        else:
             col3.metric(label="Dividend Yield", value="N/D")

        # Processamento do gráfico interativo
        if 'historicalDataPrice' in dados and dados['historicalDataPrice']:
            df = pd.DataFrame(dados['historicalDataPrice'])
            df['date'] = pd.to_datetime(df['date'], unit='s')
            
            fig = px.area(df, x='date', y='close', title=f'Variação de Preço - {ticker} (30 Dias)')
            fig.update_traces(line_color='#00C3DA', fillcolor='rgba(0, 195, 218, 0.15)')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="",
                yaxis_title="Preço",
                hovermode="x unified",
                margin=dict(l=0, r=0, t=40, b=0)
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)')
            
            st.plotly_chart(fig, use_container_width=True)

            # Botão de exportação de dados para planilhas
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descarregar Histórico em CSV",
                data=csv,
                file_name=f'{ticker}_historico.csv',
                mime='text/csv',
            )
        else:
            st.warning("Sem dados históricos disponíveis para este ativo.")
    else:
        st.error("Ativo não encontrado ou erro na API.")
