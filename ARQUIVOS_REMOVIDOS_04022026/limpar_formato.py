import re

with open('vigas_app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Remover espaços nos format specifiers
conteudo = re. sub(r':\s*\.\s*(\d+)f', r':.\1f', conteudo)

with open('vigas_app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print('✅ Format strings corrigidas!')