# 🏨 Booking.com Price Analyzer

Sistema completo de análise competitiva de preços do Booking.com com dashboard interativo, autenticação de usuários e proteções anti-bloqueio.

## 🚀 Funcionalidades

### ✅ Implementado
- ✨ Sistema de login e registro seguro
- 🔐 Autenticação com hash de senhas
- 🛡️ Proteções anti-bloqueio do Booking.com:
  - User-Agent rotativos
  - Delays aleatórios (2-10 segundos)
  - Simulação de comportamento humano
  - Headers realistas
- 📊 Dashboard interativo com gráficos:
  - Comparação de preços médios
  - Notas de avaliação
  - Distribuição de preços
- ⭐ Extração de:
  - Preços de quartos
  - Notas de avaliação
  - Número de avaliações
  - Estrelas do hotel
- 👨‍👩‍👧‍👦 Configuração flexível de hóspedes:
  - Adultos (1-10)
  - Crianças (0-10)
  - Múltiplos quartos (1-5)
- 💾 Histórico de buscas
- 📥 Exportação para Excel
- 📱 Design responsivo

## 📋 Pré-requisitos

### Sistema Operacional
- Ubuntu 20.04+ / Debian 10+
- CentOS 8+ / RHEL 8+
- Windows Server 2019+

### Software
- Python 3.9+
- Google Chrome (instalado)
- pip
- virtualenv (recomendado)

## 🔧 Instalação Local

### 1. Clone o repositório
```bash
git clone <seu-repositorio>
cd booking-analyzer
```

### 2. Crie um ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Instale o Google Chrome (Linux)
```bash
# Ubuntu/Debian
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

# CentOS/RHEL
wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
sudo yum install ./google-chrome-stable_current_x86_64.rpm
```

### 5. Configure a chave secreta
Edite `app.py` e altere a linha:
```python
app.config['SECRET_KEY'] = 'sua-chave-secreta-super-segura-aqui-12345'
```
Para uma chave aleatória gerada:
```python
import secrets
print(secrets.token_hex(32))
```

### 6. Execute a aplicação
```bash
python app.py
```

Acesse: `http://localhost:5000`

## 🌐 Deploy em Servidor (Produção)

### Opção 1: Deploy com Gunicorn (Linux)

#### 1. Instale dependências do sistema
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv nginx google-chrome-stable
```

#### 2. Configure o projeto
```bash
cd /var/www
sudo mkdir booking-analyzer
sudo chown $USER:$USER booking-analyzer
cd booking-analyzer

# Clone e configure
git clone <seu-repo> .
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Crie o arquivo de serviço systemd
```bash
sudo nano /etc/systemd/system/booking-analyzer.service
```

Conteúdo:
```ini
[Unit]
Description=Booking Price Analyzer
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/booking-analyzer
Environment="PATH=/var/www/booking-analyzer/venv/bin"
ExecStart=/var/www/booking-analyzer/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

#### 4. Configure o Nginx
```bash
sudo nano /etc/nginx/sites-available/booking-analyzer
```

Conteúdo:
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/booking-analyzer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. Inicie o serviço
```bash
sudo systemctl start booking-analyzer
sudo systemctl enable booking-analyzer
sudo systemctl status booking-analyzer
```

### Opção 2: Deploy no Heroku

#### 1. Crie o Procfile
```bash
echo "web: gunicorn app:app" > Procfile
```

#### 2. Crie o arquivo runtime.txt
```bash
echo "python-3.11.5" > runtime.txt
```

#### 3. Configure Buildpacks
```bash
heroku buildpacks:add --index 1 heroku/python
heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-google-chrome
heroku buildpacks:add --index 3 https://github.com/heroku/heroku-buildpack-chromedriver
```

#### 4. Deploy
```bash
git init
git add .
git commit -m "Initial commit"
heroku create seu-app-nome
git push heroku main
```

### Opção 3: Deploy no DigitalOcean App Platform

#### 1. Crie o arquivo .do/app.yaml
```yaml
name: booking-analyzer
services:
- name: web
  github:
    repo: seu-usuario/seu-repo
    branch: main
  build_command: pip install -r requirements.txt
  run_command: gunicorn --workers 3 app:app
  envs:
  - key: SECRET_KEY
    value: ${SECRET_KEY}
  http_port: 8080
