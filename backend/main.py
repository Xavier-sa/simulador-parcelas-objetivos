"""Servidor REST local construído somente com a biblioteca padrão."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import urlsplit

from parcelas import (
    decimal_monetario, desfazer_pagamento, formatar_decimal,
    registrar_pagamento, resumo, resumo_financeiro, validar,
)
from storage import ler, salvar

PUBLICO = Path(__file__).resolve().parent.parent / 'frontend'
TRAVA = Lock()
DATA_REFERENCIA = '2026-10-29'


def encontrar(parcelamentos, identificador):
    """Localiza um contrato pelo ID ou devolve None."""
    return next((item for item in parcelamentos if item['id'] == identificador), None)


def preparar_campos(entrada, atual=None):
    """Seleciona campos aceitos e normaliza dinheiro como texto decimal."""
    item = dict(atual or {})
    for campo in ('nome', 'tipo', 'quantidade_total', 'primeiro_vencimento'):
        if campo in entrada:
            item[campo] = entrada[campo]
    if 'valor_parcela' in entrada:
        valor = decimal_monetario(entrada['valor_parcela'])
        item['valor_parcela'] = formatar_decimal(valor) if valor is not None else None
    item.setdefault('pagamentos', [])
    validar(item)
    return item


class Servidor(BaseHTTPRequestHandler):
    def responder(self, status, dados):
        corpo = json.dumps(dados, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def receber(self):
        tamanho = int(self.headers.get('Content-Length', '0'))
        if tamanho < 1 or tamanho > 100_000:
            raise ValueError('Tamanho de requisição inválido.')
        conteudo = json.loads(self.rfile.read(tamanho).decode('utf-8'))
        if not isinstance(conteudo, dict):
            raise ValueError('Esperado objeto JSON.')
        return conteudo

    def servir_pagina(self):
        caminho = urlsplit(self.path).path
        arquivos = {
            '/': ('index.html', 'text/html'),
            '/style.css': ('style.css', 'text/css'),
            '/script.js': ('script.js', 'text/javascript'),
        }
        if caminho not in arquivos:
            return self.responder(404, {'erro': 'Rota não encontrada.'})
        nome, tipo = arquivos[caminho]
        corpo = (PUBLICO / nome).read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', tipo + '; charset=utf-8')
        self.send_header('Content-Length', str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        caminho = urlsplit(self.path).path
        # Arquivos públicos têm rotas explícitas; qualquer outro caminho /api/ é JSON.
        if not caminho.startswith('/api/'):
            return self.servir_pagina()
        try:
            dados = ler()
            if caminho == '/api/parcelamentos':
                return self.responder(200, [resumo(item, DATA_REFERENCIA) for item in dados['parcelamentos']])
            if caminho == '/api/resumo':
                return self.responder(200, resumo_financeiro(dados['parcelamentos'], DATA_REFERENCIA))
            partes = caminho.strip('/').split('/')
            if len(partes) == 3 and partes[:2] == ['api', 'parcelamentos']:
                item = encontrar(dados['parcelamentos'], int(partes[2]))
                if item is None:
                    return self.responder(404, {'erro': 'Parcelamento não encontrado.'})
                return self.responder(200, resumo(item, DATA_REFERENCIA))
            return self.responder(404, {'erro': 'Rota da API não encontrada.'})
        except ValueError as erro:
            self.responder(400, {'erro': str(erro)})
        except (OSError, json.JSONDecodeError, KeyError) as erro:
            self.responder(500, {'erro': 'Falha na leitura dos dados: ' + str(erro)})
        except Exception as erro:
            self.log_error('Erro interno na API: %s', erro)
            self.responder(500, {'erro': 'Erro interno ao processar a solicitação.'})

    def do_POST(self):
        caminho = urlsplit(self.path).path
        try:
            entrada = self.receber()
            with TRAVA:
                dados = ler()
                if caminho == '/api/parcelamentos':
                    if any(item['tipo'] == entrada.get('tipo') for item in dados['parcelamentos']):
                        return self.responder(400, {'erro': 'Já existe um parcelamento deste tipo.'})
                    item = preparar_campos(entrada)
                    item['id'] = max((p['id'] for p in dados['parcelamentos']), default=0) + 1
                    dados['parcelamentos'].append(item)
                else:
                    partes = caminho.strip('/').split('/')
                    if len(partes) != 4 or partes[:2] != ['api', 'parcelamentos'] or partes[3] != 'pagamentos':
                        return self.responder(404, {'erro': 'Rota não encontrada.'})
                    item = encontrar(dados['parcelamentos'], int(partes[2]))
                    if item is None:
                        return self.responder(404, {'erro': 'Parcelamento não encontrado.'})
                    registrar_pagamento(item, entrada.get('numero'))
                salvar(dados)
            self.responder(201, resumo(item, DATA_REFERENCIA))
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as erro:
            self.responder(400, {'erro': str(erro)})
        except (OSError, KeyError) as erro:
            self.responder(500, {'erro': 'Falha de armazenamento: ' + str(erro)})
        except Exception as erro:
            self.log_error('Erro interno na API: %s', erro)
            self.responder(500, {'erro': 'Erro interno ao processar a solicitação.'})

    def do_PUT(self):
        caminho = urlsplit(self.path).path.strip('/').split('/')
        if len(caminho) != 3 or caminho[:2] != ['api', 'parcelamentos']:
            return self.responder(404, {'erro': 'Rota não encontrada.'})
        try:
            entrada = self.receber()
            with TRAVA:
                dados = ler()
                atual = encontrar(dados['parcelamentos'], int(caminho[2]))
                if atual is None:
                    return self.responder(404, {'erro': 'Parcelamento não encontrado.'})
                item = preparar_campos(entrada, atual)
                if any(p['id'] != atual['id'] and p['tipo'] == item['tipo'] for p in dados['parcelamentos']):
                    raise ValueError('Já existe um parcelamento deste tipo.')
                dados['parcelamentos'][dados['parcelamentos'].index(atual)] = item
                salvar(dados)
            self.responder(200, resumo(item, DATA_REFERENCIA))
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as erro:
            self.responder(400, {'erro': str(erro)})
        except (OSError, KeyError) as erro:
            self.responder(500, {'erro': 'Falha de armazenamento: ' + str(erro)})
        except Exception as erro:
            self.log_error('Erro interno na API: %s', erro)
            self.responder(500, {'erro': 'Erro interno ao processar a solicitação.'})

    def do_DELETE(self):
        caminho = urlsplit(self.path).path.strip('/').split('/')
        if len(caminho) != 5 or caminho[:2] != ['api', 'parcelamentos'] or caminho[3] != 'pagamentos':
            return self.responder(404, {'erro': 'Rota não encontrada.'})
        try:
            identificador, numero = int(caminho[2]), int(caminho[4])
            with TRAVA:
                dados = ler()
                item = encontrar(dados['parcelamentos'], identificador)
                if item is None:
                    return self.responder(404, {'erro': 'Pagamento não encontrado.'})
                try:
                    desfazer_pagamento(item, numero)
                except ValueError:
                    return self.responder(404, {'erro': 'Pagamento não encontrado.'})
                salvar(dados)
            self.responder(200, resumo(item, DATA_REFERENCIA))
        except ValueError:
            self.responder(400, {'erro': 'Parâmetros inválidos.'})
        except (OSError, KeyError, json.JSONDecodeError) as erro:
            self.responder(500, {'erro': str(erro)})
        except Exception as erro:
            self.log_error('Erro interno na API: %s', erro)
            self.responder(500, {'erro': 'Erro interno ao processar a solicitação.'})


if __name__ == '__main__':
    print('Abra http://127.0.0.1:8000')
    ThreadingHTTPServer(('127.0.0.1', 8000), Servidor).serve_forever()
