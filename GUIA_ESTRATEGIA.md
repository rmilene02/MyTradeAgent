# 🎯 Guia da Estratégia Distância MME9 + Bollinger Bands

## 📋 Resumo da Estratégia

Sua estratégia implementada usa:

1. **Indicador Principal**: Distância entre preço e MME9 (em %)
2. **Filtro**: Bollinger Bands de 200 períodos (desvio 2) aplicadas na distância
3. **Sinais**:
   - **COMPRA**: Quando distância < banda inferior E há reversão
   - **VENDA**: Quando distância > banda superior E há reversão
4. **Gestão**: IA DeepSeek decide stops e alvos baseado em suporte/resistência

## 🚀 Como Usar

### 1. Instalação
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite o .env com suas chaves de API
```

**📝 Como obter as chaves de API:**
- **DeepSeek**: Acesse https://platform.deepseek.com/ → Crie conta → API Keys
- **Birdeye**: Acesse https://birdeye.so/ → Registre-se → Obtenha API key gratuita

### 2. Testar a Estratégia (SEM EXECUTAR TRADES)
```bash
# Teste completo
python test_strategy.py

# Opções disponíveis:
# 1. Testar todos os tokens em tempo real
# 2. Testar um token específico  
# 3. Backtest histórico
```

### 3. Executar o Sistema Completo (COM TRADES REAIS)
```bash
python src/main.py
```

## 📊 Interpretando os Resultados

### Sinais da Estratégia:
- **🟢 SINAL DE COMPRA**: `reversao_alta = True`
- **🔴 SINAL DE VENDA**: `reversao_baixa = True`
- **⏳ AGUARDAR**: Em exaustão mas sem reversão
- **😐 NEUTRO**: Sem sinais claros

### Indicadores Principais:
- **distanciaMME9_pct**: Distância do preço à MME9 em %
- **BB_Upper/BB_Lower**: Bandas de Bollinger
- **BB_Position**: Posição relativa (0=banda inferior, 1=banda superior)

## ⚙️ Configurações Personalizáveis

No arquivo `src/core/config.py`:

```python
# Estratégia
STRATEGY_MME_PERIOD = 9        # Período da MME
STRATEGY_BB_PERIOD = 200       # Período Bollinger Bands  
STRATEGY_BB_STD = 2           # Desvio padrão BB
DAYSBACK_4_DATA = 10          # Dias de dados históricos
DATA_TIMEFRAME = '3m'         # Timeframe (1m, 3m, 5m, 15m, etc)

# Trading
usd_size = 10                 # Tamanho da posição em USD
CASH_PERCENTAGE = 20          # % manter em cash
MAX_POSITION_PERCENTAGE = 30  # % máximo por posição
```

## 🎯 Exemplo de Análise

```
=== ESTRATÉGIA DISTÂNCIA MME9 + BOLLINGER BANDS ===

📊 DADOS ATUAIS:
- Preço Atual: $0.001234
- MME9: $0.001200  
- Distância MME9: 2.83%

🎯 BOLLINGER BANDS (200, 2):
- Banda Superior: 4.50%
- Banda Inferior: -3.20%
- Posição nas Bandas: 0.65

⚡ SINAIS DE EXAUSTÃO:
- Exaustão Alta (Venda): NÃO
- Exaustão Baixa (Compra): NÃO  
- Reversão para Baixa: NÃO
- Reversão para Cima: SIM ← SINAL DE COMPRA!

🎲 RECOMENDAÇÃO: 🟢 SINAL DE COMPRA
```

## 🛡️ Gestão de Risco

A IA automaticamente:
- Define stops baseados nos máximos/mínimos dos candles de reversão
- Calcula alvos usando níveis de suporte/resistência
- Mantém ratio risco/retorno mínimo de 1:2
- Limita posições a 30% do portfólio
- Mantém 20% em cash como buffer

## 📈 Backtesting

Use o teste para validar:
```bash
python test_strategy.py
# Escolha opção 3 para backtest
```

Métricas importantes:
- Frequência de sinais
- Distribuição temporal
- Últimos sinais gerados

## ⚠️ Avisos Importantes

1. **SEMPRE teste primeiro** com `test_strategy.py`
2. **Comece com valores pequenos** (`usd_size = 1`)
3. **Monitore os resultados** constantemente
4. **A estratégia funciona melhor em mercados com volatilidade**
5. **Não é garantia de lucro** - trading envolve risco

## 🔧 Troubleshooting

### Erro "Dados insuficientes":
- Aumente `DAYSBACK_4_DATA` para 15-20 dias
- Use timeframe maior (5m, 15m)

### Poucos sinais:
- Ajuste `STRATEGY_BB_STD` (tente 1.5 ou 2.5)
- Mude timeframe

### Muitos sinais falsos:
- Aumente `STRATEGY_MIN_EXHAUSTION_PERIODS`
- Use timeframe maior

## 📞 Suporte

Para dúvidas sobre a implementação, verifique:
1. Logs do sistema
2. Arquivo `test_strategy.py` para debug
3. Configurações em `config.py`

---
*Estratégia implementada com ❤️ por Moon Dev*