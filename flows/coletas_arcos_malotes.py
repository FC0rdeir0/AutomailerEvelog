import streamlit as st
import pandas as pd

from services.email_lookup import carregar_emails_unidades
from services.email_config import configurar_email, validar_config_email
from services.email_sender import enviar_emails
from utils.text import remover_acentos
from utils.email_form import render_email_config

def run(uploaded, email_user, senha):
     
     st.divider()

     config = render_email_config(show_assunto=False, show_corpo=False)

     cc_input = config.get("cc_input")