"""
🌙 Moon Dev's Parameter Optimizer
Testa diferentes parâmetros para otimizar a estratégia
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.custom_indicators_simple import calculate_ema, calculate_bollinger_bands, generate_signals
from termcolor import colored, cprint
import pandas as pd
import numpy as np

def test_parameters(df, ema_period=9, bb_period=200, bb_std=2):
    """Testa parâmetros específicos"""
    try:
        # Calcular distância EMA
        df['ema'] = calculate_ema(df['close'], ema_period)
        df['distance'] = ((df['close'] - df['ema']) / df['ema']) * 100
        
        # Bollinger Bands na distância
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(df['distance'], bb_period, bb_std)
        df['bb_upper'] = bb_upper
        df['bb_lower'] = bb_lower
        
        # Gerar sinais
        df['signal'], df['signal_strength'] = generate_signals(df)
        
        # Calcular performance
        buy_signals = len(df[df['signal'] == 1])
        sell_signals = len(df[df['signal'] == -1])
        
        if buy_signals > 0 and sell_signals > 0:
            avg_buy = df[df['signal'] == 1]['close'].mean()
            avg_sell = df[df['signal'] == -1]['close'].mean()
            strategy_return = ((avg_sell / avg_buy) - 1) * 100
            
            return {
                'ema_period': ema_period,
                'bb_period': bb_period,
                'bb_std': bb_std,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'total_signals': buy_signals + sell_signals,
                'strategy_return': strategy_return,
                'signal_frequency': (buy_signals + sell_signals) / len(df) * 100
            }
    except:
        pass
    
    return None

def optimize_parameters(csv_file):
    """Otimiza parâmetros para um arquivo específico"""
    cprint(f"🔧 OTIMIZANDO PARÂMETROS PARA: {csv_file}", "white", "on_blue")
    cprint("=" * 60, "blue")
    
    # Carregar dados
    df = pd.read_csv(csv_file)
    df.columns = df.columns.str.lower()
    df['timestamp'] = pd.to_datetime(df['datetime'])
    df = df.dropna()
    
    if len(df) < 500:
        cprint("❌ Dados insuficientes para otimização", "red")
        return
    
    cprint(f"📊 Testando {len(df)} períodos...", "cyan")
    
    # Parâmetros para testar
    ema_periods = [5, 9, 14, 21]
    bb_periods = [50, 100, 200, 300]
    bb_stds = [1.5, 2.0, 2.5]
    
    results = []
    total_tests = len(ema_periods) * len(bb_periods) * len(bb_stds)
    current_test = 0
    
    cprint(f"🧪 Executando {total_tests} testes...", "yellow")
    
    for ema in ema_periods:
        for bb_period in bb_periods:
            for bb_std in bb_stds:
                current_test += 1
                if current_test % 10 == 0:
                    progress = (current_test / total_tests) * 100
                    cprint(f"⏳ Progresso: {progress:.1f}%", "cyan")
                
                result = test_parameters(df.copy(), ema, bb_period, bb_std)
                if result:
                    results.append(result)
    
    if not results:
        cprint("❌ Nenhum resultado válido", "red")
        return
    
    # Ordenar por retorno
    results.sort(key=lambda x: x['strategy_return'], reverse=True)
    
    cprint(f"\n🏆 TOP 5 MELHORES CONFIGURAÇÕES:", "white", "on_green")
    cprint("=" * 60, "green")
    
    for i, result in enumerate(results[:5], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        cprint(f"{medal} EMA:{result['ema_period']} | BB:{result['bb_period']},{result['bb_std']} | "
               f"Retorno:{result['strategy_return']:+.2f}% | "
               f"Sinais:{result['total_signals']}", 
               "green" if result['strategy_return'] > 0 else "yellow")
    
    # Melhor configuração
    best = results[0]
    cprint(f"\n🎯 MELHOR CONFIGURAÇÃO:", "white", "on_blue")
    cprint(f"📊 EMA: {best['ema_period']} períodos", "cyan")
    cprint(f"📊 Bollinger: {best['bb_period']} períodos, {best['bb_std']} desvios", "cyan")
    cprint(f"📈 Retorno: {best['strategy_return']:+.2f}%", "green" if best['strategy_return'] > 0 else "red")
    cprint(f"🎯 Sinais: {best['total_signals']} ({best['signal_frequency']:.2f}%)", "yellow")
    
    return best

if __name__ == "__main__":
    # Testar com BTC 5min (melhor performance anterior)
    optimize_parameters("BTC-5m-30wks-data.csv")