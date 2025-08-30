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

2. erro(request, texto):
    - Exibe uma mensagem de erro para o usuário usando o framework de mensagens do Django.
    - Redireciona para a página principal ('home') após exibir a mensagem.

Dependências:
- Django: render, redirect, messages
- Utils: Email, Arquivo
- OpenAI: RateLimitError
"""

def home(request):
    if request.method == "POST":

        if request.FILES.get("arquivo") and request.POST.get('emailText'):
            erro(request, 'Decida o formato a ser submetido (Arquivo ou Texto).')
        
        elif request.POST.get('emailText'):
            emailTexto = Email(request.POST.get('emailText'), "")

        elif request.FILES.get("arquivo"):
            arquivo = Arquivo(request.FILES["arquivo"])
            
            if not arquivo.validaArquivo():
                erro(request, 'Formato de arquivo não suportado, apenas .pdf ou .txt')
            
            arquivo.extrairConteudoArquivo() 
            emailTexto = Email(arquivo.arquivo, "")
        else:
            erro(request, 'Envie o email por texto ou por arquivo')
        
        emailTexto.preprocessar()

        try:
            dados = emailTexto.responderEmail()
        except RateLimitError:
            erro(request, 'Limite de requisições atingido. Tente novamente mais tarde.')
        except Exception as e:
            erro(request, 'Ocorreu um erro inesperado: {e}.')
            
        return render(request, 'main/index.html', dados)
    return render(request, 'main/index.html')

def erro(request, texto):
    messages.error(request, texto)
    return redirect('home')
