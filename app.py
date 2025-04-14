import streamlit as st
import PyPDF2
import pytesseract
from pdf2image import convert_from_bytes
import io
import docx
from PIL import Image
import base64

# Configuração da página Streamlit
st.set_page_config(page_title="Conversor de PDF para Texto", layout="wide")
st.title("Conversor de PDF para Texto")

# Função para extrair texto diretamente do PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text() + "\n\n"
    return text

# Função para extrair texto usando OCR
def extract_text_with_ocr(pdf_file):
    text = ""
    try:
        # Converter PDF em imagens
        images = convert_from_bytes(pdf_file.read())
        
        total_pages = len(images)
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, image in enumerate(images):
            status_text.text(f"Processando página {i+1} de {total_pages} com OCR...")
            
            # Melhorar a qualidade da imagem para OCR
            img = image.convert('L')  # Converter para escala de cinza
            
            # Aplicar OCR na imagem
            page_text = pytesseract.image_to_string(img, lang='por+eng')
            text += page_text + "\n\n"
            
            # Atualizar a barra de progresso
            progress_bar.progress((i + 1) / total_pages)
        
        status_text.text("Processamento OCR concluído!")
    except Exception as e:
        st.error(f"Erro no processamento OCR: {str(e)}")
    
    return text

# Função para criar arquivo docx
def create_docx(text):
    doc = docx.Document()
    for paragraph in text.split('\n'):
        if paragraph.strip():
            doc.add_paragraph(paragraph)
    
    # Salvar em um buffer
    doc_io = io.BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    
    return doc_io

# Função para download de arquivo
def get_download_link(file_bytes, file_name, file_type):
    b64 = base64.b64encode(file_bytes.read()).decode()
    href = f'<a href="data:{file_type};base64,{b64}" download="{file_name}">Clique aqui para baixar o arquivo {file_name}</a>'
    return href

# Interface principal
st.write("Faça upload de um arquivo PDF para extrair seu texto, incluindo partes não selecionáveis.")

uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Opções de extração:")
        extraction_type = st.radio(
            "Escolha o método de extração:",
            ("PDF Direto", "OCR (para texto não selecionável)", "Ambos (recomendado)")
        )
    
    with col2:
        st.write("Opções de saída:")
        output_format = st.radio(
            "Escolha o formato de saída:",
            ("Texto (.txt)", "Word (.docx)")
        )
    
    if st.button("Processar PDF"):
        with st.spinner("Processando o arquivo..."):
            extracted_text = ""
            
            # Extração do texto conforme o método escolhido
            if extraction_type == "PDF Direto":
                extracted_text = extract_text_from_pdf(uploaded_file)
            elif extraction_type == "OCR (para texto não selecionável)":
                extracted_text = extract_text_with_ocr(uploaded_file)
            else:  # Ambos
                extracted_text = extract_text_from_pdf(uploaded_file)
                # Se o texto extraído for muito curto, aplicamos OCR
                if len(extracted_text.split()) < 50:
                    st.info("Texto extraído diretamente parece incompleto. Aplicando OCR...")
                    extracted_text = extract_text_with_ocr(uploaded_file)
            
            # Mostrar o texto extraído
            st.subheader("Texto Extraído:")
            st.text_area("", extracted_text, height=300)
            
            # Preparar para download
            if output_format == "Texto (.txt)":
                # Criar arquivo de texto para download
                text_io = io.BytesIO()
                text_io.write(extracted_text.encode('utf-8'))
                text_io.seek(0)
                
                st.download_button(
                    label="Baixar como TXT",
                    data=text_io,
                    file_name="texto_extraido.txt",
                    mime="text/plain"
                )
            else:  # Word
                doc_io = create_docx(extracted_text)
                
                st.download_button(
                    label="Baixar como DOCX",
                    data=doc_io,
                    file_name="texto_extraido.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

# Rodapé com instruções
st.markdown("---")
st.write("""
### Como usar:
1. Faça upload de um arquivo PDF
2. Escolha o método de extração (direto, OCR ou ambos)
3. Selecione o formato de saída desejado
4. Clique em "Processar PDF"
5. Visualize o texto extraído e baixe o arquivo
""")

# Informações sobre o aplicativo
with st.expander("Sobre este aplicativo"):
    st.write("""
    Este aplicativo converte PDFs em texto, incluindo partes não selecionáveis, usando:
    
    - Extração direta do PDF para texto normal
    - OCR (Reconhecimento Ótico de Caracteres) para texto em imagens ou não selecionável
    
    O método "Ambos" tenta primeiro extrair diretamente e, se encontrar pouco texto, aplica OCR automaticamente.
    """)