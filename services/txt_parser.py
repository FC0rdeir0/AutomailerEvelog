import pandas as pd
import re

def parse_txt(uploaded):
    linhas = uploaded.read().decode("latin-1").splitlines()
    dados = []

    for linha in linhas[1:]:  # pula cabeçalho
        if not linha.strip():
            continue

        partes = re.split(r"\s{2,}", linha.strip())

        try:
            restaurante = partes[0]
            pedido = partes[1]
            data = partes[2]
            item = partes[3]
            qtde = partes[4]
            descricao = partes[5]
            preco_rs = partes[6]

            idx = 7
            preco_usd = None
            if idx < len(partes) and re.match(r"^[\d\.,]+$", partes[idx]):
                preco_usd = partes[idx]
                idx += 1

            responsavel = partes[idx]
            idx += 1

            observacao = (
                " ".join(partes[idx:-2])
                if len(partes) > idx + 2
                else None
            )

            oc = partes[-2]
            cnpj = partes[-1]

            dados.append([
                restaurante, pedido, data, item, qtde,
                descricao, preco_rs, preco_usd,
                responsavel, observacao, oc, cnpj,
                uploaded.name
            ])

        except Exception:
            continue

    return pd.DataFrame(dados, columns=[
        "RESTAURANTE",
        "PEDIDO",
        "DATA",
        "ITEM",
        "QTDE",
        "DESCRICAO",
        "PRECO_UNIT_RS",
        "PRECO_UNIT_USD",
        "RESPONSAVEL",
        "OBSERVACAO",
        "OC",
        "CNPJ",
        "ARQUIVO_ORIGEM"
    ])