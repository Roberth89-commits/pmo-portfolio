# 🏢 PMO Portfolio Hub

Plataforma completa de gerenciamento de portfólio de projetos (PMO) com busca inteligente por IA.

## ✨ Funcionalidades

- 📊 **Dashboard** com métricas em tempo real
- ➕ **CRUD completo** de projetos (criar, editar, excluir)
- 🔍 **Assistente IA** que responde perguntas naturais sobre o portfólio
- 🎨 **Interface moderna** e responsiva
- 💾 **Banco de dados SQLite** (não precisa configurar nada)
- 🚀 **Pronto para deploy** no Render, Railway, Heroku, etc.

## 🚀 Rodar Localmente

### 1. Instalar dependências
```bash
cd pmo-platform
pip install -r requirements.txt
```

### 2. Iniciar o servidor
```bash
python main.py
```

### 3. Acessar no navegador
Abra: http://localhost:8000/static/index.html

## 🌐 Publicar na Internet

### Opção 1: Render (Grátis)
1. Crie uma conta em https://render.com
2. Clique em "New Web Service"
3. Conecte seu repositório GitHub ou faça upload do código
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
5. Clique em "Create Web Service"
6. Pronto! Acesse a URL gerada

### Opção 2: Railway (Grátis)
1. Crie conta em https://railway.app
2. Crie um novo projeto e faça deploy do código
3. Railway detecta automaticamente o Python
4. Acesse a URL pública

### Opção 3: PythonAnywhere (Grátis)
1. Crie conta em https://pythonanywhere.com
2. Faça upload dos arquivos
3. Configure um novo app web com FastAPI
4. Aponte para o arquivo `main.py`

## 🗂️ Estrutura

```
pmo-platform/
├── main.py              # Backend FastAPI + lógica IA
├── models.py            # Modelos SQLAlchemy
├── schemas.py           # Schemas Pydantic
├── database.py          # Config SQLite
├── requirements.txt     # Dependências
├── static/
│   └── index.html       # Frontend completo
└── README.md
```

## 🔍 Perguntas que a IA responde

- "Quais projetos estão atrasados?"
- "Qual o orçamento total do portfólio?"
- "Quais são os principais riscos?"
- "Resumo geral do portfólio"
- "Quem são os gerentes?"
- "Prazos dos projetos"
- E qualquer busca por nome/descrição de projeto

## 🛠️ Stack Tecnológica

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python + FastAPI |
| Banco de Dados | SQLite |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| IA | Motor de busca semântica integrado |

## 📄 Licença

MIT - Livre para uso pessoal e comercial.
