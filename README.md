# Gabora Scoop — protótipo inicial

E-commerce responsivo inspirado na organização do tema Warehouse, construído com frontend simples (HTML, CSS e JavaScript) e backend Python/FastAPI.

## O que está incluído

- Página inicial responsiva com identidade rosa e dourada baseada na logo.
- Catálogo com Scoops de Bijuterias, Skincare e Misto.
- Carrinho persistido no navegador.
- Checkout demonstrativo sem cobrança real.
- Criação e consulta de pedidos em SQLite.
- Página de acompanhamento por código e e-mail.
- Painel administrativo demonstrativo para alterar status.
- API REST documentada automaticamente pelo FastAPI.

## Como executar

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

No Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Acesse:

- Loja: http://127.0.0.1:8000
- Painel: http://127.0.0.1:8000/admin.html
- API: http://127.0.0.1:8000/docs

## Avisos

Esta é uma versão inicial para validação. Pagamentos, cálculo de frete, autenticação administrativa, estoque completo, envio de e-mails e publicação de vídeos ainda precisam de integrações reais. Os preços são demonstrativos.

