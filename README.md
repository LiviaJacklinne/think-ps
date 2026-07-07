# think-ps
Aplicação de controle de caixa, para processo seletivo da Think

## Preparando ambiente

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
```
python manage.py runserver 8000
```
Para o Ui (frontend) rode:
```
npm run dev
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