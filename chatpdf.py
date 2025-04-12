import os
import streamlit as st
import pdfplumber
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage, AIMessage

# Carrega variáveis de ambiente do .env (caso esteja usando arquivo .env também)
load_dotenv()

# Verifica se a chave da API está presente
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.error("❌ GROQ_API_KEY não foi encontrada. Verifique se está configurada corretamente.")
    st.stop()

# Inicializa o modelo LLM da Groq
def configurar_llm():
    return ChatGroq(model_name="llama3-8b-8192", api_key=groq_api_key)

# Função para extrair texto do PDF
def extrair_texto_pdf(arquivo_pdf):
    try:
        with pdfplumber.open(arquivo_pdf) as pdf:
            texto = '\n'.join([pagina.extract_text() for pagina in pdf.pages if pagina.extract_text()])
        return texto if texto else None
    except Exception as e:
        st.error(f"Erro ao extrair texto: {e}")
        return None

# Reinicia o histórico de conversa
def resetar_conversa():
    st.session_state.chat_history = [
        SystemMessage(content="Você é um especialista em contratos. Responda com base no texto fornecido.")
    ]
    st.session_state.texto_contrato = ""

# Inicializa estado da sessão
if "chat_history" not in st.session_state:
    resetar_conversa()

if "texto_contrato" not in st.session_state:
    st.session_state.texto_contrato = ""

# Interface do usuário
st.title("🤖 Assistente de Contratos")
st.sidebar.title("⚙️ Configurações")

# Upload do PDF
arquivo_pdf = st.sidebar.file_uploader("📄 Envie o contrato (PDF)", type="pdf")
if st.sidebar.button("🔁 Reiniciar conversa"):
    resetar_conversa()

# Processa o PDF
if arquivo_pdf:
    texto = extrair_texto_pdf(arquivo_pdf)
    if texto:
        st.session_state.texto_contrato = texto
        st.success("✅ Contrato carregado com sucesso!")
    else:
        st.warning("❗ Não foi possível extrair texto do PDF.")

# Exibe o histórico de mensagens
for mensagem in st.session_state.chat_history[1:]:
    if isinstance(mensagem, HumanMessage):
        st.chat_message("user").write(mensagem.content)
    elif isinstance(mensagem, AIMessage):
        st.chat_message("assistant").write(mensagem.content)

# Entrada da pergunta
pergunta = st.chat_input("Digite sua pergunta sobre o contrato...")

# Processamento da pergunta
if pergunta and st.session_state.texto_contrato:
    st.chat_message("user").write(pergunta)
    st.session_state.chat_history.append(HumanMessage(content=pergunta))

    llm = configurar_llm()
    resposta = llm.invoke(st.session_state.chat_history + [
        HumanMessage(content=f"Contrato:\n{st.session_state.texto_contrato}\n\nPergunta: {pergunta}")
    ])

    st.chat_message("assistant").write(resposta.content)
    st.session_state.chat_history.append(AIMessage(content=resposta.content))

elif pergunta and not st.session_state.texto_contrato:
    st.warning("⚠️ Por favor, envie um contrato primeiro para fazer perguntas.")
