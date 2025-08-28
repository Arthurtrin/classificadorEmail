from django.shortcuts import render, redirect
import os
from django.conf import settings
import pdfplumber
import re
from nltk.corpus import stopwords
import nltk
from unidecode import unidecode
from django.contrib import messages

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
            textoPrePro = preprocessar(conteudo) # PREPROCESSAR O TEXTO (SENDO TEXTO OU PDF/TXT)

        else:
            messages.error(request, 'Envie o email por texto ou por arquivo')
            return redirect('pegaremail')

        categoria = ""
        resposta = ""
        dados = {
            "categoria": categoria,
            "respSugerida": resposta
            }
        return render(request, 'main/index.html', dados)
    return render(request, 'main/index.html')

