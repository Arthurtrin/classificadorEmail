# 📬 Classificador Inteligente de E-mails

> Sistema **Django** para classificar emails como Produtivo ou Improdutivo e gerar respostas automáticas usando **Machine Learning** bem como o serviço de **IA da OpenAI**.
---

## 📌 Sobre o Projeto

Esta aplicação permite que usuários classifiquem e-mails como **"Produtivo"** ou **"Improdutivo"**, com base em um modelo de machine learning previamente treinado. Além disso, utiliza a **IA da OpenAI** para sugerir uma **resposta automática personalizada**, conforme a categoria e o conteúdo do e-mail.

O objetivo é ajudar empresas a ganharem produtividade ao tratar comunicações relevantes de forma rápida e automatizada.

---

## 🎯 Funcionalidades

- Suporte a envio de emails por meio de texto ou arquivo (.txt / .pdf).
- Classificação automática em "Produtivo" ou "Improdutivo".
- Geração de respostas automáticas, em tom formal, via GPT-4o-mini
- Interface responsiva com o framework **Bootstrap**.
- Tratamento de limite de requisições da API.

---

## 🖥️ Tecnologias Utilizadas

| Camada | Tecnologias |
|--------|-------------|
| 🔙 Backend | Python, Django, joblib, OpenAI, scikit-learn |
| 🔮 Machine Learning | Logistic Regression, TF-IDF, NLTK |
| 🔝 Frontend | HTML5, CSS3, Bootstrap |
| 📦 Outros | Render (deploy), SQLite (local), `.env` `.jsonl`|

---

## 🌐 Acesse o Projeto Online

🔗 Deploy: [https://classificadoremail-gz8o.onrender.com/](https://classificadoremail-gz8o.onrender.com/)

---

## 🧠 Treinamento do Modelo

O modelo foi treinado com base em um arquivo .jsonl contendo exemplos reais e simulados de e-mails categorizados como produtivos ou improdutivos. O pipeline inclui:

- Pré-processamento com **stopwords + lemmatização**
- Vetorização com **TF-IDF**
- Classificação com **Regressão Logística**
- Persistência do modelo com `joblib`

---

## ⚙️ Como Executar Localmente

1. Clone o repositório:

```bash
git clone https://github.com/Arthurtrin/classificadorEmail.git
cd classificadorEmail
```

2. Crie um ambiente virtual e ative:

```bash
python -m venv venv
venv\Scripts\activate     
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Crie um arquivo no diretorio chamado ".env" para dados sensiveis:

```bash
# exemplo

OPENAI_API_KEY=sua_chave_api_openai
DEBUG=True
SECRET_KEY=django-insecure-e2%-b-s^n72_+ir1a%+clia*2(dmui^mt!bd_26g8i#qmm(tk%

```

5. Treine o modelo:

```bash
python ml.py
```

6. Instale o modelo em português para lemmatização

```bash
python -m spacy download pt_core_news_sm
```

7. Rode o servidor local:

```bash
python manage.py runserver
```

---

## 🔑 Como obter sua chave OpenAI

Para utilizar a funcionalidade de resposta automática com IA, você precisa gerar uma chave de API da OpenAI. Siga os passos abaixo:

1. Acesse: https://platform.openai.com/account/api-keys
2. Clique em "Create new secret key"
3. Copie a chave (vai parecer algo como sk-proj-xxxxxxxxxx...)

> ⚠️ Atenção: essa chave possui limites gratuitos e pode ter custo se exceder. Consulte os termos da API para mais detalhes.

---
