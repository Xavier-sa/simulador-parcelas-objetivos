"""Valida nomes obrigatórios do CD sem jamais imprimir seus valores."""
import os
import sys

AMBIENTE = 'production-hostinger'
OBRIGATORIAS = (
    'HOSTINGER_HOST',
    'HOSTINGER_PORT',
    'HOSTINGER_USER',
    'HOSTINGER_SSH_KEY',
    'HOSTINGER_KNOWN_HOSTS',
    'HOSTINGER_DEPLOY_PATH',
)
CAMINHO_AUTORIZADO = (
    '/home/u587444950/domains/wasxtech.com.br/'
    'public_html/simulador-parcelas'
)


def validar(ambiente=None):
    valores = dict(os.environ if ambiente is None else ambiente)
    ausentes = [nome for nome in OBRIGATORIAS if not valores.get(nome, '').strip()]
    for nome in ausentes:
        print(f'::error::Erro: {nome} não configurado no ambiente {AMBIENTE}.')
    if ausentes:
        return 1

    if not valores['HOSTINGER_PORT'].isdigit():
        print('::error::Erro: HOSTINGER_PORT deve conter somente números.')
        return 1
    if valores['HOSTINGER_DEPLOY_PATH'] != CAMINHO_AUTORIZADO:
        print('::error::Erro: HOSTINGER_DEPLOY_PATH não corresponde ao diretório autorizado.')
        return 1
    print('Configuração Hostinger validada sem exibir credenciais.')
    return 0


if __name__ == '__main__':
    raise SystemExit(validar())
