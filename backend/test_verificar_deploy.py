"""Testes isolados do verificador; não acessam GitHub nem Hostinger."""
import socket
import unittest
from unittest.mock import patch
from urllib.error import URLError

from scripts.verificar_deploy import Resultado, avaliar_resposta, consultar, verificar


SHA = 'a' * 40


class TesteAvaliacaoDeploy(unittest.TestCase):
    def test_http_200_com_sha_correto(self):
        corpo = f'<html><head><meta content="{SHA}" name="deployment-commit"></head></html>'
        resultado = avaliar_resposta(200, 'text/html; charset=utf-8', corpo, SHA)
        self.assertTrue(resultado.sucesso)
        self.assertEqual(resultado.sha_encontrado, SHA)

    def test_http_200_com_sha_antigo(self):
        resultado = avaliar_resposta(
            200, 'text/html', '<meta name="deployment-commit" content="antigo">', SHA,
        )
        self.assertFalse(resultado.sucesso)
        self.assertEqual(resultado.tipo, 'versao')
        self.assertIn('antigo', resultado.mensagem)

    def test_falhas_http_sao_diferenciadas(self):
        for status, trecho in ((403, 'negado'), (404, 'não encontrada'), (500, 'transitória')):
            with self.subTest(status=status):
                resultado = avaliar_resposta(status, 'text/html', '', SHA)
                self.assertFalse(resultado.sucesso)
                self.assertIn(trecho, resultado.mensagem)

    def test_html_sem_meta(self):
        resultado = avaliar_resposta(200, 'text/html', '<html></html>', SHA)
        self.assertFalse(resultado.sucesso)
        self.assertEqual(resultado.tipo, 'conteudo')

    @patch('scripts.verificar_deploy.urlopen', side_effect=URLError(socket.timeout()))
    def test_timeout(self, _urlopen):
        resultado = consultar('https://exemplo.test', SHA, 1, 1)
        self.assertFalse(resultado.sucesso)
        self.assertEqual(resultado.tipo, 'rede')

    def test_tenta_novamente_e_nao_mascara_falha(self):
        respostas = iter([
            Resultado(False, 'versao', 'SHA antigo.'),
            Resultado(True, 'ok', 'SHA correto.', SHA),
        ])
        with patch('scripts.verificar_deploy.time.sleep') as espera:
            resultado = verificar(
                'https://exemplo.test', SHA, tentativas=2, intervalo=0,
                consultar_fn=lambda *_: next(respostas),
            )
        self.assertTrue(resultado.sucesso)
        espera.assert_called_once_with(0)


if __name__ == '__main__':
    unittest.main()
