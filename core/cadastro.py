# C:\EngenhariaPlanPro\core\cadastro.py
# ------------------------------------------------------------
# Sistema completo de cadastro de clientes e obras
# com salvamento local em JSON (/data/clientes.json)
# e suporte a autocompletar no app principal.
# ------------------------------------------------------------
import os
import json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE, "data")
os.makedirs(DATA_PATH, exist_ok=True)

CLIENTES_JSON = os.path.join(DATA_PATH, "clientes.json")


def _carregar_dados():
    if not os.path.exists(CLIENTES_JSON):
        return {}
    try:
        with open(CLIENTES_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _salvar_dados(dados):
    with open(CLIENTES_JSON, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


def cadastrar_cliente_obra(cliente: str, obra: str):
    """Cadastra um cliente e sua obra, evitando duplicatas."""
    cliente = cliente.strip()
    obra = obra.strip()
    if not cliente:
        raise ValueError("⚠ Nome do cliente é obrigatório.")
    if not obra:
        raise ValueError("⚠ Nome da obra é obrigatório.")

    dados = _carregar_dados()

    if cliente not in dados:
        dados[cliente] = []

    if obra not in dados[cliente]:
        dados[cliente].append(obra)
        _salvar_dados(dados)
        return f"✅ Obra '{obra}' adicionada ao cliente '{cliente}'."
    else:
        return f"ℹ Obra '{obra}' já cadastrada para '{cliente}'."


def listar_clientes():
    """Retorna lista de clientes cadastrados."""
    return sorted(_carregar_dados().keys())


def listar_obras(cliente: str):
    """Retorna obras vinculadas ao cliente informado."""
    dados = _carregar_dados()
    return sorted(dados.get(cliente, []))


if __name__ == "__main__":
    print(cadastrar_cliente_obra("Lecon Engenharia", "Pilares Bloco A"))
    print(listar_clientes())
    print(listar_obras("Lecon Engenharia"))
