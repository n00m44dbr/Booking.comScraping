# ============================================
# BOOKING ANALYZER - CONFIGURAÇÃO DE AMBIENTE
# ============================================
# Copie este arquivo para .env e preencha os valores

# Ambiente (development, production, testing)
FLASK_ENV=development

# Chave secreta - GERE UMA NOVA EM PRODUÇÃO
# Use: python3 -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=sua-chave-secreta-super-segura-aqui-12345

# Banco de Dados
# SQLite (desenvolvimento):
DATABASE_URL=sqlite:///booking_analyzer.db

# PostgreSQL (produção - recomendado):
# DATABASE_URL=postgresql://usuario:senha@localhost:5432/booking_analyzer

# MySQL (alternativa):
# DATABASE_URL=mysql+pymysql://usuario:senha@localhost:3306/booking_analyzer

# ============================================
# CONFIGURAÇÕES DE SCRAPING
# ============================================

# Delays entre requisições (em segundos)
SCRAPING_MIN_DELAY=3
SCRAPING_MAX_DELAY=8
SCRAPING_BETWEEN_HOTELS_MIN=5
SCRAPING_BETWEEN_HOTELS_MAX=10

# Limites de uso
MAX_SEARCHES_PER_HOUR=2
MAX_SEARCHES_PER_DAY=10

# ============================================
# CONFIGURAÇÕES DE SEGURANÇA
# ============================================

# Session timeout (em dias)
SESSION_LIFETIME_DAYS=7

# HTTPS (True em produção)
SESSION_COOKIE_SECURE=False

# ============================================
# CONFIGURAÇÕES DE PROXY (Opcional)
# ============================================
# Descomente para usar proxies

# PROXY_ENABLED=False
# PROXY_HTTP=http://proxy-server:port
# PROXY_HTTPS=https://proxy-server:port

# Lista de proxies rotativos (separados por vírgula)
# PROXY_LIST=http://proxy1:port,http://proxy2:port,http://proxy3:port

# ============================================
# CONFIGURAÇÕES DE EMAIL (Para notificações - Opcional)
# ============================================

# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=seu-email@gmail.com
# SMTP_PASSWORD=sua-senha-de-app
# SMTP_USE_TLS=True

# ============================================
# CONFIGURAÇÕES DE LOGGING
# ============================================

# Nível de log (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Arquivo de log
LOG_FILE=logs/booking_analyzer.log

# ============================================
# CONFIGURAÇÕES ESPECÍFICAS POR PLATAFORMA
# ============================================

# HEROKU
# PORT=5000
# WEB_CONCURRENCY=3

# DIGITAL OCEAN
# APP_ENV=production

# AWS
# AWS_REGION=us-east-1

# GOOGLE CLOUD
# GOOGLE_CLOUD_PROJECT=seu-projeto-id

# ============================================
# CONFIGURAÇÕES DE BACKUP (Opcional)
# ============================================

# Backup automático
# BACKUP_ENABLED=True
# BACKUP_INTERVAL_HOURS=24
# BACKUP_RETENTION_DAYS=30
# BACKUP_PATH=/var/backups/booking-analyzer

# ============================================
# CONFIGURAÇÕES DE CACHE (Opcional - Para performance)
# ============================================

# Redis (recomendado para produção)
# REDIS_URL=redis://localhost:6379/0
# CACHE_TYPE=redis
# CACHE_DEFAULT_TIMEOUT=300

# ============================================
# CONFIGURAÇÕES DE MONITORAMENTO (Opcional)
# ============================================

# Sentry (para tracking de erros)
# SENTRY_DSN=https://sua-key@sentry.io/seu-projeto

# Google Analytics
# GOOGLE_ANALYTICS_ID=UA-XXXXXXXXX-X

# ============================================
# CONFIGURAÇÕES AVANÇADAS
# ============================================

# Workers do Gunicorn
WORKERS=3
WORKER_TIMEOUT=300

# Debug mode (NUNCA usar True em produção)
DEBUG=False

# Tamanho máximo de upload (em MB)
MAX_CONTENT_LENGTH=16