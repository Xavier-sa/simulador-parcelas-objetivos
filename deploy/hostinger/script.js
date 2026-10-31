// O JavaScript apenas exibe resultados; as regras financeiras ficam no Python.
const cartoes = document.querySelector('#cartoes');
const historico = document.querySelector('#historico');
const mensagem = document.querySelector('#mensagem');
const API_BASE_URL = (window.APP_CONFIG?.apiBaseUrl || '').replace(/\/$/, '');
const formatoData = iso => iso ? iso.split('-').reverse().join('/') : 'Concluído';
const moeda = valor => valor === null ? 'Não informado' : Number(valor).toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'});

async function requisicao(caminho) {
  if (!API_BASE_URL) {
    throw new Error('API ainda não configurada. Informe a URL da Vercel em config.js após o primeiro deploy.');
  }
  let resposta;
  try {
    resposta = await fetch(`${API_BASE_URL}${caminho}`, {method: 'GET'});
  } catch (_) {
    throw new Error('Não foi possível conectar à API. Confira config.js e a configuração de CORS.');
  }
  const tipo = resposta.headers.get('Content-Type') || '';
  if (!tipo.toLowerCase().includes('application/json')) {
    throw new Error(`A API respondeu em formato inesperado (HTTP ${resposta.status}).`);
  }
  const dados = await resposta.json();
  if (!resposta.ok) throw new Error(dados.erro || 'A consulta não pôde ser concluída.');
  return dados;
}

function desenharResumo(resumo) {
  const campos = [['Total contratado', resumo.total_contratado], ['Total pago', resumo.total_pago], ['Saldo restante', resumo.saldo_restante], ['Mensalidade combinada', resumo.mensalidade_combinada]];
  document.querySelector('#resumo').innerHTML = campos.map(([nome, valor]) => `<div class="indicador"><span>${nome}</span><strong>${moeda(valor)}</strong></div>`).join('');
}

function desenharHistorico(itens) {
  historico.replaceChildren();
  for (const item of itens) {
    const grupo = document.createElement('section');
    grupo.className = 'historico-grupo';
    const titulo = document.createElement('h3');
    titulo.textContent = item.nome;
    const lista = document.createElement('div');
    lista.className = 'historico-lista';
    for (const parcela of item.historico) {
      const linha = document.createElement('div');
      linha.className = `mensalidade ${parcela.estado}`;
      const estado = parcela.estado === 'pago' ? 'Pagamento demonstrativo' : parcela.estado === 'vencido' ? 'Vencida no exemplo' : 'A vencer';
      linha.innerHTML = `<strong>Parcela ${parcela.numero}</strong><span>${formatoData(parcela.vencimento)}</span><span>${estado}</span>`;
      lista.appendChild(linha);
    }
    grupo.append(titulo, lista);
    historico.appendChild(grupo);
  }
}

function desenharCartoes(itens) {
  cartoes.replaceChildren();
  for (const item of itens) {
    const secao = document.createElement('article');
    secao.className = 'cartao';
    secao.innerHTML = '<h2></h2><div class="numero"></div><p class="referencia"></p><div class="barra"><div></div></div><div class="estados"><span class="estado pago"></span><span class="estado vencido"></span><span class="estado futuro"></span></div><div class="linha"><span>Valor mensal</span><strong class="valor"></strong></div><div class="linha"><span>Saldo restante</span><strong class="saldo"></strong></div><div class="linha"><span>Próximo vencimento</span><strong class="proximo"></strong></div><div class="linha"><span>Último vencimento</span><strong class="ultimo"></strong></div>';
    secao.querySelector('h2').textContent = item.nome;
    secao.querySelector('.numero').textContent = `${item.quantidade_paga} de ${item.quantidade_total} pagas`;
    secao.querySelector('.referencia').textContent = `${item.percentual_pago}% quitado no exemplo`;
    secao.querySelector('.barra div').style.width = `${item.percentual_pago}%`;
    secao.querySelector('.pago').textContent = `Pagas: ${item.quantidade_paga}`;
    secao.querySelector('.vencido').textContent = `Vencidas e pendentes: ${item.quantidade_vencida_nao_paga}`;
    secao.querySelector('.futuro').textContent = `Futuras: ${item.quantidade_futura}`;
    secao.querySelector('.valor').textContent = moeda(item.valor_parcela);
    secao.querySelector('.saldo').textContent = moeda(item.saldo_restante);
    secao.querySelector('.proximo').textContent = formatoData(item.proximo_vencimento);
    secao.querySelector('.ultimo').textContent = formatoData(item.ultimo_vencimento);
    cartoes.appendChild(secao);
  }
}

async function atualizar() {
  try {
    const resumo = await requisicao('/api/resumo');
    desenharResumo(resumo);
    desenharCartoes(resumo.parcelamentos);
    desenharHistorico(resumo.parcelamentos);
    mensagem.textContent = resumo.demonstracao ? 'Exibindo somente dados fictícios de demonstração.' : '';
  } catch (erro) {
    mensagem.textContent = erro.message;
  }
}

atualizar();
