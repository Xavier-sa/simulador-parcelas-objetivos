# CI/CD — GitHub Actions, Vercel e Hostinger

## Visão rápida

**LEIGO:** CI é a conferência automática do trabalho. CD é a entrega automática depois que a conferência passa.

**TÉCNICO:** Continuous Integration executa validações reproduzíveis em pushes e pull requests. Continuous Delivery promove um SHA aprovado para um ambiente protegido.

**PRÁTICO:** abra a aba **Actions**, escolha CI, execute manualmente e acompanhe cada etapa.

## Workflows, jobs e steps

**LEIGO:** workflow é a receita; job é uma parte da receita; step é uma ação pequena dessa parte.

**TÉCNICO:** arquivos YAML em `.github/workflows/` definem eventos, permissões, jobs, runners e steps. O projeto possui `ci.yml` e `deploy-hostinger.yml`.

**PRÁTICO:** encontre no `ci.yml` o job `validar` e conte quantos steps ele executa.

## Gatilhos

**LEIGO:** push executa quando algo chega à `main`; pull request confere antes da união; manual permite iniciar pela interface.

**TÉCNICO:** CI usa `push`, `pull_request` e `workflow_dispatch`. O CD usa `workflow_run` e só aceita conclusão bem-sucedida de um push na `main`; PR nunca publica.

**PRÁTICO:** abra um PR com uma alteração apenas na documentação e confirme que CI executa, mas Deploy Hostinger não publica.

## O que a CI verifica

1. Checkout do SHA do evento.
2. Python 3.12 fixo.
3. Sintaxe Python.
4. Regressão financeira histórica isolada.
5. Todos os testes `unittest`.
6. Sintaxe JavaScript com `node --check`, sem executar a aplicação.
7. Arquivos essenciais, `vercel.json`, dados demonstrativos e privacidade.

Para testar uma reprovação com segurança, crie uma branch temporária, altere um valor esperado em um teste, abra um PR e depois reverta a alteração. Para JavaScript, introduza temporariamente um parêntese sem fechamento. Nunca faça esses experimentos diretamente na `main`.

## Secrets e variável

Em **GitHub → Settings → Secrets and variables → Actions**, cadastre no ambiente `production-hostinger`:

- Secret `HOSTINGER_HOST`: host SSH/SFTP confirmado no hPanel.
- Secret `HOSTINGER_PORT`: porta confirmada no hPanel.
- Secret `HOSTINGER_USER`: usuário com acesso apenas ao necessário.
- Secret `HOSTINGER_SSH_KEY`: chave privada dedicada ao deploy.
- Secret `HOSTINGER_KNOWN_HOSTS`: linha do host obtida e conferida por canal confiável; para porta não padrão, use o formato `[host]:porta` fornecido pelo `ssh-keyscan` e compare a impressão digital no hPanel.
- Variable `HOSTINGER_DEPLOY_PATH`: `/home/u587444950/domains/wasxtech.com.br/public_html/simulador-parcelas`.

Nunca copie valores desses Secrets para arquivos do repositório. Configure proteção do ambiente com revisores obrigatórios, se o plano permitir.

### Causa da falha observada

No run `41175833129`, os cinco Secrets e a variável chegaram vazios. O workflow estava associado ao ambiente correto e bloqueou antes do upload. Portanto, a causa principal é configuração manual ausente, não falha do frontend, do SHA ou da API. O YAML foi melhorado para listar apenas os nomes ausentes.

### Preparar uma chave exclusiva

**LEIGO:** a chave pública é o cadeado colocado na Hostinger; a chave privada é a única chave que abre esse cadeado e fica protegida no GitHub.

**TÉCNICO:** use um par Ed25519 dedicado, sem reutilizar sua chave pessoal. A private key vira Secret; somente a public key é autorizada no servidor.

No PowerShell local:

```powershell
ssh-keygen -t ed25519 -a 100 -C "github-actions-simulador-parcelas" -f "$env:USERPROFILE\.ssh\hostinger_deploy_simulador"
```

Para automação não interativa, a chave precisa estar utilizável pelo runner sem prompt. Proteja esse risco restringindo a chave à conta de hospedagem, usando ambiente protegido e removendo-a no hPanel quando não for mais necessária.

### Autorizar e identificar a conexão

