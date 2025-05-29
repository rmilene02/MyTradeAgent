"""
🌙 Moon Dev's Strategy Tester
Teste sua estratégia Distância MME9 + Bollinger Bands sem executar trades reais
Built with love by Moon Dev 🚀
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.ohlcv_collector import collect_token_data
try:
    from src.data.custom_indicators import *
except ImportError:
    from src.data.custom_indicators_simple import *
from src.core.config import MONITORED_TOKENS
from termcolor import colored, cprint
import pandas as pd

def test_single_token(token):
    """Testa a estratégia em um único token"""
    cprint(f"\n🧪 Testando estratégia para token: {token}", "white", "on_blue")
    
    try:
        # Coletar dados
        data = collect_token_data(token, days_back=10, timeframe='3m')
        
        if data is None or len(data) < 200:
            cprint(f"❌ Dados insuficientes para {token} (mínimo 200 períodos)", "white", "on_red")
            return
        
        # Aplicar indicadores
        data = calculate_distance_mme9(data)
        data = calculate_bollinger_on_distance(data)
        data = detect_exhaustion_signals(data)
        
        # Mostrar últimos 5 períodos
        cprint("\n📊 Últimos 5 períodos:", "white", "on_green")
        cols_to_show = ['close', 'MME9', 'distanciaMME9_pct', 'BB_Upper', 'BB_Lower', 
                       'exaustao_alta', 'exaustao_baixa', 'reversao_alta', 'reversao_baixa']
        
        recent_data = data[cols_to_show].tail(5)
        print(recent_data.to_string())
        
        # Gerar resumo da estratégia
        strategy_summary = generate_strategy_summary(data)
        cprint("\n🎯 RESUMO DA ESTRATÉGIA:", "white", "on_blue")
        print(strategy_summary)
        
        # Análise do último período
        last_row = data.iloc[-1]
        cprint(f"\n📈 ANÁLISE ATUAL:", "white", "on_cyan")
        print(f"Preço: ${last_row['close']:.6f}")
        print(f"Distância MME9: {last_row['distanciaMME9_pct']:.2f}%")
        print(f"Posição BB: {last_row['BB_Position']:.2f}")
        
        if last_row['exaustao_alta']:
            cprint("🔴 EM EXAUSTÃO DE ALTA - Aguardar reversão para VENDER", "white", "on_red")
        elif last_row['exaustao_baixa']:
            cprint("🟢 EM EXAUSTÃO DE BAIXA - Aguardar reversão para COMPRAR", "white", "on_green")
        elif last_row['reversao_baixa']:
            cprint("🔴 SINAL DE VENDA - Reversão após exaustão detectada!", "white", "on_red")
        elif last_row['reversao_alta']:
            cprint("🟢 SINAL DE COMPRA - Reversão após exaustão detectada!", "white", "on_green")
        else:
            cprint("😐 NEUTRO - Sem sinais claros", "white", "on_yellow")
            
    except Exception as e:
        cprint(f"❌ Erro ao testar {token}: {str(e)}", "white", "on_red")

def test_all_tokens():
    """Testa a estratégia em todos os tokens monitorados"""
    cprint("🚀 Iniciando teste da estratégia em todos os tokens...", "white", "on_blue")
    
    for token in MONITORED_TOKENS:
        test_single_token(token)
        print("\n" + "="*80 + "\n")

def backtest_strategy(token, days_back=30):
    """Faz um backtest simples da estratégia"""
    cprint(f"\n📈 Backtesting estratégia para {token} ({days_back} dias)", "white", "on_blue")
    
    try:
        # Coletar mais dados para backtest
        data = collect_token_data(token, days_back=days_back, timeframe='15m')
        
        if data is None or len(data) < 200:
            cprint(f"❌ Dados insuficientes para backtest", "white", "on_red")
            return
        
        # Aplicar indicadores
        data = calculate_distance_mme9(data)
        data = calculate_bollinger_on_distance(data)
        data = detect_exhaustion_signals(data)
        
        # Contar sinais
        total_reversao_alta = data['reversao_alta'].sum()
        total_reversao_baixa = data['reversao_baixa'].sum()
        total_exaustao_alta = data['exaustao_alta'].sum()
        total_exaustao_baixa = data['exaustao_baixa'].sum()
        
        cprint(f"\n📊 ESTATÍSTICAS DO BACKTEST ({len(data)} períodos):", "white", "on_green")
        print(f"🟢 Sinais de COMPRA (reversão alta): {total_reversao_alta}")
        print(f"🔴 Sinais de VENDA (reversão baixa): {total_reversao_baixa}")
        print(f"⏳ Períodos em exaustão alta: {total_exaustao_alta}")
        print(f"⏳ Períodos em exaustão baixa: {total_exaustao_baixa}")
        
        # Calcular frequência de sinais
        freq_compra = (total_reversao_alta / len(data)) * 100
        freq_venda = (total_reversao_baixa / len(data)) * 100
        
        print(f"📈 Frequência de sinais de compra: {freq_compra:.1f}%")
        print(f"📉 Frequência de sinais de venda: {freq_venda:.1f}%")
        
        # Mostrar últimos sinais
        last_signals = data[data['reversao_alta'] | data['reversao_baixa']].tail(5)
        if not last_signals.empty:
            cprint(f"\n🎯 Últimos 5 sinais:", "white", "on_cyan")
            for idx, row in last_signals.iterrows():
                signal_type = "COMPRA" if row['reversao_alta'] else "VENDA"
                timestamp = row.name if hasattr(row, 'name') else idx
                print(f"{timestamp}: {signal_type} - Preço: ${row['close']:.6f}")
        
    except Exception as e:
        cprint(f"❌ Erro no backtest: {str(e)}", "white", "on_red")

if __name__ == "__main__":
    print("🌙 Moon Dev's Strategy Tester")
    print("Escolha uma opção:")
    print("1. Testar estratégia em tempo real (todos os tokens)")
    print("2. Testar um token específico")
    print("3. Backtest de um token")
    
    try:
        choice = input("\nDigite sua escolha (1-3): ").strip()
        
        if choice == "1":
            test_all_tokens()
        elif choice == "2":
            print(f"\nTokens disponíveis:")
            for i, token in enumerate(MONITORED_TOKENS, 1):
                print(f"{i}. {token}")
            
            token_choice = int(input("\nEscolha o número do token: ")) - 1
            if 0 <= token_choice < len(MONITORED_TOKENS):
                test_single_token(MONITORED_TOKENS[token_choice])
            else:
                print("❌ Escolha inválida!")
                
        elif choice == "3":
            print(f"\nTokens disponíveis:")
            for i, token in enumerate(MONITORED_TOKENS, 1):
                print(f"{i}. {token}")
            
            token_choice = int(input("\nEscolha o número do token: ")) - 1
            days = int(input("Quantos dias de backtest? (padrão 30): ") or "30")
            
            if 0 <= token_choice < len(MONITORED_TOKENS):
                backtest_strategy(MONITORED_TOKENS[token_choice], days)
            else:
                print("❌ Escolha inválida!")
        else:
            print("❌ Opção inválida!")
            
    except KeyboardInterrupt:
        print("\n👋 Teste interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")