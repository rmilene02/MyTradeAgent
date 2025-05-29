# 🚀 INSTALAÇÃO RÁPIDA - MyTradeAgent

## ⚡ Instalação Automática (Recomendada)

```bash
# 1. Clone o repositório
git clone https://github.com/rmilene02/MyTradeAgent.git
cd MyTradeAgent

# 2. Execute o instalador automático
python install_dependencies.py
```

## 🛠️ Instalação Manual (Se a automática falhar)

```bash
# 1. Instalar dependências básicas
pip install --upgrade pip
pip install setuptools>=65.0.0 wheel>=0.37.0 packaging>=21.0

# 2. Instalar versões compatíveis
pip install numpy>=1.21.0,<1.25.0
pip install pandas>=1.5.0,<2.0.0
pip install openai>=1.0.0
pip install requests>=2.28.0
pip install python-dotenv>=0.19.0
pip install termcolor>=1.1.0
```

## 🧪 Teste Rápido

```bash
# Testar se tudo está funcionando
python -c "
from src.data.custom_indicators_simple import *
import pandas as pd
import numpy as np
print('✅ Tudo funcionando!')
"
```

## 🎮 Executar Simuladores

```bash
# Simulador visual (recomendado para iniciantes)
python simulador_visual.py

# Teste de estratégia
python test_strategy.py

# Verificar APIs
python verificar_apis.py
```

## 🔑 Configurar APIs

1. Copie o arquivo `.env.example` para `.env`
2. Adicione suas chaves de API:
   - **DeepSeek API**: Para análise de IA
   - **Birdeye API**: Para dados de mercado

## 📚 Próximos Passos

1. Leia o `GUIA_ESTRATEGIA.md` para entender a estratégia
2. Configure suas APIs no arquivo `.env`
3. Execute os simuladores para testar
4. Personalize a estratégia conforme necessário

## ❓ Problemas?

- Consulte `TROUBLESHOOTING.md` para soluções
- Verifique se está usando Python 3.8+
- Use a versão simplificada se houver problemas com pandas_ta

## 🌙 Moon Dev Strategy

Esta implementação usa:
- **Distância MME9**: Diferença entre preço e média móvel exponencial de 9 períodos
- **Bollinger Bands**: Aplicadas na distância (período 200, desvio 2)
- **Sinais**: Compra quando abaixo da banda inferior, venda quando acima da superior
- **IA**: DeepSeek API para análise e decisões de stop/target