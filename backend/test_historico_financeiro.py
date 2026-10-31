"""Regressão histórica isolada; nunca lê o JSON financeiro privado."""
import unittest

from api.demo_data import DATA_BASE_DEMONSTRACAO, DEMO_PARCELAMENTOS
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
        self.assertEqual(resultado['mensalidade_combinada'], '1100.00')

    def test_quantidades_e_ultimo_vencimento(self):
        for contrato in (self.principal, self.secundaria):
            resultado = resumo(contrato, '2026-10-29')
            self.assertEqual(resultado['quantidade_total'], 67)
            self.assertEqual(resultado['quantidade_paga'], 33)
            self.assertEqual(resultado['quantidade_pendente'], 34)
            self.assertEqual(resultado['percentual_pago'], '49.25')
            self.assertEqual(resultado['proxima_parcela'], 34)
            self.assertEqual(resultado['proximo_vencimento'], '2026-11-10')
            self.assertEqual(resultado['ultimo_vencimento'], '2029-08-10')

    def test_datas_de_controle(self):
        self.assertEqual(resumo(self.principal, '2026-10-29')['historico'][0]['vencimento'], '2024-02-10')
        self.assertEqual(resumo(self.principal, '2026-10-29')['historico'][32]['vencimento'], '2026-10-10')
        self.assertEqual(resumo(self.principal, '2026-10-29')['historico'][33]['vencimento'], '2026-11-10')
        self.assertEqual(resumo(self.principal, '2026-10-29')['historico'][66]['vencimento'], '2029-08-10')

    def test_api_usa_exatamente_o_cenario_ficticio_confirmado(self):
        self.assertEqual(DATA_BASE_DEMONSTRACAO, '2026-10-29')
        self.assertEqual(DEMO_PARCELAMENTOS, [
            {**self.principal, 'nome': 'Objetivo principal', 'demonstracao': True},
            {**self.secundaria, 'nome': 'Objetivo secundário', 'demonstracao': True},
        ])


if __name__ == '__main__':
    unittest.main()
