# test_ui_preview.py
"""
Página de preview para testar componentes visuais sem gastar créditos da API.
Execute com: streamlit run test_ui_preview.py
"""
import streamlit as st
from pathlib import Path
import html

# Carregar CSS
def load_css():
    css_path = Path("styles.css")
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Função de exibição dos 5 Porquês
def display_five_whys(five_whys, display_mode="cards"):
    """
    Exibe os 5 Porquês com layout moderno em cards verticais.
    """
    if not five_whys:
        st.write("Nenhum dado disponível")
        return

    if display_mode == "cards":
        # Construir HTML de cada card individualmente
        for i, why in enumerate(five_whys[:5]):
            parts = why.split(":", 1)
            pergunta = html.escape(parts[0].strip())
            resposta = html.escape(parts[1].strip()) if len(parts) > 1 else ""
            
            card_html = f'''
            <div style="
                display: flex;
                align-items: flex-start;
                gap: 15px;
                background: linear-gradient(135deg, rgba(30, 58, 138, 0.15) 0%, rgba(37, 99, 235, 0.1) 100%);
                border: 1px solid rgba(37, 99, 235, 0.3);
                border-radius: 10px;
                padding: 15px 18px;
                margin-bottom: 12px;
                transition: all 0.3s ease;
            ">
                <div style="
                    flex-shrink: 0;
                    width: 36px;
                    height: 36px;
                    background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    font-size: 16px;
                    color: #FFFFFF;
                    box-shadow: 0 2px 8px rgba(30, 58, 138, 0.4);
                ">{i + 1}</div>
                <div style="flex: 1; line-height: 1.6;">
                    <div style="font-weight: 600; color: #60A5FA; margin-bottom: 6px; font-size: 1rem;">{pergunta}</div>
                    <div style="opacity: 0.9; font-size: 0.95rem;">{resposta}</div>
                </div>
            </div>
            '''
            st.markdown(card_html, unsafe_allow_html=True)
    
    elif display_mode == "columns":
        cols = st.columns(min(len(five_whys), 5))
        for i, why in enumerate(five_whys[:5]):
            parts = why.split(":", 1)
            pergunta = parts[0].strip()
            resposta = parts[1].strip() if len(parts) > 1 else ""
            with cols[i]:
                st.markdown(
                    f"<div style='background-color: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 5px; padding: 10px; margin: 5px;'><strong>{pergunta}</strong><br>{resposta}</div>",
                    unsafe_allow_html=True
                )


