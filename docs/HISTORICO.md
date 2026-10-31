# Histórico de alterações

## 31/10/2026 — finalização do fluxo por webhook

- Diagnosticada a falha atual como ausência de `HOSTINGER_PAGES_TOKEN` no Environment `production-hostinger`, antes de qualquer push.
- Mantido o PAT dedicado para que a atualização de `hostinger-pages` produza um evento de push normal para o webhook externo.
- Registrado que o webhook Hostinger já foi cadastrado manualmente e não deve ser duplicado ou substituído.
- Reforçados os testes para rejeitar configuração de uma segunda URL de webhook no workflow.
- API Python, regras financeiras e configuração Vercel preservadas.

## 31/10/2026 — migração do CD para Git/Webhook Hostinger

- Removidos SSH, SCP, cinco Secrets SSH e variável de caminho do workflow ativo.
- Adicionada publicação incremental de `hostinger-pages` após CI verde da `main`.
- Adotado PAT fine-grained `HOSTINGER_PAGES_TOKEN` para gerar o push consumido pelo webhook.
- Limitada a branch pública a três arquivos estáticos na raiz.
- Adicionada marca do SHA aprovado ao HTML e verificação do domínio.
- Preservado rollback por SHA anterior, sem force push.
- Documentada configuração Git/webhook sem inventar URL.
- API Python e Vercel preservadas.

## 31/10/2026 — diagnóstico definitivo do CD Hostinger

- Confirmada a falha do run `41175833129` por Secrets e variável ausentes no ambiente `production-hostinger`.
- Substituído o `exit code 1` genérico por mensagens individuais sem exposição de valores.
- Tornada exata a validação do diretório remoto autorizado.
- Atualizados `actions/checkout` e `actions/setup-python` para releases estáveis baseadas em Node.js 24, fixadas por SHA.
- Adicionada verificação HTTP do HTML e JavaScript publicados.
- Adicionado rollback automático dos três arquivos se a verificação pública pós-ativação falhar.
- API Python e configuração Vercel preservadas.

## 31/10/2026 — correção do pacote Hostinger

- Reutilizado o `frontend/index.html` existente, sem página alternativa ou redirecionamento.
- Reduzido o pacote público para `index.html`, `style.css` e `script.js`.
- Centralizada a URL Vercel no topo de `script.js`; removido o `config.js` desnecessário.
- Melhorado o tratamento de falha de conexão, CORS, HTTP e JSON inválido.
- Criado ZIP com `index.html` diretamente na raiz e teste automatizado de sua estrutura.
- API Python, regras financeiras, armazenamento, endpoints e `vercel.json` preservados.

## 31/10/2026 — CI/CD seguro e mínimo

- Criada CI para sintaxe, unittest, regressão financeira, JavaScript, JSON, arquivos essenciais e privacidade.
- Criado CD Hostinger condicionado à CI aprovada e ao SHA exato da `main`.
- Actions externas fixadas por SHA e permissões reduzidas a leitura.
- Adicionados ambiente de produção, controle de concorrência, host SSH conhecido, preparação temporária e cópia para rollback.
- Mantido o deploy Git nativo da Vercel, sem Vercel CLI duplicada.
- Configurada no frontend a URL real `https://simulador-parcelas-objetivos.vercel.app`.
- Criado teste histórico isolado, sem leitura do JSON privado.

## 31/10/2026 — integração Hostinger + Vercel

- Configurada a origem CORS `https://simulador-parcelas.wasxtech.com.br`.
- Mantida vazia a URL Vercel de produção até o primeiro deploy real.
- Criado `deploy/hostinger/` com os quatro arquivos estáticos necessários.
- Criado gerador PowerShell para reproduzir o artefato a partir de `frontend/`.
- Adicionados testes de conteúdo, caminhos relativos e ausência de dados privados no artefato.
- DNS do subdomínio confirmado; associação ao diretório interno aguarda conferência no painel Hostinger.

## 31/10/2026 — identidade genérica “Objetivos”

- Substituída a identidade específica do terreno por “Objetivos”.
- Generalizados os exemplos públicos para curso e equipamento fictícios.
- Preservadas as rotas REST existentes para não quebrar compatibilidade.

## 30/10/2026 — preparação para Vercel e Hostinger

- Criada a função serverless `api/index.py`, sem `serve_forever()`.
- Publicadas somente `GET /api/health`, `/api/resumo` e `/api/parcelamentos`.
- Criado conjunto separado e explicitamente fictício em `api/demo_data.py`.
- Desabilitados POST, PUT e DELETE na API pública com HTTP 405.
- Adicionado CORS por origem exata, preflight OPTIONS e localhost opcional.
- Separada a URL da API em `frontend/config.js` e removidas ações de escrita da interface pública.
- Adicionados `vercel.json`, `.env.example`, `.gitignore` e testes da função pública.
- Sanitizadas fixtures e documentação versionáveis; o JSON real não foi alterado.
- Detectada ausência de repositório Git local, impossibilitando auditoria de commits antigos neste diretório.

## Estado anterior preservado

As regras de calendário, `Decimal`, validação e agregação permanecem em `backend/parcelas.py`. A aplicação local ainda pode persistir no JSON privado; ela não é a API enviada ao público.
