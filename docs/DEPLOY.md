# Deploy manual — Hostinger + Vercel

Nenhuma publicação ou alteração remota é feita automaticamente.

## Arquitetura

```text
Navegador
  ├─ Hostinger: https://simulador-parcelas.wasxtech.com.br
  │    └─ index.html, style.css e script.js
  └─ Vercel: https://simulador-parcelas-objetivos.vercel.app
       └─ API Python /api/health, /api/resumo e /api/parcelamentos
```

## 1. Publicar primeiro a API na Vercel

1. Importe o repositório na Vercel usando a raiz do projeto.
2. Confirme que `api/index.py` foi reconhecido como Python Function.
3. Configure as variáveis:

```text
HOSTINGER_ALLOWED_ORIGIN=https://simulador-parcelas.wasxtech.com.br
ALLOW_LOCALHOST_CORS=false
```

4. A integração Git da Vercel já publica a API; não há segundo workflow de deploy Vercel.
5. Teste a URL confirmada:

```powershell
curl.exe -i https://simulador-parcelas-objetivos.vercel.app/api/health
curl.exe -i https://simulador-parcelas-objetivos.vercel.app/api/resumo
curl.exe -i https://simulador-parcelas-objetivos.vercel.app/api/parcelamentos
curl.exe -i -X POST https://simulador-parcelas-objetivos.vercel.app/api/parcelamentos
curl.exe -i -X OPTIONS https://simulador-parcelas-objetivos.vercel.app/api/resumo -H "Origin: https://simulador-parcelas.wasxtech.com.br" -H "Access-Control-Request-Method: GET"
```

Resultados esperados: GET 200 com JSON, POST 405 e OPTIONS 204 com a origem autorizada.

## 2. Gerar o frontend da Hostinger

O topo de `frontend/script.js` contém a URL pública:

```javascript
const API_BASE_URL = 'https://simulador-parcelas-objetivos.vercel.app';
```

Depois gere o artefato:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\gerar-deploy-hostinger.ps1
```

`deploy/hostinger/` conterá exclusivamente:

- `index.html`
- `style.css`
- `script.js`

O mesmo comando cria `deploy/simulador-parcelas-hostinger.zip`. Dentro dele, `index.html` fica diretamente na raiz.

Não edite a cópia gerada como fonte principal; altere `frontend/` e gere novamente.

## 3. Confirmar o diretório Hostinger

Domínio: `https://simulador-parcelas.wasxtech.com.br`

Diretório informado: `/home/u587444950/domains/wasxtech.com.br/public_html/simulador-parcelas`

O DNS do subdomínio resolve, mas DNS não comprova o diretório interno. No hPanel, abra **Domínios → Subdomínios** e confirme que o “diretório raiz/document root” é exatamente o caminho informado. Por SSH, uma alternativa é conferir o caminho e os arquivos sem mover ou apagar nada.

Somente depois dessa confirmação, extraia `deploy/simulador-parcelas-hostinger.zip` diretamente em `/home/u587444950/domains/wasxtech.com.br/public_html/simulador-parcelas`. O resultado precisa ser `.../simulador-parcelas/index.html`, não `.../simulador-parcelas/hostinger/index.html` nem outra subpasta.

## 4. Verificação final

1. Abra `https://simulador-parcelas.wasxtech.com.br`.
2. Confirme HTTPS, estilo e responsividade.
3. No DevTools → Network, confirme que `/api/resumo` vai para a URL Vercel e retorna JSON 200.
4. Confirme que nenhuma chamada POST, PUT ou DELETE é feita.
5. Teste uma rota inexistente e confirme JSON 404 na API.

## Decisões

**LEIGO:** o site precisa encontrar `index.html` logo na pasta principal do subdomínio. O ZIP já organiza os três arquivos dessa maneira.

**TÉCNICO:** a API base não é inferida nem inventada. O artefato estático é reproduzível, usa caminhos relativos e consome uma origem distinta protegida por allowlist CORS exata.

**LEIGO:** o arquivo de dados real fica somente no computador.

**TÉCNICO:** `.gitignore`, `.vercelignore`, API demonstrativa imutável e testes do artefato impedem a inclusão acidental de persistência local e dados privados.

Para CI/CD, Secrets, proteção da `main` e rollback, consulte `docs/CI-CD.md`.
