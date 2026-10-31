"""Testes da função pública sem tocar nos dados financeiros reais."""
import json
import os
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from threading import Thread
import unittest

from api.index import handler


class TesteAPIPublica(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        cls.thread = Thread(target=cls.servidor.serve_forever, daemon=True)
        cls.thread.start()
        cls.porta = cls.servidor.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()
        cls.thread.join()

    def setUp(self):
        self.ambiente = dict(os.environ)
        os.environ['HOSTINGER_ALLOWED_ORIGIN'] = 'https://simulador-parcelas.wasxtech.com.br'
        os.environ['ALLOW_LOCALHOST_CORS'] = 'true'

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.ambiente)

    def requisitar(self, metodo, caminho, origem=None):
        conexao = HTTPConnection('127.0.0.1', self.porta)
        headers = {'Origin': origem} if origem else {}
        conexao.request(metodo, caminho, headers=headers)
        resposta = conexao.getresponse()
        corpo = resposta.read()
        resultado = resposta.status, dict(resposta.getheaders()), corpo
        conexao.close()
        return resultado

    def test_tres_gets_retornam_json_demonstrativo(self):
        for caminho in ('/api/health', '/api/resumo', '/api/parcelamentos'):
            status, headers, corpo = self.requisitar('GET', caminho)
            self.assertEqual(status, 200)
            self.assertIn('application/json', headers['Content-Type'])
            dados = json.loads(corpo)
            self.assertTrue(dados.get('demonstracao') or dados.get('modo') == 'demonstracao')

    def test_resumo_publico_tem_resultados_financeiros_confirmados(self):
        status, _, corpo = self.requisitar('GET', '/api/resumo')
        self.assertEqual(status, 200)
        dados = json.loads(corpo)
        self.assertEqual(dados['data_referencia'], '2026-10-29')
        self.assertEqual(dados['total_contratado'], '73700.00')
        self.assertEqual(dados['total_pago'], '36300.00')
        self.assertEqual(dados['saldo_restante'], '37400.00')
        self.assertEqual(dados['mensalidade_combinada'], '1100.00')
        self.assertEqual([item['quantidade_paga'] for item in dados['parcelamentos']], [33, 33])
        self.assertEqual([len(item['historico']) for item in dados['parcelamentos']], [67, 67])

    def test_cors_permita_hostinger_e_recuse_origem_desconhecida(self):
        status, headers, _ = self.requisitar('GET', '/api/health', 'https://simulador-parcelas.wasxtech.com.br')
        self.assertEqual(status, 200)
        self.assertEqual(headers.get('Access-Control-Allow-Origin'), 'https://simulador-parcelas.wasxtech.com.br')
        _, headers, _ = self.requisitar('GET', '/api/health', 'https://site-invasor.test')
        self.assertNotIn('Access-Control-Allow-Origin', headers)

    def test_options_e_metodos_de_escrita(self):
        status, headers, corpo = self.requisitar('OPTIONS', '/api/resumo', 'http://localhost:8000')
        self.assertEqual(status, 204)
        self.assertEqual(headers.get('Access-Control-Allow-Methods'), 'GET, OPTIONS')
        self.assertEqual(corpo, b'')
        for metodo in ('POST', 'PUT', 'DELETE'):
            status, headers, corpo = self.requisitar(metodo, '/api/parcelamentos')
            self.assertEqual(status, 405)
            self.assertEqual(headers.get('Allow'), 'GET, OPTIONS')
            self.assertIn('desabilitadas', json.loads(corpo)['erro'])

    def test_rota_inexistente(self):
        status, _, corpo = self.requisitar('GET', '/api/nao-existe')
        self.assertEqual(status, 404)
        self.assertIn('erro', json.loads(corpo))

    def test_parametro_do_rewrite_da_vercel(self):
        status, _, corpo = self.requisitar('GET', '/api/index?path=health')
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(corpo)['status'], 'ok')


if __name__ == '__main__':
    unittest.main()
