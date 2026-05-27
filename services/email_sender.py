import smtplib
import time
import pandas as pd
import streamlit as st

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def enviar_emails(lista_envios, email_user, senha):

    if not email_user and not senha:
        raise ValueError("Informe o e-mail e a senha.")

    if not email_user:
        st.error("Informe o e-mail do remetente.")
        st.stop()

    if not senha:
        st.error("Informe a senha do e-mail.")
        st.stop()
    
    if not lista_envios:
        st.warning("Nenhum e-mail para enviar.")
        return

    log_envio = []
    falhas_envio = []
    sem_email = []

    total = len(lista_envios)
    enviados = 0

    progress_bar = st.progress(0)
    contador_placeholder = st.empty()
    warnings_por_unidade = {}

    with st.spinner("📨 Enviando e-mails..."):

        try:
            smtp = smtplib.SMTP_SSL("email-ssl.com.br", 465, timeout=120)
            smtp.login(email_user, senha)
        except Exception as e:
            st.error(f"Erro de conexão SMTP inicial: {e}")
            return

        for envio in lista_envios:

            try:
                erro_envio = None
                enviado = False

                unidade = envio["unidade"]
                if unidade not in warnings_por_unidade:
                    warnings_por_unidade[unidade] = st.empty()
                emails_to = envio["to"]
                cc_list = list(set(envio["cc"] + [email_user]))
                assunto = envio["subject"]
                corpo_html = envio["html"]

                if not emails_to:
                    sem_email.append({
                        "unidade": unidade,
                        "df": envio.get("df"),
                        "qtd_pedidos": envio.get("qtd_pedidos", 0)
                    })
                    continue

                anexos = envio.get("anexos", [])
                anexos_processados = []

                for arquivo in anexos:
                    try:
                        arquivo.seek(0)
                        conteudo = arquivo.read()
                        anexos_processados.append((arquivo.name, conteudo))
                    except Exception as e:
                        st.warning(f"Erro ao ler {arquivo.name}: {e}")

                tentativas = 10

                for tentativa in range(tentativas):
                    try:
                        msg = MIMEMultipart()
                        msg["From"] = email_user
                        msg["To"] = ", ".join(emails_to)
                        msg["Cc"] = ", ".join(cc_list)
                        msg["Subject"] = assunto

                        msg.attach(MIMEText(corpo_html, "html"))

                        for nome, conteudo in anexos_processados:
                            part = MIMEApplication(conteudo, _subtype="pdf")
                            part.add_header(
                                "Content-Disposition",
                                "attachment",
                                filename=nome
                            )
                            msg.attach(part)

                        smtp.send_message(
                            msg,
                            to_addrs=list(set(emails_to + cc_list))
                        )

                        enviado = True
                        break

                    except Exception as e:
                        erro_envio = e

                        warnings_por_unidade[unidade].warning(
                            f"""
                        ❌ Falha no envio - {unidade}  
                        Tentativa {tentativa + 1}/{tentativas}  

                        Erro: {str(e)}
                        """
                        )

                        time.sleep(5 * (tentativa + 1))

                        try:
                            smtp.quit()
                        except:
                            pass

                        try:
                            smtp = smtplib.SMTP_SSL("email-ssl.com.br", 465, timeout=30)
                            smtp.login(email_user, senha)
                        except Exception as erro_reconexao:
                            erro_envio = erro_reconexao

                if enviado:
                    warnings_por_unidade[unidade].empty()
                    enviados += 1

                    time.sleep(5)

                    if enviados % 20 == 0:
                        try:
                            smtp.quit()
                        except:
                            pass

                        smtp = smtplib.SMTP_SSL("email-ssl.com.br", 465, timeout=30)
                        smtp.login(email_user, senha)

                    percentual = int((enviados / total) * 100)
                    progress_bar.progress(percentual)

                    contador_placeholder.markdown(
                        f"""
                        **📧 E-mails enviados:** {enviados}  
                        **📊 Progresso:** {enviados} / {total}
                        """
                    )

                    log_envio.append({
                        "Unidade": unidade,
                        "Qtd Pedidos": envio.get("qtd_pedidos", 0),
                        "Para": ", ".join(emails_to),
                        "CC": ", ".join(cc_list)
                    })

                else:
                    falhas_envio.append({
                        "Unidade": unidade,
                        "Erro": str(erro_envio) if erro_envio else "Erro desconhecido"
                    })

            except Exception as erro_geral:
                falhas_envio.append({
                    "Unidade": envio.get("unidade", "Desconhecida"),
                    "Erro": f"Erro geral: {erro_geral}"
                })
                continue

        try:
            smtp.quit()
        except:
            pass

        st.success(f"✅ {len(log_envio)} e-mails enviados com sucesso!")

        if log_envio:
            st.subheader("Log de envio")
            st.dataframe(pd.DataFrame(log_envio))

        if sem_email:
            st.warning("⚠️ Pedidos não enviados: unidades sem e-mail cadastrado")

            lista_dfs = []

            for item in sem_email:
                unidade = item["unidade"]
                df_unidade = item["df"]

                if df_unidade is not None:
                    df_temp = df_unidade.copy()
                    df_temp["UNIDADE"] = unidade
                    lista_dfs.append(df_temp)

            if lista_dfs:
                df_final = pd.concat(lista_dfs, ignore_index=True)
                st.dataframe(df_final)
            else:
                st.write("Sem dados disponíveis")

        if falhas_envio:
            st.error("❌ Falhas no envio")
            st.dataframe(pd.DataFrame(falhas_envio))