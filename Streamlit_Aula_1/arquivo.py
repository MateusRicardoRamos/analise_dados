import streamlit as st
import pandas as pd

nome = "Mateus"
idade = 17

st.write("Bem-vindo: ",nome,"sabemos que você tem: ",idade,"anos")

st.title("Meu primeiro dash")
st.subheader("Mateus Ricardo Ramos")

df = pd.DataFrame({
'Notas em Matemática': [1, 2, 3, 4],
'Notas em Português': [5, 9, 7, 10]
})

st.write(df)

precos_itens = {
    "Arroz (5kg)": 25.00,
    "Feijão (1kg)": 8.50,
    "Leite (1L)": 4.80,
    "Café (500g)": 16.00
}

item_selecionado = st.selectbox(
    "Selecione um item do supermercado:",
    options=list(precos_itens.keys())
)

quantidade = st.number_input("Quantidade:", min_value=1, value=1, step=1)

def calcular_preco_total(item: str, qtd: int) -> float:
    preco_unitario = precos_itens[item]
    return preco_unitario * qtd

valor_total = calcular_preco_total(item_selecionado, quantidade)

st.metric(label=f"Total a pagar ({item_selecionado})", value=f"R$ {valor_total:.2f}")