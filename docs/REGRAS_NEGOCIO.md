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
