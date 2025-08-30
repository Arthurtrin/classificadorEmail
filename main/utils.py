from django.shortcuts import render, redirect
import os
from django.conf import settings
import pdfplumber
import re
from nltk.corpus import stopwords
import nltk
from unidecode import unidecode
from django.contrib import messages
import openai
import joblib
from dotenv import load_dotenv
import spacy


"""
Módulo principal de configuração e processamento de emails.

Este arquivo contém as classes responsáveis por:
    - Configuração e carregamento de variáveis de ambiente, modelo e vetorizer.
    - Manipulação e leitura de arquivos (.txt e .pdf).
    - Pré-processamento de texto (limpeza, remoção de stopwords, normalização).
    - Classificação do email utilizando modelo treinado (Logistic Regression).
    - Geração de respostas automáticas com auxílio da API da OpenAI.

Classes:
    Configuracao:
        Responsável por carregar as configurações globais do projeto:
            - API key da OpenAI.
            - Modelo de classificação treinado.
            - Vetorizer TF-IDF.

    Arquivo:
        Responsável por validar e extrair conteúdo de arquivos enviados:
            - Suporte para `.txt` e `.pdf`.
            - Conversão de PDF para texto usando pdfplumber.

    Email:
        Responsável pelo processamento do conteúdo textual:
            - Pré-processamento (lowercase, remoção de acentos, stopwords).
            - Predição da categoria do email (Produtivo ou Improdutivo).
            - Geração de uma resposta automática apropriada com GPT.

Dependências:
    - openai, dotenv, joblib, pdfplumber, nltk, unidecode, scikit-learn
    - Arquivos: modelo_email.pkl, vectorizer.pkl (treinados previamente)
"""


class Configuracao:
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Caminho absoluto para os arquivos na raiz do projeto
    base_dir = settings.BASE_DIR  # geralmente é a raiz do projeto
    modelo_path = os.path.join(base_dir, 'modelo_email.pkl')
    vectorizer_path = os.path.join(base_dir, 'vectorizer.pkl')

    # Carregar modelo e vetorizer
    model = joblib.load(modelo_path)
    vectorizer = joblib.load(vectorizer_path)

class Arquivo:
    def __init__(self, arquivo):
        self.arquivo = arquivo

    # Extrai o conteudo do arquivo 
    def extrairConteudoArquivo(self):
        if self.arquivo.name.endswith(".txt"):
            self.arquivo = self.arquivo.read().decode("utf-8")
        else:
            conteudoArq = ""
            with pdfplumber.open(self.arquivo) as pdf:
                for pagina in pdf.pages:
                    conteudoArq += pagina.extract_text() + "\n"
            self.arquivo = conteudoArq
    
    # Valida o arquivo sendo .txt ou .pdf
    def validaArquivo(self):
        return self.arquivo.name.lower().endswith((".txt", ".pdf"))

class Email:
    def __init__(self, texto, textopre):
        self.texto = texto
        self.textoProcessado = textopre

    # remoção de stop words, lemmatização, etc.
    

    
    def preprocessar(self):
        # Carregar modelo em português do spaCy (baixar antes com: python -m spacy download pt_core_news_sm)
        nlp = spacy.load("pt_core_news_sm")
        
        # 1. Limpeza básica
        texto = self.texto.lower()
        texto = unidecode(texto)
        texto = re.sub(r"[^a-zA-Z0-9\s]", "", texto)
        
        # 2. Remover stopwords
        try:
            stop_words = set(stopwords.words("portuguese"))
        except LookupError:
            
            nltk.download('stopwords')
            stop_words = set(stopwords.words("portuguese"))

        # 3. Tokenizar e lemmatizar
        doc = nlp(texto)
        tokens = [token.lemma_ for token in doc if token.text not in stop_words]

        # 4. Armazenar texto processado
        self.textoProcessado = " ".join(tokens)


    # Gera a categoria e uma resposta
    def responderEmail(self):
        email_vec = Configuracao.vectorizer.transform([self.textoProcessado])
        categoria = Configuracao.model.predict(email_vec)[0]

        if categoria == "Produtivo":
            prompt = f"Escreva uma resposta educada e útil para este email: {self.textoProcessado}"
        else:
            prompt = f"Escreva uma resposta breve e educada para este email: {self.textoProcessado}"

        resposta = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        return {"categoria": categoria, "resposta": resposta.choices[0].message.content.strip()}