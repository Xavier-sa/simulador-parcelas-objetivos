"""Valida que o pacote Hostinger contém somente arquivos públicos esperados."""
from pathlib import Path
from functools import partial
from http.client import HTTPConnection
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import unittest
from zipfile import ZipFile


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

    def test_contem_somente_tres_arquivos_estaticos(self):
        encontrados = {item.name for item in self.deploy.iterdir() if item.is_file()}
        self.assertEqual(encontrados, {'index.html', 'style.css', 'script.js'})

    def test_html_usa_caminhos_relativos(self):
        html = (self.deploy / 'index.html').read_text(encoding='utf-8')
        for caminho in ('style.css', 'script.js'):
            self.assertIn(f'"{caminho}"', html)
        self.assertNotIn('href="/', html)
        self.assertNotIn('src="/', html)
        self.assertIn('Versão: __DEPLOY_SHA__', html)

    def test_aba_tem_nome_claro_e_favicon_embutido(self):
        html = (self.deploy / 'index.html').read_text(encoding='utf-8')
        self.assertIn('<title>Simulador de Parcelas | Objetivos</title>', html)
        self.assertIn('rel="icon"', html)
        self.assertIn('data:image/svg+xml,', html)

    def test_pacote_nao_contem_dados_privados(self):
        conteudo = '\n'.join(
            arquivo.read_text(encoding='utf-8')
            for arquivo in self.deploy.iterdir()
            if arquivo.is_file()
        )
        self.assertNotIn('parcelas.json', conteudo)
        self.assertNotIn('backup-antes', conteudo)
        self.assertNotIn('1000.00', conteudo)

    def test_script_aponta_para_api_e_trata_erros(self):
        script = (self.deploy / 'script.js').read_text(encoding='utf-8')
        self.assertIn('https://simulador-parcelas-objetivos.vercel.app', script)
        for trecho in ('resposta.ok', 'application/json', 'JSON inválido',
                       'Não foi possível conectar', 'configuração de CORS'):
            self.assertIn(trecho, script)

    def test_arquivos_carregam_em_servidor_estatico(self):
        for caminho, tipo in (('/', 'text/html'), ('/style.css', 'text/css'),
                              ('/script.js', 'javascript')):
            conexao = HTTPConnection('127.0.0.1', self.porta)
            conexao.request('GET', caminho)
            resposta = conexao.getresponse()
            resposta.read()
            self.assertEqual(resposta.status, 200)
            self.assertIn(tipo, resposta.getheader('Content-Type'))
            conexao.close()

    def test_zip_tem_index_diretamente_na_raiz(self):
        caminho = self.raiz / 'deploy' / 'simulador-parcelas-hostinger.zip'
        with ZipFile(caminho) as arquivo:
            self.assertEqual(set(arquivo.namelist()), {'index.html', 'style.css', 'script.js'})


if __name__ == '__main__':
    unittest.main()
