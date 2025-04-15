# Conversor de PDF para Texto

Aplicativo Streamlit que converte arquivos PDF em texto, incluindo partes não selecionáveis usando OCR avançado.

## Recursos

- Extração direta de texto de PDFs
- OCR avançado para texto em imagens ou não selecionável
- Pré-processamento de imagem para melhorar a precisão do OCR
- Exportação para TXT ou DOCX
- Interface amigável com Streamlit

## Requisitos

- Python 3.7+
- Tesseract OCR instalado no sistema
- Poppler Utils

## Instalação

1. Clone este repositório
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Instale os pacotes do sistema necessários:

```bash
apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-por poppler-utils
```

## Uso

Execute o aplicativo com:

```bash
streamlit run app.py
```

### Como usar:
1. Faça upload de um arquivo PDF
2. Escolha o método de extração (direto, OCR ou ambos)
3. Selecione o formato de saída desejado
4. Clique em "Processar PDF"
5. Visualize o texto extraído e baixe o arquivo

## Melhorias no OCR:
O aplicativo implementa várias técnicas avançadas para melhorar a extração de texto:

- Pré-processamento avançado de imagens (usando OpenCV)
- Limiarização adaptativa para melhorar o contraste
- Redução de ruído e melhoria de nitidez
- Configurações otimizadas do Tesseract OCR
