"""Cenário fictício, público e somente leitura usado na demonstração."""

DATA_BASE_DEMONSTRACAO = '2026-10-29'

DEMO_PARCELAMENTOS = [
    {'id': 1, 'nome': 'Objetivo principal', 'tipo': 'principal',
     'valor_parcela': '1000.00', 'quantidade_total': 67,
     'primeiro_vencimento': '2024-02-10', 'pagamentos': list(range(1, 34)),
     'demonstracao': True},
    {'id': 2, 'nome': 'Objetivo secundário', 'tipo': 'secundaria',
     'valor_parcela': '100.00', 'quantidade_total': 67,
     'primeiro_vencimento': '2024-02-10', 'pagamentos': list(range(1, 34)),
     'demonstracao': True},
]