1. No hPanel, abra **Websites → Dashboard → SSH Access** e habilite SSH.
2. Copie de lá o host/IP, porta e usuário reais.
3. Em **Add SSH key**, cole todo o conteúdo de `hostinger_deploy_simulador.pub`.
4. Cadastre o conteúdo do arquivo privado `hostinger_deploy_simulador` como `HOSTINGER_SSH_KEY` no ambiente GitHub.
5. Não presuma porta ou usuário. A porta frequente da Hostinger é 65002, mas vale a informação exibida na conta.

SSH por chave está disponível nos planos compatíveis da Hostinger; planos Single ou modo Website Builder podem não oferecer shell. Se houver apenas SFTP, o workflow atual, que usa comandos remotos seguros para ativação e rollback, não é compatível. Nesse caso, mantenha o CD bloqueado e publique o ZIP pelo hPanel/SFTP até escolher uma automação específica para SFTP.

### Known hosts e teste sem expor segredo

Obtenha a chave apresentada pelo servidor usando os valores reais:

```powershell
ssh-keyscan -p <PORTA> <HOST> | Set-Content -Encoding ascii hostinger_known_hosts
ssh-keygen -lf hostinger_known_hosts
```

Compare a impressão digital com a exibida no hPanel ou confirmada pelo suporte Hostinger. Só depois cadastre o conteúdo de `hostinger_known_hosts` como `HOSTINGER_KNOWN_HOSTS`.

Teste localmente sem imprimir a chave:

```powershell
ssh -i "$env:USERPROFILE\.ssh\hostinger_deploy_simulador" -p <PORTA> -o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=hostinger_known_hosts <USUARIO>@<HOST> "pwd; test -d '/home/u587444950/domains/wasxtech.com.br/public_html/simulador-parcelas'; test -w '/home/u587444950/domains/wasxtech.com.br/public_html/simulador-parcelas'"
```

**PRÁTICO:** execute primeiro apenas `pwd` e compare o diretório retornado com o caminho informado, sem criar, mover ou apagar arquivos.

## Vercel versus Hostinger

**LEIGO:** a Vercel observa o GitHub por conta própria. A Hostinger recebe os três arquivos públicos pelo nosso workflow.

**TÉCNICO:** o CI não bloqueia automaticamente a integração Git da Vercel. Configure proteção da `main` exigindo o check **Validar aplicação** antes do merge. Se disponível no plano Vercel, use Deployment Checks ou promoção manual para impedir produção antes da aprovação.

**PRÁTICO:** em **Settings → Branches → Branch protection**, exija pull request e o status check da CI para `main`.

## Segurança do deploy Hostinger

O CD baixa o SHA aprovado, confirma que ele pertence à `main`, prepara somente três arquivos, impede concorrência e exige host conhecido. O upload vai primeiro para `.incoming-<SHA>`. Antes da substituição, os três arquivos anteriores são copiados para `.rollback-<SHA>`.

O workflow requer SSH com execução de comandos fixos. Se a conta tiver somente SFTP, não cadastre os Secrets para este workflow: gere o ZIP e extraia manualmente seus três arquivos pelo hPanel/SFTP.

Depois da ativação, o workflow consulta o domínio com HTTPS e confere o título da página e a URL Vercel em `script.js`. Se essa etapa falhar, restaura os três arquivos guardados em `.rollback-<SHA>` e mantém o job reprovado para investigação.

## Rollback

**LEIGO:** rollback é voltar aos três arquivos que estavam no site antes de uma publicação.

**TÉCNICO:** cada deploy preserva os arquivos anteriores em `.rollback-<SHA>`. Um operador com SSH pode copiá-los de volta após confirmar o SHA e o diretório. Outra opção é executar manualmente o workflow informando um SHA anterior que ainda pertença à `main`.

**PRÁTICO:** sem executar em produção, identifique no histórico Git o SHA que seria usado em um rollback e confira seus três arquivos com `git show`.

## Como reconhecer falha

Na aba Actions, verde significa que todos os steps passaram; vermelho indica falha. Abra o job, localize o primeiro step vermelho e leia a mensagem. Não reexecute repetidamente um deploy sem entender a causa.

Quando um Secret estiver ausente, o log agora mostra, por exemplo, `Erro: HOSTINGER_HOST não configurado no ambiente production-hostinger.` O conteúdo do Secret nunca é impresso.
