"""
🌙 Moon Dev's Custom Indicators for Advanced Trading Strategy (Versão Simplificada)
Implementa a estratégia de distância MME9 com Bollinger Bands SEM pandas_ta
Built with love by Moon Dev 🚀
"""

import pandas as pd
import numpy as np
from termcolor import colored, cprint

def calculate_ema(series, period):
    """
    Calcula Exponential Moving Average (EMA) manualmente
    """
    alpha = 2 / (period + 1)
    ema = series.ewm(alpha=alpha, adjust=False).mean()
    return ema

def calculate_sma(series, period):
    """
    Calcula Simple Moving Average (SMA) manualmente
    """
    return series.rolling(window=period).mean()

def calculate_bollinger_bands(series, period=20, std_dev=2):
    """
    Calcula Bollinger Bands manualmente
    """
    sma = calculate_sma(series, period)
    std = series.rolling(window=period).std()
    
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    
    return upper_band, sma, lower_band

def calculate_distance_mme9(df):
    """
    Calcula a distância entre o preço de fechamento e a MME de 9 períodos
    """
    try:
        # Calcular MME9
        df['MME9'] = calculate_ema(df['close'], 9)
        
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
            cprint("⚠️ Calculando distância MME9 primeiro...", "yellow")
            df = calculate_distance_mme9(df)
        
        # Calcular Bollinger Bands na distância
        upper, middle, lower = calculate_bollinger_bands(
            df['distanciaMME9_pct'], 
            period=period, 
            std_dev=std_dev
        )
        
        df['BB_upper'] = upper
        df['BB_middle'] = middle
        df['BB_lower'] = lower
        
        cprint(f"✅ Bollinger Bands ({period}, {std_dev}) aplicadas na distância!", "white", "on_green")
        return df
        
    except Exception as e:
        cprint(f"❌ Erro ao calcular Bollinger Bands: {str(e)}", "white", "on_red")
        return df

def generate_signals(df):
    """
    Gera sinais de compra/venda baseados na estratégia
    """
    try:
        # Inicializar colunas de sinais
        df['signal'] = 0
        df['signal_type'] = 'HOLD'
        df['signal_strength'] = 0.0
        
        # Condições para sinais
        buy_condition = df['distanciaMME9_pct'] < df['BB_lower']  # Abaixo da banda inferior
        sell_condition = df['distanciaMME9_pct'] > df['BB_upper']  # Acima da banda superior
        
        # Aplicar sinais
        df.loc[buy_condition, 'signal'] = 1
        df.loc[buy_condition, 'signal_type'] = 'BUY'
        
        df.loc[sell_condition, 'signal'] = -1
        df.loc[sell_condition, 'signal_type'] = 'SELL'
        
        # Calcular força do sinal (distância das bandas)
        df.loc[buy_condition, 'signal_strength'] = abs(
            (df.loc[buy_condition, 'distanciaMME9_pct'] - df.loc[buy_condition, 'BB_lower']) / 
            df.loc[buy_condition, 'BB_lower']
        )
        
        df.loc[sell_condition, 'signal_strength'] = abs(
            (df.loc[sell_condition, 'distanciaMME9_pct'] - df.loc[sell_condition, 'BB_upper']) / 
            df.loc[sell_condition, 'BB_upper']
        )
        
        # Contar sinais
        buy_signals = len(df[df['signal'] == 1])
        sell_signals = len(df[df['signal'] == -1])
        
        cprint(f"✅ Sinais gerados: {buy_signals} BUY, {sell_signals} SELL", "white", "on_green")
        return df
        
    except Exception as e:
        cprint(f"❌ Erro ao gerar sinais: {str(e)}", "white", "on_red")
        return df

def analyze_strategy_performance(df):
    """
    Analisa a performance da estratégia
    """
    try:
        if 'signal' not in df.columns:
            cprint("⚠️ Gerando sinais primeiro...", "yellow")
            df = generate_signals(df)
        
        # Estatísticas básicas
        total_signals = len(df[df['signal'] != 0])
        buy_signals = len(df[df['signal'] == 1])
        sell_signals = len(df[df['signal'] == -1])
        
        # Calcular retornos simulados (simplificado)
        df['returns'] = df['close'].pct_change()
        df['strategy_returns'] = df['signal'].shift(1) * df['returns']
        
        # Métricas de performance
        total_return = (df['strategy_returns'] + 1).prod() - 1
        win_rate = len(df[df['strategy_returns'] > 0]) / len(df[df['strategy_returns'] != 0]) if total_signals > 0 else 0
        
        # Relatório
        performance = {
            'total_signals': total_signals,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'total_return': total_return * 100,
            'win_rate': win_rate * 100,
            'avg_signal_strength': df[df['signal'] != 0]['signal_strength'].mean() if total_signals > 0 else 0
        }
        
        cprint("\n📊 ANÁLISE DE PERFORMANCE DA ESTRATÉGIA", "white", "on_blue")
        cprint(f"🎯 Total de Sinais: {performance['total_signals']}", "cyan")
        cprint(f"📈 Sinais de Compra: {performance['buy_signals']}", "green")
        cprint(f"📉 Sinais de Venda: {performance['sell_signals']}", "red")
        cprint(f"💰 Retorno Total: {performance['total_return']:.2f}%", "yellow")
        cprint(f"🎲 Taxa de Acerto: {performance['win_rate']:.2f}%", "magenta")
        cprint(f"💪 Força Média dos Sinais: {performance['avg_signal_strength']:.4f}", "white")
        
        return df, performance
        
    except Exception as e:
        cprint(f"❌ Erro na análise de performance: {str(e)}", "white", "on_red")
        return df, {}

def run_complete_analysis(df):
    """
    Executa análise completa da estratégia
    """
    cprint("\n🌙 INICIANDO ANÁLISE COMPLETA DA ESTRATÉGIA MOON DEV", "white", "on_blue")
    cprint("=" * 60, "blue")
    
    # Passo 1: Calcular distância MME9
    cprint("\n📊 Passo 1: Calculando distância MME9...", "cyan")
    df = calculate_distance_mme9(df)
    
    # Passo 2: Aplicar Bollinger Bands
    cprint("\n📊 Passo 2: Aplicando Bollinger Bands (200, 2)...", "cyan")
    df = calculate_bollinger_on_distance(df, period=200, std_dev=2)
    
    # Passo 3: Gerar sinais
    cprint("\n📊 Passo 3: Gerando sinais de trading...", "cyan")
    df = generate_signals(df)
    
    # Passo 4: Analisar performance
    cprint("\n📊 Passo 4: Analisando performance...", "cyan")
    df, performance = analyze_strategy_performance(df)
    
    cprint("\n🎉 ANÁLISE COMPLETA FINALIZADA!", "white", "on_green")
    cprint("=" * 60, "green")
    
    return df, performance

# Função de compatibilidade para manter a interface original
def moon_dev_strategy_analysis(df):
    """
    Função principal para análise da estratégia Moon Dev
    Mantém compatibilidade com código existente
    """
    return run_complete_analysis(df)