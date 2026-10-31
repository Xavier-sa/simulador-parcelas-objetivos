"""Regressão histórica isolada; nunca lê o JSON financeiro privado."""
import unittest

from parcelas import resumo, resumo_financeiro


class TesteHistoricoFinanceiroConfirmado(unittest.TestCase):
    def setUp(self):
        base = {
            'quantidade_total': 67,
            'primeiro_vencimento': '2024-02-10',
            'pagamentos': list(range(1, 34)),
        }
        self.principal = {
            'id': 1, 'nome': 'Fixture histórica principal', 'tipo': 'principal',
            'valor_parcela': '1000.00', **base,
        }
        self.secundaria = {
            'id': 2, 'nome': 'Fixture histórica secundária', 'tipo': 'secundaria',
            'valor_parcela': '100.00', **base,
        }

    def test_totais_confirmados_na_data_base(self):
        resultado = resumo_financeiro(
            [self.principal, self.secundaria], '2026-10-29'
        )
        self.assertEqual(resultado['total_contratado'], '73700.00')
        self.assertEqual(resultado['total_pago'], '36300.00')
        self.assertEqual(resultado['saldo_restante'], '37400.00')

    def test_quantidades_e_ultimo_vencimento(self):
        for contrato in (self.principal, self.secundaria):
            resultado = resumo(contrato, '2026-10-29')
            self.assertEqual(resultado['quantidade_total'], 67)
            self.assertEqual(resultado['quantidade_paga'], 33)
            self.assertEqual(resultado['ultimo_vencimento'], '2029-08-10')


if __name__ == '__main__':
    unittest.main()
