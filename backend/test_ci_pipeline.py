"""Testes estruturais do pipeline sem acessar GitHub ou Hostinger."""
from pathlib import Path
import os
import subprocess
import sys
import unittest


class TestePipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raiz = Path(__file__).resolve().parent.parent
        cls.ci = (cls.raiz / '.github/workflows/ci.yml').read_text(encoding='utf-8')
        cls.cd = (cls.raiz / '.github/workflows/deploy-hostinger.yml').read_text(encoding='utf-8')

    def test_ci_possui_tres_gatilhos_e_permissao_minima(self):
        for trecho in ('pull_request:', 'push:', 'workflow_dispatch:', 'contents: read'):
            self.assertIn(trecho, self.ci)

    def test_cd_depende_da_ci_do_sha_e_nao_aceita_pr(self):
        for trecho in ('workflow_run:', "conclusion == 'success'", "event == 'push'",
                       'head_sha', 'git rev-parse HEAD', 'merge-base --is-ancestor'):
            self.assertIn(trecho, self.cd)

    def test_diagnostico_nomeia_configuracoes_ausentes(self):
        script = self.raiz / 'scripts' / 'validar_config_hostinger.py'
        ambiente = {
            chave: valor for chave, valor in os.environ.items()
            if chave in ('PATH', 'PATHEXT', 'SYSTEMROOT', 'WINDIR')
        }
        resultado = subprocess.run(
            [sys.executable, str(script)], env=ambiente,
            capture_output=True, text=True, check=False,
        )
        self.assertNotEqual(resultado.returncode, 0)
        for nome in ('HOSTINGER_HOST', 'HOSTINGER_PORT', 'HOSTINGER_USER',
                     'HOSTINGER_SSH_KEY', 'HOSTINGER_KNOWN_HOSTS',
                     'HOSTINGER_DEPLOY_PATH'):
            self.assertIn(f'Erro: {nome} não configurado', resultado.stdout)
        self.assertIn('python scripts/validar_config_hostinger.py', self.cd)

    def test_configuracao_valida_e_caminho_incorreto(self):
        script = self.raiz / 'scripts' / 'validar_config_hostinger.py'
        ambiente = dict(os.environ)
        ambiente.update({
            'HOSTINGER_HOST': 'host.test',
            'HOSTINGER_PORT': '65002',
            'HOSTINGER_USER': 'usuario_teste',
            'HOSTINGER_SSH_KEY': 'chave-nao-real',
            'HOSTINGER_KNOWN_HOSTS': 'host-key-nao-real',
            'HOSTINGER_DEPLOY_PATH': '/home/u587444950/domains/wasxtech.com.br/public_html/simulador-parcelas',
        })
        valido = subprocess.run(
            [sys.executable, str(script)], env=ambiente,
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(valido.returncode, 0)
        ambiente['HOSTINGER_DEPLOY_PATH'] = '/caminho/incorreto'
        invalido = subprocess.run(
            [sys.executable, str(script)], env=ambiente,
            capture_output=True, text=True, check=False,
        )
        self.assertNotEqual(invalido.returncode, 0)
        self.assertIn('não corresponde ao diretório autorizado', invalido.stdout)

    def test_cd_valida_caminho_verifica_site_e_possui_rollback(self):
        self.assertIn('validar_config_hostinger.py', self.cd)
        self.assertIn('Verificar site publicado', self.cd)
        self.assertIn('steps.ativacao.outcome', self.cd)
        self.assertIn('.rollback-$sha', self.cd)

    def test_cd_transfere_somente_tres_arquivos(self):
        linha = next(linha for linha in self.cd.splitlines() if linha.strip().startswith('cp frontend/'))
        for nome in ('index.html', 'style.css', 'script.js'):
            self.assertIn(f'frontend/{nome}', linha)
        self.assertNotIn('config.js', linha)
        for proibido in ('backend/', 'api/', 'data/', 'docs/'):
            self.assertNotIn(proibido, linha)

    def test_javascript_invalido_reprova_node_check(self):
        resultado = subprocess.run(
            ['node', '--check', '-'], input='function quebrada( {',
            text=True, capture_output=True, check=False,
        )
        self.assertNotEqual(resultado.returncode, 0)

    def test_unittest_com_falha_retorna_erro(self):
        codigo = (
            'import unittest\n'
            'class T(unittest.TestCase):\n'
            ' def test_falha(self): self.fail("falha simulada")\n'
            'unittest.main()\n'
        )
        resultado = subprocess.run(
            [sys.executable, '-c', codigo], capture_output=True, text=True, check=False,
        )
        self.assertNotEqual(resultado.returncode, 0)


if __name__ == '__main__':
    unittest.main()
