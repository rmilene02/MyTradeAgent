# 🔑 Guia Completo das API Keys

## 📋 APIs Necessárias e Suas Funções

### 1. 🧠 **DeepSeek API** (OBRIGATÓRIA)
**Para que serve:** Inteligência Artificial que analisa os dados e toma decisões de trading

**Função no código:**
- Analisa indicadores técnicos da sua estratégia
- Decide quando comprar/vender baseado nos sinais
- Calcula stops e alvos automaticamente
- Gerencia alocação de portfólio

**Como obter:**
1. Acesse: https://platform.deepseek.com/
2. Clique em "Sign Up" (Cadastrar)
3. Confirme email
4. Vá em "API Keys" no painel
5. Clique "Create API Key"
6. Copie a chave gerada

**Custo:** 
- Muito barato (~$0.14 por 1M tokens de input)
- Para trading: ~$1-5 por mês de uso normal

---

### 2. 📊 **Birdeye API** (OBRIGATÓRIA)
**Para que serve:** Fornece dados de mercado em tempo real (preços, volume, etc.)

**Função no código:**
- Coleta dados OHLCV (Open, High, Low, Close, Volume)
- Fornece preços atuais dos tokens
- Histórico de preços para calcular indicadores
- Dados necessários para sua estratégia MME9 + Bollinger

**Como obter:**
1. Acesse: https://birdeye.so/
2. Clique em "API" no menu superior
3. Clique "Get Started" 
4. Faça cadastro
5. Vá em "Dashboard" → "API Keys"
6. Copie sua API key

**Custo:**
- Plano gratuito: 1000 requests/dia
- Plano pago: $49/mês para uso profissional

---

### 3. 🔐 **Solana Private Key** (OPCIONAL - só para trades reais)
**Para que serve:** Executar transações na blockchain Solana

**Função no código:**
- Executar compras e vendas reais
- Assinar transações
- Interagir com DEXs (Jupiter, Raydium, etc.)

**Como obter:**
1. **Phantom Wallet:**
   - Instale extensão Phantom
   - Crie carteira
   - Vá em Configurações → "Export Private Key"

2. **Solflare Wallet:**
   - Instale Solflare
   - Crie carteira
   - Exporte chave privada

3. **Comando (avançado):**
   ```bash
   solana-keygen new --outfile ~/my-wallet.json
   ```

**⚠️ CUIDADO:**
- NUNCA compartilhe sua chave privada
- Use carteira separada para testes
- Comece com valores pequenos

---

### 4. 🌐 **Solana RPC URL** (OPCIONAL)
**Para que serve:** Conectar com a rede Solana

**Função no código:**
- Enviar transações
- Consultar saldos
- Interagir com contratos

**Opções gratuitas:**
- `https://api.mainnet-beta.solana.com` (oficial, limitada)
- `https://rpc.ankr.com/solana` (Ankr)
- `https://solana-api.projectserum.com` (Serum)

**Opções pagas (mais rápidas):**
- **Helius:** https://helius.xyz/ (~$10/mês)
- **QuickNode:** https://quicknode.com/ (~$9/mês)
- **Alchemy:** https://alchemy.com/ (tem plano gratuito)

---

## 🎯 Configuração Passo a Passo

### 1. Crie o arquivo .env:
```bash
cp .env.example .env
```

### 2. Edite o arquivo .env:
```bash
# APIs OBRIGATÓRIAS
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
BIRDEYE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx

# OPCIONAL (só para trades reais)
SOLANA_PRIVATE_KEY=sua_chave_privada_aqui
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
```

### 3. Teste sem trades reais:
```bash
# Só precisa das 2 primeiras APIs
python test_strategy.py
```

---

## 💰 Resumo de Custos

| API | Custo Mensal | Necessária Para |
|-----|-------------|----------------|
| DeepSeek | $1-5 | IA/Análise |
| Birdeye | Grátis/49 | Dados mercado |
| Solana RPC | Grátis/10 | Trades reais |
| **TOTAL** | **$1-64** | **Sistema completo** |

---

## 🚀 Ordem de Implementação Recomendada

### **Fase 1: Teste da Estratégia (SEM RISCO)**
```bash
# Só precisa dessas 2:
DEEPSEEK_API_KEY=xxx
BIRDEYE_API_KEY=xxx

# Execute:
python test_strategy.py
```

### **Fase 2: Simulação Avançada**
- Adicione RPC URL para dados mais precisos
- Teste com valores pequenos

### **Fase 3: Trading Real**
- Adicione chave privada
- Configure carteira com poucos dólares
- Execute trades reais

---

## 🔧 Troubleshooting

### ❌ "DEEPSEEK_API_KEY not found"
- Verifique se criou o arquivo `.env`
- Confirme que a chave está correta
- Não deixe espaços antes/depois do `=`

### ❌ "Birdeye API limit exceeded"
- Você excedeu 1000 requests/dia
- Aguarde 24h ou upgrade para plano pago
- Use timeframe maior (15m ao invés de 3m)

### ❌ "Insufficient funds"
- Sua carteira não tem SOL suficiente
- Transfira SOL para pagar taxas de transação
- Mínimo ~0.01 SOL para taxas

### ❌ "RPC rate limit"
- Use RPC pago (Helius, QuickNode)
- Ou diminua frequência de requests

---

## 🛡️ Segurança

### ✅ Boas Práticas:
- Use carteira separada para trading
- Comece com $10-50 máximo
- NUNCA compartilhe chaves privadas
- Mantenha backup das chaves
- Use 2FA quando disponível

### ❌ Nunca Faça:
- Compartilhar chaves em Discord/Telegram
- Usar carteira principal para testes
- Deixar chaves em código público
- Usar APIs suspeitas/não oficiais

---

## 📞 Suporte

**Problemas com APIs:**
- DeepSeek: https://platform.deepseek.com/docs
- Birdeye: https://docs.birdeye.so/
- Solana: https://docs.solana.com/

**Dúvidas sobre o código:**
- Verifique logs em `test_strategy.py`
- Consulte `GUIA_ESTRATEGIA.md`
- Teste uma API por vez

---
*Guia criado com ❤️ por Moon Dev*