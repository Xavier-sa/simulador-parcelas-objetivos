# CI/CD — GitHub Actions e Git nativo da Hostinger

## Fluxo escolhido

```text
push main → CI aprovada → hostinger-pages atualizada → webhook → Hostinger publica
```

**LEIGO:** depois dos testes, o GitHub monta uma branch que contém somente o site. A Hostinger observa essa branch e copia os arquivos para o subdomínio.

**TÉCNICO:** `workflow_run` consome o SHA aprovado da `main`, cria um commit incremental em `hostinger-pages` e faz push autenticado por PAT. O Git deploy do hPanel acompanha essa branch e recebe eventos pelo webhook fornecido pela própria Hostinger.

**PRÁTICO:** compare `main` e `hostinger-pages` no GitHub e identifique por que apenas a segunda pode ser publicada como frontend estático.

## CI e branch pública

A CI executa em PR, push na `main` e manualmente. PR nunca publica: o CD exige uma CI bem-sucedida cujo evento original seja `push` na `main`.

`hostinger-pages` contém diretamente na raiz apenas `index.html`, `style.css` e `script.js`. O workflow não usa force push, preservando o histórico. O HTML recebe uma meta `deployment-commit` com o SHA aprovado para verificação posterior.

## Autenticação do push

Crie um fine-grained Personal Access Token dedicado:

1. GitHub → Settings pessoais → Developer settings → Personal access tokens → Fine-grained tokens.
2. Restrinja a `Xavier-sa/simulador-parcelas-objetivos`.
3. Conceda somente **Contents: Read and write**.
4. Defina expiração e rotação.
5. Em **Settings → Environments → production-hostinger**, cadastre o Environment Secret `HOSTINGER_PAGES_TOKEN`.

O PAT é usado porque o push automatizado precisa produzir o evento consumido pelo webhook externo. O `GITHUB_TOKEN` possui supressões para evitar recursão. Nenhum token aparece no YAML, branch pública ou logs.

## Configurar Git no hPanel

1. Confirme que o plano oferece **Git** em **Sites → Gerenciar → Git**.
2. Selecione o repositório correto e a branch `hostinger-pages`.
3. Confirme visualmente que o destino é a raiz de `simulador-parcelas.wasxtech.com.br`.
4. O diretório deve estar vazio na primeira associação Git; faça backup antes de mover os arquivos atuais.
5. Se o Git estiver no contexto do próprio subdomínio e o hPanel mostrar a raiz correta, deixe Install Path vazio. Em outro contexto, não adivinhe o caminho: confirme no painel ou suporte.
6. Faça um deploy manual inicial somente depois que a branch existir.

Para repositório público, use HTTPS. Para repositório privado, o hPanel pode fornecer uma chave de deploy de leitura para GitHub. Essa chave é Hostinger→GitHub e não reintroduz SSH no GitHub Actions.

## Webhook

Ao clicar **Auto Deployment**, o hPanel fornece a URL real. Não registre essa URL em código ou documentação.

No GitHub, use **Settings → Webhooks → Add webhook**:

- Payload URL: URL fornecida pelo hPanel.
- Content type: `application/json`.
- SSL verification: habilitado.
- Evento: somente `push`.
- Active: habilitado.

Configure Secret de assinatura somente se o receptor Hostinger oferecer suporte e exigir o mesmo segredo. Não invente um receptor nem uma URL.

O webhook recebe pushes de outras branches; a integração Hostinger deve permanecer selecionada em `hostinger-pages`. No primeiro teste, confira **Recent Deliveries** e o log do hPanel para confirmar a filtragem e evitar implantação duplicada.

## Verificação e rollback

O workflow aguarda até três minutos e procura no domínio a marca do SHA aprovado. Se ela não aparecer, a branch foi atualizada, mas o deploy Hostinger não está comprovado.

Para rollback, execute manualmente o workflow com um SHA anterior ainda ancestral da `main`. Ele recompõe os três arquivos e cria um novo commit em `hostinger-pages`, sem reescrever o histórico.

**PRÁTICO:** localize um SHA anterior com `git log --oneline` e confira `git show <SHA>:frontend/index.html`, sem executar o deploy.

## Mecanismo SSH anterior

Os commits anteriores preservam o desenho SSH para auditoria. Ele foi removido do workflow ativo. O novo fluxo não usa host, porta, usuário, chave SSH, known_hosts ou caminho remoto no GitHub Actions.
