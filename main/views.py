from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import Email, Arquivo
from openai import RateLimitError

"""
Arquivo de views do Django para lidar com submissão de emails e arquivos.

Contém a lógica para receber emails enviados pelo usuário, seja por texto direto
ou por arquivo (.txt ou .pdf), processar o conteúdo, classificar o email usando
modelo pré-treinado e gerar uma resposta automática com a API OpenAI.

Funções e classes principais:

1. home(request):
    - Método: POST
    - Recebe email ou arquivo do usuário.
    - Valida se apenas um tipo de entrada foi enviado.
    - Para arquivos, valida a extensão e extrai o conteúdo.
    - Preprocessa o texto (remoção de stopwords, normalização, etc.).
    - Chama o método 'responderEmail' da classe Email para gerar categoria e resposta.
    - Tratamento de erros:
        * RateLimitError: limite de requisições da OpenAI atingido.
        * Exception genérica: captura qualquer outro erro inesperado.
    - Renderiza a página principal com os dados processados ou mensagens de erro.

Dependências:
- Django: render, redirect, messages
- Utils: Email, Arquivo
- OpenAI: RateLimitError
"""

def home(request):
    if request.method == "POST":
        
        if request.FILES.get("arquivo") and request.POST.get('emailText'):
            messages.error(request, 'Decida o formato a ser submetido (Arquivo ou Texto).')
            return redirect('home')
        
        elif request.POST.get('emailText'):
            emailTexto = Email(request.POST.get('emailText'), "")

        elif request.FILES.get("arquivo"):
            arquivo = Arquivo(request.FILES["arquivo"])
            
            if not arquivo.validaArquivo():
                messages.error(request, 'Formato de arquivo não suportado, apenas .pdf ou .txt')
                return redirect('home')
     
            arquivo.extrairConteudoArquivo() 
            emailTexto = Email(arquivo.arquivo, "")
            emailTexto.preprocessar()
        else:
            messages.error(request, 'Envie o email por texto ou por arquivo')
            return redirect('home')
        
        try:
            dados = emailTexto.responderEmail()
        except RateLimitError:
            messages.error(request, 'Limite de requisições atingido. Tente novamente mais tarde.')
            return redirect('home')
        except Exception as e:
            messages.error(request, 'Ocorreu um erro inesperado: {e}.')
            return redirect('home')
            
        return render(request, 'main/index.html', dados)
    return render(request, 'main/index.html')

