#!/bin/bash

# ============================================
# BOOKING ANALYZER - SCRIPT DE INSTALAÇÃO
# ============================================
# Este script automatiza a instalação completa

set -e  # Parar em caso de erro

echo "🏨 BOOKING PRICE ANALYZER - INSTALAÇÃO AUTOMÁTICA"
echo "=================================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para printar mensagens coloridas
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Detectar sistema operacional
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
            print_info "Sistema detectado: Debian/Ubuntu"
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
            print_info "Sistema detectado: CentOS/RHEL"
        else
            OS="linux"
            print_info "Sistema detectado: Linux genérico"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_info "Sistema detectado: macOS"
    else
        OS="unknown"
        print_error "Sistema operacional não suportado"
        exit 1
    fi
}

# Verificar se está rodando como root (para instalação do sistema)
check_root() {
    if [ "$EUID" -eq 0 ]; then
        SUDO=""
    else
        SUDO="sudo"
    fi
}

# Instalar dependências do sistema
install_system_deps() {
    echo ""
    echo "📦 Instalando dependências do sistema..."
    
    if [ "$OS" == "debian" ]; then
        $SUDO apt update
        $SUDO apt install -y python3 python3-pip python3-venv wget gnupg
        
        # Instalar Google Chrome
        if ! command -v google-chrome &> /dev/null; then
            print_info "Instalando Google Chrome..."
            wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
            $SUDO apt install -y ./google-chrome-stable_current_amd64.deb
            rm google-chrome-stable_current_amd64.deb
            print_success "Google Chrome instalado"
        else
            print_success "Google Chrome já instalado"
        fi
        
    elif [ "$OS" == "redhat" ]; then
        $SUDO yum update -y
        $SUDO yum install -y python3 python3-pip wget
        
        # Instalar Google Chrome
        if ! command -v google-chrome &> /dev/null; then
            print_info "Instalando Google Chrome..."
            wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
            $SUDO yum install -y ./google-chrome-stable_current_x86_64.rpm
            rm google-chrome-stable_current_x86_64.rpm
            print_success "Google Chrome instalado"
        else
            print_success "Google Chrome já instalado"
        fi
        
    elif [ "$OS" == "macos" ]; then
        if ! command -v brew &> /dev/null; then
            print_error "Homebrew não encontrado. Instale em: https://brew.sh"
            exit 1
        fi
        brew install python3 wget
        
        # Instalar Google Chrome
        if ! command -v google-chrome &> /dev/null; then
            print_info "Instalando Google Chrome..."
            brew install --cask google-chrome
            print_success "Google Chrome instalado"
        else
            print_success "Google Chrome já instalado"
        fi
    fi
    
    print_success "Dependências do sistema instaladas"
}

# Criar ambiente virtual Python
setup_python_env() {
    echo ""
    echo "🐍 Configurando ambiente Python..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Ambiente virtual criado"
    else
        print_info "Ambiente virtual já existe"
    fi
    
    # Ativar ambiente virtual
    source venv/bin/activate
    
    # Atualizar pip
    pip install --upgrade pip
    
    # Instalar dependências Python
    if [ -f "requirements.txt" ]; then
        print_info "Instalando dependências Python..."
        pip install -r requirements.txt
        print_success "Dependências Python instaladas"
    else
        print_error "requirements.txt não encontrado"
        exit 1
    fi
}

# Gerar chave secreta
generate_secret_key() {
    echo ""
    echo "🔐 Gerando chave secreta..."
    
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    
    if [ -f ".env" ]; then
        print_info "Arquivo .env já existe"
        read -p "Deseja sobrescrever? (s/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            return
        fi
    fi
    
    # Criar .env a partir do .env.example
    if [ -f ".env.example" ]; then
        cp .env.example .env
        # Substituir a chave secreta
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        print_success "Arquivo .env criado com chave secreta única"
    else
        # Criar .env básico
        cat > .env << EOF
FLASK_ENV=development
SECRET_KEY=$SECRET_KEY
DATABASE_URL=sqlite:///booking_analyzer.db
EOF
        print_success "Arquivo .env criado"
    fi
}

# Inicializar banco de dados
init_database() {
    echo ""
    echo "💾 Inicializando banco de dados..."
    
    source venv/bin/activate
    
    python3 << EOF
from app import app, db
with app.app_context():
    db.create_all()
    print("Banco de dados inicializado")
EOF
    
    print_success "Banco de dados pronto"
}

# Criar estrutura de diretórios
create_directories() {
    echo ""
    echo "📁 Criando estrutura de diretórios..."
    
    mkdir -p logs
    mkdir -p backups
    mkdir -p instance
    
    print_success "Diretórios criados"
}

