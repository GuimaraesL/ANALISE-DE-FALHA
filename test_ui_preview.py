# test_ui_preview.py
"""
Página de preview para testar componentes visuais sem gastar créditos da API.

Este arquivo usa os mesmos componentes do app.py para garantir consistência
visual, mas com dados mockados para teste.

Execute com: streamlit run test_ui_preview.py
"""
import streamlit as st
from pathlib import Path
import html as html_lib
import sys

# Adicionar diretório raiz ao path para imports
sys.path.insert(0, str(Path(__file__).parent))

# Imports dos componentes modulares
from ui.styles import load_css
from ui.components import display_five_whys, display_raw_response
from ui.pages.results import (
    _render_excel_data, 
    _render_history_card,
    _render_tokens,
    STYLE_CARD,
    STYLE_REFINED_HISTORY,
)
from ui.utils import clean_empty_values
from ui.texts import TEXTS


# ============================================================================
# DADOS MOCKADOS
# ============================================================================

MOCK_FIVE_WHYS = [
    "Por que o rolamento dianteiro do mandril enrolador travou?: Porque operou com lubrificação deficiente ou inexistente.",
    "Por que a lubrificação estava deficiente?: Porque o fluxo de óleo para o mancal do rolamento estava abaixo do mínimo necessário para sua correta refrigeração e lubrificação.",
    "Por que o fluxo de óleo estava abaixo do necessário?: Porque o sistema de entrega de óleo pode ter falhado ou o sistema de monitoramento (fluxostato) não atuou para indicar a condição de baixo fluxo.",
    "Por que o sistema de monitoramento não atuou ou a falha não foi detectada?: Porque não há uma rotina estabelecida para verificar periodicamente se o fluxo real de óleo e o setpoint de acionamento do fluxostato estão corretos e conforme especificado pelo fabricante.",
    "Por que esta rotina de verificação crítica não foi estabelecida?: Porque houve uma falha no planejamento da manutenção preventiva, que não identificou este ponto de verificação como essencial para garantir a confiabilidade do sistema de lubrificação do mandril."
]

MOCK_RAW_RESPONSE = """**Diagrama de Ishikawa**
- Material: [Rolamento operando com lubrificação deficiente, Óleo lubrificante com possível contaminação ou degradação]
- Máquina: [Falha no sistema de lubrificação por óleo circulatório, Desgaste ou falha do fluxostato (sensor de fluxo)]
- Método: [Inexistência de rotina para aferição do fluxo de óleo, Execução parcial do plano de lubrificação]
- Mão de obra: [Falta de conhecimento no ajuste de fluxo do sistema de lubrificação, Falha na execução do plano de manutenção preventiva]
- Meio ambiente: [Contaminação do sistema de lubrificação por partículas do processo, Operação em alta temperatura afetando a viscosidade do óleo]
- Medição: [Setpoint de acionamento do fluxostato não verificado, Monitoramento ineficaz do fluxo de óleo para o rolamento]

**5 Porquês**
- Por que o rolamento dianteiro do mandril enrolador travou? Porque operou com lubrificação deficiente ou inexistente.
- Por que a lubrificação estava deficiente? Porque o fluxo de óleo estava abaixo do necessário.
- Por que o fluxo de óleo estava abaixo do necessário? Porque o sistema de entrega falhou.
- Por que o sistema falhou? Porque não há rotina de verificação estabelecida.
- Por que a rotina não foi estabelecida? Porque houve falha no planejamento da manutenção preventiva.

**Plano de Ação**
- Realizar uma auditoria completa no circuito de lubrificação do mandril enrolador
- Desenvolver e formalizar um Procedimento Operacional Padrão (POP) para o ajuste de folgas
- Implementar uma rotina de manutenção preditiva com medição de vibração e temperatura
- Estabelecer check-list de verificação do sistema de lubrificação

**Conclusão Final**
A análise da falha recorrente de travamento do rolamento dianteiro do mandril enrolador indica que a causa raiz está relacionada a deficiências sistêmicas no sistema de lubrificação. O travamento repetitivo sugere que as ações corretivas anteriores não foram eficazes."""

# Mock com backticks para testar limpeza
MOCK_RAW_RESPONSE_WITH_BACKTICKS = MOCK_RAW_RESPONSE + """

```

```
"""

MOCK_EXCEL_DATA = {
    "excel_data": {
        "area": "MEC - Mecânica",
        "equipment": "CM2 - Mandril Enrolador",
        "subgroup": "Rolamentos",
        "description": "Travamento do rolamento dianteiro (LO) do mandril enrolador"
    }
}

