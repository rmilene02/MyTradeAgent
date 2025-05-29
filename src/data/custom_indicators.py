"""
🌙 Moon Dev's Custom Indicators for Advanced Trading Strategy
Implementa a estratégia de distância MME9 com Bollinger Bands
Built with love by Moon Dev 🚀
"""

import pandas as pd
import numpy as np
import pandas_ta as ta
from termcolor import colored, cprint

def calculate_distance_mme9(df):
    """
    Calcula a distância entre o preço de fechamento e a MME de 9 períodos
    """
    try:
        # Calcular MME9
        df['MME9'] = ta.ema(df['close'], length=9)
        
        # Calcular distância (preço - MME9)
        df['distanciaMME9'] = df['close'] - df['MME9']
        
        # Calcular distância percentual para normalizar
        df['distanciaMME9_pct'] = ((df['close'] - df['MME9']) / df['MME9']) * 100
        
        cprint("✅ Distância MME9 calculada com sucesso!", "white", "on_green")
        return df
        
    except Exception as e:
        cprint(f"❌ Erro ao calcular distância MME9: {str(e)}", "white", "on_red")
        return df

def calculate_bollinger_on_distance(df, period=200, std_dev=2):
    """
    Aplica Bollinger Bands no indicador distanciaMME9
    """
    try:
        if 'distanciaMME9_pct' not in df.columns:
            cprint("⚠️ distanciaMME9_pct não encontrado. Calculando primeiro...", "white", "on_yellow")
            df = calculate_distance_mme9(df)
        
        # Calcular Bollinger Bands na distância percentual
        bb = ta.bbands(df['distanciaMME9_pct'], length=period, std=std_dev)
        
        if bb is not None:
            df['BB_Upper'] = bb[f'BBU_{period}_{std_dev}.0']
            df['BB_Middle'] = bb[f'BBM_{period}_{std_dev}.0']
            df['BB_Lower'] = bb[f'BBL_{period}_{std_dev}.0']
            
            # Calcular posição relativa dentro das bandas
            df['BB_Position'] = (df['distanciaMME9_pct'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
            
            cprint(f"✅ Bollinger Bands ({period}, {std_dev}) aplicadas na distância MME9!", "white", "on_green")
        else:
            cprint("❌ Erro ao calcular Bollinger Bands", "white", "on_red")
            
        return df
        
    except Exception as e:
        cprint(f"❌ Erro ao calcular Bollinger Bands: {str(e)}", "white", "on_red")
        return df

def detect_exhaustion_signals(df):
    """
    Detecta sinais de exaustão baseado na estratégia:
    - Acima da banda superior = exaustão de alta (sinal de venda)
    - Abaixo da banda inferior = exaustão de baixa (sinal de compra)
    """
    try:
        # Verificar se temos os dados necessários
        required_cols = ['distanciaMME9_pct', 'BB_Upper', 'BB_Lower']
        if not all(col in df.columns for col in required_cols):
            cprint("⚠️ Dados insuficientes para detectar sinais. Calculando indicadores...", "white", "on_yellow")
            df = calculate_distance_mme9(df)
            df = calculate_bollinger_on_distance(df)
        
        # Detectar exaustão
        df['exaustao_alta'] = df['distanciaMME9_pct'] > df['BB_Upper']  # Sinal de VENDA
        df['exaustao_baixa'] = df['distanciaMME9_pct'] < df['BB_Lower']  # Sinal de COMPRA
        
        # Detectar reversões (quando sai da zona de exaustão)
        df['reversao_baixa'] = (df['exaustao_alta'].shift(1) == True) & (df['exaustao_alta'] == False)  # Era exaustão alta, agora não
        df['reversao_alta'] = (df['exaustao_baixa'].shift(1) == True) & (df['exaustao_baixa'] == False)  # Era exaustão baixa, agora não
        
        # Contar quantos períodos em exaustão
        df['periodos_exaustao_alta'] = df['exaustao_alta'].groupby((df['exaustao_alta'] != df['exaustao_alta'].shift()).cumsum()).cumsum()
        df['periodos_exaustao_baixa'] = df['exaustao_baixa'].groupby((df['exaustao_baixa'] != df['exaustao_baixa'].shift()).cumsum()).cumsum()
        
        # Status atual
        last_row = df.iloc[-1]
        
        status = "NEUTRO"
        if last_row['exaustao_alta']:
            status = f"EXAUSTÃO ALTA ({int(last_row['periodos_exaustao_alta'])} períodos)"
        elif last_row['exaustao_baixa']:
            status = f"EXAUSTÃO BAIXA ({int(last_row['periodos_exaustao_baixa'])} períodos)"
        elif last_row['reversao_baixa']:
            status = "REVERSÃO DE ALTA (Sinal de VENDA)"
        elif last_row['reversao_alta']:
            status = "REVERSÃO DE BAIXA (Sinal de COMPRA)"
            
        cprint(f"🎯 Status da estratégia: {status}", "white", "on_blue")
        
        return df
        
    except Exception as e:
        cprint(f"❌ Erro ao detectar sinais de exaustão: {str(e)}", "white", "on_red")
        return df

def calculate_support_resistance_levels(df):
    """
    Calcula níveis de suporte e resistência para auxiliar na definição de stops e alvos
    """
    try:
        # Máximos e mínimos locais (últimos 20 períodos)
        df['max_local'] = df['high'].rolling(window=20, center=True).max()
        df['min_local'] = df['low'].rolling(window=20, center=True).min()
        
        # Níveis de suporte e resistência recentes
        recent_highs = df['high'].tail(50).nlargest(3).values
        recent_lows = df['low'].tail(50).nsmallest(3).values
        
        return df, recent_highs, recent_lows
        
    except Exception as e:
        cprint(f"❌ Erro ao calcular suporte/resistência: {str(e)}", "white", "on_red")
        return df, [], []

def generate_strategy_summary(df):
    """
    Gera um resumo completo da estratégia para o AI Agent
    """
    try:
        if len(df) < 200:
            return "❌ Dados insuficientes para análise (mínimo 200 períodos para Bollinger 200)"
        
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]
        
        # Calcular todos os indicadores
        df = calculate_distance_mme9(df)
        df = calculate_bollinger_on_distance(df)
        df = detect_exhaustion_signals(df)
        df, resistance_levels, support_levels = calculate_support_resistance_levels(df)
        
        # Dados atuais
        current_price = last_row['close']
        mme9 = last_row['MME9']
        distancia_pct = last_row['distanciaMME9_pct']
        bb_upper = last_row['BB_Upper']
        bb_lower = last_row['BB_Lower']
        bb_position = last_row['BB_Position']
        
        # Sinais
        exaustao_alta = last_row['exaustao_alta']
        exaustao_baixa = last_row['exaustao_baixa']
        reversao_alta = last_row['reversao_alta']
        reversao_baixa = last_row['reversao_baixa']
        
        # Máximo do candle anterior (para stop loss)
        max_candle_anterior = prev_row['high']
        min_candle_anterior = prev_row['low']
        
        summary = f"""
=== ESTRATÉGIA DISTÂNCIA MME9 + BOLLINGER BANDS ===

📊 DADOS ATUAIS:
- Preço Atual: ${current_price:.6f}
- MME9: ${mme9:.6f}
- Distância MME9: {distancia_pct:.2f}%

🎯 BOLLINGER BANDS (200, 2):
- Banda Superior: {bb_upper:.2f}%
- Banda Inferior: {bb_lower:.2f}%
- Posição nas Bandas: {bb_position:.2f} (0=inferior, 1=superior)

⚡ SINAIS DE EXAUSTÃO:
- Exaustão Alta (Venda): {'SIM' if exaustao_alta else 'NÃO'}
- Exaustão Baixa (Compra): {'SIM' if exaustao_baixa else 'NÃO'}
- Reversão para Baixa: {'SIM' if reversao_baixa else 'NÃO'}
- Reversão para Cima: {'SIM' if reversao_alta else 'NÃO'}

🛡️ REFERÊNCIAS PARA STOP:
- Máximo Candle Anterior: ${max_candle_anterior:.6f}
- Mínimo Candle Anterior: ${min_candle_anterior:.6f}

📈 NÍVEIS TÉCNICOS:
- Resistências: {[f'${r:.6f}' for r in resistance_levels[:3]]}
- Suportes: {[f'${s:.6f}' for s in support_levels[:3]]}

🎲 RECOMENDAÇÃO ESTRATÉGIA:
"""
        
        if reversao_baixa:
            summary += "🔴 SINAL DE VENDA - Reversão após exaustão de alta detectada"
        elif reversao_alta:
            summary += "🟢 SINAL DE COMPRA - Reversão após exaustão de baixa detectada"
        elif exaustao_alta:
            summary += "⏳ AGUARDAR - Em exaustão de alta, esperar reversão para vender"
        elif exaustao_baixa:
            summary += "⏳ AGUARDAR - Em exaustão de baixa, esperar reversão para comprar"
        else:
            summary += "😐 NEUTRO - Sem sinais de exaustão ou reversão"
            
        return summary
        
    except Exception as e:
        cprint(f"❌ Erro ao gerar resumo da estratégia: {str(e)}", "white", "on_red")
        return f"❌ Erro na análise: {str(e)}"

if __name__ == "__main__":
    print("🌙 Moon Dev's Custom Indicators - Testando...")
    # Aqui você pode adicionar testes dos indicadores