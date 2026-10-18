import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Mercado Mateus",
    page_icon="🛒",
    layout="centered"
)

nome = "Mateus"
idade = 17

st.write("Bem-vindo: ", nome, "sabemos que você tem: ", idade, "anos")

st.title("Mercado Mateus")
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

def calcular_preco_total(item: str, qtd: int) -> float:
    preco_unitario = precos_itens[item]
    return preco_unitario * qtd

col1, col2 = st.columns(2)

with col1:
    quantidade = st.number_input("Quantidade:", min_value=1, value=1, step=1)

with col2:
    valor_pago = st.number_input(
        "Valor pago em dinheiro (R$):",
        min_value=0.0,
        value=0.0,
        step=1.0
    )

valor_total = round(calcular_preco_total(item_selecionado, quantidade), 2)

st.metric(label=f"Total a pagar ({item_selecionado})", value=f"R$ {valor_total:.2f}")

resultado = None

if st.button("Calcular troco", type="primary"):
    if valor_pago < valor_total:
        st.error(f"Valor insuficiente. O total da compra é R$ {valor_total:.2f}.")
    else:
        resultado = round(valor_pago - valor_total, 2)

if resultado is not None:
    st.success(f"**Troco:** R$ {resultado:.2f}")