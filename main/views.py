from django.shortcuts import render, redirect
import os
from django.conf import settings
import pdfplumber
import re
from nltk.corpus import stopwords
import nltk
from unidecode import unidecode
from django.contrib import messages
from django.conf import settings
import openai

# Pega a chave diretamente do settings
openai.api_key = settings.OPENAI_API_KEY

def extrairConteudoArquivo(arquivo):
    if arquivo.name.endswith(".txt"):
        return arquivo.read().decode("utf-8")

    conteudoArq = ""
    with pdfplumber.open(arquivo) as pdf:
        for pagina in pdf.pages:
            conteudoArq += pagina.extract_text() + "\n"
    return conteudoArq

def validaArquivo(arquivo):
    return arquivo.name.lower().endswith((".txt", ".pdf"))

# remoção de stop words, stemming/lemmatização, etc.
def preprocessar(texto):
    texto = texto.lower()
    texto = unidecode(texto)
    texto = re.sub(r"[^a-zA-Z0-9\s]", "", texto)
    try:
        stop_words = set(stopwords.words("portuguese"))
    except LookupError:
        nltk.download('stopwords')
        stop_words = set(stopwords.words("portuguese"))

    texto = [p for p in texto.split() if p not in stop_words]
    return " ".join(texto)

def pegaremail(request):
    if request.method == "POST":

        if request.FILES.get("arquivo") and request.POST.get('emailText'):
            messages.error(request, 'Decida o formato a ser submetido (Arquivo ou Texto).')
            return redirect('pegaremail')
        
        elif request.POST.get('emailText'):
            conteudo = request.POST.get('emailText')

        elif request.FILES.get("arquivo"):
            arquivo = request.FILES["arquivo"]

            if not validaArquivo(arquivo):
                messages.error(request, 'Formato de arquivo não suportado, apenas PDF ou txt.')
                return redirect('pegaremail')
            conteudo = extrairConteudoArquivo(arquivo) # EXTRAIR O CONTEUDO DO ARQUIVO
        
        else:
            messages.error(request, 'Envie o email por texto ou por arquivo')
            return redirect('pegaremail')
        
        textoPrePro = preprocessar(conteudo) # PREPROCESSAR O TEXTO (SENDO TEXTO OU PDF/TXT)

        textoResposta  = classificarEmail(textoPrePro)
        print(textoResposta)
        dados = separaTexto(textoResposta)

        return render(request, 'main/index.html', dados)
    return render(request, 'main/index.html')


def separaTexto(texto_resposta):
    categoria = None
    resposta = None

    # Captura a categoria
    match_categoria = re.search(r"Classificação:\s*\*\*(.*?)\*\*", texto_resposta)
    if match_categoria:
        categoria = match_categoria.group(1).strip()

    # Captura a resposta automática
    match_resposta = re.search(r"Resposta automática:\s*\"(.*)\"", texto_resposta, re.DOTALL)
    if match_resposta:
        resposta = match_resposta.group(1).strip()

    return {
            "categoria": categoria,
            "resposta": resposta
            }


def classificarEmail(email_texto):
    prompt = f"""
    Analise o seguinte email e:
    1. Classifique como 'Produtivo' ou 'Improdutivo'.
    2. Gere uma resposta automática curta e adequada.

    Email: {email_texto}
    Sempre retorne no formato:
    'Classificação: **[Produtivo/Improdutivo]**
    Resposta automática: "[resposta gerada]"'
    """
    
    resposta = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return resposta.choices[0].message.content



def classificar_email(email):
    resposta = openai.chat.completions.create(
        model="ft:gpt-4o-mini-turbo-xxxxx",  # seu modelo fine-tunado
        messages=[{"role": "user", "content": f"Email: {email}\nClassifique e responda:"}]
    )
    return resposta.choices[0].message.content

print(classificar_email("Oi, preciso de ajuda para acessar o sistema."))