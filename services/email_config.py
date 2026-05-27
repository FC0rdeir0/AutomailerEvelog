def configurar_email(cc_input=None, assunto=None, corpo=None):

    cc_list = []
    if cc_input:
        cc_list = [e.strip() for e in cc_input.split(",") if e.strip()]

    config = {
        "cc": cc_list,
        "assunto": assunto.strip() if assunto else None,
        "corpo": corpo.strip() if corpo else None
    }

    return config

def validar_config_email(config, exigir_assunto=True, exigir_corpo=True):
    erros = []

    if exigir_assunto and not config["assunto"]:
        erros.append("Assunto não preenchido")

    if exigir_corpo and not config["corpo"]:
        erros.append("Corpo do e-mail não preenchido")

    return erros