# 🔧 Guia de Solução de Problemas

## ❌ Erro: "ModuleNotFoundError: No module named 'pkg_resources'"

### 🎯 **Solução Rápida:**
```bash
# 1. Instalar setuptools
pip install --upgrade setuptools wheel

# 2. Reinstalar dependências
pip install -r requirements.txt

# 3. OU usar o instalador automático
python install_dependencies.py
```

### 🔍 **Causa:**
- Python 3.13+ removeu `pkg_resources` do setuptools padrão
- Algumas bibliotecas ainda dependem dele

### 💡 **Soluções Alternativas:**

#### **Opção 1: Instalador Automático**
```bash
python install_dependencies.py
```

#### **Opção 2: Manual Passo a Passo**
```bash
# 1. Atualizar pip
pip install --upgrade pip

# 2. Instalar setuptools
pip install setuptools>=65.0.0 wheel>=0.37.0

# 3. Instalar packaging
pip install packaging>=21.0

# 4. Instalar dependências
pip install -r requirements.txt
```

#### **Opção 3: Ambiente Virtual Limpo**
```bash
# 1. Criar novo ambiente
python -m venv .venv_new

# 2. Ativar
source .venv_new/bin/activate  # Linux/Mac
# OU
.venv_new\Scripts\activate     # Windows

# 3. Instalar
python install_dependencies.py
```

---

## ❌ Erro: "API Key not found" ou "Authentication failed"

### 🎯 **Solução:**
```bash
# 1. Verificar arquivo .env
ls -la .env

# 2. Se não existir, criar:
cp .env.example .env

# 3. Editar com suas chaves:
nano .env  # ou seu editor preferido

# 4. Verificar configuração:
python verificar_apis.py
```

### 📝 **Formato correto do .env:**
```bash
# DeepSeek AI (Obrigatório)
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Birdeye API (Obrigatório)
BIRDEYE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Solana (Opcional)
SOLANA_PRIVATE_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
```

---

## ❌ Erro: "Dados insuficientes" ou "Token not found"

### 🎯 **Possíveis Causas:**
1. **Token com pouco volume**
2. **API rate limit**
3. **Token não listado na Birdeye**

### 💡 **Soluções:**

#### **1. Testar Token Diferente:**
```python
# Edite src/core/config.py
MONITORED_TOKENS = [
    "So11111111111111111111111111111111111111112",  # SOL
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    # Adicione outros tokens líquidos
]
```

#### **2. Verificar Rate Limits:**
```bash
# Aguardar 1 minuto entre testes
python test_strategy.py
# Aguardar...
python test_strategy.py
```

#### **3. Aumentar Período de Dados:**
```python
# Em test_strategy.py, linha 23:
data = collect_token_data(token, days_back=30, timeframe='15m')  # Era 10
```

---

## ❌ Erro: "Connection timeout" ou "Network error"

### 🎯 **Soluções:**

#### **1. Verificar Conexão:**
```bash
# Testar conectividade
ping google.com
curl -I https://public-api.birdeye.so
```

#### **2. Configurar Proxy (se necessário):**
```bash
export https_proxy=http://seu-proxy:porta
export http_proxy=http://seu-proxy:porta
```

#### **3. Aumentar Timeout:**
```python
# Em src/data/ohlcv_collector.py, adicionar:
import requests
requests.adapters.DEFAULT_RETRIES = 3
```

---

## ❌ Erro: "Permission denied" ou "Access denied"

### 🎯 **Soluções:**

#### **1. Verificar Permissões:**
```bash
# Linux/Mac
chmod +x *.py
chmod 644 .env

# Verificar proprietário
ls -la
```

#### **2. Executar como Usuário:**
```bash
# Não usar sudo para instalar pacotes Python
pip install --user -r requirements.txt
```

---

## ❌ Erro: "Import error" ou "Module not found"

### 🎯 **Diagnóstico:**
```bash
# 1. Verificar instalação
pip list | grep pandas
pip list | grep openai

# 2. Verificar Python path
python -c "import sys; print(sys.path)"

# 3. Reinstalar problema específico
pip uninstall pandas-ta
pip install pandas-ta
```

### 💡 **Solução Completa:**
```bash
# 1. Limpar cache
pip cache purge

# 2. Reinstalar tudo
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# 3. OU usar instalador
python install_dependencies.py
```

---

## ❌ Erro: "JSON decode error" ou "API response error"

### 🎯 **Causas Comuns:**
1. **API key inválida**
2. **Rate limit excedido**
3. **Serviço temporariamente indisponível**

### 💡 **Soluções:**

#### **1. Verificar API Keys:**
```bash
python verificar_apis.py
```

#### **2. Aguardar Rate Limit:**
```bash
# Aguardar 1-5 minutos
sleep 300
python test_strategy.py
```

#### **3. Verificar Status dos Serviços:**
- DeepSeek: https://platform.deepseek.com/
- Birdeye: https://birdeye.so/

---

## 🐛 Debug Avançado

### **1. Modo Verbose:**
```bash
# Adicionar debug nos scripts
python -v test_strategy.py
```

### **2. Logs Detalhados:**
```python
# Adicionar no início dos scripts:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### **3. Testar Componentes Isoladamente:**
```python
# Testar só a coleta de dados:
from src.data.ohlcv_collector import collect_token_data
data = collect_token_data("So11111111111111111111111111111111111111112", days_back=1, timeframe='1h')
print(data)
```

---

## 📞 Suporte

### **1. Verificação Sistemática:**
```bash
# Execute em ordem:
python --version
pip --version
python install_dependencies.py
python verificar_apis.py
python test_strategy.py
```

### **2. Informações para Suporte:**
- Sistema operacional
- Versão do Python
- Saída do `pip list`
- Mensagem de erro completa
- Arquivo .env (SEM as chaves)

### **3. Logs Úteis:**
```bash
# Salvar logs para análise
python test_strategy.py > debug.log 2>&1
cat debug.log
```

---

## ✅ Checklist de Verificação

- [ ] Python 3.8+ instalado
- [ ] Ambiente virtual ativado
- [ ] Dependências instaladas (`pip list`)
- [ ] Arquivo .env configurado
- [ ] APIs verificadas (`python verificar_apis.py`)
- [ ] Conexão com internet funcionando
- [ ] Permissões de arquivo corretas

---

**🔧 Se nenhuma solução funcionou, execute:**
```bash
python install_dependencies.py
python verificar_apis.py
```

**E consulte os logs para mais detalhes!**