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

## Vercel versus Hostinger

**LEIGO:** a Vercel observa o GitHub por conta própria. A Hostinger recebe os quatro arquivos pelo nosso workflow.

**TÉCNICO:** o CI não bloqueia automaticamente a integração Git da Vercel. Configure proteção da `main` exigindo o check **Validar aplicação** antes do merge. Se disponível no plano Vercel, use Deployment Checks ou promoção manual para impedir produção antes da aprovação.

**PRÁTICO:** em **Settings → Branches → Branch protection**, exija pull request e o status check da CI para `main`.

## Segurança do deploy Hostinger

O CD baixa o SHA aprovado, confirma que ele pertence à `main`, prepara somente quatro arquivos, impede concorrência e exige host conhecido. O upload vai primeiro para `.incoming-<SHA>`. Antes da substituição, os quatro arquivos anteriores são copiados para `.rollback-<SHA>`.

O workflow requer SSH com execução de comandos fixos. Se a conta tiver somente SFTP, não cadastre os Secrets para este workflow: gere `deploy/hostinger/` e envie manualmente os quatro arquivos pelo hPanel/SFTP.

## Rollback

**LEIGO:** rollback é voltar aos quatro arquivos que estavam no site antes de uma publicação.

**TÉCNICO:** cada deploy preserva os arquivos anteriores em `.rollback-<SHA>`. Um operador com SSH pode copiá-los de volta após confirmar o SHA e o diretório. Outra opção é executar manualmente o workflow informando um SHA anterior que ainda pertença à `main`.

**PRÁTICO:** sem executar em produção, identifique no histórico Git o SHA que seria usado em um rollback e confira seus quatro arquivos com `git show`.

## Como reconhecer falha

Na aba Actions, verde significa que todos os steps passaram; vermelho indica falha. Abra o job, localize o primeiro step vermelho e leia a mensagem. Não reexecute repetidamente um deploy sem entender a causa.
