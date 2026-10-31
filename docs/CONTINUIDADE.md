# Continuidade

O produto público chama-se **Objetivos** e foi generalizado para que outras pessoas possam acompanhar diferentes objetivos parcelados.

## Estado da primeira fase

A arquitetura foi separada sem alterar as regras financeiras de `backend/parcelas.py`:

- a aplicação privada local continua em `backend/main.py` e `backend/storage.py`;
- a API pública fica em `api/index.py`, usa somente `api/demo_data.py` e aceita apenas GET/OPTIONS;
- o frontend público fica em `frontend/`; a URL pública da API está centralizada no topo de `frontend/script.js`;
- `vercel.json` encaminha as três URLs públicas para a função única;
- `.gitignore` impede a inclusão dos dados reais, backups, segredos e cache.

Não há persistência pública nesta fase. POST, PUT e DELETE retornam HTTP 405. O cenário público usa a data-base fixa `29/10/2026`, definida junto aos dados fictícios, para que os resultados sejam reproduzíveis.

## Antes de continuar

1. Execute todos os testes.
2. Confira `git status --ignored` depois de iniciar o repositório.
3. Procure segredos e dados privados antes de cada commit.
4. Só implemente escrita após autenticação e banco externo.

Em 31/10/2026, o repositório e seus objetos Git foram auditados. O histórico continha somente o README e não foram encontrados JSON real, backup, `.env` privado ou script de migração. O remoto configurado não foi alterado nem recebeu push nesta etapa.

## Integração real preparada

- Frontend: `https://simulador-parcelas.wasxtech.com.br`.
- Diretório informado: `/home/u587444950/domains/wasxtech.com.br/public_html/simulador-parcelas`.
- Artefato para envio: `deploy/hostinger/`, gerado de `frontend/` por `scripts/gerar-deploy-hostinger.ps1`.
- ZIP para upload manual: `deploy/simulador-parcelas-hostinger.zip`, com `index.html` diretamente na raiz.
- Backend: Vercel Function em `api/index.py`, publicada em `https://simulador-parcelas-objetivos.vercel.app`.
- CORS de produção: somente a origem exata do subdomínio acima.

O DNS do subdomínio foi resolvido em 31/10/2026. O caminho interno da Hostinger não pode ser confirmado por DNS; confira o diretório raiz no painel antes da publicação.

## CI/CD preparado

- `.github/workflows/ci.yml`: valida PRs, pushes na `main` e execução manual.
- `.github/workflows/deploy-hostinger.yml`: atualiza `hostinger-pages` somente após CI aprovada para o mesmo SHA da `main` ou por execução manual protegida.
- A Vercel mantém sua integração Git nativa; não foi criado deploy duplicado por CLI.
- A Hostinger deve acompanhar `hostinger-pages` pelo Git nativo do hPanel e pelo webhook real já cadastrado manualmente no GitHub.

## Falha do Deploy Hostinger #2

O run `41175833129`, no commit `6cb7c2a0f641c4a093d9926dde829dcbf61de2bb`, parou em **Validar configuração SSH**. Checkout, SHA e pacote público já haviam passado. A causa confirmada foi a ausência dos cinco Environment Secrets e da variável `HOSTINGER_DEPLOY_PATH`; nenhuma transferência ocorreu.

O workflow agora informa nominalmente cada configuração ausente, sem mostrar valores. Também usa Actions compatíveis com Node.js 24, verifica o site depois da ativação e tenta rollback automático se a verificação pública falhar.

## Substituição do SSH por Git/Webhook

O workflow SSH foi substituído pela publicação incremental da branch `hostinger-pages`. O novo CD exige somente `HOSTINGER_PAGES_TOKEN`, restrito ao repositório e com `Contents: read/write`. A branch contém apenas `index.html`, `style.css` e `script.js` na raiz e não usa force push.

A falha atual ocorre antes do push: `HOSTINGER_PAGES_TOKEN` ainda precisa existir como Secret do Environment `production-hostinger`. Sem ele, a branch não é atualizada e o webhook já cadastrado não recebe um novo evento. A ativação também depende de o hPanel estar apontando para `hostinger-pages` e para a raiz confirmada do subdomínio. Nenhuma URL de webhook foi criada, substituída ou registrada no repositório por esta preparação.

## Atualização financeira aguardando publicação

O commit funcional `767ea69` substituiu os exemplos antigos por Objetivo principal e Objetivo secundário, ambos com 67 parcelas e 33 pagamentos fictícios. Também adicionou o marcador visível `Versão: <SHA>` ao artefato gerado pelo CD. O CI e o push de `hostinger-pages` foram comprovados no run #9; o usuário e a verificação posterior confirmaram a versão no domínio.

Antes do push, as URLs públicas foram consultadas em `31/10/2026`: Vercel respondeu 200, CORS autorizou a origem Hostinger, OPTIONS respondeu 204 e POST respondeu 405. A produção ainda apresentava o cenário antigo (R$ 3.420,00 contratados) e a Hostinger servia o SHA `c8e8413116850ea73f912cb469b78e2533c16824`, como esperado antes da nova publicação.

Próxima etapa: após autorização, enviar a `main` e observar cada elo sem realizar deploy manual.

## Diagnóstico da verificação do run #9

O run `41184361538` aprovou o CI e atualizou `hostinger-pages` para o commit público `1273203`, mas a verificação terminou após aproximadamente 3 minutos sem registrar as respostas intermediárias. Depois, o domínio foi confirmado com HTTP 200, `text/html` e o SHA esperado `3453a1e028c6b4133719f3692b461de6f80886f1`.

Não há evidência suficiente para afirmar se, durante as 18 tentativas, houve HTTP diferente de 200, conteúdo antigo ou atraso de publicação. A causa confirmada é a falta de diagnóstico do verificador anterior. O novo `scripts/verificar_deploy.py` registra cada status e diferencia rede, HTTP, conteúdo e versão, mantendo falha quando não há comprovação.
