"""
🌙 Moon Dev's Optimized Strategy Tester
Testa a estratégia com as configurações otimizadas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from termcolor import colored, cprint
import pandas as pd
import numpy as np

def calculate_optimized_strategy(df, ema_period=21, bb_period=100, bb_std=2.5):
    """Calcula estratégia com parâmetros otimizados"""
    
    # Calcular EMA otimizada
    df['ema_opt'] = df['close'].ewm(span=ema_period).mean()
    df['distance_opt'] = ((df['close'] - df['ema_opt']) / df['ema_opt']) * 100
    
    # Bollinger Bands otimizadas
    rolling_mean = df['distance_opt'].rolling(window=bb_period).mean()
    rolling_std = df['distance_opt'].rolling(window=bb_period).std()
    
    df['bb_upper_opt'] = rolling_mean + (rolling_std * bb_std)
    df['bb_lower_opt'] = rolling_mean - (rolling_std * bb_std)
    
    # Gerar sinais otimizados
    df['signal_opt'] = 0
    df['signal_strength_opt'] = 0.0
    
    # Condições otimizadas
    buy_condition = df['distance_opt'] < df['bb_lower_opt']
    sell_condition = df['distance_opt'] > df['bb_upper_opt']
    
    df.loc[buy_condition, 'signal_opt'] = 1
    df.loc[sell_condition, 'signal_opt'] = -1
    
    # Força do sinal otimizada
    df.loc[buy_condition, 'signal_strength_opt'] = abs(
        (df.loc[buy_condition, 'distance_opt'] - df.loc[buy_condition, 'bb_lower_opt']) / 
        df.loc[buy_condition, 'bb_lower_opt']
    )
    
    df.loc[sell_condition, 'signal_strength_opt'] = abs(
        (df.loc[sell_condition, 'distance_opt'] - df.loc[sell_condition, 'bb_upper_opt']) / 
        df.loc[sell_condition, 'bb_upper_opt']
    )
    
    return df

def test_optimized_config(csv_file):
    """Testa configuração otimizada em arquivo específico"""
    
    # Configurações específicas por arquivo (baseadas na otimização)
    configs = {
        'ETH-1h-1000wks-data.csv': {'ema': 14, 'bb_period': 100, 'bb_std': 2.5},
        'SOL-1h-1000wks-data.csv': {'ema': 21, 'bb_period': 50, 'bb_std': 2.5},
        'ETH-1d-1000wks-data.csv': {'ema': 21, 'bb_period': 100, 'bb_std': 1.5},
        'BTC-5m-30wks-data.csv': {'ema': 21, 'bb_period': 200, 'bb_std': 2.5},
        'BTC-6h-1000wks-data.csv': {'ema': 5, 'bb_period': 100, 'bb_std': 2.5},
    }
    
    file_name = os.path.basename(csv_file)
    config = configs.get(file_name, {'ema': 21, 'bb_period': 100, 'bb_std': 2.5})
    
    cprint(f"🎯 TESTANDO CONFIGURAÇÃO OTIMIZADA: {file_name}", "white", "on_blue")
    cprint("=" * 60, "blue")
    
    # Carregar dados
    df = pd.read_csv(csv_file)
    df.columns = df.columns.str.lower()
    df['timestamp'] = pd.to_datetime(df['datetime'])
    df = df.dropna()
    
    cprint(f"📊 Períodos: {len(df)}", "cyan")
    cprint(f"📅 De: {df['timestamp'].min()} até {df['timestamp'].max()}", "cyan")
    cprint(f"💰 Preço inicial: ${df['close'].iloc[0]:.2f}", "white")
    cprint(f"💰 Preço final: ${df['close'].iloc[-1]:.2f}", "white")
    
    # Variação buy & hold
    price_change = ((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100
    cprint(f"📈 Buy & Hold: {price_change:+.2f}%", "green" if price_change > 0 else "red")
    
    # Aplicar configuração otimizada
    cprint(f"\n🔧 CONFIGURAÇÃO OTIMIZADA:", "white", "on_green")
    cprint(f"📊 EMA: {config['ema']} períodos", "cyan")
    cprint(f"📊 Bollinger Bands: {config['bb_period']} períodos, {config['bb_std']} desvios", "cyan")
    
    # Calcular estratégia
    df = calculate_optimized_strategy(df, config['ema'], config['bb_period'], config['bb_std'])
    
    # Analisar resultados
    buy_signals = len(df[df['signal_opt'] == 1])
    sell_signals = len(df[df['signal_opt'] == -1])
    total_signals = buy_signals + sell_signals
    
    if total_signals > 0:
        signal_frequency = (total_signals / len(df)) * 100
        avg_strength = df[df['signal_opt'] != 0]['signal_strength_opt'].mean()
        
        cprint(f"\n🎯 RESULTADOS OTIMIZADOS:", "white", "on_green")
        cprint(f"📈 Sinais de COMPRA: {buy_signals}", "green")
        cprint(f"📉 Sinais de VENDA: {sell_signals}", "red")
        cprint(f"🎯 Total de sinais: {total_signals}", "yellow")
        cprint(f"⚡ Frequência: {signal_frequency:.2f}%", "magenta")
        cprint(f"💪 Força média: {avg_strength:.4f}", "cyan")
        
        if buy_signals > 0 and sell_signals > 0:
            avg_buy = df[df['signal_opt'] == 1]['close'].mean()
            avg_sell = df[df['signal_opt'] == -1]['close'].mean()
            strategy_return = ((avg_sell / avg_buy) - 1) * 100
            
            cprint(f"\n💰 PERFORMANCE FINANCEIRA:", "white", "on_blue")
            cprint(f"🟢 Preço médio de compra: ${avg_buy:.2f}", "green")
            cprint(f"🔴 Preço médio de venda: ${avg_sell:.2f}", "red")
            cprint(f"📊 Retorno da estratégia: {strategy_return:+.2f}%", "green" if strategy_return > 0 else "red")
            
            # Comparação
            if strategy_return > price_change:
                outperformance = strategy_return - price_change
                cprint(f"🏆 ESTRATÉGIA SUPEROU buy & hold em {outperformance:+.2f}%!", "green")
            elif strategy_return > 0:
                underperformance = price_change - strategy_return
                cprint(f"📊 Estratégia positiva, mas buy & hold foi {underperformance:.2f}% melhor", "yellow")
            else:
                cprint(f"📉 Buy & hold foi melhor (estratégia: {strategy_return:.2f}%)", "red")
        
        # Últimos sinais
        recent_signals = df[df['signal_opt'] != 0].tail(5)
        if len(recent_signals) > 0:
            cprint(f"\n🕐 ÚLTIMOS 5 SINAIS:", "white", "on_blue")
            for _, signal in recent_signals.iterrows():
                signal_type = "🟢 COMPRA" if signal['signal_opt'] == 1 else "🔴 VENDA"
                timestamp = signal['timestamp'].strftime('%Y-%m-%d %H:%M')
                cprint(f"{signal_type} - {timestamp} - ${signal['close']:.2f} - Força: {signal['signal_strength_opt']:.4f}", 
                       "green" if signal['signal_opt'] == 1 else "red")
        
        return {
            'file': file_name,
            'config': config,
            'strategy_return': strategy_return if buy_signals > 0 and sell_signals > 0 else None,
            'buy_hold_return': price_change,
            'total_signals': total_signals,
            'signal_frequency': signal_frequency
        }
    
    else:
        cprint("❌ Nenhum sinal gerado", "red")
        return None

def test_all_optimized():
    """Testa todas as configurações otimizadas"""
    import glob
    
    csv_files = glob.glob("*.csv")
    
    if not csv_files:
        cprint("❌ Nenhum arquivo CSV encontrado!", "red")
        return
    
    cprint("🌙 TESTE COMPLETO - CONFIGURAÇÕES OTIMIZADAS", "white", "on_blue")
    cprint("🚀 Aplicando melhores parâmetros para cada ativo", "white", "on_blue")
    cprint("=" * 70, "blue")
    
    results = []
    
    for csv_file in csv_files:
        result = test_optimized_config(csv_file)
        if result:
            results.append(result)
    
    # Resumo final
    if results:
        cprint(f"\n🏆 RESUMO FINAL - ESTRATÉGIAS OTIMIZADAS", "white", "on_green")
        cprint("=" * 70, "green")
        
        positive_results = [r for r in results if r['strategy_return'] and r['strategy_return'] > 0]
        
        if positive_results:
            positive_results.sort(key=lambda x: x['strategy_return'], reverse=True)
            
            cprint(f"✅ ESTRATÉGIAS LUCRATIVAS:", "green")
            for i, result in enumerate(positive_results, 1):
                file_short = result['file'].replace('.csv', '').replace('-data', '')
                config = result['config']
                cprint(f"{i}. {file_short:15s} | EMA:{config['ema']:2d} BB:({config['bb_period']:3d},{config['bb_std']:.1f}) | "
                       f"Ret:{result['strategy_return']:+6.2f}% | Sinais:{result['total_signals']:3d}", "green")
        
        # Estatísticas gerais
        total_signals = sum(r['total_signals'] for r in results)
        avg_frequency = sum(r['signal_frequency'] for r in results) / len(results)
        profitable_count = len([r for r in results if r['strategy_return'] and r['strategy_return'] > 0])
        
        cprint(f"\n📊 ESTATÍSTICAS FINAIS:", "white", "on_blue")
        cprint(f"🎯 Total de sinais: {total_signals}", "yellow")
        cprint(f"⚡ Frequência média: {avg_frequency:.2f}%", "cyan")
        cprint(f"💰 Estratégias lucrativas: {profitable_count}/{len(results)}", "green")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_optimized_config(sys.argv[1])
    else:
        test_all_optimized()