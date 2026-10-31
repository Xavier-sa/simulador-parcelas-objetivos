"""Persistência em JSON local com gravação atômica."""
import json
import os
import tempfile
from pathlib import Path

ARQUIVO = Path(__file__).resolve().parent.parent / 'data' / 'parcelas.json'


def ler():
    # Não substituímos dados inválidos: um erro visível evita perda silenciosa.
    if not ARQUIVO.exists():
        return {'parcelamentos': []}
    with ARQUIVO.open('r', encoding='utf-8') as f:
        dados = json.load(f)
    if not isinstance(dados, dict) or not isinstance(dados.get('parcelamentos'), list):
        raise ValueError('Estrutura de dados inválida.')
    return dados


def salvar(dados):
    # Gravamos primeiro em arquivo temporário; só depois substituímos o original.
    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    caminho = None
    try:
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=ARQUIVO.parent, delete=False) as arquivo:
            caminho = arquivo.name
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(caminho, ARQUIVO)
    finally:
        if caminho and os.path.exists(caminho):
            os.unlink(caminho)
