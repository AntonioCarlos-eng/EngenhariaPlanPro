# LEITOR DXF V2 - Extrai textos de arquivos DXF/DWG
# Versao: 2.0. 1 | Data: 2025-12-04

import ezdxf


def extrair_textos_entidade(entity, lista, profundidade=0):
    """
    Extrai textos de qualquer entidade, inclusive blocos dentro de blocos. 

    Args:
        entity: entidade DXF a processar
        lista: lista onde os textos sao acumulados
        profundidade: controle de recursao para evitar loops infinitos
    """
    MAX_PROFUNDIDADE = 10
    if profundidade > MAX_PROFUNDIDADE:
        return

    try:
        tipo = entity. dxftype()

        # TEXT normal
        if tipo == "TEXT":
            texto = entity. dxf.text. strip()
            if texto:
                lista.append(texto)
            return

        # MTEXT
        if tipo == "MTEXT":
            texto = entity.plain_text().replace("\n", " ").strip()
            if texto:
                lista.append(texto)
            return

        # ATTRIB (texto dentro de blocos)
        if tipo == "ATTRIB":
            texto = entity. dxf.text.strip()
            if texto:
                lista.append(texto)
            return

        # INSERT (referencia de bloco)
        if tipo == "INSERT":
            try:
                block = entity. doc.blocks. get(entity. dxf.name)
                if block:
                    # Entidades internas do bloco
                    for e in block:
                        extrair_textos_entidade(e, lista, profundidade + 1)

                    # Atributos do bloco
                    if hasattr(entity, 'attribs') and entity.attribs:
                        for att in entity.attribs:
                            texto = att. dxf.text.strip()
                            if texto:
                                lista.append(texto)
            except:
                pass
            return

    except:
        pass


def ler_dxf_v2(caminho):
    """
    Le arquivo DXF e extrai todos os textos de:
    - Modelspace
    - Paperspace (layouts)
    - Blocos (INSERT e conteudo de blocos)

    Args:
        caminho: path do arquivo . dxf

    Returns:
        lista de strings de texto encontradas
    """
    textos = []

    try:
        doc = ezdxf.readfile(caminho)

        # --------------------------------
        # 1) Modelspace
        # --------------------------------
        try:
            msp = doc.modelspace()
            for e in msp:
                extrair_textos_entidade(e, textos)
        except Exception as e:
            print(f"[READER] Aviso ao ler modelspace: {e}")

        # --------------------------------
        # 2) Paperspace (layouts)
        # --------------------------------
        try:
            for layout_name in doc.layouts:
                try:
                    layout = doc. layouts. get(layout_name)
                    for e in layout:
                        extrair_textos_entidade(e, textos)
                except:
                    pass
        except Exception as e:
            print(f"[READER] Aviso ao ler layouts: {e}")

        # --------------------------------
        # 3) TODOS os blocos
        # --------------------------------
        try:
            for nome_bloco in doc.blocks:
                block = doc.blocks.get(nome_bloco)
                if block:
                    for e in block:
                        extrair_textos_entidade(e, textos)
        except Exception as e:
            print(f"[READER] Aviso ao ler blocos: {e}")

        # Remove strings vazias
        textos = [t for t in textos if t]

        print(f"[READER V2] Total textos extraidos: {len(textos)}")
        return textos

    except Exception as e:
        print(f"[READER V2] ERRO FATAL: {e}")
        return []