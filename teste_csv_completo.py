"""
🌙 Moon Dev's CSV Strategy Tester
Testa a estratégia com seus dados históricos em CSV
Análise completa de múltiplos ativos e timeframes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.custom_indicators_simple import run_complete_analysis
from termcolor import colored, cprint
import pandas as pd
import glob
from datetime import datetime

def load_csv_data(file_path):
    """Carrega dados do CSV e padroniza formato"""
    try:
        df = pd.read_csv(file_path)
        
        # Padronizar nomes das colunas
        df.columns = df.columns.str.lower()
        
        # Converter datetime
        if 'datetime' in df.columns:
            df['timestamp'] = pd.to_datetime(df['datetime'])
        elif 'date' in df.columns:
            df['timestamp'] = pd.to_datetime(df['date'])
        
        # Verificar se tem todas as colunas necessárias
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            cprint(f"❌ Colunas faltando: {missing_cols}", "red")
            return None
        
        # Remover dados inválidos
        df = df.dropna()
        df = df[df['close'] > 0]
        
        return df
        
    except Exception as e:
        cprint(f"❌ Erro ao carregar {file_path}: {e}", "red")
        return None

def analyze_csv_file(file_path):
    """Analisa um arquivo CSV específico"""
    file_name = os.path.basename(file_path)
    cprint(f"\n🔍 ANALISANDO: {file_name}", "white", "on_blue")
    cprint("=" * 60, "blue")
    
    # Carregar dados
    df = load_csv_data(file_path)
    if df is None:
        return None
    
    # Informações básicas
    cprint(f"📊 Períodos: {len(df)}", "cyan")
    cprint(f"📅 De: {df['timestamp'].min()} até {df['timestamp'].max()}", "cyan")
    cprint(f"💰 Preço inicial: ${df['close'].iloc[0]:.2f}", "white")
    cprint(f"💰 Preço final: ${df['close'].iloc[-1]:.2f}", "white")
    
    # Calcular variação total
    price_change = ((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100
    color = "green" if price_change > 0 else "red"
    cprint(f"📈 Variação total: {price_change:+.2f}%", color)
    
    # Verificar se tem dados suficientes
    if len(df) < 250:
        cprint(f"⚠️  Poucos dados ({len(df)} períodos). Mínimo recomendado: 250", "yellow")
        if len(df) < 50:
            cprint("❌ Dados insuficientes para análise", "red")
            return None
    
    try:
        # Executar análise da estratégia
        cprint(f"\n🚀 Executando estratégia Moon Dev...", "cyan")
        df_result, performance = run_complete_analysis(df)
        
        # Extrair resultados
        buy_signals = len(df_result[df_result['signal'] == 1])
        sell_signals = len(df_result[df_result['signal'] == -1])
        total_signals = buy_signals + sell_signals
        
        # Calcular métricas
        if total_signals > 0:
            signal_frequency = (total_signals / len(df)) * 100
            avg_strength = df_result[df_result['signal'] != 0]['signal_strength'].mean()
            
            # Análise de preços nos sinais
            buy_prices = df_result[df_result['signal'] == 1]['close']
            sell_prices = df_result[df_result['signal'] == -1]['close']
            
            results = {
                'file': file_name,
                'periods': len(df),
                'price_change': price_change,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'total_signals': total_signals,
                'signal_frequency': signal_frequency,
                'avg_strength': avg_strength,
                'avg_buy_price': buy_prices.mean() if len(buy_prices) > 0 else 0,
                'avg_sell_price': sell_prices.mean() if len(sell_prices) > 0 else 0,
            }
            
            # Mostrar resultados
            cprint(f"\n🎯 RESULTADOS DA ESTRATÉGIA:", "white", "on_green")
            cprint(f"📈 Sinais de COMPRA: {buy_signals}", "green")
            cprint(f"📉 Sinais de VENDA: {sell_signals}", "red")
            cprint(f"🎯 Total de sinais: {total_signals}", "yellow")
            cprint(f"⚡ Frequência de sinais: {signal_frequency:.2f}%", "magenta")
            cprint(f"💪 Força média: {avg_strength:.4f}", "cyan")
            
            if buy_signals > 0 and sell_signals > 0:
                strategy_return = ((results['avg_sell_price'] / results['avg_buy_price']) - 1) * 100
                results['strategy_return'] = strategy_return
                
                cprint(f"\n💰 ANÁLISE DE PREÇOS:", "white", "on_blue")
                cprint(f"🟢 Preço médio de compra: ${results['avg_buy_price']:.2f}", "green")
                cprint(f"🔴 Preço médio de venda: ${results['avg_sell_price']:.2f}", "red")
                
                if strategy_return > 0:
                    cprint(f"📈 Retorno da estratégia: +{strategy_return:.2f}%", "green")
                else:
                    cprint(f"📉 Retorno da estratégia: {strategy_return:.2f}%", "red")
                
                # Comparar com buy & hold
                if strategy_return > price_change:
                    cprint(f"🏆 Estratégia SUPEROU buy & hold em {strategy_return - price_change:.2f}%!", "green")
                else:
                    cprint(f"📊 Buy & hold foi melhor em {price_change - strategy_return:.2f}%", "yellow")
            
            # Mostrar últimos sinais
            recent_signals = df_result[df_result['signal'] != 0].tail(3)
            if len(recent_signals) > 0:
                cprint(f"\n🕐 ÚLTIMOS SINAIS:", "white", "on_blue")
                for _, signal in recent_signals.iterrows():
                    signal_type = "🟢 COMPRA" if signal['signal'] == 1 else "🔴 VENDA"
                    timestamp = signal['timestamp'].strftime('%Y-%m-%d %H:%M') if 'timestamp' in signal else 'N/A'
                    cprint(f"{signal_type} - {timestamp} - ${signal['close']:.2f} - Força: {signal['signal_strength']:.4f}", 
                           "green" if signal['signal'] == 1 else "red")
            
            return results
        
        else:
            cprint("❌ Nenhum sinal gerado pela estratégia", "red")
            return None
            
    except Exception as e:
        cprint(f"❌ Erro na análise: {e}", "red")
        return None

def test_all_csv_files():
    """Testa todos os arquivos CSV disponíveis"""
    cprint("🌙 MOON DEV'S CSV STRATEGY TESTER", "white", "on_blue")
    cprint("🚀 Testando estratégia em todos os dados históricos", "white", "on_blue")
    cprint("=" * 70, "blue")
    
    # Encontrar todos os CSVs
    csv_files = glob.glob("*.csv")
    
    if not csv_files:
        cprint("❌ Nenhum arquivo CSV encontrado!", "red")
        return
    
    cprint(f"📁 Encontrados {len(csv_files)} arquivos CSV:", "cyan")
    for i, file in enumerate(csv_files, 1):
        cprint(f"  {i}. {file}", "white")
    
    # Analisar cada arquivo
    results = []
    
    for file_path in csv_files:
        result = analyze_csv_file(file_path)
        if result:
            results.append(result)
    
    # Resumo comparativo
    if len(results) > 1:
        cprint(f"\n🏆 RESUMO COMPARATIVO", "white", "on_green")
        cprint("=" * 70, "green")
        
        # Ordenar por retorno da estratégia
        results_with_return = [r for r in results if 'strategy_return' in r]
        if results_with_return:
            results_with_return.sort(key=lambda x: x['strategy_return'], reverse=True)
            
            cprint(f"🥇 MELHORES PERFORMANCES:", "yellow")
            for i, result in enumerate(results_with_return[:3], 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                cprint(f"{medal} {result['file']}: {result['strategy_return']:+.2f}% "
                       f"({result['total_signals']} sinais)", "green" if result['strategy_return'] > 0 else "red")
        
        # Estatísticas gerais
        total_signals = sum(r['total_signals'] for r in results)
        avg_frequency = sum(r['signal_frequency'] for r in results) / len(results)
        
        cprint(f"\n📊 ESTATÍSTICAS GERAIS:", "white", "on_blue")
        cprint(f"🎯 Total de sinais gerados: {total_signals}", "yellow")
        cprint(f"⚡ Frequência média de sinais: {avg_frequency:.2f}%", "cyan")
        cprint(f"📈 Arquivos analisados: {len(results)}", "white")

def interactive_csv_tester():
    """Interface interativa para testar CSVs específicos"""
    csv_files = glob.glob("*.csv")
    
    if not csv_files:
        cprint("❌ Nenhum arquivo CSV encontrado!", "red")
        return
    
    while True:
        cprint(f"\n🌙 SELETOR DE ARQUIVOS CSV", "white", "on_blue")
        cprint("=" * 40, "blue")
        
        for i, file in enumerate(csv_files, 1):
            size_mb = os.path.getsize(file) / (1024*1024)
            cprint(f"  {i}. {file} ({size_mb:.1f}MB)", "white")
        
        cprint(f"  0. Testar TODOS os arquivos", "yellow")
        cprint(f"  q. Sair", "red")
        
        try:
            choice = input("\n🎯 Escolha uma opção: ").strip().lower()
            
            if choice == 'q':
                cprint("👋 Até logo!", "cyan")
                break
            elif choice == '0':
                test_all_csv_files()
            else:
                file_index = int(choice) - 1
                if 0 <= file_index < len(csv_files):
                    analyze_csv_file(csv_files[file_index])
                else:
                    cprint("❌ Opção inválida!", "red")
        
        except (ValueError, KeyboardInterrupt):
            cprint("\n👋 Saindo...", "cyan")
            break

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Modo linha de comando
        if sys.argv[1] == "all":
            test_all_csv_files()
        else:
            analyze_csv_file(sys.argv[1])
    else:
        # Modo interativo
        interactive_csv_tester()