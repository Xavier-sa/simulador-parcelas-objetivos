"""Regras de negócio e cálculos exatos dos objetivos parcelados."""
from calendar import monthrange
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENTAVOS = Decimal('0.01')


def vencimento(primeiro_vencimento, numero):
    """Retorna, em ISO, o vencimento mensal de uma parcela."""
    # LEIGO: avançamos meses no calendário, sem fingir que todo mês tem 30 dias.
    # TÉCNICO: convertemos o mês em índice absoluto e limitamos o dia ao fim do mês.
    inicio = date.fromisoformat(primeiro_vencimento)
    indice = inicio.year * 12 + inicio.month - 1 + numero - 1
    ano, mes_zero = divmod(indice, 12)
    mes = mes_zero + 1
    dia = min(inicio.day, monthrange(ano, mes)[1])
    return date(ano, mes, dia).isoformat()


def decimal_monetario(valor):
    """Converte texto ou inteiro em Decimal positivo com duas casas."""
    if valor is None:
        return None
    # Float é recusado para que nenhum cálculo financeiro use ponto flutuante binário.
    if isinstance(valor, (float, bool)) or not isinstance(valor, (str, int, Decimal)):
        raise ValueError('Valor monetário deve ser enviado como texto decimal.')
    try:
        convertido = Decimal(str(valor))
    except InvalidOperation as erro:
        raise ValueError('Valor monetário inválido.') from erro
    if not convertido.is_finite() or convertido <= 0:
        raise ValueError('Valor da parcela deve ser positivo ou vazio.')
    return convertido.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def formatar_decimal(valor):
    """Transforma Decimal em texto JSON exato com duas casas."""
    return format(valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP), '.2f')


def quantidade_vencidas(dados, data_referencia):
    """Conta vencimentos ocorridos até a data de referência, inclusive."""
    referencia = _converter_data(data_referencia)
    return sum(
        date.fromisoformat(vencimento(dados['primeiro_vencimento'], numero)) <= referencia
        for numero in range(1, dados['quantidade_total'] + 1)
    )


def quantidade_pagas(dados):
    """Conta somente pagamentos explicitamente registrados."""
    return len(dados['pagamentos'])


def quantidade_pendentes(dados):
    """Conta parcelas sem confirmação de pagamento."""
    return dados['quantidade_total'] - quantidade_pagas(dados)


def quantidade_futuras(dados, data_referencia):
    """Conta vencimentos posteriores à data de referência."""
    return dados['quantidade_total'] - quantidade_vencidas(dados, data_referencia)


def proximo_vencimento(dados, data_referencia):
    """Retorna número e data da primeira ocorrência futura."""
    numero = quantidade_vencidas(dados, data_referencia) + 1
    if numero > dados['quantidade_total']:
        return None, None
    return numero, vencimento(dados['primeiro_vencimento'], numero)


def historico_mensal(dados, data_referencia):
    """Produz o estado de cada parcela para a interface, sem regra no JavaScript."""
    referencia = _converter_data(data_referencia)
    pagamentos = set(dados['pagamentos'])
    historico = []
    for numero in range(1, dados['quantidade_total'] + 1):
        data_vencimento = vencimento(dados['primeiro_vencimento'], numero)
        if numero in pagamentos:
            estado = 'pago'
        elif date.fromisoformat(data_vencimento) <= referencia:
            estado = 'vencido'
        else:
            estado = 'futuro'
        historico.append({'numero': numero, 'vencimento': data_vencimento, 'estado': estado})
    return historico


def registrar_pagamento(dados, numero):
    """Registra uma parcela paga, impedindo números inválidos e duplicados."""
    if type(numero) is not int or numero < 1 or numero > dados['quantidade_total']:
        raise ValueError('Número da parcela inválido.')
    if numero in dados['pagamentos']:
        raise ValueError('Parcela já registrada como paga.')
    dados['pagamentos'].append(numero)
    dados['pagamentos'].sort()


