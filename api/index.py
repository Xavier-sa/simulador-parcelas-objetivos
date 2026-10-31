"""Entrada serverless pública: não inicia servidor, não grava e não lê dados reais."""
import json
import os
import sys
from datetime import date
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'backend'))
from parcelas import resumo, resumo_financeiro  # noqa: E402
from api.demo_data import DEMO_PARCELAMENTOS  # noqa: E402

ROTAS_GET = {'/api/health', '/api/resumo', '/api/parcelamentos'}
ORIGENS_LOCAIS = {'http://localhost:8000', 'http://127.0.0.1:8000'}
ORIGEM_HOSTINGER = 'https://simulador-parcelas.wasxtech.com.br'


def origens_permitidas():
    origens = set()
    producao = os.environ.get('HOSTINGER_ALLOWED_ORIGIN', ORIGEM_HOSTINGER).rstrip('/')
    if producao:
        origens.add(producao)
    if os.environ.get('ALLOW_LOCALHOST_CORS', '').lower() == 'true':
        origens.update(ORIGENS_LOCAIS)
    return origens


def caminho_publico(url):
    """Aceita a URL original e o parâmetro repassado pelo rewrite da Vercel."""
    partes = urlsplit(url)
    if partes.path in ROTAS_GET:
        return partes.path
    parametro = parse_qs(partes.query).get('path', [''])[0].strip('/')
    return f'/api/{parametro}' if parametro else partes.path


class handler(BaseHTTPRequestHandler):
    """Interface reconhecida pelo runtime Python da Vercel."""

    def _cors(self):
        origem = self.headers.get('Origin')
        if origem in origens_permitidas():
            self.send_header('Access-Control-Allow-Origin', origem)
            self.send_header('Vary', 'Origin')

    def responder(self, status, dados=None):
        corpo = b'' if dados is None else json.dumps(dados, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(corpo)))
        self._cors()
        self.end_headers()
        if corpo:
            self.wfile.write(corpo)

    def do_OPTIONS(self):
        caminho = caminho_publico(self.path)
        if caminho not in ROTAS_GET:
            return self.responder(404, {'erro': 'Rota pública não encontrada.'})
        self.send_response(204)
        self.send_header('Content-Length', '0')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '600')
        self._cors()
        self.end_headers()

    def do_GET(self):
        caminho = caminho_publico(self.path)
        referencia = date.today().isoformat()
        if caminho == '/api/health':
            return self.responder(200, {'status': 'ok', 'servico': 'objetivos-api',
                                        'modo': 'demonstracao', 'somente_leitura': True})
        if caminho == '/api/parcelamentos':
            itens = [resumo(item, referencia) for item in DEMO_PARCELAMENTOS]
            return self.responder(200, {'demonstracao': True, 'parcelamentos': itens})
        if caminho == '/api/resumo':
            dados = resumo_financeiro(DEMO_PARCELAMENTOS, referencia)
            dados.update({'demonstracao': True, 'somente_leitura': True})
            return self.responder(200, dados)
        return self.responder(404, {'erro': 'Rota pública não encontrada.'})

    def _metodo_desabilitado(self):
        corpo = json.dumps({'erro': 'Operações de escrita estão desabilitadas na versão pública.'},
                           ensure_ascii=False).encode('utf-8')
        self.send_response(405)
        self.send_header('Allow', 'GET, OPTIONS')
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(corpo)))
        self._cors()
        self.end_headers()
        self.wfile.write(corpo)

    do_POST = _metodo_desabilitado
    do_PUT = _metodo_desabilitado
    do_DELETE = _metodo_desabilitado
