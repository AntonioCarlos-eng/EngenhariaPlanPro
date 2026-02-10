# CALCULO DE PESO LINEAR - Aco CA-50
# Tabela de peso linear para diferentes bitolas
# Versao: 1.0. 0 | Data: 2025-12-04

# Tabela de peso linear em kg/m para aco CA-50
PESO_LINEAR_ACA_CA50 = {
    5.0: 0.154,
    6.3: 0.245,
    8.0: 0.395,
    10.0: 0.617,
    12.5: 0.963,
    16.0: 1.578,
    20.0: 2.466,
    25.0: 3.853,
    32.0: 6.313,
    40.0: 9.865,
}


def peso_linear_kg_m(bitola: float) -> float:
    """
    Retorna o peso linear em kg/m para uma dada bitola de aco. 

    Args:
        bitola: Bitola em milimetros (ex: 8.0, 10.0, 12.5, etc)

    Returns:
        Peso linear em kg/m

    Raises:
        ValueError: Se a bitola nao estiver na tabela
    """
    # Tentar match exato primeiro
    if bitola in PESO_LINEAR_ACA_CA50:
        return PESO_LINEAR_ACA_CA50[bitola]

    # Se nao encontrar exato, procurar bitola mais proxima
    bitolas_disponiveis = sorted(PESO_LINEAR_ACA_CA50.keys())

    # Encontrar a bitola mais proxima
    bitola_mais_proxima = min(
        bitolas_disponiveis,
        key=lambda x: abs(x - bitola)
    )

    # Se a diferenca for maior que 1mm, avisar
    if abs(bitola_mais_proxima - bitola) > 1.0:
        print(f"[AVISO] Bitola {bitola}mm nao encontrada.  "
              f"Usando {bitola_mais_proxima}mm")

    return PESO_LINEAR_ACA_CA50[bitola_mais_proxima]