def main():
    st.set_page_config(page_title="Preview UI - Análise de Falha", layout="wide")
    load_css()
    
    st.title("🧪 Preview de Componentes UI")
    st.markdown("*Teste visual sem gastar créditos da API*")
    st.divider()
    
    # ========================================
    # DADOS MOCKADOS (baseados na imagem real)
    # ========================================
    mock_five_whys = [
        "Por que o rolamento dianteiro do mandril enrolador travou?: Porque sofreu uma falha catastrófica por fadiga superficial avançada (spalling) e desgaste severo, resultando em superaquecimento e bloqueio mecânico.",
        "Por que o rolamento sofreu fadiga e desgaste severo?: Porque operou com uma película de lubrificante deficiente ou inexistente, levando ao contato direto metal-metal entre os elementos rolantes e as pistas.",
        "Por que a lubrificação estava deficiente?: Porque o óleo lubrificante estava severamente contaminado com água e partículas abrasivas, além de apresentar viscosidade fora da especificação, perdendo sua capacidade de carga e proteção.",
        "Por que o óleo estava contaminado e degradado?: Porque houve falhas sistêmicas que permitiram o ingresso de contaminantes externos (água, poeira) e a falha na execução dos procedimentos de manutenção e lubrificação.",
        "Por que as falhas sistêmicas de lubrificação não foram corrigidas a tempo?: Porque há uma falha recorrente na gestão da lubrificação, evidenciada pelo histórico de problemas similares, incluindo execução parcial de planos e falta de procedimentos para ajustes críticos, indicando que as ações corretivas anteriores não foram eficazes ou sustentadas."
    ]
    
    # ========================================
    # SEÇÃO: 5 PORQUÊS
    # ========================================
    st.header("📋 5 Porquês - Novo Layout (Cards)")
    
    with st.expander("🔍 5 Porquês", expanded=True):
        display_five_whys(mock_five_whys, "cards")
    
    st.divider()
    
    # ========================================
    # COMPARAÇÃO ENTRE LAYOUTS
    # ========================================
    st.header("📊 Comparação de Layouts")
    
    tab1, tab2 = st.tabs(["📱 Novo Layout (Cards)", "📰 Layout Antigo (Colunas)"])
    
    with tab1:
        st.subheader("Layout Cards (Vertical)")
        display_five_whys(mock_five_whys, "cards")
    
    with tab2:
        st.subheader("Layout Colunas (Horizontal)")
        display_five_whys(mock_five_whys, "columns")
    
    st.divider()
    
    # ========================================
    # OUTROS COMPONENTES DE TESTE
    # ========================================
    st.header("🎨 Outros Componentes")
    
    with st.expander("📊 Dados do Excel (Mock)"):
        st.write("- **Área**: Laminação")
        st.write("- **Equipamento**: Mandril Enrolador")
        st.write("- **Subgrupo**: Rolamentos")
        st.write("- **Descrição**: Travamento do rolamento dianteiro")
    
    with st.expander("📏 Tokens (Mock)"):
        st.write("**Tokens de entrada:** 15.234")
        st.write("**Tokens de saída:** 8.456")
        st.markdown("**Custo estimado:** US$ 0.002728")
        st.success("✅ Tokens dentro do limite!")
    
    st.divider()
    
    # ========================================
    # ANÁLISE DE VÍDEO/IMAGEM DESABILITADOS
    # ========================================
    st.header("🎥🖼️ Análise de Mídia - Estados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Quando Desabilitado")
        with st.expander("🎥 Análise de Vídeo", expanded=True):
            st.info("🎥 Análise de vídeo desabilitada")
        
        with st.expander("🖼️ Análise de Imagens", expanded=True):
            st.info("🖼️ Análise de imagem desabilitada")
    
    with col2:
        st.subheader("Quando Habilitado (sem conteúdo)")
        with st.expander("🎥 Análise de Vídeo", expanded=True):
            st.info("Nenhuma análise de vídeo encontrada")
        
        with st.expander("🖼️ Análise de Imagens", expanded=True):
            st.info("Nenhuma análise de imagem encontrada")
    
    st.divider()
    
    # ========================================
    # ANÁLISE DE MÍDIA COM CONTEÚDO
    # ========================================
    st.subheader("Quando Habilitado (com conteúdo)")
    
    with st.expander("🎥 Análise de Vídeo", expanded=True):
        st.markdown("""
**Análise do Vídeo:**

O vídeo mostra o processo de desmontagem do rolamento danificado. Observa-se:

1. **Desgaste severo nas pistas** - Marcas de spalling visíveis na pista interna
2. **Contaminação do lubrificante** - Coloração escurecida indicando degradação térmica
3. **Partículas metálicas** - Debris visível no lubrificante residual
4. **Superaquecimento** - Descoloração azulada nas superfícies de contato

A falha é consistente com operação prolongada sob lubrificação inadequada.
        """)
    
    with st.expander("🖼️ Análise de Imagens", expanded=True):
        st.markdown("""
**Análise das Imagens:**

As imagens documentam o estado do rolamento após a falha:

- **Imagem 1**: Vista geral do rolamento travado mostrando acúmulo de debris
- **Imagem 2**: Detalhe da pista interna com marcas de spalling
- **Imagem 3**: Elementos rolantes com desgaste irregular
- **Imagem 4**: Amostra do lubrificante degradado

O padrão de desgaste indica falha por fadiga superficial agravada por contaminação.
        """)
    
    st.divider()
    
    # ========================================
    # RESPOSTA BRUTA
    # ========================================
    st.header("🤖 Resposta Bruta")
    
    mock_raw_response = """**Diagrama de Ishikawa**
- Material: [Rolamento com vida útil esgotada ou defeito de fabricação, Especificação incorreta do rolamento para a aplicação]
- Máquina: [Baixa performance ou falha na bomba do sistema de lubrificação, Obstrução nas linhas de óleo]
- Método: [Plano de lubrificação não especifica todos os pontos ou a frequência adequada, Falta de procedimento para ajuste de folgas]
- Mão de obra: [Falha na execução da rotina de lubrificação, Falta de conhecimento específico sobre o equipamento]
- Meio ambiente: [Contaminação do sistema de lubrificação por particulados, Operação em condições severas de temperatura]
- Medição: [Sensores de fluxo de óleo (fluxostatos) inoperantes ou descalibrados, Falta de monitoramento de vibração]

**5 Porquês**
- Por que o rolamento dianteiro do mandril enrolador travou? Porque operou com lubrificação deficiente.
- Por que o rolamento operou com lubrificação deficiente? Porque o fluxo de óleo estava abaixo do necessário.
- Por que o fluxo de óleo estava abaixo do necessário? Porque há uma falha sistêmica no sistema de lubrificação.
- Por que o sistema de entrega falha ou é ajustado incorretamente? Porque os planos não são adequados.
- Por que os planos e procedimentos são ineficazes ou inexistentes? Porque falta gestão adequada.

**Plano de Ação**
- Realizar uma auditoria completa no circuito de lubrificação do mandril enrolador
- Desenvolver e formalizar um Procedimento Operacional Padrão (POP) para o ajuste de folgas
- Implementar uma rotina de manutenção preditiva com medição de vibração e/ou temperatura

**Conclusão Final**
A análise da falha recorrente de travamento do rolamento dianteiro do mandril enrolador indica que a causa raiz está relacionada a deficiências sistêmicas no sistema de lubrificação."""

    with st.expander("🤖 Resposta Bruta", expanded=True):
        tab_rendered, tab_source = st.tabs(["📄 Renderizado", "💻 Código Fonte"])
        with tab_rendered:
            # Enhanced premium styling for raw response
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 58, 138, 0.9) 100%);
                border: 2px solid rgba(37, 99, 235, 0.5);
                border-radius: 15px;
                padding: 25px;
                margin: 10px 0;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                backdrop-filter: blur(10px);
                color: #E2E8F0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.7;
            ">
            """, unsafe_allow_html=True)
            
            # Split the response into sections and style each one
            sections = mock_raw_response.split("**")
            for i, section in enumerate(sections):
                if section.strip():
                    if "Diagrama de Ishikawa" in section:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(37, 99, 235, 0.2) 0%, rgba(59, 130, 246, 0.1) 100%);
                            border-left: 4px solid #3B82F6;
                            padding: 15px 20px;
                            margin: 15px 0;
                            border-radius: 8px;
                            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
                        ">
                        <h3 style="color: #60A5FA; margin: 0 0 10px 0; font-size: 1.3em; font-weight: 600;">📊 {section.strip()}</h3>
                        """, unsafe_allow_html=True)
                    elif "5 Porquês" in section:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(74, 222, 128, 0.1) 100%);
                            border-left: 4px solid #22C55E;
                            padding: 15px 20px;
                            margin: 15px 0;
                            border-radius: 8px;
                            box-shadow: 0 4px 12px rgba(34, 197, 94, 0.15);
                        ">
                        <h3 style="color: #4ADE80; margin: 0 0 10px 0; font-size: 1.3em; font-weight: 600;">🔍 {section.strip()}</h3>
                        """, unsafe_allow_html=True)
                    elif "Plano de Ação" in section:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(251, 191, 36, 0.1) 100%);
                            border-left: 4px solid #F59E0B;
                            padding: 15px 20px;
                            margin: 15px 0;
                            border-radius: 8px;
                            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.15);
                        ">
                        <h3 style="color: #FBBF24; margin: 0 0 10px 0; font-size: 1.3em; font-weight: 600;">🎯 {section.strip()}</h3>
                        """, unsafe_allow_html=True)
                    elif "Conclusão Final" in section:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(196, 181, 253, 0.1) 100%);
                            border-left: 4px solid #A855F7;
                            padding: 15px 20px;
                            margin: 15px 0;
                            border-radius: 8px;
                            box-shadow: 0 4px 12px rgba(168, 85, 247, 0.15);
                        ">
                        <h3 style="color: #C4B5FD; margin: 0 0 10px 0; font-size: 1.3em; font-weight: 600;">🏁 {section.strip()}</h3>
                        """, unsafe_allow_html=True)
                    else:
                        # Content sections
                        lines = section.strip().split('\n')
                        for line in lines:
                            if line.strip():
                                if line.startswith('- '):
                                    st.markdown(f"""
                                    <div style="
                                        background: rgba(255, 255, 255, 0.05);
                                        border-radius: 6px;
                                        padding: 8px 12px;
                                        margin: 5px 0;
                                        border-left: 3px solid rgba(255, 255, 255, 0.3);
                                        font-size: 0.95em;
                                    ">
                                    {line.strip()}
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown(f"""
                                    <p style="
                                        margin: 8px 0;
                                        padding: 5px 10px;
                                        background: rgba(255, 255, 255, 0.03);
                                        border-radius: 4px;
                                        font-size: 0.95em;
                                        line-height: 1.6;
                                    ">
                                    {line.strip()}
                                    </p>
                                    """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        with tab_source:
            st.code(mock_raw_response, language="markdown")
    
    st.success("✅ Preview carregado com sucesso!")


if __name__ == "__main__":
    main()
