# 🚀 Guia de Início Rápido - 5 Minutos

## Para Teste Local (Desenvolvimento)

### 1️⃣ Preparação (2 minutos)
```bash
# Clone ou descompacte os arquivos
cd booking-analyzer

# Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate no Windows

# Instale dependências
pip install -r requirements.txt
```

### 2️⃣ Primeira Execução (1 minuto)
```bash
# Execute
python app.py

# Abra no navegador
http://localhost:5000
```

### 3️⃣ Use a Aplicação (2 minutos)
1. Clique em "Registre-se aqui"
2. Crie sua conta (usuário, email, senha)
3. Faça login
4. Configure uma busca:
   - Check-in: amanhã
   - Check-out: depois de amanhã
   - Adultos: 2
   - Crianças: 0
   - Quartos: 1
5. Clique em "Buscar Preços"
6. Aguarde 5-10 minutos

✅ **Pronto! Você verá o dashboard com gráficos e análises.**

---

## Para Deploy em Servidor (Produção)

### Opção A: VPS/Cloud (Ubuntu/Debian)

```bash
# 1. Conecte ao servidor via SSH
ssh usuario@seu-servidor.com

# 2. Instale dependências do sistema
sudo apt update
sudo apt install -y python3-pip python3-venv nginx git

# 3. Instale Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

# 4. Clone o projeto
cd /var/www
sudo mkdir booking-analyzer
sudo chown $USER:$USER booking-analyzer
cd booking-analyzer
git clone <seu-repositorio> .

# 5. Configure Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Gere chave secreta
python3 -c "import secrets; print(secrets.token_hex(32))"
# Copie o resultado e cole em app.py na linha SECRET_KEY

# 7. Teste local
python app.py
# Se funcionar, pressione Ctrl+C

# 8. Configure systemd
sudo nano /etc/systemd/system/booking-analyzer.service
```

Cole este conteúdo:
```ini
[Unit]
Description=Booking Analyzer
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

```bash
# 9. Configure Nginx
sudo nano /etc/nginx/sites-available/booking-analyzer
```

Cole este conteúdo:
```nginx
server {
    listen 80;
    server_name seu-dominio.com;  # ALTERE AQUI

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# 10. Ative e inicie
sudo ln -s /etc/nginx/sites-available/booking-analyzer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl start booking-analyzer
sudo systemctl enable booking-analyzer

# 11. Verifique status
sudo systemctl status booking-analyzer
```

✅ **Acesse: http://seu-dominio.com**

### Opção B: Heroku (Mais Fácil)

```bash
# 1. Instale Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. No diretório do projeto
echo "web: gunicorn app:app" > Procfile
echo "python-3.11.5" > runtime.txt

# 3. Configure buildpacks
heroku login
heroku create seu-app-nome
heroku buildpacks:add --index 1 heroku/python
heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-google-chrome
heroku buildpacks:add --index 3 https://github.com/heroku/heroku-buildpack-chromedriver

# 4. Deploy
git init
git add .
git commit -m "Deploy inicial"
git push heroku main

# 5. Abra
heroku open
```

✅ **Aplicação está no ar!**

---

## 📋 Checklist Pós-Deploy

### Segurança
- [ ] Alterou SECRET_KEY para valor único
- [ ] Configurou HTTPS (Let's Encrypt)
- [ ] Configurou firewall
- [ ] Criou primeiro usuário admin

### Funcionalidade
- [ ] Testou registro de usuário
- [ ] Testou login
- [ ] Executou primeira busca
- [ ] Verificou dashboard
- [ ] Testou exportação Excel

### Manutenção
- [ ] Configurou backup automático do banco
- [ ] Configurou monitoramento de logs
- [ ] Documentou credenciais de acesso

---

## 🆘 Problemas Comuns

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "Chrome não encontrado"
```bash
# Ubuntu/Debian
sudo apt install google-chrome-stable

# Manualmente
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```

### "Porta 5000 já em uso"
```bash
# Mude a porta em app.py:
app.run(debug=True, host='0.0.0.0', port=8080)
```

### "Database locked"
```bash
# Reinicie a aplicação
sudo systemctl restart booking-analyzer
```

### "Booking.com bloqueou"
- Aguarde 24 horas
- Aumente delays em app.py
- Reduza frequência de buscas

---

## 📞 Próximos Passos

1. **Personalize hotéis**: Edite `DEFAULT_PROPERTIES` em app.py
2. **Configure SSL**: Use Certbot para HTTPS
3. **Monitore logs**: `journalctl -u booking-analyzer -f`
4. **Faça backups**: Configure cron para backup diário
5. **Otimize delays**: Ajuste conforme necessidade

---

## 💡 Dicas de Uso

### Para Melhores Resultados
- ✅ Faça buscas em horários diferentes (evite picos)
- ✅ Teste com datas variadas (próximas e futuras)
- ✅ Compare quartos similares
- ✅ Analise tendências semanais/mensais

### Para Evitar Bloqueios
- ❌ Não faça mais de 2 buscas por hora
- ❌ Não reduza os delays
- ❌ Não execute em paralelo
- ✅ Use sempre em horários comerciais

---

## 📊 Exemplo de Análise

Após executar uma busca, você verá:

1. **Estatísticas Principais**
   - Seu preço médio
   - Preço médio dos concorrentes
   - Diferença percentual
   - Total de hotéis analisados

2. **Gráficos Interativos**
   - Comparação de preços por hotel
   - Notas de avaliação
   - Distribuição de preços

3. **Tabela Detalhada**
   - Todos os quartos e preços
   - Avaliações e estrelas
   - Filtros e ordenação

4. **Exportação**
   - Download completo em Excel
   - Pronto para apresentações

---

## ✅ Está tudo funcionando?

Se chegou até aqui e tudo funcionou:
1. Faça seu primeiro backup: `cp instance/booking_analyzer.db backup.db`
2. Documente suas credenciais
3. Configure monitoramento
4. Comece a usar regularmente!

**Boa análise! 🎉**