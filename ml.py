import joblib
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import openai
import os
from dotenv import load_dotenv

"""
Arquivo para treinar o modelo de classificação de emails.

Este script lê um arquivo `.jsonl` contendo exemplos de emails já rotulados 
(com categoria e resposta), processa os dados e treina um modelo de 
classificação para distinguir entre emails **Produtivos** e **Improdutivos**.  

Passos principais:
    1. Carrega o arquivo `emails_train.jsonl`.
    2. Extrai os textos dos emails e suas respectivas categorias.
    3. Constrói um DataFrame com os exemplos.
    4. Divide os dados em treino e teste.
    5. Vetoriza os textos usando TF-IDF.
    6. Treina um modelo de regressão logística.
    7. Avalia o modelo com os dados de teste.
    8. Salva o modelo treinado (`modelo_email.pkl`) e o vetorizer (`vectorizer.pkl`)
       para uso posterior na aplicação Django.

Requisitos:
    - Arquivo `emails_train.jsonl` no mesmo diretório do script.
    - Bibliotecas: joblib, pandas, scikit-learn, openai, dotenv.

Saídas:
    - `modelo_email.pkl` → modelo de classificação treinado.
    - `vectorizer.pkl` → vetorizer TF-IDF treinado.
"""


# Carregar API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Ler arquivo JSONL e criar DataFrame
emails = []
categorias = []

with open("emails_train.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        # Extrair apenas o email e a categoria
        emails.append(data['prompt'].replace("Classifique e responda:\n\n###\n\n", "").replace("Email: ", "").strip())
        # Extrair categoria do completion
        completion = data['completion']
        if "Categoria: Produtivo" in completion:
            categorias.append("Produtivo")
        else:
            categorias.append("Improdutivo")

df = pd.DataFrame({"email": emails, "categoria": categorias})

# Separar treino e teste
X_train, X_test, y_train, y_test = train_test_split(df['email'], df['categoria'], test_size=0.2, random_state=42)

# Vetorização TF-IDF
vectorizer = TfidfVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Treinar modelo de classificação
model = LogisticRegression()
model.fit(X_train_vec, y_train)

# Avaliar modelo
y_pred = model.predict(X_test_vec)

# Salvar modelo e vetorizer para usar depois
joblib.dump(model, 'modelo_email.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')