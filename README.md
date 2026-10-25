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
app.py                      # ponto de entrada Streamlit
sql/                        # schema V1 congelado (não alterar)
src/config.py               # variáveis de ambiente
src/db/client.py            # conexão Supabase
src/repositories/           # acesso a tabelas (sem CRUD ainda)
src/services/               # regras de aplicação (sem CRUD ainda)
src/ui/navigation.py        # menu lateral
src/views/                  # páginas vazias
```