MOCK_HISTORY = [
    {
        "area": "MEC - Mecânica",
        "equipamento": "CM2 - Mandril Enrolador",
        "subgrupo": "Rolamentos",
        "data": "2024-08-15",
        "descricao_falha": "Travamento do rolamento traseiro do mandril enrolador por falta de lubrificação",
        "causa_raiz": "Falha no fluxostato que não detectou baixo fluxo de óleo",
        "acao_corretiva": "Substituição do fluxostato e revisão do plano de lubrificação"
    },
    {
        "area": "MEC - Mecânica",
        "equipamento": "CM2 - Mandril Desenrolador",
        "subgrupo": "Rolamentos",
        "data": "2024-06-22",
        "descricao_falha": "Superaquecimento do rolamento principal por contaminação do óleo",
        "causa_raiz": "Entrada de água no sistema de lubrificação",
        "acao_corretiva": "Troca do óleo e instalação de filtro adicional"
    },
    {
        "area": "MEC - Mecânica",
        "equipamento": "CM1 - Mandril Enrolador",
        "subgrupo": "Rolamentos",
        "data": "2024-03-10",
        "descricao_falha": "Ruído excessivo no rolamento dianteiro",
        "causa_raiz": "Desgaste prematuro por falta de manutenção preventiva",
        "acao_corretiva": ""
    }
]

MOCK_REFINED_HISTORY = """### Falhas Correlacionadas Identificadas

Com base na análise do histórico de falhas, identificamos **3 ocorrências** altamente relevantes:

1. **Travamento do rolamento traseiro (Ago/2024)**
   - Mesmo equipamento, mesmo componente
   - Causa similar: falha no sistema de lubrificação
   - Indica problema sistêmico recorrente

2. **Superaquecimento no Desenrolador (Jun/2024)**
   - Equipamento similar, mesmo subgrupo
   - Contaminação do óleo como fator contribuinte
   - Sugere vulnerabilidade comum no sistema

3. **Ruído no CM1 (Mar/2024)**
   - Equipamento equivalente em outra linha
   - Falta de manutenção preventiva identificada
   - Padrão de negligência em rotinas de lubrificação

### Padrão Identificado
As falhas demonstram um **problema sistêmico na gestão de lubrificação** dos mandris, 
com falhas recorrentes relacionadas a:
- Monitoramento ineficaz do fluxo de óleo
- Falta de rotinas de verificação preventiva
- Contaminação do lubrificante
"""

MOCK_TOKEN_RESULT = {
    "token_details": {
        "prompt_tokens": 12543,
        "response_tokens": 3421,
        "history_input_tokens": 2876,
        "history_output_tokens": 1234,
        "media_output_tokens": 567
    }
}


