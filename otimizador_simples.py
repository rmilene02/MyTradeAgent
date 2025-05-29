"""
🌙 Moon Dev's Simple Parameter Optimizer
Testa diferentes parâmetros de forma simplificada
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.custom_indicators_simple import run_complete_analysis
from termcolor import colored, cprint
import pandas as pd
import numpy as np

def test_single_parameter_set(df, ema_period, bb_period, bb_std):
    """Testa um conjunto específico de parâmetros"""
    try:
        # Fazer cópia dos dados
        test_df = df.copy()
        
        # Calcular EMA personalizada
        test_df['ema_custom'] = test_df['close'].ewm(span=ema_period).mean()
        test_df['distance_custom'] = ((test_df['close'] - test_df['ema_custom']) / test_df['ema_custom']) * 100
        
        # Calcular Bollinger Bands personalizadas
        rolling_mean = test_df['distance_custom'].rolling(window=bb_period).mean()
        rolling_std = test_df['distance_custom'].rolling(window=bb_period).std()
        
        test_df['bb_upper_custom'] = rolling_mean + (rolling_std * bb_std)
        test_df['bb_lower_custom'] = rolling_mean - (rolling_std * bb_std)
        
        # Gerar sinais
        test_df['signal'] = 0
        test_df['signal_strength'] = 0.0
        
        # Condições
        buy_condition = test_df['distance_custom'] < test_df['bb_lower_custom']
        sell_condition = test_df['distance_custom'] > test_df['bb_upper_custom']
        
        test_df.loc[buy_condition, 'signal'] = 1
        test_df.loc[sell_condition, 'signal'] = -1
        
        # Força do sinal
        test_df.loc[buy_condition, 'signal_strength'] = abs(
            (test_df.loc[buy_condition, 'distance_custom'] - test_df.loc[buy_condition, 'bb_lower_custom']) / 
            test_df.loc[buy_condition, 'bb_lower_custom']
        )
        
        test_df.loc[sell_condition, 'signal_strength'] = abs(
            (test_df.loc[sell_condition, 'distance_custom'] - test_df.loc[sell_condition, 'bb_upper_custom']) / 
            test_df.loc[sell_condition, 'bb_upper_custom']
        )
        
        # Calcular métricas
        buy_signals = len(test_df[test_df['signal'] == 1])
        sell_signals = len(test_df[test_df['signal'] == -1])
        
        if buy_signals > 0 and sell_signals > 0:
            avg_buy = test_df[test_df['signal'] == 1]['close'].mean()
            avg_sell = test_df[test_df['signal'] == -1]['close'].mean()
            strategy_return = ((avg_sell / avg_buy) - 1) * 100
            
            return {
                'ema_period': ema_period,
                'bb_period': bb_period,
                'bb_std': bb_std,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'total_signals': buy_signals + sell_signals,
                'strategy_return': strategy_return,
                'signal_frequency': (buy_signals + sell_signals) / len(test_df) * 100,
                'avg_strength': test_df[test_df['signal'] != 0]['signal_strength'].mean()
            }
    
    except Exception as e:
        # cprint(f"❌ Erro nos parâmetros EMA:{ema_period}, BB:{bb_period},{bb_std}: {e}", "red")
        pass
    
    return None

def quick_optimization(csv_file, sample_size=5000):
    """Otimização rápida com amostra dos dados"""
    cprint(f"🔧 OTIMIZAÇÃO RÁPIDA: {csv_file}", "white", "on_blue")
    cprint("=" * 50, "blue")
    
    # Carregar dados
    df = pd.read_csv(csv_file)
    df.columns = df.columns.str.lower()
    df['timestamp'] = pd.to_datetime(df['datetime'])
    df = df.dropna()
    
    # Usar amostra para acelerar
    if len(df) > sample_size:
        df = df.tail(sample_size)  # Usar dados mais recentes
        cprint(f"📊 Usando amostra de {len(df)} períodos (dados recentes)", "cyan")
    else:
        cprint(f"📊 Usando todos os {len(df)} períodos", "cyan")
    
    # Parâmetros para testar (reduzidos para velocidade)
    ema_periods = [5, 9, 14, 21]
    bb_periods = [50, 100, 200]
    bb_stds = [1.5, 2.0, 2.5]
    
    results = []
    total_tests = len(ema_periods) * len(bb_periods) * len(bb_stds)
    
    cprint(f"🧪 Testando {total_tests} combinações...", "yellow")
    
    for i, ema in enumerate(ema_periods):
        for j, bb_period in enumerate(bb_periods):
            for k, bb_std in enumerate(bb_stds):
                result = test_single_parameter_set(df, ema, bb_period, bb_std)
                if result:
                    results.append(result)
    
    if not results:
        cprint("❌ Nenhum resultado válido encontrado", "red")
        return
    
    cprint(f"✅ {len(results)} configurações válidas testadas", "green")
    
    # Ordenar por retorno
    results.sort(key=lambda x: x['strategy_return'], reverse=True)
    
    cprint(f"\n🏆 TOP 5 MELHORES CONFIGURAÇÕES:", "white", "on_green")
    cprint("=" * 60, "green")
    
    for i, result in enumerate(results[:5], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        cprint(f"{medal} EMA:{result['ema_period']:2d} | BB:({result['bb_period']:3d},{result['bb_std']:.1f}) | "
               f"Ret:{result['strategy_return']:+6.2f}% | "
               f"Sinais:{result['total_signals']:3d} | "
               f"Freq:{result['signal_frequency']:4.1f}%", 
               "green" if result['strategy_return'] > 0 else "yellow")
    
    # Melhor configuração
    best = results[0]
    cprint(f"\n🎯 CONFIGURAÇÃO RECOMENDADA:", "white", "on_blue")
    cprint(f"📊 EMA: {best['ema_period']} períodos", "cyan")
    cprint(f"📊 Bollinger Bands: {best['bb_period']} períodos, {best['bb_std']} desvios", "cyan")
    cprint(f"📈 Retorno estimado: {best['strategy_return']:+.2f}%", "green" if best['strategy_return'] > 0 else "red")
    cprint(f"🎯 Sinais gerados: {best['total_signals']} ({best['signal_frequency']:.1f}%)", "yellow")
    cprint(f"💪 Força média: {best['avg_strength']:.4f}", "magenta")
    
    return best

def test_multiple_files():
    """Testa otimização em múltiplos arquivos"""
    import glob
    
    csv_files = glob.glob("*.csv")
    
    if not csv_files:
        cprint("❌ Nenhum arquivo CSV encontrado!", "red")
        return
    
    cprint("🌙 OTIMIZAÇÃO MULTI-ARQUIVO", "white", "on_blue")
    cprint("=" * 50, "blue")
    
    all_results = {}
    
    for csv_file in csv_files:
        cprint(f"\n📁 Processando: {csv_file}", "white")
        result = quick_optimization(csv_file)
        if result:
            all_results[csv_file] = result
    
    if all_results:
        cprint(f"\n🏆 RESUMO GERAL - MELHORES CONFIGURAÇÕES:", "white", "on_green")
        cprint("=" * 70, "green")
        
        # Ordenar arquivos por performance
        sorted_files = sorted(all_results.items(), key=lambda x: x[1]['strategy_return'], reverse=True)
        
        for i, (file, result) in enumerate(sorted_files, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            file_short = file.replace('.csv', '').replace('-data', '')
            cprint(f"{medal} {file_short:15s} | EMA:{result['ema_period']:2d} BB:({result['bb_period']:3d},{result['bb_std']:.1f}) | "
                   f"Ret:{result['strategy_return']:+6.2f}%", 
                   "green" if result['strategy_return'] > 0 else "yellow")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            test_multiple_files()
        else:
            quick_optimization(sys.argv[1])
    else:
        # Testar arquivo com melhor performance anterior
        quick_optimization("BTC-5m-30wks-data.csv")