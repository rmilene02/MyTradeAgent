"""
🎮 DEMO DA ESTRATÉGIA MOON DEV
Demonstração completa sem necessidade de APIs externas
Built with love by Moon Dev 🚀
"""

import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.custom_indicators_simple import *
from termcolor import colored, cprint
import time

def create_demo_data(periods=500):
    """Cria dados de demonstração realistas"""
    cprint("📊 Gerando dados de demonstração...", "cyan")
    
    # Criar série temporal realista
    dates = pd.date_range('2024-01-01', periods=periods, freq='1h')
    
    # Simular movimento de preço com tendência e volatilidade
    np.random.seed(42)
    
    # Preço base com tendência
    trend = np.linspace(100, 120, periods)
    
    # Adicionar volatilidade e ruído
    volatility = np.random.randn(periods) * 2
    noise = np.random.randn(periods) * 0.5
    
    # Preço final
    close_prices = trend + np.cumsum(volatility) + noise
    
    # Garantir que não haja preços negativos
    close_prices = np.maximum(close_prices, 10)
    
    # Criar OHLC baseado no close
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices + np.random.randn(periods) * 0.2,
        'high': close_prices + abs(np.random.randn(periods) * 0.5),
        'low': close_prices - abs(np.random.randn(periods) * 0.5),
        'close': close_prices,
        'volume': np.random.randint(1000, 50000, periods)
    })
    
    # Garantir que high >= max(open, close) e low <= min(open, close)
    df['high'] = np.maximum(df['high'], np.maximum(df['open'], df['close']))
    df['low'] = np.minimum(df['low'], np.minimum(df['open'], df['close']))
    
    cprint(f"✅ Dados criados: {periods} períodos de 1h", "green")
    return df

def print_ascii_chart(df, column='close', height=15, width=60):
    """Cria um gráfico ASCII simples"""
    data = df[column].dropna().tail(width)
    
    if len(data) == 0:
        return
    
    min_val = data.min()
    max_val = data.max()
    
    if max_val == min_val:
        max_val = min_val + 1
    
    # Normalizar dados para altura do gráfico
    normalized = ((data - min_val) / (max_val - min_val) * (height - 1)).round().astype(int)
    
    # Criar matriz do gráfico
    chart = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Preencher com dados
    for i, val in enumerate(normalized):
        if i < width:
            chart[height - 1 - val][i] = '█'
    
    # Imprimir gráfico
    cprint(f"\n📈 Gráfico ASCII - {column.upper()}", "white", "on_blue")
    cprint(f"Max: {max_val:.2f}", "green")
    
    for row in chart:
        print(''.join(row))
    
    cprint(f"Min: {min_val:.2f}", "red")
    print('-' * width)

def show_signals_summary(df):
    """Mostra resumo dos sinais gerados"""
    if 'signal' not in df.columns:
        return
    
    buy_signals = df[df['signal'] == 1]
    sell_signals = df[df['signal'] == -1]
    
    cprint("\n🎯 RESUMO DOS SINAIS", "white", "on_blue")
    cprint(f"📈 Sinais de COMPRA: {len(buy_signals)}", "green")
    cprint(f"📉 Sinais de VENDA: {len(sell_signals)}", "red")
    
    if len(buy_signals) > 0:
        cprint(f"💰 Preço médio de compra: ${buy_signals['close'].mean():.2f}", "green")
        cprint(f"🔥 Força média (compra): {buy_signals['signal_strength'].mean():.4f}", "green")
    
    if len(sell_signals) > 0:
        cprint(f"💸 Preço médio de venda: ${sell_signals['close'].mean():.2f}", "red")
        cprint(f"🔥 Força média (venda): {sell_signals['signal_strength'].mean():.4f}", "red")

