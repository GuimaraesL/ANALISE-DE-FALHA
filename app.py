# app.py
import streamlit as st
from pathlib import Path
import os
import sys
import logging
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as mpath
from datetime import datetime
from ui.texts import TEXTS  
from core.prompts import format_ishikawa, format_5whys, format_list
from core.failure_analysis_app import FailureAnalysisApp
from core.config_loader import load_config

config = load_config()

credentials_path = config.get("google_credentials_path")
if credentials_path and Path(credentials_path).exists():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    logging.info(f"Credenciais do Google Cloud carregadas de: {credentials_path}")
else:
    # Emite um aviso se o arquivo não for encontrado, pois a análise de vídeo falhará.
    st.warning(f"Arquivo de credenciais '{credentials_path}' não encontrado. A análise de vídeo pode falhar.")

api_key = config.get("gemini_api_key")

# Ajustar o PYTHONPATH para incluir o diretório raiz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from core.excel_reader import ExcelReader
    from core.image_analyzer import ImageAnalyzer
    from core.ai_processor import AIProcessor
    from core.report_generator import ReportGenerator
except ModuleNotFoundError as e:
    st.error(f"❌ Erro ao importar módulos: {e}. Verifique se o diretório 'core' existe e contém '__init__.py'.")
    logging.error(f"Erro ao importar módulos: {e}")
    st.stop()

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Carregar CSS
def load_css():
    css_path = Path("styles.css")
    if css_path.exists():
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Arquivo styles.css não encontrado. Usando estilo padrão.")

# Função aprimorada com cabeça de peixe

def plot_ishikawa(ishikawa_data, texts, lang_code="pt"):


    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 22)
    ax.set_ylim(-10, 10)
    ax.axis("off")

    # Linha central
    ax.plot([4, 19], [0, 0], color="#FF6600", lw=3)

    # Cabeça de peixe (efeito)
    head = mpath.Path(
        [(19, -2), (21, 0), (19, 2), (19, -2)],
        [mpath.Path.MOVETO, mpath.Path.LINETO, mpath.Path.LINETO, mpath.Path.CLOSEPOLY]
    )
    patch = patches.PathPatch(head, facecolor="#FF6600", edgecolor="black", lw=2)
    ax.add_patch(patch)
    ax.text(20, 0, texts["ishikawa_effect"], va="center", ha="center", fontsize=12, fontweight="bold", color="white")

    # Categorias alternadas
    categorias = list(ishikawa_data["causes"].keys())
    y_positions = [6, 4, 2, -2, -4, -6]

    for idx, (categoria, y_cat) in enumerate(zip(categorias, y_positions)):
        y_target = 0
        x_base = 4 + (idx + 1) * 2

        # Linha da categoria
        ax.plot([x_base, x_base], [y_target, y_cat], color="#1E3A8A", lw=2)

        # Caixa da categoria
        ax.add_patch(patches.FancyBboxPatch((x_base - 1.2, y_cat - 0.6), 2.4, 1.2,
                                            boxstyle="round,pad=0.3", fc="#1E3A8A", ec="black"))
        ax.text(x_base, y_cat, categoria, va="center", ha="center", fontsize=10, color="white", fontweight="bold")

        # Causas conectadas
        causas = ishikawa_data["causes"].get(categoria, [])
        for j, causa in enumerate(causas):
            offset = 0.8 * (j + 1)
            sinal = 1 if y_cat > 0 else -1
            y_causa = y_cat + sinal * offset
            x_causa = x_base + (1.5 if y_cat > 0 else -1.5)
            ax.plot([x_base, x_causa], [y_cat, y_causa], color="#2563EB", lw=1.5)
            ax.text(x_causa + (0.3 if y_cat > 0 else -0.3), y_causa,
                    f"- {causa}", va="center",
                    ha="left" if y_cat > 0 else "right",
                    fontsize=9)

    ax.set_title(texts["ishikawa_title"], fontsize=16, pad=20)
    st.pyplot(fig)
    plt.close(fig)


