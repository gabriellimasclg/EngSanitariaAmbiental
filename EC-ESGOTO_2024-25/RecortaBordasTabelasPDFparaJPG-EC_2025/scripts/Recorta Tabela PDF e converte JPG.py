# -*- coding: utf-8 -*-
"""
Created on Fri May 23 15:30:19 2025

@author: gabriel.coimbra
"""

import os
import fitz  # PyMuPDF
from PIL import Image
import cv2
import numpy as np

def crop_pdf_to_table(input_folder, output_folder, zoom=3.0, quality=100):
    os.makedirs(output_folder, exist_ok=True)

    # Percorrer todos os arquivos na pasta de entrada
    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_folder, file_name)
            pdf_document = fitz.open(pdf_path)

            # Processar cada página do PDF
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]

                # Renderizar a página em alta resolução
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)

                # Converter a imagem da página para um formato compatível com o OpenCV
                img_cv = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
                if pix.n == 4:
                    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGBA2RGB)
                elif pix.n == 1:
                    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_GRAY2RGB)

                # Converter a imagem para escala de cinza
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

                # Aplicar limiarização
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

                # Encontrar contornos
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Encontrar o maior contorno
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)

                # Recortar
                cropped_img = img_cv[y:y+h, x:x+w]

                # Converter para PIL e salvar
                cropped_img_pil = Image.fromarray(cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB))

                output_file_name = f"{os.path.splitext(file_name)[0]}.jpg"
                output_path = os.path.join(output_folder, output_file_name)
                cropped_img_pil.save(output_path, "JPEG", quality=quality, dpi=(300, 300))

                print(f"{output_file_name} - {output_path}\n")

    print("Processing complete.")

# Definir caminhos
repoPath = r'C:\Users\gabriel.coimbra\Documents\GitHub\NovaEngevix\recortaimagens'
input_folder = os.path.join(repoPath, 'inputs')
output_folder = os.path.join(repoPath, 'outputs')
static_folder = os.path.join(repoPath, 'static')

# Criar diretórios se não existirem
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)
os.makedirs(static_folder, exist_ok=True)

crop_pdf_to_table(input_folder, output_folder, zoom=4.0, quality=100)
