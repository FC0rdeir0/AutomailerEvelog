import streamlit as st
import pandas as pd

@st.cache_data
def carregar_emails_unidades(caminho_arquivo):

    df = pd.read_excel(caminho_arquivo, header=0)

    df.columns = ["UNIDADE", "EMAIL"]

    df["UNIDADE"] = df["UNIDADE"].astype(str).str.strip().str.upper()
    df["EMAIL"] = df["EMAIL"].astype(str).str.strip()

    mapa = dict(zip(df["UNIDADE"], df["EMAIL"]))

    return df, mapa