# Função para exibir a resposta bruta de forma estilizada
def display_raw_response(raw_response: str):
    """
    Exibe a resposta bruta da IA de forma visualmente atraente com design premium.
    Divide o conteúdo em seções e aplica estilos diferentes para cada uma.

    Args:
        raw_response: Texto bruto da resposta da IA
    """
    import html as html_lib
    import re

    if not raw_response or not raw_response.strip():
        st.info("Nenhuma resposta bruta disponível")
        return

    # Split the response into sections and style each one
    sections = re.split(r'\*\*([^*]+)\*\*', raw_response)

    if len(sections) > 1:
        # Formato com **Título** detectado
        i = 1
        while i < len(sections):
            section_title = sections[i].strip()
            section_content = sections[i + 1] if i + 1 < len(sections) else ""

            if section_title and section_content.strip():
                if "Diagrama de Ishikawa" in section_title:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(37, 99, 235, 0.2) 0%, rgba(59, 130, 246, 0.1) 100%);
                        border-left: 4px solid #3B82F6;
                        padding: 15px 20px;
                        margin: 15px 0;
                        border-radius: 8px;
                        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
                    ">
                    <h3 style="color: #60A5FA; margin: 0 0 10px 0; font-size: 1.3em; font-weight: 600;">📊 {html_lib.escape(section_title)}</h3>
                    """, unsafe_allow_html=True)
                elif "5 Porquês" in section_title:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(74, 222, 128, 0.1) 100%);
                        border-left: 4px solid #22C55E;
                        padding: 15px 20px;
                        margin: 15px 0;
                        border-radius: 8px;
                        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.15);
                    ">
                    <h3 style="color: #4ADE80; margin: 0 0 10px 0; font-size: 1.3em; font-weight: 600;">🔍 {html_lib.escape(section_title)}</h3>
                    """, unsafe_allow_html=True)
                elif "Plano de Ação" in section_title:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(251, 191, 36, 0.1) 100%);
                        border-left: 4px solid #F59E0B;
                        padding: 15px 20px;
                        margin: 15px 0;
                        border-radius: 8px;
                        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.15);
                    ">
                    <h3 style="color: #FBBF24; margin: 0 0 10px 0; font-size: 1.3em; font-weight: 600;">🎯 {html_lib.escape(section_title)}</h3>
                    """, unsafe_allow_html=True)
                elif "Conclusão Final" in section_title:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(196, 181, 253, 0.1) 100%);
                        border-left: 4px solid #A855F7;
                        padding: 15px 20px;
                        margin: 15px 0;
                        border-radius: 8px;
                        box-shadow: 0 4px 12px rgba(168, 85, 247, 0.15);
                    ">
                    <h3 style="color: #C4B5FD; margin: 0 0 10px 0; font-size: 1.3em; font-weight: 600;">🏁 {html_lib.escape(section_title)}</h3>
                    """, unsafe_allow_html=True)
                else:
                    # Outras seções
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(107, 114, 128, 0.2) 0%, rgba(156, 163, 175, 0.1) 100%);
                        border-left: 4px solid #6B7280;
                        padding: 15px 20px;
                        margin: 15px 0;
                        border-radius: 8px;
                        box-shadow: 0 4px 12px rgba(107, 114, 128, 0.15);
                    ">
                    <h3 style="color: #9CA3AF; margin: 0 0 10px 0; font-size: 1.3em; font-weight: 600;">📝 {html_lib.escape(section_title)}</h3>
                    """, unsafe_allow_html=True)

                # Renderizar conteúdo da seção
                lines = section_content.strip().split('\n')
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
                            {html_lib.escape(line.strip())}
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
                            {html_lib.escape(line.strip())}
                            </p>
                            """, unsafe_allow_html=True)

                # Fechar a div da seção
                st.markdown("</div>", unsafe_allow_html=True)

            i += 2
    else:
        # Sem padrão detectado, mostra como markdown simples com estilo básico
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 58, 138, 0.9) 100%);
            border: 2px solid rgba(37, 99, 235, 0.5);
            border-radius: 15px;
            padding: 25px;
            margin: 10px 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            color: #E2E8F0;
            line-height: 1.7;
        ">
        {raw_response}
        </div>
        """, unsafe_allow_html=True)
    
# Função para exibir 5 Porquês com layout aprimorado
def display_five_whys(five_whys, display_mode="cards", texts=None, lang_code="pt"):
    """
    Exibe os 5 Porquês com layout moderno em cards verticais.
    
    Args:
        five_whys: Lista de strings no formato "Pergunta: Resposta"
        display_mode: "cards" (novo layout) ou "columns" (layout legado)
        texts: Dicionário de textos traduzidos
        lang_code: Código do idioma ("pt" ou "en")
    """
    import html as html_lib
    
    if not five_whys:
        st.write(texts["no_five_whys"])
        return

    if display_mode == "cards":
        # Novo layout: cards verticais com numeração e estilos inline
        for i, why in enumerate(five_whys[:5]):
            parts = why.split(":", 1)
            pergunta = html_lib.escape(parts[0].strip())
            resposta = html_lib.escape(parts[1].strip()) if len(parts) > 1 else ""
            
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
        # Layout legado: colunas lado a lado
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
    else:
        # Fallback: lista simples
        st.write(texts["five_whys_title"])
        for why in five_whys[:5]:
            st.write(f"- {why}")


# Função para gerar Markdown para download
def generate_markdown_result(result, lang_code="pt"):
    texts = TEXTS[lang_code]
    markdown = f"# Pasta / Folder: {result['folder']}\n\n"

    if result["status"] == "error":
        return markdown + f"**Erro / Error**: {result['details']}\n"

    details = result.get("details", {})

    # Excel
    markdown += f"## {texts['excel_data']}\n"
    if "excel_data" in details:
        markdown += f"- {texts['area']}: {details['excel_data'].get('area', 'N/A')}\n"
        markdown += f"- {texts['equipment']}: {details['excel_data'].get('equipment', 'N/A')}\n"
        markdown += f"- {texts['subgroup']}: {details['excel_data'].get('subgroup', 'N/A')}\n"
        markdown += f"- {texts['description']}: {details['excel_data'].get('description', 'N/A')}\n"
    else:
        markdown += "⚠️ Dados do Excel não disponíveis.\n"

    # Mídias
    markdown += f"\n## {texts['video_analysis_title']}\n{details.get('video_results', 'N/A')}\n"
    markdown += f"\n## {texts['image_analysis']}\n{details.get('image_results', 'N/A')}\n"

    # Correlação histórica (refined_history)
    refined_history = details.get("refined_history", "").strip()
    if refined_history:
        markdown += f"\n## {texts['correlation_title_md']}\n{refined_history}\n"

    # Raw response
    markdown += f"\n## {texts['raw_response']}\n```markdown\n{details.get('ai_results', {}).get('raw_response', 'N/A')}\n```"

    # Tokens
    tokens = result.get("token_details", {})
    input_tokens = tokens.get("prompt_tokens", 0) + tokens.get("history_input_tokens", 0)
    output_tokens = (
        tokens.get("response_tokens", 0) +
        tokens.get("history_output_tokens", 0) +
        tokens.get("media_output_tokens", 0)
    )
    total_tokens = tokens.get("total", input_tokens + output_tokens)

    markdown += f"\n## {texts['tokens_title_md']}\n"
    markdown += f"- {texts['tokens_input']} **{input_tokens}**\n"
    markdown += f"- {texts['tokens_output']} **{output_tokens}**\n"
    markdown += f"- {texts['token_total']} **{total_tokens}**\n"
    total_cost = total_tokens / 1000 * 0.0115
    markdown += f"\n**{texts['analysis_cost']}** US$ {total_cost:.6f}\n"

    return markdown


def clean_empty_values(data):
    """
    Remove recursivamente chaves de dicionários e itens de listas
    que sejam None, strings vazias ou listas/dicionários vazios.
    """
    if isinstance(data, dict):
        # Filtra o dicionário, chamando a função para cada valor
        cleaned_dict = {k: clean_empty_values(v) for k, v in data.items() if v is not None and v != "" and v != []}
        return {k: v for k, v in cleaned_dict.items() if v is not None and v != "" and v != [] and v != {}}
    
    if isinstance(data, list):
        # Filtra a lista, chamando a função para cada item
        cleaned_list = [clean_empty_values(item) for item in data if item is not None and item != ""]
        return [item for item in cleaned_list if item is not None and item != "" and item != [] and item != {}]
        
    return data


def main():
    load_css()

    with st.sidebar:
        language = st.selectbox("🌐 Selecione a linguagem / Select language:", ["Português", "English"])
        lang_code = "pt" if language == "Português" else "en"
        texts = TEXTS[lang_code]
        st.title(texts["title"])
        st.write(texts["folder_instruction"])
        default_folder = r"G:\Meu Drive\01_PYTHON\02_ARQUIVOS PARA TESTES\AF\TESTES"
        root_folder = st.text_input(texts["root_path_input"], value=default_folder)
        enable_videos = st.checkbox(texts["video_disabled_ui"], value=False)
        enable_images = st.checkbox(texts["image_disabled_ui"], value=False)

    # Botão de execução
    if st.sidebar.button(texts["run_button"]):
        if not api_key:
            st.error(texts["no_api_key"])
            return
        if not root_folder:
            st.error(texts["no_folder"])
            return
        if not Path(root_folder).exists():
            st.error(texts["folder_not_found"].format(root_folder))
            return

        processing_msg = st.empty()
        processing_msg.write(texts["processing"])
        logger.info("Iniciando análise" if lang_code == "pt" else "Starting analysis")

        app = FailureAnalysisApp(
        root_folder=root_folder,
        gemini_api_key=api_key,
        enable_images=enable_images,
        enable_videos=enable_videos,
        language=lang_code 
        )

        app.run()
        results = app.results if app.results else []

        processing_msg.empty()  # remove o texto "Processando..."
        st.session_state["results"] = results
        # Armazena o estado das opções de análise para exibição correta
        st.session_state["enable_videos"] = enable_videos
        st.session_state["enable_images"] = enable_images


    # Exibição dos resultados
    if "results" in st.session_state:
        results = st.session_state["results"]
        for result in results:
            st.subheader(f"📁 {texts['folder']}: {result['folder']}")
            if result["status"] == "error":
                st.error(f"❌ Erro / Error: {result['details']}")
                continue
            details = result["details"]
            with st.expander(texts["excel_data"]):
                st.write(f"- {texts['area']}: {details['excel_data'].get('area', 'N/A')}")
                st.write(f"- {texts['equipment']}: {details['excel_data'].get('equipment', 'N/A')}")
                st.write(f"- {texts['subgroup']}: {details['excel_data'].get('subgroup', 'N/A')}")
                st.write(f"- {texts['description']}: {details['excel_data'].get('description', 'N/A')}")

                #EXIBE A ANÁLISE DE VÍDEO
            with st.expander(texts["video_analysis_title"]):
                video_result = details.get("video_results", "")
                if video_result and video_result.strip():
                    st.markdown(video_result)
                else:
                    # Verifica se foi desabilitado ou simplesmente não encontrado
                    if not st.session_state.get("enable_videos", False):
                        st.info(texts["video_disabled"])
                    else:
                        st.info(texts["no_video_found"])

                #EXIBE A ANÁLISE DE IMAGEM
            with st.expander(texts["image_analysis"]):
                image_result = details.get("image_results", "")
                if image_result and str(image_result).strip():
                    st.write(image_result)
                else:
                    # Verifica se foi desabilitado ou simplesmente não encontrado
                    if not st.session_state.get("enable_images", False):
                        st.info(texts["image_disabled"])
                    else:
                        st.info("Nenhuma análise de imagem encontrada.")

                #EXIBE A RAW RESPONSE
            with st.expander(texts["raw_response"]):
                raw_response = details["ai_results"].get("raw_response", texts["no_raw_response"])
                if raw_response and raw_response.strip():
                    display_raw_response(raw_response)
                else:
                    st.info(texts["no_raw_response"])

                #EXIBE O DIAGRAMA DE ISHIKAWA
            if "ishikawa" in details.get("ai_results", {}):
                with st.expander(texts["ishikawa_expander"]):
                    plot_ishikawa(details["ai_results"]["ishikawa"], texts, lang_code)

                # EXIBE OS 5 PORQUÊS
            if "five_whys" in details["ai_results"]:
                with st.expander(texts["five_whys_expander"]):
                    display_five_whys(details["ai_results"]["five_whys"], "cards", texts, lang_code)

            # Expander para o Histórico Bruto Encontrado
            if details.get("broad_history_found"):
                
                history_count = len(details['broad_history_found'])
                expander_title = texts["broad_history_expander"].format(count=history_count)
                
                with st.expander(expander_title):
                    for i, failure in enumerate(details["broad_history_found"]):
              
                        analysis_title = texts["historical_analysis_title"].format(index=i+1)
                        st.markdown(analysis_title)
                        
                        cleaned_failure_data = clean_empty_values(failure)
                        st.json(cleaned_failure_data, expanded=True)
                        st.divider()

                # exibir o histórico correlacionado pela IA
            if details.get("refined_history"):
                with st.expander(texts["history_expander"]):
                    st.markdown(details["refined_history"])

               #EXIBE OS TOKENS
            with st.expander("📏 Tokens"):
                token_details = result.get("token_details", {})

                # Totais simplificados
                input_tokens = token_details.get("prompt_tokens", 0) + token_details.get("history_input_tokens", 0)
                output_tokens = (
                    token_details.get("response_tokens", 0) +
                    token_details.get("history_output_tokens", 0) +
                    token_details.get("media_output_tokens", 0)
                )


                st.write(f"**{texts['tokens_input']}** {input_tokens}")
                st.write(f"**{texts['tokens_output']}** {output_tokens}")

                # Custo estimado
                input_cost = input_tokens / 1000 * 0.0115
                output_cost = output_tokens / 1000 * 0.0115
                total_cost = input_cost + output_cost

                st.markdown(f"**{texts['analysis_cost']}** US$ {total_cost:.6f}")

                # Verificação do limite de prompt final
                if token_details.get("prompt_tokens", 0) <= 30000:
                    st.success(texts["token_ok"])
                else:
                    st.warning(texts["token_exceeded"])


            markdown_content = generate_markdown_result(result, lang_code)
            st.download_button(
                label=texts["download_button"],
                data=markdown_content,
                file_name=f"resultado_{result['folder'].replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )

        st.success(texts["success"])

if __name__ == "__main__":
    main()
