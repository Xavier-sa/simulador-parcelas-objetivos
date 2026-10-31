# Regras de negócio e fórmulas

## Dinheiro

- Persistência: string decimal com duas casas, como `"250.00"` (exemplo fictício).
- Cálculos: exclusivamente `decimal.Decimal` criado a partir de texto.
- `float` é recusado para valores financeiros.
- Não existem juros, multas, correção ou amortização variável.

Fórmulas:

```text
total contratado = valor da parcela × quantidade total
valor pago = valor da parcela × quantidade paga
saldo = total contratado − valor pago
quantidade restante = quantidade total − quantidade paga
percentual pago = quantidade paga ÷ quantidade total × 100
mensalidade combinada = mensalidade principal + mensalidade secundária
```

## Cenário público de demonstração

Data-base fixa: `29/10/2026`. Essa data torna o exemplo reproduzível; ela não representa a data de uma dívida real.

| Objetivo | Parcela | Total | Pagas | Contratado | Pago | Saldo |
|---|---:|---:|---:|---:|---:|---:|
| Principal | R$ 1.000,00 | 67 | 33 | R$ 67.000,00 | R$ 33.000,00 | R$ 34.000,00 |
| Secundário | R$ 100,00 | 67 | 33 | R$ 6.700,00 | R$ 3.300,00 | R$ 3.400,00 |
| Combinado | R$ 1.100,00/mês | — | — | R$ 73.700,00 | R$ 36.300,00 | R$ 37.400,00 |

Cada objetivo está 49,25% quitado (`33 ÷ 67 × 100`), tem 34 parcelas restantes, próximo vencimento em `10/11/2026` e último vencimento em `10/08/2029`. A origem pública é exclusivamente `api/demo_data.py`; o JSON privado não participa da API.

**LEIGO:** usamos um exemplo fixo para que todas as pessoas vejam a mesma conta e consigam conferi-la.

**TÉCNICO:** valores monetários entram como strings e são calculados com `Decimal`; calendário e agregação permanecem em `backend/parcelas.py`.

**PRÁTICO:** confirme `33 × 1.000 + 33 × 100 = 36.300` e `73.700 − 36.300 = 37.400`.

## Calendário

- Parcela 1 usa o primeiro vencimento.
- Cada parcela seguinte avança um mês de calendário.
- Se o dia não existir no mês de destino, usa-se o último dia válido.
- Vencida: data menor ou igual à referência.
- Futura: data posterior à referência.
- Próximo vencimento: primeira ocorrência posterior à referência.

## Pagamentos

- Somente confirmação explícita torna uma parcela paga.
- O número deve estar entre 1 e a quantidade total.
- Duplicatas são rejeitadas.
- Cancelamento exige um pagamento existente.
- Pagamentos 1–33 dos dois contratos foram confirmados pelo usuário; a data efetiva é desconhecida.

## Migração

- Conferir dados existentes antes de alterar.
- Interromper em caso de divergência.
- Criar backup antes da primeira gravação.
- Preservar pagamentos existentes e impedir duplicação.
- Registrar identificador da migração para execução única.

## Persistência

- JSON inválido gera erro e permanece intocado.
- A gravação usa arquivo temporário, `fsync` e substituição atômica.
- Reiniciar o servidor não recria nem limpa o arquivo de dados.
