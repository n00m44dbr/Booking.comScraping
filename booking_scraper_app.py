"""
BOOKING.COM PRICE ANALYZER - Web Application
Sistema completo de análise competitiva de preços
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import random
import os
from datetime import datetime, timedelta
from functools import wraps
import re

# ============================================
# CONFIGURAÇÃO DA APLICAÇÃO
# ============================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-super-segura-aqui-12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///booking_analyzer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ============================================
# MODELOS DO BANCO DE DADOS
# ============================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    searches = db.relationship('Search', backref='user', lazy=True)

class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    checkin = db.Column(db.String(10), nullable=False)
    checkout = db.Column(db.String(10), nullable=False)
    adults = db.Column(db.Integer, nullable=False)
    children = db.Column(db.Integer, nullable=False)
    rooms = db.Column(db.Integer, nullable=False)
    results_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============================================
# USER AGENTS ROTATIVOS
# ============================================

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

# ============================================
# PROPRIEDADES PADRÃO
# ============================================

DEFAULT_PROPERTIES = [
    {"name": "Reserva Ilhabela", "id": "4247488", "url": "reserva-ilhabela", "yours": True},
    {"name": "Ilhasol", "id": "356668", "url": "ilhasol", "yours": False},
    {"name": "Pousada Villa Nina", "id": "469569", "url": "pousada-villa-nina", "yours": False},
    {"name": "Ilhote da Prainha", "id": "342549", "url": "ilhote-da-prainha", "yours": False},
    {"name": "Villa Galileu Ilhabela", "id": "4348234", "url": "villa-galiileu-ilhabela", "yours": False},
    {"name": "Templo do Ser", "id": "4208689", "url": "templo-do-ser", "yours": False},
    {"name": "Pousada Villa da Prainha", "id": "270503", "url": "pousada-villa-da-prainha", "yours": False},
    {"name": "Mirante da Praia Grande", "id": "376105", "url": "mirante-da-praia-grande", "yours": False},
    {"name": "Pousada Refúgio da Harmonia", "id": "320275", "url": "pousada-refugio-da-harmonia", "yours": False},
    {"name": "Pousada Iguana Azul", "id": "779800", "url": "pousada-iguana-azul", "yours": False},
]

# ============================================
# DECORADOR DE AUTENTICAÇÃO
# ============================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# FUNÇÕES DE SCRAPING APRIMORADAS
# ============================================

def setup_driver():
    """Configura Selenium com proteções anti-bloqueio"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User-Agent rotativo
    user_agent = random.choice(USER_AGENTS)
    chrome_options.add_argument(f'user-agent={user_agent}')
    
    # Headers adicionais
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--no-default-browser-check')
    chrome_options.add_argument('--lang=pt-BR')
    chrome_options.add_argument('--accept-language=pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Remover indicadores de webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def random_delay(min_seconds=2, max_seconds=5):
    """Delay aleatório para parecer humano"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def extract_rating(driver):
    """Extrai nota de avaliação e número de estrelas"""
    rating_data = {
        'review_score': None,
        'review_count': None,
        'stars': None
    }
    
    try:
        # Nota de avaliação
        try:
            score_elem = driver.find_element(By.CSS_SELECTOR, '[data-testid="review-score-component"], .bui-review-score__badge')
            rating_data['review_score'] = float(score_elem.text.strip().replace(',', '.'))
        except:
            pass
        
        # Número de avaliações
        try:
            count_elem = driver.find_element(By.CSS_SELECTOR, '[data-testid="review-score-component"] + div, .bui-review-score__text')
            count_text = count_elem.text.strip()
            numbers = re.findall(r'\d+', count_text.replace('.', '').replace(',', ''))
            if numbers:
                rating_data['review_count'] = int(numbers[0])
        except:
            pass
        
        # Número de estrelas
        try:
            stars_elem = driver.find_element(By.CSS_SELECTOR, '[data-testid="rating-stars"], .bui-rating__stars')
            stars_text = stars_elem.get_attribute('aria-label') or stars_elem.text
            stars_match = re.search(r'(\d+)', stars_text)
            if stars_match:
                rating_data['stars'] = int(stars_match.group(1))
        except:
            pass
            
    except Exception as e:
        print(f"Erro ao extrair avaliações: {str(e)}")
    
    return rating_data

def extract_room_data(driver, property_info, checkin, checkout, adults, children, rooms):
    """Extrai dados dos quartos com proteções anti-bloqueio"""
    hotel_name = property_info['name']
    hotel_id = property_info['id']
    url_slug = property_info['url']
    
    # Montar URL
    url = f"https://www.booking.com/hotel/br/{url_slug}.html"
    url += f"?checkin={checkin}&checkout={checkout}"
    url += f"&group_adults={adults}&no_rooms={rooms}&group_children={children}"
    
    print(f"Processando: {hotel_name}")
    
    try:
        driver.get(url)
        random_delay(4, 7)  # Delay mais longo
        
        # Scroll suave para simular comportamento humano
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        random_delay(1, 2)
        driver.execute_script("window.scrollTo(0, 0);")
        random_delay(1, 2)
        
        # Fechar popups
        try:
            close_buttons = driver.find_elements(By.CSS_SELECTOR, '[aria-label*="Dismiss"], .bui-modal__close, button[aria-label*="Fechar"]')
            for btn in close_buttons[:2]:
                try:
                    btn.click()
                    random_delay(0.5, 1)
                except:
                    pass
        except:
            pass
        
        # Extrair avaliações
        rating_data = extract_rating(driver)
        
        # Extrair quartos
        rooms_data = []
        
        try:
            room_blocks = driver.find_elements(By.CSS_SELECTOR, '[data-block-id]')
            print(f"Encontrados {len(room_blocks)} blocos de quartos")
            
            for block in room_blocks:
                try:
                    room_name_elem = block.find_element(By.CSS_SELECTOR, '.hprt-roomtype-icon-link, .roomName, [data-room-name]')
                    room_name = room_name_elem.text.strip()
                    
                    price_elem = block.find_element(By.CSS_SELECTOR, '.bui-price-display__value, .prco-valign-middle-helper')
                    price_text = price_elem.text.strip()
                    
                    price_numbers = re.findall(r'\d+[.,]?\d*', price_text.replace('.', '').replace(',', '.'))
                    price = float(price_numbers[0]) if price_numbers else 0
                    
                    if room_name and price > 0:
                        rooms_data.append({
                            'room_type': room_name,
                            'price': price,
                            'currency': 'BRL'
                        })
                        print(f"✓ {room_name}: R$ {price:.2f}")
                except:
                    continue
        except Exception as e:
            print(f"Erro ao extrair quartos: {str(e)}")
        
        # Método alternativo se não encontrou quartos
        if len(rooms_data) == 0:
            try:
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                scripts = soup.find_all('script', {'type': 'application/ld+json'})
                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        if 'offers' in data:
                            price = data['offers'].get('price', 0)
                            if price:
                                rooms_data.append({
                                    'room_type': 'Quarto Padrão',
                                    'price': float(price),
                                    'currency': 'BRL'
                                })
                    except:
                        continue
            except:
                pass
        
        return {
            'hotel_name': hotel_name,
            'booking_id': hotel_id,
            'url': url,
            'is_yours': property_info['yours'],
            'rooms': rooms_data,
            'total_rooms': len(rooms_data),
            'rating': rating_data,
            'scraped_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Erro: {str(e)}")
        return {
            'hotel_name': hotel_name,
            'booking_id': hotel_id,
            'url': url,
            'is_yours': property_info['yours'],
            'rooms': [],
            'total_rooms': 0,
            'rating': {'review_score': None, 'review_count': None, 'stars': None},
            'error': str(e),
            'scraped_at': datetime.now().isoformat()
        }

def run_scraping(checkin, checkout, adults, children, rooms):
    """Executa o scraping completo"""
    driver = setup_driver()
    all_results = []
    
    try:
        for i, prop in enumerate(DEFAULT_PROPERTIES):
            print(f"\nProcessando {i+1}/{len(DEFAULT_PROPERTIES)}")
            result = extract_room_data(driver, prop, checkin, checkout, adults, children, rooms)
            all_results.append(result)
            
            # Delay maior entre hotéis para evitar bloqueio
            if i < len(DEFAULT_PROPERTIES) - 1:
                random_delay(5, 10)
        
        return {'success': True, 'data': all_results}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
        
    finally:
        driver.quit()

# ============================================
# ROTAS DA APLICAÇÃO
# ============================================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Usuário já existe'})
        
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email já cadastrado'})
        
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Usuário criado com sucesso'})
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'message': 'Credenciais inválidas'})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    recent_searches = Search.query.filter_by(user_id=user.id).order_by(Search.created_at.desc()).limit(5).all()
    return render_template('dashboard.html', user=user, recent_searches=recent_searches)

@app.route('/api/scrape', methods=['POST'])
@login_required
def api_scrape():
    data = request.get_json()
    
    checkin = data.get('checkin')
    checkout = data.get('checkout')
    adults = int(data.get('adults', 2))
    children = int(data.get('children', 0))
    rooms = int(data.get('rooms', 1))
    
    # Executar scraping
    results = run_scraping(checkin, checkout, adults, children, rooms)
    
    if results['success']:
        # Salvar no banco
        new_search = Search(
            user_id=session['user_id'],
            checkin=checkin,
            checkout=checkout,
            adults=adults,
            children=children,
            rooms=rooms,
            results_json=json.dumps(results['data'])
        )
        db.session.add(new_search)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'search_id': new_search.id,
            'data': results['data']
        })
    
    return jsonify({'success': False, 'error': results.get('error', 'Erro desconhecido')})

@app.route('/api/search/<int:search_id>')
@login_required
def api_get_search(search_id):
    search = Search.query.get_or_404(search_id)
    
    if search.user_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    return jsonify({
        'success': True,
        'data': json.loads(search.results_json),
        'checkin': search.checkin,
        'checkout': search.checkout,
        'adults': search.adults,
        'children': search.children,
        'rooms': search.rooms,
        'created_at': search.created_at.isoformat()
    })

@app.route('/api/export/<int:search_id>')
@login_required
def api_export(search_id):
    search = Search.query.get_or_404(search_id)
    
    if search.user_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    data = json.loads(search.results_json)
    
    # Criar DataFrame
    all_rooms = []
    for hotel in data:
        for room in hotel['rooms']:
            all_rooms.append({
                'Hotel': hotel['hotel_name'],
                'Tipo_Quarto': room['room_type'],
                'Preço_BRL': room['price'],
                'Nota_Avaliação': hotel['rating']['review_score'],
                'Num_Avaliações': hotel['rating']['review_count'],
                'Estrelas': hotel['rating']['stars'],
                'É_Seu': 'SIM' if hotel['is_yours'] else 'NÃO'
            })
    
    df = pd.DataFrame(all_rooms)
    
    # Salvar Excel temporário
    filename = f'booking_analysis_{search_id}.xlsx'
    filepath = os.path.join('/tmp', filename)
    df.to_excel(filepath, index=False)
    
    return send_file(filepath, as_attachment=True, download_name=filename)

# ============================================
# INICIALIZAÇÃO
# ============================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)