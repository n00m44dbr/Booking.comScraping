"""
Arquivo de configuração para diferentes ambientes
"""
import os
from datetime import timedelta

class Config:
    """Configuração base"""
    # Chave secreta - ALTERE EM PRODUÇÃO
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-super-segura-aqui-12345'
    
    # Banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///booking_analyzer.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Sessão
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True  # Usar apenas com HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload e limites
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    
    # Scraping - Configurações de proteção
    SCRAPING_MIN_DELAY = 3  # segundos
    SCRAPING_MAX_DELAY = 8  # segundos
    SCRAPING_BETWEEN_HOTELS_MIN = 5  # segundos
    SCRAPING_BETWEEN_HOTELS_MAX = 10  # segundos
    
    # Limites de uso
    MAX_SEARCHES_PER_HOUR = 2
    MAX_SEARCHES_PER_DAY = 10


class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False  # Permite HTTP em desenvolvimento
    
    # Delays menores para desenvolvimento
    SCRAPING_MIN_DELAY = 2
    SCRAPING_MAX_DELAY = 4
    SCRAPING_BETWEEN_HOTELS_MIN = 3
    SCRAPING_BETWEEN_HOTELS_MAX = 5


class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    TESTING = False
    
    # Forçar HTTPS
    SESSION_COOKIE_SECURE = True
    
    # Delays maiores em produção (mais seguro)
    SCRAPING_MIN_DELAY = 4
    SCRAPING_MAX_DELAY = 10
    SCRAPING_BETWEEN_HOTELS_MIN = 8
    SCRAPING_BETWEEN_HOTELS_MAX = 15
    
    # PostgreSQL recomendado em produção
    # Exemplo: postgresql://usuario:senha@localhost/booking_analyzer
    if os.environ.get('DATABASE_URL'):
        # Fix para Heroku (muda postgres:// para postgresql://)
        uri = os.environ.get('DATABASE_URL')
        if uri and uri.startswith('postgres://'):
            uri = uri.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = uri


class TestingConfig(Config):
    """Configuração para testes"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


# Configurações específicas por plataforma de hosting
class HerokuConfig(ProductionConfig):
    """Configuração otimizada para Heroku"""
    # Heroku usa variáveis de ambiente
    pass


class DigitalOceanConfig(ProductionConfig):
    """Configuração otimizada para DigitalOcean"""
    # DigitalOcean App Platform
    pass


class AWSConfig(ProductionConfig):
    """Configuração otimizada para AWS"""
    # AWS Elastic Beanstalk
    pass


class GoogleCloudConfig(ProductionConfig):
    """Configuração otimizada para Google Cloud"""
    # Google App Engine
    pass


# Lista de hotéis competidores - PERSONALIZE AQUI
DEFAULT_PROPERTIES = [
    {
        "name": "Reserva Ilhabela",
        "id": "4247488",
        "url": "reserva-ilhabela",
        "yours": True
    },
    {
        "name": "Ilhasol",
        "id": "356668",
        "url": "ilhasol",
        "yours": False
    },
    {
        "name": "Pousada Villa Nina",
        "id": "469569",
        "url": "pousada-villa-nina",
        "yours": False
    },
    {
        "name": "Ilhote da Prainha",
        "id": "342549",
        "url": "ilhote-da-prainha",
        "yours": False
    },
    {
        "name": "Villa Galileu Ilhabela",
        "id": "4348234",
        "url": "villa-galiileu-ilhabela",
        "yours": False
    },
    {
        "name": "Templo do Ser",
        "id": "4208689",
        "url": "templo-do-ser",
        "yours": False
    },
    {
        "name": "Pousada Villa da Prainha",
        "id": "270503",
        "url": "pousada-villa-da-prainha",
        "yours": False
    },
    {
        "name": "Mirante da Praia Grande",
        "id": "376105",
        "url": "mirante-da-praia-grande",
        "yours": False
    },
    {
        "name": "Pousada Refúgio da Harmonia",
        "id": "320275",
        "url": "pousada-refugio-da-harmonia",
        "yours": False
    },
    {
        "name": "Pousada Iguana Azul",
        "id": "779800",
        "url": "pousada-iguana-azul",
        "yours": False
    },
]


# User Agents para rotação
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
]


# Função auxiliar para obter configuração
def get_config():
    """Retorna a configuração baseada na variável de ambiente FLASK_ENV"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])


# Função para adicionar/remover hotéis dinamicamente
def add_property(name, booking_id, url_slug, is_yours=False):
    """
    Adiciona um hotel à lista de propriedades
    
    Args:
        name: Nome do hotel
        booking_id: ID do Booking.com
        url_slug: Slug da URL (ex: 'nome-do-hotel')
        is_yours: True se for seu hotel
    """
    property_data = {
        "name": name,
        "id": booking_id,
        "url": url_slug,
        "yours": is_yours
    }
    DEFAULT_PROPERTIES.append(property_data)
    return property_data


def remove_property(name):
    """
    Remove um hotel da lista
    
    Args:
        name: Nome do hotel a remover
    """
    global DEFAULT_PROPERTIES
    DEFAULT_PROPERTIES = [p for p in DEFAULT_PROPERTIES if p['name'] != name]


# Exemplo de uso:
# Para adicionar um novo hotel:
# from config import add_property
# add_property("Novo Hotel", "123456", "novo-hotel", False)

# Para encontrar o ID e URL de um hotel no Booking.com:
# 1. Acesse o hotel no Booking.com
# 2. Na URL, você verá algo como:
#    https://www.booking.com/hotel/br/nome-do-hotel.html?...
#    - URL slug: "nome-do-hotel"
# 3. Procure no HTML da página por "hotel_id" ou inspecione o código
#    - Ou use: view-source:https://www.booking.com/hotel/br/nome-do-hotel.html
#    - Procure por "hotel_id":