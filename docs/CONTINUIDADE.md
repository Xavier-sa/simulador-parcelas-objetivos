# Continuidade

O produto público chama-se **Objetivos** e foi generalizado para que outras pessoas possam acompanhar diferentes objetivos parcelados.

## Estado da primeira fase

A arquitetura foi separada sem alterar as regras financeiras de `backend/parcelas.py`:

- a aplicação privada local continua em `backend/main.py` e `backend/storage.py`;
- a API pública fica em `api/index.py`, usa somente `api/demo_data.py` e aceita apenas GET/OPTIONS;
- o frontend público fica em `frontend/`; a URL pública da API está centralizada no topo de `frontend/script.js`;
- `vercel.json` encaminha as três URLs públicas para a função única;
- `.gitignore` impede a inclusão dos dados reais, backups, segredos e cache.

Não há persistência pública nesta fase. POST, PUT e DELETE retornam HTTP 405. A data de referência da demonstração é calculada no dia da requisição.

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
- `.github/workflows/deploy-hostinger.yml`: publica somente após CI aprovada para o mesmo SHA da `main` ou por execução manual protegida.
- A Vercel mantém sua integração Git nativa; não foi criado deploy duplicado por CLI.
- O CD Hostinger depende da confirmação de SSH com shell, dos Secrets e da variável documentados em `docs/CI-CD.md`.

## Falha do Deploy Hostinger #2

O run `41175833129`, no commit `6cb7c2a0f641c4a093d9926dde829dcbf61de2bb`, parou em **Validar configuração SSH**. Checkout, SHA e pacote público já haviam passado. A causa confirmada foi a ausência dos cinco Environment Secrets e da variável `HOSTINGER_DEPLOY_PATH`; nenhuma transferência ocorreu.

O workflow agora informa nominalmente cada configuração ausente, sem mostrar valores. Também usa Actions compatíveis com Node.js 24, verifica o site depois da ativação e tenta rollback automático se a verificação pública falhar.
