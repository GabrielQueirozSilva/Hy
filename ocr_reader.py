from PIL import Image
import pytesseract
import cv2
import numpy as np

# CONFIGURAÇÃO IMPORTANTE PARA WINDOWS:
# Certifique-se de que este caminho está correto no seu sistema
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_image(img):
    """
    Pré-processa a imagem de forma otimizada para a fonte pixelada do Minecraft.
    """
    # Converter a imagem PIL (escala de cinza) para o formato do OpenCV
    img_cv = np.array(img)

    # 1. Redimensionar a imagem para aumentar a contagem de pixels da fonte.
    # Usamos INTER_NEAREST para manter a nitidez da fonte pixelada.
    scale_factor = 3
    width = int(img_cv.shape[1] * scale_factor)
    height = int(img_cv.shape[0] * scale_factor)
    resized = cv2.resize(img_cv, (width, height), interpolation=cv2.INTER_NEAREST)

    # 2. Binarização da imagem. O texto no Minecraft é claro sobre um fundo escuro.
    # THRESH_OTSU encontra o melhor valor de limiar automaticamente.
    # O resultado será texto branco em um fundo preto.
    _, thresh = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 3. Inverter as cores. Tesseract prefere texto PRETO em fundo BRANCO.
    inverted = cv2.bitwise_not(thresh)

    # 4. Adicionar uma borda branca. Isso pode melhorar a detecção de caracteres
    # que estão muito próximos das bordas da imagem.
    bordered = cv2.copyMakeBorder(inverted, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255])

    return Image.fromarray(bordered)

def image_to_text(image_path):
    """
    Extrai texto de uma imagem de tela inteira, recortando e pré-processando a área de interesse.
    """
    try:
        # Abrir imagem original
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"Erro: O arquivo de imagem não foi encontrado em '{image_path}'")
        return ""

    # Recortar a área onde a descrição do item aparece
    # ATENÇÃO: Estes valores podem precisar de ajuste dependendo da resolução da sua tela!
    left, top, right, bottom = 600, 300, 1450, 850
    img_cropped = img.crop((left, top, right, bottom))

    # Converter para escala de cinza ANTES de passar para o pré-processamento
    img_gray = img_cropped.convert('L')

    # Pré-processar a imagem recortada e em escala de cinza
    img_processed = preprocess_image(img_gray)

    # Salvar imagem processada para depuração (muito útil para ver o resultado)
    img_processed.save("debug_cropped.png")
    print("Imagem pré-processada salva como 'debug_cropped.png'")

    # Extrair texto com OCR. O psm 6 trata a imagem como um bloco uniforme de texto.
    text = pytesseract.image_to_string(img_processed, lang='eng', config='--psm 6')

    return text

def parse_item_text(text):
    """
    Analisa o texto extraído para encontrar dados específicos do item.
    Esta função provavelmente precisará de ajustes após obter um texto limpo.
    """
    lines = text.splitlines()
    item_data = {}

    print("\n--- Início do Texto para Análise ---")
    for line in lines:
        print(line)
        line_clean = line.strip()
        if not line_clean:
            continue

        # Exemplo de como você pode adaptar a análise:
        # O texto "Auctions Browser" pode ser o título
        
        # O texto "Find items for sale" pode ser parte da descrição
        if "Buy it now:" in line_clean:
            item_data['price'] = line_clean
            
        if "Seller:" in line_clean:
            item_data['vendedor'] = line_clean

    print("--- Fim do Texto para Análise ---\n")
    return item_data

if __name__ == "__main__":
    # IMPORTANTE: Verifique se este caminho está correto!
    caminho_da_imagem = r"C:\Users\gabri\Pictures\Screenshots\Captura de tela 2025-09-18 171852.png"
    
    print("Texto extraído (COM pré-processamento otimizado):")
    print("=" * 50)
    
    texto_melhorado = image_to_text(caminho_da_imagem)
    print(texto_melhorado)
    
    print("=" * 50)

    dados_do_item = parse_item_text(texto_melhorado)
    print("\nDados Extraídos do Item:")
    print(dados_do_item)