# 🌙 Moon Dev's AI Trading System

[![Moon Dev](moondev.png)](https://www.moondev.com/)

**⚠️ IMPORTANTE: Este é um projeto experimental. NÃO há garantias de lucratividade. Trading envolve risco substancial de perda.**

Sistema de trading automatizado com IA que implementa estratégias personalizadas usando DeepSeek AI e dados em tempo real.

## 🎯 Estratégia Implementada: Distância MME9 + Bollinger Bands

✅ **Sistema Completo Funcionando:**
- 📊 Indicador: Distância entre preço e MME9 (%)
- 🎯 Filtro: Bollinger Bands de 200 períodos aplicadas na distância
- 🧠 IA: DeepSeek analisa e decide stops/alvos automaticamente
- 🎮 Simuladores: Teste sem risco antes de usar dinheiro real

## 🚀 Como Começar (5 minutos)

### 1. **Configure as APIs** (2 min)
```bash
# Copie o template
cp .env.example .env

# Edite o .env com suas chaves:
# DEEPSEEK_API_KEY=sua_chave_deepseek
# BIRDEYE_API_KEY=sua_chave_birdeye
```

### 2. **Instale dependências** (1 min)
```bash
# Opção 1: Instalador automático (recomendado)
python install_dependencies.py

# Opção 2: Manual
pip install -r requirements.txt
```

### 3. **Teste o sistema** (2 min)
```bash
# Verificar APIs
python verificar_apis.py

# Testar estratégia (SEM RISCO)
python test_strategy.py

# Simulador visual
python simulador_visual.py
```

## 🎮 Simuladores Disponíveis

### 📊 **Teste Básico**
```bash
python test_strategy.py
```
- ✅ Análise de indicadores
- ✅ Sinais de compra/venda
- ✅ Backtest histórico
- ✅ Estatísticas de performance

### 🎮 **Simulador Visual**
```bash
python simulador_visual.py
```
- ✅ Gráficos ASCII em tempo real
- ✅ Simulação de P&L
- ✅ Monitor live de sinais
- ✅ Visualização das Bollinger Bands

## 📚 Documentação Completa

| Arquivo | Descrição |
|---------|-----------|
| `GUIA_API_KEYS.md` | Como obter todas as APIs necessárias |
| `GUIA_ESTRATEGIA.md` | Como usar o sistema completo |
| `GUIA_SIMULADOR.md` | Como usar os simuladores visuais |
| `TROUBLESHOOTING.md` | Solução de problemas comuns |
| `RESUMO_FINAL.md` | Resumo completo do projeto |

## 🗺️ Research Roadmap

### 1. Risk Control Agents
Exploring AI agents that could assist with risk management. This is purely experimental research into risk oversight possibilities.

### 2. Exit Agents
Researching potential exit timing assistance. This overlaps with risk management research but focuses on position management concepts.

### 3. Entry Agents
Investigating entry-focused concepts after risk management research.

### 4. Sentiment Collection Agents
Exploring ways to gather market sentiment from Twitter, Discord, and Telegram for research purposes.

### 5. Strategy Execution Agents
Researching concepts like:
- Multi-agent consensus
- Strategy validation
- Dynamic trade filtering

## ⚠️ Critical Disclaimers

**PLEASE READ CAREFULLY:**

1. This is an experimental research project, NOT a trading system
2. There are NO plug-and-play solutions for guaranteed profits
3. We do NOT provide trading strategies
4. Success depends entirely on YOUR:
   - Trading strategy
   - Risk management
   - Market research
   - Testing and validation
   - Overall trading approach

5. NO AI agent can guarantee profitable trading
6. You MUST develop and validate your own trading approach
7. Trading involves substantial risk of loss
8. Past performance does not indicate future results

## 👂 Looking for Updates?
Project updates will be posted on [moondev.com](http://moondev.com) in the AI Agents for Trading Section.

## 📜 Detailed Disclaimer
The content presented is for educational and informational purposes only and does not constitute financial advice. All trading involves risk and may not be suitable for all investors. You should carefully consider your investment objectives, level of experience, and risk appetite before investing.

Past performance is not indicative of future results. There is no guarantee that any trading strategy or algorithm discussed will result in profits or will not incur losses.

**CFTC Disclaimer:** Commodity Futures Trading Commission (CFTC) regulations require disclosure of the risks associated with trading commodities and derivatives. There is a substantial risk of loss in trading and investing.

I am not a licensed financial advisor or a registered broker-dealer. Content & code is based on personal research perspectives and should not be relied upon as a guarantee of success in trading.

## 🔗 Links
- Trading Education: [https://algotradecamp.com](https://algotradecamp.com)
- Business

---
*Built with love by Moon Dev - Pioneering the future of AI-powered trading*

