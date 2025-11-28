import streamlit as st
import pandas as pd
import unicodedata
import base64
import io
import os

# Função para normalizar textos (remover acentos e padronizar)
def normalize(text):
    if pd.isna(text):
        return ""
    text = text.strip().lower()
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    return text

# Carregar dados
@st.cache_data
def load_data():
    data = os.environ["MERITO_BASE64"]
    decoded = base64.b64decode(data)
    df = pd.read_csv(io.BytesIO(decoded), dtype=str)

    df = df.rename(columns={
        "NOME": "nome",
        "CPF": "cpf",
        "NOTA": "nota"
    })

    df["cpf"] = (
        df["cpf"].astype(str)
        .str.replace(".", "", regex=False)
        .str.replace("-", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.strip()
    )

    df["nome_norm"] = df["nome"].apply(normalize)
    return df

# Configuração do app
st.set_page_config(page_title="Consulta de Nota", layout="centered")

# Logo
st.image("logo.png", width=300)

st.title("Consulta de Nota - Meritocracia")
st.write("Digite seu primeiro nome e CPF (apenas números).")

# Campos de entrada
nome_input = st.text_input("Primeiro nome")
cpf_input = st.text_input("CPF (somente números)")

df = load_data()

# Lógica da busca
if st.button("VER NOTA"):
    if not cpf_input.isdigit():
        st.error("CPF inválido. Digite apenas números, sem pontos ou traço.")
    else:
        nome_norm = normalize(nome_input)

        # Busca DEFINITIVA: nome contém nome digitado e CPF bate exatamente
        resultado = df[
            (df["cpf"] == cpf_input.strip()) &
            (df["nome_norm"].str.contains(nome_norm))
        ]

        if not resultado.empty:
            nota = resultado.iloc[0]["nota"]

            st.write("Sua Nota")
            st.markdown(
                f"<h1 style='text-align:center; font-size:60px;'>{nota}</h1>",
                unsafe_allow_html=True
            )
        else:
            st.error(
                "Nome e CPF não encontrados. "
                "Entre em contato com a Secretaria Municipal de Educação."
            )
