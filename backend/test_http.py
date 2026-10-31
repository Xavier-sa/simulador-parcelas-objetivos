"""Testes HTTP locais com dados fictícios e arquivo isolado."""
import json
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import unittest

import main
import storage


class TesteHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arquivo_original = storage.ARQUIVO
        cls.arquivo_teste = Path(__file__).resolve().parent / '_parcelas_http_teste.json'
        dados = {'parcelamentos': [
            {'id': 1, 'nome': 'Exemplo A', 'tipo': 'principal', 'valor_parcela': '250.00', 'quantidade_total': 12, 'primeiro_vencimento': '2026-01-15', 'pagamentos': [1, 2, 3]},
            {'id': 2, 'nome': 'Exemplo B', 'tipo': 'secundaria', 'valor_parcela': '35.00', 'quantidade_total': 12, 'primeiro_vencimento': '2026-01-15', 'pagamentos': [1, 2, 3]},
        ]}
        cls.arquivo_teste.write_text(json.dumps(dados), encoding='utf-8')
        storage.ARQUIVO = cls.arquivo_teste
        cls.servidor = ThreadingHTTPServer(('127.0.0.1', 0), main.Servidor)
        cls.thread = Thread(target=cls.servidor.serve_forever, daemon=True)
        cls.thread.start()
        cls.porta = cls.servidor.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown(); cls.servidor.server_close(); cls.thread.join()
        storage.ARQUIVO = cls.arquivo_original
        cls.arquivo_teste.unlink(missing_ok=True)

    def requisitar(self, metodo, caminho, corpo=None):
        conexao = HTTPConnection('127.0.0.1', self.porta)
        headers = {'Content-Type': 'application/json'} if corpo is not None else {}
        conexao.request(metodo, caminho, json.dumps(corpo) if corpo is not None else None, headers)
        resposta = conexao.getresponse()
        resultado = resposta.status, resposta.getheader('Content-Type'), resposta.read()
        conexao.close()
        return resultado

    def test_api_e_arquivos_publicos_usam_tipos_corretos(self):
        for caminho in ('/api/resumo', '/api/parcelamentos'):
            status, tipo, corpo = self.requisitar('GET', caminho)
            self.assertEqual(status, 200); self.assertIn('application/json', tipo); json.loads(corpo)
        for caminho, esperado in (('/', 'text/html'), ('/style.css', 'text/css'), ('/script.js', 'text/javascript')):
            status, tipo, _ = self.requisitar('GET', caminho)
            self.assertEqual(status, 200); self.assertIn(esperado, tipo)

    def test_api_inexistente_retorna_404_json(self):
        status, tipo, corpo = self.requisitar('GET', '/api/rota-inexistente')
        self.assertEqual(status, 404); self.assertIn('application/json', tipo); self.assertIn('erro', json.loads(corpo))

    def test_registrar_e_cancelar_pagamento_local(self):
        status, _, corpo = self.requisitar('POST', '/api/parcelamentos/1/pagamentos', {'numero': 4})
        self.assertEqual(status, 201); self.assertEqual(json.loads(corpo)['quantidade_paga'], 4)
        status, _, corpo = self.requisitar('DELETE', '/api/parcelamentos/1/pagamentos/4')
        self.assertEqual(status, 200); self.assertEqual(json.loads(corpo)['quantidade_paga'], 3)


if __name__ == '__main__':
    unittest.main()
