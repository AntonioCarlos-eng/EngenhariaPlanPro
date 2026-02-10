"""
Integração de etiquetas dinâmicas no vigas_app.py
Modifica o fluxo para ler DXF reais e gerar etiquetas instantaneamente
"""

def integrar_etiquetas_dinamicas(app_instance):
    """
    Substitui o método gerar_etiquetas para usar o novo GeradorEtiquetasDinamico
    """
    from core.etiquetas_generator import GeradorEtiquetasDinamico
    
    original_gerar_etiquetas = app_instance.gerar_etiquetas
    
    def nova_gerar_etiquetas(self):
        """Gera etiquetas de forma dinâmica a partir dos DXF selecionados"""
        
        # Verificar se há arquivos selecionados
        if not hasattr(self, 'arquivos_selecionados') or not self.arquivos_selecionados:
            # Tentar usar dados_processados como fallback
            if not self.dados_processados:
                import tkinter.messagebox as messagebox
                messagebox.showwarning("Atenção", "Selecione arquivos DXF primeiro!")
                return
            # Usar método original com dados já processados
            return original_gerar_etiquetas(self)
        
        try:
            # Gerar dados dinamicamente
            gerador = GeradorEtiquetasDinamico(
                self.arquivos_selecionados,
                obra=self.var_obra.get() if hasattr(self, 'var_obra') else "OBRA 001",
                pavimento=self.var_pavimento.get() if hasattr(self, 'var_pavimento') else "TÉRREO"
            )
            
            # Armazenar o gerador para uso posterior
            self.gerador_etiquetas_dinamico = gerador
            
            # Atualizar dados_processados com os dados do gerador
            self.dados_processados = [
                (d['viga'], d['pos'], d['bitola'], d['qtde'], d['comp'], d['peso'])
                for d in gerador.listar_todas()
            ]
            
            # Chamar método original para renderizar
            return original_gerar_etiquetas(self)
            
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Erro", f"Erro ao gerar etiquetas: {e}")
            raise
    
    # Substituir o método
    app_instance.gerar_etiquetas = lambda: nova_gerar_etiquetas(app_instance)


if __name__ == "__main__":
    print("Módulo de integração de etiquetas dinâmicas criado com sucesso!")
