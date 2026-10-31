"""Testes das regras financeiras com dados inteiramente fictícios."""
import copy
import unittest

from parcelas import desfazer_pagamento, registrar_pagamento, resumo, resumo_financeiro, validar, vencimento


class TesteControleParcelas(unittest.TestCase):
    def setUp(self):
        base = {'quantidade_total': 12, 'primeiro_vencimento': '2026-01-15', 'pagamentos': [1, 2, 3]}
        self.principal = {'id': 1, 'nome': 'Exemplo A', 'tipo': 'principal', 'valor_parcela': '250.00', **base}
        self.secundaria = {'id': 2, 'nome': 'Exemplo B', 'tipo': 'secundaria', 'valor_parcela': '35.00', **base}

    def test_datas_e_meses_de_tamanhos_diferentes(self):
        self.assertEqual(vencimento('2026-01-15', 1), '2026-01-15')
        self.assertEqual(vencimento('2026-01-15', 12), '2026-12-15')
        self.assertEqual(vencimento('2024-01-31', 2), '2024-02-29')
        self.assertEqual(vencimento('2023-01-31', 2), '2023-02-28')
        self.assertEqual(vencimento('2024-03-31', 2), '2024-04-30')

    def test_calculos_principal(self):
        resultado = resumo(self.principal, '2026-04-01')
        self.assertEqual(resultado['valor_total'], '3000.00')
        self.assertEqual(resultado['valor_pago'], '750.00')
        self.assertEqual(resultado['saldo_restante'], '2250.00')
        self.assertEqual(resultado['quantidade_paga'], 3)
        self.assertEqual(resultado['quantidade_pendente'], 9)
        self.assertEqual(resultado['percentual_pago'], '25.00')
        self.assertEqual(resultado['proximo_vencimento'], '2026-04-15')

    def test_calculos_secundario_e_combinado(self):
        resultado = resumo(self.secundaria, '2026-04-01')
        self.assertEqual(resultado['valor_total'], '420.00')
        self.assertEqual(resultado['valor_pago'], '105.00')
        self.assertEqual(resultado['saldo_restante'], '315.00')
        combinado = resumo_financeiro([self.principal, self.secundaria], '2026-04-01')
        self.assertEqual(combinado['total_contratado'], '3420.00')
        self.assertEqual(combinado['total_pago'], '855.00')
        self.assertEqual(combinado['saldo_restante'], '2565.00')
        self.assertEqual(combinado['mensalidade_combinada'], '285.00')

    def test_registrar_cancelar_e_impedir_duplicado(self):
        dados = copy.deepcopy(self.principal)
        registrar_pagamento(dados, 4)
        self.assertIn(4, dados['pagamentos'])
        with self.assertRaisesRegex(ValueError, 'já registrada'):
            registrar_pagamento(dados, 4)
        desfazer_pagamento(dados, 4)
        self.assertNotIn(4, dados['pagamentos'])

    def test_float_e_pagamento_duplicado_sao_invalidos(self):
        dados = copy.deepcopy(self.principal)
        dados['valor_parcela'] = 250.0
        with self.assertRaisesRegex(ValueError, 'texto decimal'):
            validar(dados)
        dados = copy.deepcopy(self.principal)
        dados['pagamentos'].append(3)
        with self.assertRaisesRegex(ValueError, 'pagamentos inválida'):
            validar(dados)


if __name__ == '__main__':
    unittest.main()
