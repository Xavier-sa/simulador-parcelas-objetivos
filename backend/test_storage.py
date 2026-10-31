"""Testes da persistência sem tocar no arquivo real do usuário."""
import json
from pathlib import Path
import unittest

import storage


class TesteStorage(unittest.TestCase):
    def setUp(self):
        self.original = storage.ARQUIVO
        storage.ARQUIVO = Path(__file__).resolve().parent / '_parcelas_teste.json'
        storage.ARQUIVO.unlink(missing_ok=True)

    def tearDown(self):
        storage.ARQUIVO = self.original
        arquivo_teste = Path(__file__).resolve().parent / '_parcelas_teste.json'
        arquivo_teste.unlink(missing_ok=True)

    def test_salvar_e_reler_preserva_dados(self):
        dados = {'parcelamentos': [{'id': 1, 'pagamentos': [1, 2, 3]}]}
        storage.salvar(dados)
        self.assertEqual(storage.ler(), dados)
        self.assertEqual(storage.ler(), dados)

    def test_json_invalido_nao_e_sobrescrito(self):
        conteudo = '{arquivo quebrado'
        storage.ARQUIVO.write_text(conteudo, encoding='utf-8')
        with self.assertRaises(json.JSONDecodeError):
            storage.ler()
        self.assertEqual(storage.ARQUIVO.read_text(encoding='utf-8'), conteudo)


if __name__ == '__main__':
    unittest.main()