# Teste rápido
run_test() {
    echo ""
    echo "🧪 Executando teste rápido..."
    
    source venv/bin/activate
    
    python3 << EOF
import sys
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    print("✓ Todas as bibliotecas carregadas com sucesso")
    sys.exit(0)
except Exception as e:
    print(f"✗ Erro: {e}")
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        print_success "Teste passou com sucesso"
    else
        print_error "Teste falhou"
        exit 1
    fi
}

# Menu de escolha de ambiente
choose_environment() {
    echo ""
    echo "🎯 Escolha o ambiente:"
    echo "1) Desenvolvimento (local)"
    echo "2) Produção (servidor)"
    echo "3) Apenas testar"
    read -p "Escolha (1-3): " choice
    
    case $choice in
        1)
            ENV="development"
            ;;
        2)
            ENV="production"
            setup_production
            ;;
        3)
            ENV="development"
            ;;
        *)
            print_error "Escolha inválida"
            exit 1
            ;;
    esac
    
    # Atualizar .env
    sed -i "s/FLASK_ENV=.*/FLASK_ENV=$ENV/" .env
}

# Configuração adicional para produção
setup_production() {
    echo ""
    echo "🚀 Configuração para PRODUÇÃO"
    echo "============================="
    
    # Nginx
    read -p "Deseja instalar e configurar Nginx? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        install_nginx
    fi
    
    # Systemd service
    read -p "Deseja criar serviço systemd? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        create_systemd_service
    fi
    
    # SSL
    read -p "Deseja configurar SSL com Let's Encrypt? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        setup_ssl
    fi
}

# Instalar Nginx
install_nginx() {
    print_info "Instalando Nginx..."
    
    if [ "$OS" == "debian" ]; then
        $SUDO apt install -y nginx
    elif [ "$OS" == "redhat" ]; then
        $SUDO yum install -y nginx
    fi
    
    # Configurar
    read -p "Digite seu domínio (ex: example.com): " domain
    
    cat > /tmp/booking-analyzer-nginx << EOF
server {
    listen 80;
    server_name $domain;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    
    $SUDO mv /tmp/booking-analyzer-nginx /etc/nginx/sites-available/booking-analyzer
    $SUDO ln -sf /etc/nginx/sites-available/booking-analyzer /etc/nginx/sites-enabled/
    $SUDO nginx -t && $SUDO systemctl restart nginx
    
    print_success "Nginx configurado"
}

# Criar serviço systemd
create_systemd_service() {
    print_info "Criando serviço systemd..."
    
    CURRENT_DIR=$(pwd)
    
    cat > /tmp/booking-analyzer.service << EOF
[Unit]
Description=Booking Price Analyzer
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
EOF
    
    $SUDO mv /tmp/booking-analyzer.service /etc/systemd/system/
    $SUDO systemctl daemon-reload
    $SUDO systemctl enable booking-analyzer
    $SUDO systemctl start booking-analyzer
    
    print_success "Serviço systemd criado e iniciado"
}

# Configurar SSL
setup_ssl() {
    print_info "Configurando SSL com Let's Encrypt..."
    
    if [ "$OS" == "debian" ]; then
        $SUDO apt install -y certbot python3-certbot-nginx
    elif [ "$OS" == "redhat" ]; then
        $SUDO yum install -y certbot python3-certbot-nginx
    fi
    
    read -p "Digite seu domínio: " domain
    $SUDO certbot --nginx -d $domain
    
    print_success "SSL configurado"
}

# Exibir instruções finais
show_final_instructions() {
    echo ""
    echo "=============================================="
    echo "✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
    echo "=============================================="
    echo ""
    
    if [ "$ENV" == "development" ]; then
        echo "Para iniciar em modo desenvolvimento:"
        echo "  source venv/bin/activate"
        echo "  python app.py"
        echo ""
        echo "Acesse: http://localhost:5000"
    else
        echo "Serviço iniciado em modo produção"
        echo "Verifique status: sudo systemctl status booking-analyzer"
        echo "Ver logs: sudo journalctl -u booking-analyzer -f"
    fi
    
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Crie sua primeira conta em /register"
    echo "2. Faça login"
    echo "3. Execute uma busca de preços"
    echo ""
    echo "📚 Documentação completa: README.md"
    echo "🆘 Problemas? Consulte: QUICK_START.md"
    echo ""
}

# ============================================
# EXECUTAR INSTALAÇÃO
# ============================================

main() {
    detect_os
    check_root
    
    # Menu de escolha
    echo "Este script irá instalar o Booking Price Analyzer"
    read -p "Deseja continuar? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 0
    fi
    
    install_system_deps
    setup_python_env
    create_directories
    generate_secret_key
    init_database
    run_test
    choose_environment
    show_final_instructions
}

# Executar
main