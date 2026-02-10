try:
    from core.vigas_motor import processar_vigas
    print('Fallback import bem-sucedido')
except Exception as e:
    print(f'Erro no fallback: {e}')