def desfazer_pagamento(dados, numero):
    """Remove uma confirmação existente sem alterar outras parcelas."""
    if numero not in dados['pagamentos']:
        raise ValueError('Pagamento não encontrado.')
    dados['pagamentos'].remove(numero)


def validar(dados):
    """Valida um parcelamento antes de sua gravação."""
    if dados.get('tipo') not in ('principal', 'secundaria'):
        raise ValueError('Tipo deve ser principal ou secundaria.')
    if not isinstance(dados.get('nome'), str) or not dados['nome'].strip():
        raise ValueError('Informe o nome do parcelamento.')
    total = dados.get('quantidade_total')
    if type(total) is not int or not 1 <= total <= 1200:
        raise ValueError('Quantidade deve ser inteira entre 1 e 1200.')
    decimal_monetario(dados.get('valor_parcela'))
    try:
        date.fromisoformat(dados['primeiro_vencimento'])
    except (KeyError, TypeError, ValueError) as erro:
        raise ValueError('Data deve estar no formato AAAA-MM-DD.') from erro
    pagamentos = dados.get('pagamentos', [])
    if (
        not isinstance(pagamentos, list)
        or any(type(numero) is not int or numero < 1 or numero > total for numero in pagamentos)
        or len(set(pagamentos)) != len(pagamentos)
    ):
        raise ValueError('Lista de pagamentos inválida.')


def resumo(dados, data_referencia=None):
    """Monta indicadores derivados sem alterar o dicionário persistido."""
    referencia = _converter_data(data_referencia or date.today())
    total = dados['quantidade_total']
    pagos = quantidade_pagas(dados)
    vencidas = quantidade_vencidas(dados, referencia)
    pagamentos = set(dados['pagamentos'])
    vencidas_nao_pagas = sum(numero not in pagamentos for numero in range(1, vencidas + 1))
    proxima_parcela, proxima_data = proximo_vencimento(dados, referencia)
    valor = decimal_monetario(dados.get('valor_parcela'))
    valor_total = valor * total if valor is not None else None
    valor_pago = valor * pagos if valor is not None else None
    saldo = valor_total - valor_pago if valor is not None else None

    return {
        **dados,
        'data_referencia': referencia.isoformat(),
        'quantidade_vencida': vencidas,
        'quantidade_vencida_nao_paga': vencidas_nao_pagas,
        'quantidade_futura': total - vencidas,
        'quantidade_paga': pagos,
        'quantidade_pendente': total - pagos,
        'percentual_pago': formatar_decimal(Decimal(pagos) * 100 / Decimal(total)),
        'valor_total': formatar_decimal(valor_total) if valor_total is not None else None,
        'valor_pago': formatar_decimal(valor_pago) if valor_pago is not None else None,
        'saldo_restante': formatar_decimal(saldo) if saldo is not None else None,
        'ultimo_vencimento': vencimento(dados['primeiro_vencimento'], total),
        'proxima_parcela': proxima_parcela,
        'proximo_vencimento': proxima_data,
        'historico': historico_mensal(dados, referencia),
    }


def resumo_financeiro(parcelamentos, data_referencia=None):
    """Soma os dois contratos com Decimal e retorna um resumo combinado."""
    itens = [resumo(item, data_referencia) for item in parcelamentos]

    def somar(campo):
        valores = [Decimal(item[campo]) for item in itens if item[campo] is not None]
        return formatar_decimal(sum(valores, Decimal('0.00')))

    mensalidades = [
        decimal_monetario(item.get('valor_parcela'))
        for item in parcelamentos
        if item.get('valor_parcela') is not None
    ]
    return {
        'data_referencia': _converter_data(data_referencia or date.today()).isoformat(),
        'total_contratado': somar('valor_total'),
        'total_pago': somar('valor_pago'),
        'saldo_restante': somar('saldo_restante'),
        'mensalidade_combinada': formatar_decimal(sum(mensalidades, Decimal('0.00'))),
        'parcelamentos': itens,
    }


def _converter_data(valor):
    if isinstance(valor, date):
        return valor
    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError) as erro:
        raise ValueError('Data de referência deve estar no formato AAAA-MM-DD.') from erro
