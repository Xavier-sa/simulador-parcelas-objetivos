"""Valida que o pacote Hostinger contém somente arquivos públicos esperados."""
from pathlib import Path
from functools import partial
from http.client import HTTPConnection
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import unittest


class TesteDeployHostinger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        deploy = Path(__file__).resolve().parent.parent / 'deploy' / 'hostinger'
        servidor_handler = partial(SimpleHTTPRequestHandler, directory=deploy)
        cls.servidor = ThreadingHTTPServer(('127.0.0.1', 0), servidor_handler)
        cls.thread = Thread(target=cls.servidor.serve_forever, daemon=True)
        cls.thread.start()
        cls.porta = cls.servidor.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()
        cls.thread.join()

    def setUp(self):
        self.raiz = Path(__file__).resolve().parent.parent
        self.deploy = self.raiz / 'deploy' / 'hostinger'

    def test_contem_somente_quatro_arquivos_estaticos(self):
        encontrados = {item.name for item in self.deploy.iterdir() if item.is_file()}
        self.assertEqual(encontrados, {'index.html', 'style.css', 'config.js', 'script.js'})

    def test_html_usa_caminhos_relativos(self):
        html = (self.deploy / 'index.html').read_text(encoding='utf-8')
        for caminho in ('style.css', 'config.js', 'script.js'):
            self.assertIn(f'"{caminho}"', html)
        self.assertNotIn('href="/', html)
        self.assertNotIn('src="/', html)

    def test_pacote_nao_contem_dados_privados(self):
        conteudo = '\n'.join(
            arquivo.read_text(encoding='utf-8')
            for arquivo in self.deploy.iterdir()
            if arquivo.is_file()
        )
        self.assertNotIn('parcelas.json', conteudo)
        self.assertNotIn('backup-antes', conteudo)
        self.assertNotIn('1000.00', conteudo)

    def test_arquivos_carregam_em_servidor_estatico(self):
        for caminho, tipo in (('/', 'text/html'), ('/style.css', 'text/css'),
                              ('/config.js', 'javascript'), ('/script.js', 'javascript')):
            conexao = HTTPConnection('127.0.0.1', self.porta)
            conexao.request('GET', caminho)
            resposta = conexao.getresponse()
            resposta.read()
            self.assertEqual(resposta.status, 200)
            self.assertIn(tipo, resposta.getheader('Content-Type'))
            conexao.close()


if __name__ == '__main__':
    unittest.main()
