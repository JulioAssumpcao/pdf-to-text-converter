import streamlit as st
import PyPDF2
import pytesseract
from pdf2image import convert_from_bytes
import io
import docx
from PIL import Image
import base64
import cv2
import numpy as np

# Configuração da página Streamlit
st.set_page_config(page_title="Conversor de PDF para Texto", layout="wide")
st.title("Conversor de PDF para Texto")

# Configuração avançada do Tesseract
pytesseract.pytesseract.tesseract_cmd = r'tesseract'  # Certifique-se de que o caminho está correto

# Função para extrair texto diretamente do PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page_num in range(len(pdf_reader.pages)):
        page_text = pdf_reader.pages[page_num].extract_text()
        if page_text:
            text += page_text + "\n\n"
    return text

# Função para melhorar a qualidade da imagem para OCR
def preprocess_image(image):
    # Convertendo a imagem PIL para o formato numpy array para uso com OpenCV
    img_np = np.array(image)
    
    # Convertendo para escala de cinza
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY) if len(img_np.shape) == 3 else img_np
    
    # Aplicando limiarização adaptativa para melhorar o contraste
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY, 11, 2)
    
    # Aplicando filtro de desfoque para remover ruído
    blur = cv2.GaussianBlur(thresh, (3, 3), 0)
    
    # Aplicando filtro de nitidez para melhorar a definição do texto
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(blur, -1, kernel)
    
    # Convertendo de volta para o formato PIL
    processed_img = Image.fromarray(sharpened)
    
    return processed_img

# Função para extrair texto usando OCR com melhorias
def extract_text_with_ocr(pdf_file):
    text = ""
    try:
        # Guardar conteúdo do arquivo em um buffer
        pdf_content = pdf_file.read()
        pdf_file.seek(0)  # Rebobinar o arquivo para uso posterior
        
        # Converter PDF em imagens com maior DPI para melhor qualidade
        images = convert_from_bytes(pdf_content, dpi=300)
        
        total_pages = len(images)
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, image in enumerate(images):
            status_text.text(f"Processando página {i+1} de {total_pages} com OCR...")
            
            # Pré-processamento da imagem para melhorar o OCR
            processed_img = preprocess_image(image)
            
            # Configuração avançada do OCR para melhorar resultados
            config = '--oem 3 --psm 6 -l por+eng'
            page_text = pytesseract.image_to_string(processed_img, config=config)
            
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
        
        # Adicionar opção para qualidade OCR
        if extraction_type in ["OCR (para texto não selecionável)", "Ambos (recomendado)"]:
            ocr_quality = st.select_slider(
                "Qualidade do OCR (maior qualidade = mais lento):",
                options=["Baixa", "Média", "Alta"],
                value="Média"
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
                if not extracted_text.strip():
                    st.warning("Não foi possível extrair texto diretamente. O PDF pode conter apenas imagens ou texto não selecionável.")
                    st.info("Tentando extrair com OCR...")
                    extracted_text = extract_text_with_ocr(uploaded_file)
            elif extraction_type == "OCR (para texto não selecionável)":
                extracted_text = extract_text_with_ocr(uploaded_file)
            else:  # Ambos
                direct_text = extract_text_from_pdf(uploaded_file)
                
                # Verificar se o texto extraído diretamente é suficiente
                if len(direct_text.split()) < 50:
                    st.info("Texto extraído diretamente parece incompleto. Aplicando OCR...")
                    ocr_text = extract_text_with_ocr(uploaded_file)
                    
                    # Combinar resultados (OCR geralmente é mais completo mas pode ter erros)
                    if len(ocr_text.split()) > len(direct_text.split()):
                        extracted_text = ocr_text
                    else:
                        extracted_text = direct_text
                else:
                    extracted_text = direct_text
            
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
    
    ### Melhorias no OCR:
    - Pré-processamento avançado de imagens
    - Limiarização adaptativa para melhorar o contraste
    - Redução de ruído e melhoria de nitidez
    - Configurações otimizadas do Tesseract OCR
    """)