def main():
    st.set_page_config(
        page_title="Preview UI - Análise de Falha", 
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    load_css()
    
    st.title("🧪 Preview de Componentes UI")
    st.markdown("*Teste visual dos componentes refatorados sem gastar créditos da API*")
    st.divider()
    
    texts = TEXTS["pt"]
    
    # ========================================
    # SEÇÃO: DADOS DO EXCEL (NOVO VISUAL)
    # ========================================
    st.header("📊 Dados do Excel - Visual Premium")
    
    with st.expander(texts["excel_data"], expanded=True):
        excel_data = MOCK_EXCEL_DATA.get("excel_data", {})
        
        fields = [
            (texts['area'], excel_data.get('area', 'N/A'), "🏭"),
            (texts['equipment'], excel_data.get('equipment', 'N/A'), "⚙️"),
            (texts['subgroup'], excel_data.get('subgroup', 'N/A'), "📦"),
            (texts['description'], excel_data.get('description', 'N/A'), "📝"),
        ]
        
        for label, value, emoji in fields:
            st.markdown(f"""
            <div style="{STYLE_CARD}">
                <span style="color: #60A5FA; font-weight: 600; margin-right: 8px;">
                    {emoji} {html_lib.escape(label)}:
                </span>
                <span style="color: #E2E8F0;">
                    {html_lib.escape(str(value))}
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # ========================================
    # SEÇÃO: 5 PORQUÊS (USANDO COMPONENTE)
    # ========================================
    st.header("🔍 5 Porquês - Componente Modular")
    
    with st.expander(texts["five_whys_expander"], expanded=True):
        display_five_whys(MOCK_FIVE_WHYS, "cards", texts, "pt")
    
    st.divider()
    
    # ========================================
    # SEÇÃO: RESPOSTA BRUTA (COM LIMPEZA DE BACKTICKS)
    # ========================================
    st.header("🤖 Resposta Bruta - Com Limpeza de Backticks")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sem backticks")
        with st.expander("Resposta Limpa", expanded=True):
            display_raw_response(MOCK_RAW_RESPONSE)
    
    with col2:
        st.subheader("Com backticks (limpeza automática)")
        with st.expander("Resposta com ``` no final", expanded=True):
            display_raw_response(MOCK_RAW_RESPONSE_WITH_BACKTICKS)
    
    st.divider()
    
    # ========================================
    # SEÇÃO: HISTÓRICO BRUTO (NOVO VISUAL COM TABS)
    # ========================================
    st.header("📚 Histórico Bruto - Visual Amigável + JSON")
    
    history_count = len(MOCK_HISTORY)
    expander_title = texts["broad_history_expander"].format(count=history_count)
    
    with st.expander(expander_title, expanded=True):
        # Tabs: Visual Amigável | JSON Técnico
        tab_visual, tab_json = st.tabs(["📋 Visualização", "🔧 JSON Técnico"])
        
        with tab_visual:
            for i, failure in enumerate(MOCK_HISTORY):
                _render_history_card(failure, i + 1, texts)
        
        with tab_json:
            for i, failure in enumerate(MOCK_HISTORY):
                analysis_title = texts["historical_analysis_title"].format(index=i+1)
                st.markdown(analysis_title)
                
                cleaned_failure_data = clean_empty_values(failure)
                st.json(cleaned_failure_data, expanded=True)
                st.divider()
    
    st.divider()
    
    # ========================================
    # SEÇÃO: HISTÓRICO CORRELACIONADO PELA IA
    # ========================================
    st.header("🔍 Histórico Correlacionado pela IA")
    
    with st.expander(texts["history_expander"], expanded=True):
        st.markdown(f"""
        <div style="{STYLE_REFINED_HISTORY}">
            <h4 style="color: #4ADE80; margin: 0 0 15px 0;">
                🔍 Análise de Correlação pela IA
            </h4>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(MOCK_REFINED_HISTORY)
    
    st.divider()
    
    # ========================================
    # SEÇÃO: TOKENS (NOVO VISUAL)
    # ========================================
    st.header("📏 Tokens - Visual Premium")
    
    with st.expander("📏 Tokens", expanded=True):
        token_details = MOCK_TOKEN_RESULT.get("token_details", {})
        
        # Cálculo de totais
        input_tokens = (
            token_details.get("prompt_tokens", 0) + 
            token_details.get("history_input_tokens", 0)
        )
        output_tokens = (
            token_details.get("response_tokens", 0) +
            token_details.get("history_output_tokens", 0) +
            token_details.get("media_output_tokens", 0)
        )
        total_tokens = input_tokens + output_tokens

        # Custo estimado
        input_cost = input_tokens / 1000 * 0.0115
        output_cost = output_tokens / 1000 * 0.0115
        total_cost = input_cost + output_cost

        # Layout em colunas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="{STYLE_CARD}; text-align: center;">
                <div style="color: #60A5FA; font-size: 0.9em;">📥 Input</div>
                <div style="color: #E2E8F0; font-size: 1.3em; font-weight: bold;">{input_tokens:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="{STYLE_CARD}; text-align: center;">
                <div style="color: #4ADE80; font-size: 0.9em;">📤 Output</div>
                <div style="color: #E2E8F0; font-size: 1.3em; font-weight: bold;">{output_tokens:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="{STYLE_CARD}; text-align: center;">
                <div style="color: #FBBF24; font-size: 0.9em;">💰 Custo</div>
                <div style="color: #E2E8F0; font-size: 1.3em; font-weight: bold;">US$ {total_cost:.4f}</div>
            </div>
            """, unsafe_allow_html=True)

        st.success(texts["token_ok"])
    
    st.divider()
    
    # ========================================
    # ANÁLISE DE VÍDEO/IMAGEM - ESTADOS
    # ========================================
    st.header("🎥🖼️ Análise de Mídia - Estados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Quando Desabilitado")
        with st.expander("🎥 Análise de Vídeo", expanded=True):
            st.info(texts["video_disabled"])
        
        with st.expander("🖼️ Análise de Imagens", expanded=True):
            st.info(texts["image_disabled"])
    
    with col2:
        st.subheader("Quando Habilitado (com conteúdo)")
        with st.expander("🎥 Análise de Vídeo", expanded=True):
            st.markdown(f"""
            <div style="{STYLE_CARD}">
            <strong>Análise do Vídeo:</strong><br><br>
            O vídeo mostra o processo de desmontagem do rolamento danificado. Observa-se:<br>
            • <strong>Desgaste severo nas pistas</strong> - Marcas de spalling visíveis<br>
            • <strong>Contaminação do lubrificante</strong> - Coloração escurecida<br>
            • <strong>Partículas metálicas</strong> - Debris visível no lubrificante residual
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander("🖼️ Análise de Imagens", expanded=True):
            st.markdown(f"""
            <div style="{STYLE_CARD}">
            <strong>Análise das Imagens:</strong><br><br>
            As imagens documentam o estado do rolamento após a falha:<br>
            • <strong>Imagem 1:</strong> Vista geral do rolamento travado<br>
            • <strong>Imagem 2:</strong> Detalhe da pista interna com spalling<br>
            • <strong>Imagem 3:</strong> Elementos rolantes com desgaste
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    st.success("✅ Preview carregado com sucesso! Todos os componentes refatorados estão funcionando.")


if __name__ == "__main__":
    main()
