# Deploy manual — Vercel e Hostinger

Nenhuma publicação foi executada nesta preparação. Substitua os exemplos pelos seus domínios reais.

## 1. Conferência de privacidade e GitHub

Inicialize o Git somente após revisar os arquivos:

```powershell
git init
git status --short --ignored
git check-ignore data\parcelas.json
git check-ignore data\parcelas.json.backup-antes-dados-confirmados-2026-10-29-v1
git check-ignore backend\migrar_dados_2026.py
python -m unittest discover -s backend -p "test_*.py"
```

Antes de cada commit, procure nomes, valores, chaves e tokens próprios. `.gitignore` impede novos arquivos, mas não apaga um segredo já commitado. Para repetir a auditoria do histórico, use:

```powershell
git log --all --stat
git log --all -p -- data
git rev-list --objects --all
```

Se encontrar dado privado no histórico, não torne o repositório público; revogue credenciais expostas e reescreva o histórico com uma ferramenta apropriada antes do push.

## 2. Publicar a API na Vercel

1. Crie um repositório privado no GitHub e envie-o somente depois da auditoria e autorização.
2. Na Vercel, importe o repositório mantendo a raiz do projeto.
3. Em **Environment Variables**, defina:
   - `HOSTINGER_ALLOWED_ORIGIN=https://seudominio.com.br`
   - `ALLOW_LOCALHOST_CORS=false`
4. Faça o deploy e anote a URL real, por exemplo `https://seu-projeto.vercel.app`.
5. Não envie `data/`, `.env`, backups ou a migração privada.

Teste as URLs reais:

```powershell
curl.exe -i https://seu-projeto.vercel.app/api/health
curl.exe -i https://seu-projeto.vercel.app/api/resumo
curl.exe -i https://seu-projeto.vercel.app/api/parcelamentos
curl.exe -i -X POST https://seu-projeto.vercel.app/api/parcelamentos
curl.exe -i -X OPTIONS https://seu-projeto.vercel.app/api/resumo -H "Origin: https://seudominio.com.br" -H "Access-Control-Request-Method: GET"
```

Espere respectivamente JSON 200 nas três consultas, 405 no POST e 204 com `Access-Control-Allow-Origin` no OPTIONS.

## 3. Publicar o frontend na Hostinger

1. Edite `frontend/config.js` e troque `https://SEU-PROJETO.vercel.app` pela URL real.
2. Envie somente o conteúdo de `frontend/` para `public_html` (ou para a pasta do domínio): `index.html`, `style.css`, `config.js` e `script.js`.
3. Abra o domínio por HTTPS e confira o painel responsivo no navegador e no celular.
4. No DevTools, aba Network, confirme que `/api/resumo` vai para a Vercel e retorna JSON 200.

A URL da API não é segredo. Senhas, tokens e chaves jamais podem aparecer em `config.js`.

## 4. Desenvolvimento local

Para a aplicação privada existente:

```powershell
python backend\main.py
```

Para testar especificamente a função pública, use os testes automatizados. Ao usar Vercel localmente, defina `ALLOW_LOCALHOST_CORS=true` apenas no ambiente de desenvolvimento e volte para `false` em produção.

## 5. Diagnóstico rápido

- **Erro de CORS:** confirme que `HOSTINGER_ALLOWED_ORIGIN` contém protocolo e domínio exatos, sem barra final, e refaça o deploy da API.
- **HTML no lugar de JSON:** confirme a URL em `config.js` e as regras de rewrite de `vercel.json`.
- **404 na API:** teste primeiro `/api/health` na URL real da Vercel.
- **Frontend sem estilo:** envie os quatro arquivos juntos; os caminhos são relativos para funcionar também em subpastas.
- **Mudanças não salvas:** esperado; a versão pública é somente leitura.

Deploy só está concluído quando as URLs reais da Vercel e da Hostinger forem verificadas. Este documento não substitui essa validação.
