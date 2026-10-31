"""Confirma, com diagnóstico seguro, qual commit está no HTML público."""
import argparse
from dataclasses import dataclass
from html.parser import HTMLParser
import socket
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class Resultado:
    sucesso: bool
    tipo: str
    mensagem: str
    sha_encontrado: str | None = None


class LeitorMetaDeploy(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sha = None

    def handle_starttag(self, tag, attrs):
        if tag.lower() != 'meta':
            return
        atributos = {nome.lower(): valor for nome, valor in attrs}
        if atributos.get('name', '').lower() == 'deployment-commit':
            self.sha = atributos.get('content')


def avaliar_resposta(status, content_type, corpo, sha_esperado):
    """Classifica HTTP, formato e versão sem esconder o motivo da falha."""
    if status == 403:
        return Resultado(False, 'http', 'HTTP 403: acesso automatizado negado.')
    if status == 404:
        return Resultado(False, 'http', 'HTTP 404: rota pública não encontrada.')
    if status >= 500:
        return Resultado(False, 'http', f'HTTP {status}: falha transitória do servidor.')
    if status != 200:
        return Resultado(False, 'http', f'HTTP {status}: resposta inesperada.')
    if content_type.split(';', 1)[0].strip().lower() != 'text/html':
        return Resultado(False, 'conteudo', f'Content-Type inesperado: {content_type or "ausente"}.')

    leitor = LeitorMetaDeploy()
    leitor.feed(corpo)
    if not leitor.sha:
        return Resultado(False, 'conteudo', 'HTML sem meta deployment-commit.')
    if leitor.sha != sha_esperado:
        return Resultado(
            False, 'versao',
            f'Versão divergente: esperado {sha_esperado}, encontrado {leitor.sha}.',
            leitor.sha,
        )
    return Resultado(True, 'ok', f'Versão confirmada: {sha_esperado}.', leitor.sha)


def consultar(url, sha_esperado, tentativa, timeout):
    partes = urlsplit(url)
    consulta = urlencode({'deployment_sha': sha_esperado, 'tentativa': tentativa})
    destino = urlunsplit((partes.scheme, partes.netloc, partes.path or '/', consulta, ''))
    requisicao = Request(
        destino,
        headers={'Accept': 'text/html', 'User-Agent': 'verificador-deploy/1.0'},
    )
    try:
        with urlopen(requisicao, timeout=timeout) as resposta:
            status = resposta.status
            content_type = resposta.headers.get('Content-Type', '')
            corpo = resposta.read().decode('utf-8', errors='replace')
            final = urlsplit(resposta.geturl())
            print(f'Tentativa {tentativa}: HTTP {status}; Content-Type {content_type or "ausente"}; URL final {final.scheme}://{final.netloc}{final.path}')
            return avaliar_resposta(status, content_type, corpo, sha_esperado)
    except HTTPError as erro:
        content_type = erro.headers.get('Content-Type', '') if erro.headers else ''
        print(f'Tentativa {tentativa}: HTTP {erro.code}; Content-Type {content_type or "ausente"}.')
        return avaliar_resposta(erro.code, content_type, '', sha_esperado)
    except (URLError, TimeoutError, socket.timeout) as erro:
        motivo = getattr(erro, 'reason', erro)
        return Resultado(False, 'rede', f'Falha de rede ou timeout: {type(motivo).__name__}.')


def verificar(url, sha_esperado, tentativas=24, intervalo=10, timeout=10, consultar_fn=consultar):
    ultimo = None
    for tentativa in range(1, tentativas + 1):
        ultimo = consultar_fn(url, sha_esperado, tentativa, timeout)
        print(f'Tentativa {tentativa}: {ultimo.mensagem}')
        if ultimo.sucesso:
            return ultimo
        if tentativa < tentativas:
            time.sleep(intervalo)
    return ultimo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--sha', required=True)
    parser.add_argument('--tentativas', type=int, default=24)
    parser.add_argument('--intervalo', type=int, default=10)
    parser.add_argument('--timeout', type=int, default=10)
    args = parser.parse_args()
    resultado = verificar(args.url, args.sha, args.tentativas, args.intervalo, args.timeout)
    if not resultado or not resultado.sucesso:
        print('::error::Branch publicada no GitHub; verificação do domínio inconclusiva.')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
