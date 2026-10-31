# Histórico de alterações

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
