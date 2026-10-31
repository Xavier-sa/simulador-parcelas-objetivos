# Continuidade

O produto público chama-se **Objetivos** e foi generalizado para que outras pessoas possam acompanhar diferentes objetivos parcelados.

## Estado da primeira fase

A arquitetura foi separada sem alterar as regras financeiras de `backend/parcelas.py`:

- a aplicação privada local continua em `backend/main.py` e `backend/storage.py`;
- a API pública fica em `api/index.py`, usa somente `api/demo_data.py` e aceita apenas GET/OPTIONS;
- o frontend público fica em `frontend/` e obtém a URL da API em `frontend/config.js`;
- `vercel.json` encaminha as três URLs públicas para a função única;
- `.gitignore` impede a inclusão dos dados reais, backups, segredos e cache.

Não há persistência pública nesta fase. POST, PUT e DELETE retornam HTTP 405. A data de referência da demonstração é calculada no dia da requisição.

## Antes de continuar

1. Execute todos os testes.
2. Confira `git status --ignored` depois de iniciar o repositório.
3. Procure segredos e dados privados antes de cada commit.
4. Só implemente escrita após autenticação e banco externo.

Em 31/10/2026, o repositório e seus objetos Git foram auditados. O histórico continha somente o README e não foram encontrados JSON real, backup, `.env` privado ou script de migração. O remoto configurado não foi alterado nem recebeu push nesta etapa.
