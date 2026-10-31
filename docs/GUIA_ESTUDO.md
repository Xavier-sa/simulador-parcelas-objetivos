# Guia de estudo — leigo, técnico e prático

## CI e CD

**LEIGO:** CI confere automaticamente; CD entrega a versão que passou na conferência.

**TÉCNICO:** GitHub Actions executa validações por evento e promove o SHA aprovado para um ambiente protegido, com permissões mínimas.

**PRÁTICO:** leia `.github/workflows/ci.yml`, escolha um step e explique qual erro ele detecta. O guia completo está em `docs/CI-CD.md`.

## Serverless

**LEIGO:** a Vercel liga uma pequena execução Python quando chega um pedido e cuida do servidor por nós.

**TÉCNICO:** uma Function é efêmera e orientada a requisições. O runtime instancia `handler`; por isso `api/index.py` não chama `serve_forever()` e não depende de disco persistente.

**PRÁTICO:** abra `api/index.py` e identifique qual classe a Vercel instancia e quais métodos tratam GET e OPTIONS.

## API REST e requisições HTTP

**LEIGO:** o navegador pede dados em um endereço; a API responde com JSON e um número que indica sucesso ou erro.

**TÉCNICO:** cada recurso possui URI, método e contrato. Esta fase expõe GET idempotente; 200 indica sucesso, 204 preflight sem corpo, 404 rota ausente e 405 método proibido.

**PRÁTICO:** consulte `/api/health` e verifique o status, o `Content-Type` e o campo `modo`.

## Deploy

**LEIGO:** deploy é colocar os arquivos em um serviço acessível pela internet.

**TÉCNICO:** Vercel empacota o backend serverless; Hostinger serve os arquivos estáticos. São dois artefatos e duas origens independentes.

**PRÁTICO:** desenhe o caminho: navegador → Hostinger (`index.html`) → Vercel (`/api/resumo`) → JSON.

## CORS

**LEIGO:** é a lista de sites que o navegador aceita deixar conversar com a API.

**TÉCNICO:** a API compara o header `Origin` com uma allowlist exata e responde `Access-Control-Allow-Origin`. OPTIONS faz o preflight. CORS é proteção do navegador, não autenticação.

**PRÁTICO:** rode o teste com a origem autorizada e depois troque para uma origem diferente; compare os headers.

## Variáveis de ambiente

**LEIGO:** são configurações fornecidas ao programa sem gravá-las diretamente no código.

**TÉCNICO:** `HOSTINGER_ALLOWED_ORIGIN` configura a origem de produção; `ALLOW_LOCALHOST_CORS` controla a exceção local. Segredos nunca devem ir a `config.js`, pois JavaScript entregue ao navegador é público.

**PRÁTICO:** copie os nomes de `.env.example` para a configuração da Vercel, sem enviar um arquivo `.env` ao Git.

## Persistência de dados

**LEIGO:** persistir é guardar algo para continuar existindo depois que o programa termina.

**TÉCNICO:** o JSON local é adequado ao protótipo privado, mas o filesystem de Functions não é banco persistente. Escrita pública exigirá autenticação, autorização e armazenamento externo transacional.

**PRÁTICO:** explique por que alterar `api/demo_data.py` durante uma requisição não seria uma forma confiável de salvar um pagamento.

## Separação das regras financeiras

**LEIGO:** a mesma calculadora Python atende o exemplo sem copiar contas para o JavaScript.

**TÉCNICO:** `api/index.py` reutiliza `resumo` e `resumo_financeiro` de `parcelas.py`; valores monetários continuam sendo strings convertidas para `Decimal`.

**PRÁTICO:** altere apenas uma fixture fictícia em um teste, calcule o resultado esperado e confirme que o frontend não precisa mudar.
