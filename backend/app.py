import os
from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
from flask_cors import CORS # Importe o CORS no início também

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configura a chave de API do Gemini
# Certifique-se que GEMINI_API_KEY está definida no seu arquivo .env
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("A variável de ambiente GEMINI_API_KEY não está definida.")
genai.configure(api_key=API_KEY)

app = Flask(__name__)
CORS(app) # Configure o CORS aqui, fora do if __name__ == '__main__' para consistência

# Rota principal para verificar se o servidor está funcionando
@app.route('/')
def home():
    return "Backend do gerador de texto alternativo está funcionando!"

# Rota para gerar o texto alternativo da imagem
@app.route('/generate_alt_text', methods=['POST'])
def generate_alt_text():
    if 'image' not in request.files:
        return jsonify({'error': 'Nenhuma imagem enviada.'}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'error': 'Nenhuma imagem selecionada.'}), 400

    if image_file:
        try:
            # Carrega o modelo Gemini Pro Vision
            # O modelo 'gemini-1.5-flash' é ideal para análise de imagem e texto
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Prepara a imagem para o modelo
            image_bytes = image_file.read()
            image_part = {
                "mime_type": image_file.mimetype,
                "data": image_bytes
            }

            # Define o prompt para o modelo Gemini
            prompt_parts = [
                "Descreva esta imagem de forma concisa e útil para uma pessoa com deficiência visual. Inclua os elementos mais importantes e o contexto da cena. Seja objetivo e evite floreios. Maximo 100 palavras.",
                image_part
            ]

            # Gera a descrição da imagem
            response = model.generate_content(prompt_parts)
            alt_text = response.text

            return jsonify({'alt_text': alt_text}), 200

        except Exception as e:
            print(f"Erro ao processar imagem: {e}")
            return jsonify({'error': f'Erro ao processar imagem: {str(e)}'}), 500
    return jsonify({'error': 'Erro desconhecido.'}), 500

# Esta parte só é executada quando o script é rodado diretamente (não importado)
if __name__ == '__main__':
    # No Render, a porta é fornecida via variável de ambiente PORT
    # E o host deve ser 0.0.0.0 para que o serviço seja acessível externamente
    port = int(os.environ.get("PORT", 5000)) # Pega a porta do ambiente ou usa 5000 como fallback
    app.run(host='0.0.0.0', port=port, debug=True)