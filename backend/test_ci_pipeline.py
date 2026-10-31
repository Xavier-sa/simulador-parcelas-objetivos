"""Testes estruturais do pipeline sem acessar GitHub ou Hostinger."""
from pathlib import Path
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

    def test_cd_exige_somente_token_da_branch_publica(self):
        self.assertIn('HOSTINGER_PAGES_TOKEN', self.cd)
        self.assertIn(
            'HOSTINGER_PAGES_TOKEN não configurado no ambiente production-hostinger',
            self.cd,
        )
        for antigo in ('HOSTINGER_HOST', 'HOSTINGER_PORT', 'HOSTINGER_USER',
                       'HOSTINGER_SSH_KEY', 'HOSTINGER_KNOWN_HOSTS',
                       'HOSTINGER_DEPLOY_PATH', 'HOSTINGER_WEBHOOK',
                       'ssh ', 'scp '):
            self.assertNotIn(antigo, self.cd)

    def test_cd_atualiza_branch_sem_force_e_verifica_sha_publicado(self):
        self.assertIn('HEAD:hostinger-pages', self.cd)
        self.assertNotIn('git push --force', self.cd)
        self.assertIn('git commit --allow-empty', self.cd)
        self.assertIn('deployment-commit', self.cd)
        self.assertIn('Verificar publicação da Hostinger', self.cd)

    def test_cd_publica_somente_tres_arquivos(self):
        linha = next(
            linha for linha in self.cd.splitlines()
            if linha.strip().startswith('cp frontend/')
        )
        for nome in ('index.html', 'style.css', 'script.js'):
            self.assertIn(f'frontend/{nome}', linha)
        for proibido in ('config.js', 'backend/', 'api/', 'data/', 'docs/'):
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
