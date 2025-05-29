"""
🌙 Teste com Sistema de Cache
Evita rate limiting usando dados em cache
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.custom_indicators_simple import run_complete_analysis
from termcolor import colored, cprint
import pandas as pd
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def create_sample_data():
    """Cria dados de exemplo baseados no preço real do SOL"""
    cprint("📊 Criando dados de exemplo baseados no SOL...", "cyan")
    
    # Preço base do SOL (aproximado)
    base_price = 169.0
    
    # Criar 300 períodos de 1h
    periods = 300
    dates = pd.date_range('2025-05-01', periods=periods, freq='1h')
    
    # Simular movimento realista
    import numpy as np
    np.random.seed(42)
    
    # Tendência + volatilidade
    trend = np.linspace(base_price * 0.9, base_price * 1.1, periods)
    volatility = np.random.randn(periods) * 3  # 3% volatilidade
    noise = np.random.randn(periods) * 0.5
    
    close_prices = trend + np.cumsum(volatility * 0.1) + noise
    close_prices = np.maximum(close_prices, base_price * 0.5)  # Não deixar muito baixo
    
    # Criar OHLC
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices + np.random.randn(periods) * 0.3,
        'high': close_prices + abs(np.random.randn(periods) * 0.8),
        'low': close_prices - abs(np.random.randn(periods) * 0.8),
        'close': close_prices,
        'volume': np.random.randint(100000, 1000000, periods)
    })
    
    # Garantir OHLC válido
    df['high'] = np.maximum(df['high'], np.maximum(df['open'], df['close']))
    df['low'] = np.minimum(df['low'], np.minimum(df['open'], df['close']))
    
    return df

def test_strategy_with_cache():
    """Testa estratégia com dados em cache ou simulados"""
    cprint("🌙 TESTE DA ESTRATÉGIA - VERSÃO CACHE", "white", "on_blue")
    cprint("=" * 60, "blue")
    
    # Verificar se existe cache
    cache_file = "temp_data/Sol1_latest.csv"
    
    if os.path.exists(cache_file):
        cprint("📂 Dados em cache encontrados!", "green")
        try:
            df = pd.read_csv(cache_file)
            df['timestamp'] = pd.to_datetime(df['Datetime (UTC)'])
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high', 
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            cprint(f"✅ Cache carregado: {len(df)} períodos", "green")
        except Exception as e:
            cprint(f"❌ Erro no cache: {e}", "red")
            df = create_sample_data()
    else:
        cprint("📊 Criando dados de exemplo...", "yellow")
        df = create_sample_data()
    
    if len(df) < 200:
        cprint("❌ Dados insuficientes", "red")
        return
    
    # Executar análise
    cprint(f"\n🔍 Analisando {len(df)} períodos...", "cyan")
    cprint(f"📈 Preço inicial: ${df['close'].iloc[0]:.2f}", "white")
    cprint(f"📈 Preço final: ${df['close'].iloc[-1]:.2f}", "white")
    
    try:
        df_result, performance = run_complete_analysis(df)
        
        # Mostrar resultados
        buy_signals = len(df_result[df_result['signal'] == 1])
        sell_signals = len(df_result[df_result['signal'] == -1])
        
        cprint(f"\n🎯 RESULTADOS DA ESTRATÉGIA:", "white", "on_blue")
        cprint(f"📈 Sinais de COMPRA: {buy_signals}", "green")
        cprint(f"📉 Sinais de VENDA: {sell_signals}", "red")
        cprint(f"🎯 Total de sinais: {buy_signals + sell_signals}", "yellow")
        
        # Últimos sinais
        recent_signals = df_result[df_result['signal'] != 0].tail(3)
        if len(recent_signals) > 0:
            cprint(f"\n🕐 ÚLTIMOS SINAIS:", "white", "on_blue")
            for _, signal in recent_signals.iterrows():
                signal_type = "🟢 COMPRA" if signal['signal'] == 1 else "🔴 VENDA"
                cprint(f"{signal_type} - ${signal['close']:.2f} - Força: {signal['signal_strength']:.4f}", 
                       "green" if signal['signal'] == 1 else "red")
        
        # Performance
        if buy_signals > 0 and sell_signals > 0:
            avg_buy = df_result[df_result['signal'] == 1]['close'].mean()
            avg_sell = df_result[df_result['signal'] == -1]['close'].mean()
            cprint(f"\n📊 ANÁLISE DE PREÇOS:", "white", "on_blue")
            cprint(f"💰 Preço médio de compra: ${avg_buy:.2f}", "green")
            cprint(f"💸 Preço médio de venda: ${avg_sell:.2f}", "red")
            
            if avg_sell > avg_buy:
                profit = ((avg_sell / avg_buy) - 1) * 100
                cprint(f"📈 Potencial lucro: +{profit:.2f}%", "green")
            else:
                loss = ((avg_buy / avg_sell) - 1) * 100
                cprint(f"📉 Potencial perda: -{loss:.2f}%", "red")
        
        cprint(f"\n✅ ANÁLISE CONCLUÍDA COM SUCESSO!", "white", "on_green")
        
    except Exception as e:
        cprint(f"❌ Erro na análise: {e}", "red")

if __name__ == "__main__":
    test_strategy_with_cache()