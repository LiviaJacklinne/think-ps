# think-ps
Aplicação de controle de caixa, para processo seletivo da Think.

## Sumário
1. [Preparando ambiente local](#preparando-ambiente-local)
2. [Executando o Docker](#executano-o-docker)
3. [Documentação](#documentação)

## Preparando ambiente local

### Ativando env
```bash
python -m venv venv

.\venv\Scripts\Activate.ps1

# Se aparecer erro de política de execução no comando anterior, rode o comando abaixo e em seguida execute o .\venv de novo
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Instalando o Django
```bash
pip install django
```

### Executando a aplicação

Para executar a Api rode:
```bash
python manage.py runserver 8000
```

Para o Ui (frontend) rode:
```bash
npm run dev
```

Para executar os testes:
```bash
python.exe manage.py test accounts compras
```

## Executando o Docker

Rode o comando abaixo, na raiz do projeto, para subir o container:
```bash
docker compose up --build
```

### Acessando o MongoDB dentro do Docker

```bash
# acessando o mongo via terminal
docker compose exec mongo mongosh

# seleiconando o banco de uso
use think_ps

show collections

# exibir os dados dentro das collections
db.produtos.find().pretty()
db.compras.find().pretty()

# fazendo um select pelo nome do produto
db.produtos.find({ nome: "Pneu" }).pretty()

# count 
db.produtos.countDocuments()
db.compras.countDocuments()
```

## Documentação

Abre a tela do Swagger UI.
```bash
http://localhost:8000/api/docs/
```

Retorna o JSON OpenAPI:
```bash
http://localhost:8000/api/schema/
```