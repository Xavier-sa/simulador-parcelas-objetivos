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

O DNS do subdomínio resolve, mas DNS não comprova o diretório interno. No hPanel, abra **Domínios → Subdomínios** e confirme que o “diretório raiz/document root” é exatamente o caminho informado.

Somente depois dessa confirmação, extraia `deploy/simulador-parcelas-hostinger.zip` diretamente em `/home/u587444950/domains/wasxtech.com.br/public_html/simulador-parcelas`. O resultado precisa ser `.../simulador-parcelas/index.html`, não `.../simulador-parcelas/hostinger/index.html` nem outra subpasta.

## 4. Verificação final

1. Abra `https://simulador-parcelas.wasxtech.com.br`.
2. Confirme HTTPS, estilo e responsividade.
3. No DevTools → Network, confirme que `/api/resumo` vai para a URL Vercel e retorna JSON 200.
4. Confirme que nenhuma chamada POST, PUT ou DELETE é feita.
5. Teste uma rota inexistente e confirme JSON 404 na API.
6. Compare `Versão: <SHA>` no rodapé com o SHA aprovado pela CI.

## Decisões

**LEIGO:** o site precisa encontrar `index.html` logo na pasta principal do subdomínio. O ZIP já organiza os três arquivos dessa maneira.

**TÉCNICO:** a API base não é inferida nem inventada. O artefato estático é reproduzível, usa caminhos relativos e consome uma origem distinta protegida por allowlist CORS exata.

**LEIGO:** o arquivo de dados real fica somente no computador.

**TÉCNICO:** `.gitignore`, `.vercelignore`, API demonstrativa imutável e testes do artefato impedem a inclusão acidental de persistência local e dados privados.

Para CI/CD, Secrets, proteção da `main` e rollback, consulte `docs/CI-CD.md`.

## Primeiro deploy automático

1. Cadastre `HOSTINGER_PAGES_TOKEN` no ambiente `production-hostinger`.
2. Após o primeiro push autorizado, confirme que `hostinger-pages` contém apenas os três arquivos.
3. No hPanel, configure Git para o repositório e branch `hostinger-pages`, confirmando a raiz do subdomínio.
4. Em GitHub **Settings → Webhooks**, confirme que o webhook já cadastrado está ativo para o evento `push`; não crie outro nem altere sua URL.
5. No hPanel, confirme que Auto Deployment usa a mesma integração e faça o deploy inicial se o painel exigir.
6. Nas atualizações seguintes, acompanhe **Actions → CI**, **Publicar branch Hostinger**, **Recent Deliveries** do webhook e o histórico no hPanel.

Se o ambiente exigir revisores, o processo pausa antes de liberar os Secrets. Isso preserva a segurança, mas significa que o deploy não é totalmente automático até uma pessoa aprovar.

Para confirmar a publicação, abra os logs do step **Verificar publicação da Hostinger** e confira a entrega do webhook e o último deploy no hPanel.

## Teste controlado executado

Os commits `767ea69` e `3453a1e` foram enviados e o fluxo atualizou `hostinger-pages`. O domínio passou a exibir o SHA esperado e os dados corrigidos, embora o run #9 tenha encerrado antes de reconhecê-los. A próxima alteração deve repetir a observação sem usar o botão de deploy manual.

Linha de base medida antes do teste: API Vercel acessível com GET 200, OPTIONS 204 e POST 405; CORS permitiu exatamente a origem Hostinger. O frontend estava acessível com a marca `c8e8413116850ea73f912cb469b78e2533c16824` e ainda consumia os exemplos anteriores. Isso não comprova o novo CD; serve para comparar o estado depois do push autorizado.

Se a integração Hostinger foi recriada, abra a configuração **Auto Deployment** no hPanel e compare cuidadosamente a URL mostrada com a Payload URL do webhook existente em GitHub **Settings → Webhooks**. Se forem diferentes, desative ou corrija o cadastro antigo em vez de criar duplicatas. Nunca copie essas URLs para a documentação ou para o frontend.

## Repetir somente a validação

Sem publicar nada, execute:

```powershell
python scripts/verificar_deploy.py --url https://simulador-parcelas.wasxtech.com.br --sha SHA_COMPLETO --tentativas 1 --intervalo 0 --timeout 10
```

Para o CD, o workflow usa 24 tentativas, intervalo de 10 segundos e timeout de 10 segundos. Mesmo no pior caso, a verificação permanece dentro do limite de 10 minutos do job. Redirecionamentos HTTPS são seguidos pela biblioteca padrão, mas o log mostra somente esquema, host e caminho finais. TLS continua validado; não há opção insegura.

No run #9, os logs comprovaram o push da branch, mas não guardaram status ou HTML das tentativas. Por isso, atraso, cache e bloqueio HTTP permanecem hipóteses não confirmadas para aquela janela. A consulta posterior com o novo script confirmou HTTP 200, `text/html` e o SHA esperado.
