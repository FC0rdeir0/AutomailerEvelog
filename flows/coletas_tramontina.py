import streamlit as st
import pandas as pd

from services.email_lookup import carregar_emails_unidades
from services.email_config import configurar_email, validar_config_email
from services.email_sender import enviar_emails
from utils.text import remover_acentos
from utils.email_form import render_email_config

def run(uploaded, email_user, senha):
    df_emails, emails_unidades = carregar_emails_unidades("bases/emails_unidades.xlsx")

    if not uploaded:
        st.warning("Envie um arquivo")
        return

    file = uploaded[0] if isinstance(uploaded, list) else uploaded

    try:
        file.seek(0)
    except:
        pass

    if file.name.lower().endswith(".csv"):
        df = pd.read_csv(file, header=1)
    else:
        df = pd.read_excel(file, header=1)

    df.columns = df.columns.astype(str).str.strip().str.upper()

    df.columns = [
        remover_acentos(col)
        for col in df.columns
    ]

    st.divider()

    st.subheader("Upload dos PDFs")

    col_pdfs, _ = st.columns([1, 2])

    with col_pdfs:
        pdfs = st.file_uploader(
            "Importar PDFs",
            type=["pdf"],
            accept_multiple_files=True
        )

        if not pdfs:
            st.info("Aguardando upload dos PDFs.")
            st.stop()
    
    
    pdf_map = {
        pdf.name.replace(".pdf", "").strip(): pdf
        for pdf in pdfs
    }

    df["ORDEM"] = df["ORDEM"].astype(str).str.strip()

    df["PDF"] = df["ORDEM"].map(pdf_map)

    df_envio = df[df["PDF"].notna()].copy()

    df_sem_pdf = df[df["PDF"].isna()].copy()

    if not df_sem_pdf.empty:

        st.warning("Pedidos abaixo estão sem PDF e serão ignorados no envio.")

        cols = ["ORDEM", "ORIGEM"] if "ORIGEM" in df.columns else ["ORDEM"]

        st.dataframe(df_sem_pdf[cols])

        st.divider()

    if df_envio.empty:
        st.warning("Nenhum pedido com PDF encontrado.")
        st.stop()

    config = render_email_config(show_assunto=False)

    cc_input = config.get("cc_input")
    texto_base = config.get("texto_base")

    if st.button("🚀 Enviar e-mails"):

        config = configurar_email(cc_input, None, texto_base)

        erros = validar_config_email(config, False, True)

        if erros:
            for erro in erros:
                st.warning(erro)
            st.stop()

        grupos = df_envio.groupby("ORIGEM")    
        
        lista_envios = []

        for unidade, pedidos_unidade in grupos:

            emails_to = emails_unidades.get(unidade, [])

            ordens = pedidos_unidade["ORDEM"].astype(str).tolist()

            ordens_txt = " ".join(ordens)

            assunto = f"PRÉ ALERTA DE COLETA TRAMONTINA - {ordens_txt}"

            if isinstance(emails_to, str):
                emails_to = [e.strip() for e in emails_to.split(",") if e.strip()]

            if not emails_to:
                continue

            anexos = [pdf for pdf in pedidos_unidade["PDF"] if pdf is not None]

            tabela_html = pedidos_unidade.drop(columns=["PDF"]).to_html(index=False)

            cc_list = config["cc"] or []

            if isinstance(cc_list, str):
                cc_list = [e.strip() for e in cc_list.split(",") if e.strip()]

            corpo_html = f"""
                <p>{config['corpo']}</p>
                <br>
                {tabela_html}
                <br><br>
                <p><i>Mensagem automática.</i></p>
            """

            lista_envios.append({
                "unidade": unidade,
                "to": emails_to,
                "cc": cc_list,
                "subject": assunto,
                "html": corpo_html,
                "anexos": anexos,
                "qtd_pedidos": len(pedidos_unidade)
            })

        if not lista_envios:
            st.warning("Nenhum e-mail foi gerado")
            st.stop()

        try:
            enviar_emails(lista_envios, email_user, senha)

        except ValueError as e:
            st.error(str(e))
            st.stop()