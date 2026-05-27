import streamlit as st

def render_email_config(show_cc=True, show_assunto=True, show_corpo=True):
    st.subheader("Configuração do e-mail")

    result = {}

    if show_cc:
        result["cc_input"] = st.text_input(
            "CC (separados por vírgula)",
            placeholder="email1@evelog.com.br, email2@evelog.com.br",
            key="cc_input"
        )

    if show_assunto:
        result["assunto"] = st.text_input(
            "Assunto",
            placeholder="Assunto do e-mail",
            key="assunto"
        )

    if show_corpo:
        result["texto_base"] = st.text_area(
            "Corpo do e-mail",
            placeholder="Digite a mensagem",
            height=150,
            key="texto_base"
        )

    return result