```

#### 2. Deploy via CLI
```bash
doctl apps create --spec .do/app.yaml
```

## 🔒 Segurança em Produção

### 1. Use HTTPS
```bash
# Com Certbot (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com
```

### 2. Configure variáveis de ambiente
Crie `.env`:
```bash
SECRET_KEY=sua-chave-secreta-gerada
DATABASE_URL=sqlite:///booking_analyzer.db
FLASK_ENV=production
```

Modifique `app.py`:
```python
from dotenv import load_dotenv
import os

load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
```

### 3. Configure firewall
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

## 📊 Uso da Aplicação

### 1. Registro
- Acesse `/register`
- Crie uma conta com usuário, email e senha

### 2. Login
- Acesse `/login`
- Entre com suas credenciais

### 3. Nova Análise
- Selecione datas de check-in e check-out
- Configure número de adultos, crianças e quartos
- Clique em "Buscar Preços"
- Aguarde 5-10 minutos (depende do número de hotéis)

### 4. Visualizar Resultados
- Dashboard com gráficos interativos
- Tabela detalhada com todos os dados
- Exportação para Excel

## ⚙️ Configurações Avançadas

### Adicionar mais hotéis
Edite `app.py`, seção `DEFAULT_PROPERTIES`:
```python
DEFAULT_PROPERTIES = [
    {
        "name": "Nome do Hotel",
        "id": "ID_BOOKING",
        "url": "slug-do-hotel",
        "yours": False  # True se for seu hotel
    },
    # ... mais hotéis
]
```

### Ajustar delays anti-bloqueio
Em `app.py`, função `random_delay()`:
```python
def random_delay(min_seconds=3, max_seconds=8):  # Aumente os valores
    time.sleep(random.uniform(min_seconds, max_seconds))
```

### Alterar Workers do Gunicorn
```bash
gunicorn --workers 4 --timeout 300 app:app
```

## 🐛 Troubleshooting

### Erro: "ChromeDriver not found"
```bash
# Reinstale webdriver-manager
pip uninstall webdriver-manager
pip install webdriver-manager
```

### Erro: "Database locked"
```bash
# Use PostgreSQL em produção
pip install psycopg2-binary
# Altere DATABASE_URL para PostgreSQL
```

### Scraping muito lento
- Reduza o número de hotéis simultâneos
- Aumente os delays
- Use proxies rotativos

### Booking.com bloqueou IP
- Aguarde 24 horas
- Use proxies
- Aumente delays entre requisições
- Reduza frequência de buscas

## 📝 Estrutura do Projeto

```
booking-analyzer/
│
├── app.py                 # Aplicação principal
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
│
├── templates/            # Templates HTML
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
│
├── static/              # Arquivos estáticos (se necessário)
│   ├── css/
│   └── js/
│
└── instance/            # Banco de dados (criado automaticamente)
    └── booking_analyzer.db
```

## 🔄 Atualizações e Manutenção

### Backup do banco de dados
```bash
# Diário
cp instance/booking_analyzer.db backups/db_$(date +%Y%m%d).db

# Automatizar com cron
0 2 * * * /path/to/backup-script.sh
```

### Atualizar dependências
```bash
pip install --upgrade -r requirements.txt
```

### Limpar buscas antigas
```python
# No Python shell
from app import app, db, Search
from datetime import datetime, timedelta

with app.app_context():
    old_date = datetime.now() - timedelta(days=30)
    Search.query.filter(Search.created_at < old_date).delete()
    db.session.commit()
```

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs: `journalctl -u booking-analyzer -f`
2. Consulte a documentação do Selenium
3. Teste localmente antes de fazer deploy

## ⚠️ Avisos Legais

- Use com responsabilidade e respeite os termos de serviço do Booking.com
- Não faça requisições excessivas (máximo 1-2 buscas por hora)
- Os delays anti-bloqueio são essenciais - não os remova
- Este sistema é para análise competitiva legítima

## 📄 Licença

Este projeto é fornecido "como está" para fins educacionais e de análise competitiva legítima.