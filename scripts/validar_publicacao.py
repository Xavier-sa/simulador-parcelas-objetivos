"""Valida arquivos públicos sem acessar dados privados."""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ESSENCIAIS = {
    'api/index.py', 'api/demo_data.py', 'backend/parcelas.py',
    'frontend/index.html', 'frontend/style.css', 'frontend/script.js', 'vercel.json',
}
PUBLICOS = [RAIZ / 'frontend', RAIZ / 'deploy' / 'hostinger', RAIZ / 'api']
PROIBIDOS = ('parcelas.json', 'backup-antes', 'BEGIN PRIVATE KEY', '1000.00')


def validar():
    ausentes = sorted(caminho for caminho in ESSENCIAIS if not (RAIZ / caminho).is_file())
    if ausentes:
        raise SystemExit('Arquivos essenciais ausentes: ' + ', '.join(ausentes))

    with (RAIZ / 'vercel.json').open(encoding='utf-8') as arquivo:
        json.load(arquivo)

    demo = (RAIZ / 'api' / 'demo_data.py').read_text(encoding='utf-8')
    if "'demonstracao': True" not in demo:
        raise SystemExit('Dados públicos não estão identificados como demonstração.')

    for pasta in PUBLICOS:
        for arquivo in pasta.rglob('*'):
            if not arquivo.is_file() or '__pycache__' in arquivo.parts:
                continue
            if arquivo.suffix not in {'.py', '.html', '.css', '.js', '.json'}:
                continue
            texto = arquivo.read_text(encoding='utf-8')
            for proibido in PROIBIDOS:
                if proibido in texto:
                    relativo = arquivo.relative_to(RAIZ)
                    raise SystemExit(f'Conteúdo privado em {relativo}: {proibido}')

    print('Publicação validada: arquivos essenciais, JSON e privacidade OK.')


if __name__ == '__main__':
    validar()
