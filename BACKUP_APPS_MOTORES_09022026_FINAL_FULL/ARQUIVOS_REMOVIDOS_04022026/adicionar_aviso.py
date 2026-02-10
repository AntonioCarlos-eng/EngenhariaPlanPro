#!/usr/bin/env python3
"""Adicionar aviso quando não consegue ler linhas"""

arquivo = r"c:\EngenhariaPlanPro\core\pilares_motor_dual.py"

with open(arquivo, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Encontrar e modificar
old = """                else:
                    print(f"[MOTOR RÁPIDO] Nenhum pilar novo encontrado (tabela processou todos)")
        
        except Exception as e:"""

new = """                else:
                    # Se não processou NADA, avisar
                    if not pilares_processados:
                        print(f"[AVISO] Detectados pilares {sorted(pilares_encontrados)} mas formato não compatível")
                        print(f"[AVISO] Arquivo pode ter tabela com textos muito fragmentados")
                    else:
                        print(f"[MOTOR RÁPIDO] Nenhum pilar novo encontrado (tabela processou todos)")
        
        except Exception as e:"""

if old in conteudo:
    conteudo = conteudo.replace(old, new)
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print("✓ Aviso adicionado para arquivos não compatíveis")
else:
    print("✗ Bloco não encontrado")