def interactive_demo():
    """Demo interativo da estratégia"""
    cprint("\n🌙 BEM-VINDO AO DEMO DA ESTRATÉGIA MOON DEV!", "white", "on_blue")
    cprint("=" * 60, "blue")
    
    # Criar dados de demo
    df = create_demo_data(500)
    
    # Executar análise completa
    df_result, performance = run_complete_analysis(df)
    
    # Mostrar gráficos ASCII
    print_ascii_chart(df_result, 'close', height=12, width=50)
    print_ascii_chart(df_result, 'distanciaMME9_pct', height=8, width=50)
    
    # Mostrar resumo de sinais
    show_signals_summary(df_result)
    
    # Mostrar últimos sinais
    recent_signals = df_result[df_result['signal'] != 0].tail(5)
    if len(recent_signals) > 0:
        cprint("\n🕐 ÚLTIMOS 5 SINAIS", "white", "on_blue")
        for _, signal in recent_signals.iterrows():
            signal_type = "🟢 COMPRA" if signal['signal'] == 1 else "🔴 VENDA"
            cprint(f"{signal_type} - Preço: ${signal['close']:.2f} - Força: {signal['signal_strength']:.4f}", 
                   "green" if signal['signal'] == 1 else "red")
    
    # Menu interativo
    while True:
        cprint("\n🎮 OPÇÕES DO DEMO:", "cyan")
        cprint("1. 📊 Ver gráfico de preços", "white")
        cprint("2. 📈 Ver gráfico de distância MME9", "white")
        cprint("3. 🎯 Ver todos os sinais", "white")
        cprint("4. 📋 Ver estatísticas detalhadas", "white")
        cprint("5. 🔄 Gerar novos dados", "white")
        cprint("6. ❌ Sair", "white")
        
        choice = input("\n👉 Escolha uma opção (1-6): ").strip()
        
        if choice == '1':
            print_ascii_chart(df_result, 'close', height=15, width=60)
        elif choice == '2':
            print_ascii_chart(df_result, 'distanciaMME9_pct', height=10, width=60)
        elif choice == '3':
            signals = df_result[df_result['signal'] != 0]
            cprint(f"\n📋 TODOS OS SINAIS ({len(signals)} total):", "white", "on_blue")
            for i, (_, signal) in enumerate(signals.iterrows(), 1):
                signal_type = "🟢 COMPRA" if signal['signal'] == 1 else "🔴 VENDA"
                cprint(f"{i:2d}. {signal_type} - ${signal['close']:.2f} - Força: {signal['signal_strength']:.4f}", 
                       "green" if signal['signal'] == 1 else "red")
        elif choice == '4':
            cprint("\n📊 ESTATÍSTICAS DETALHADAS", "white", "on_blue")
            cprint(f"📈 Preço inicial: ${df_result['close'].iloc[0]:.2f}", "cyan")
            cprint(f"📈 Preço final: ${df_result['close'].iloc[-1]:.2f}", "cyan")
            cprint(f"📊 Variação total: {((df_result['close'].iloc[-1] / df_result['close'].iloc[0]) - 1) * 100:.2f}%", "yellow")
            cprint(f"📊 Volatilidade: {df_result['close'].std():.2f}", "magenta")
            cprint(f"📊 Volume médio: {df_result['volume'].mean():.0f}", "white")
        elif choice == '5':
            cprint("🔄 Gerando novos dados...", "yellow")
            df = create_demo_data(500)
            df_result, performance = run_complete_analysis(df)
            cprint("✅ Novos dados gerados e analisados!", "green")
        elif choice == '6':
            cprint("👋 Obrigado por usar o demo! Até logo!", "white", "on_green")
            break
        else:
            cprint("❌ Opção inválida! Tente novamente.", "red")

if __name__ == "__main__":
    try:
        interactive_demo()
    except KeyboardInterrupt:
        cprint("\n\n👋 Demo interrompido pelo usuário. Até logo!", "yellow")
    except Exception as e:
        cprint(f"\n❌ Erro no demo: {e}", "red")
        cprint("💡 Verifique se todas as dependências estão instaladas.", "yellow")