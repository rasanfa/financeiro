# Finanças Pessoais

Sistema financeiro pessoal com Streamlit, PostgreSQL e Supabase.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Preencha `SUPABASE_URL` e `SUPABASE_KEY` no `.env` (painel do Supabase → Project Settings → API).

## Executar

```powershell
streamlit run app.py
```

## Estrutura

```
app.py                 # ponto de entrada
src/config.py          # variáveis de ambiente
src/db/client.py       # cliente Supabase
src/ui/navigation.py   # menu lateral
src/views/             # telas (Dashboard, Categorias, Contas)
```
