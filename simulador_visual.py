"""
🎮 SIMULADOR VISUAL DA ESTRATÉGIA
Veja sua estratégia funcionando em tempo real com gráficos visuais!
Built with love by Moon Dev 🚀
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.ohlcv_collector import collect_token_data
from src.data.custom_indicators import *
from src.core.config import MONITORED_TOKENS
from termcolor import colored, cprint
import pandas as pd
import time

def print_chart_ascii(data, rows=15):
    """Cria um gráfico ASCII simples dos preços"""
    prices = data['close'].tail(50).values
    if len(prices) < 2:
        return
    
    min_price = min(prices)
    max_price = max(prices)
    price_range = max_price - min_price
    
    if price_range == 0:
        return
    
    print("\n📈 GRÁFICO DE PREÇOS (últimos 50 períodos):")
    print("=" * 60)
    
    for i in range(rows, 0, -1):
        line = ""
        threshold = min_price + (price_range * i / rows)
        
        for price in prices[-50:]:
            if price >= threshold:
                line += "█"
            else:
                line += " "
        
        print(f"{threshold:8.4f} |{line}")
    
    print(" " * 9 + "+" + "-" * 50)
    print(" " * 11 + "Tempo →")

def print_bollinger_visual(data):
    """Mostra visualmente a posição nas Bollinger Bands"""
    last_row = data.iloc[-1]
    
    distance = last_row['distanciaMME9_pct']
    bb_upper = last_row['BB_Upper']
    bb_lower = last_row['BB_Lower']
    bb_middle = last_row['BB_Middle']
    
    print("\n🎯 BOLLINGER BANDS VISUAL:")
    print("=" * 50)
    
    # Criar escala visual
    scale_width = 40
    
    # Normalizar posição (0 = banda inferior, 1 = banda superior)
    if bb_upper != bb_lower:
        position = (distance - bb_lower) / (bb_upper - bb_lower)
        position = max(0, min(1, position))  # Limitar entre 0 e 1
    else:
        position = 0.5
    
    # Criar linha visual
    line = [" "] * scale_width
    pos_index = int(position * (scale_width - 1))
    line[pos_index] = "●"
    
    # Marcar bandas
    line[0] = "["  # Banda inferior
    line[-1] = "]"  # Banda superior
    line[scale_width//2] = "|"  # Banda média
    
    visual_line = "".join(line)
    
    print(f"Banda Superior: {bb_upper:+.2f}%")
    print(f"Banda Média:    {bb_middle:+.2f}%")
    print(f"Banda Inferior: {bb_lower:+.2f}%")
    print()
    print(f"Posição Atual:  {visual_line}")
    print(f"Distância:      {distance:+.2f}%")
    
    # Interpretação
    if position > 0.8:
        cprint("🔴 ZONA DE EXAUSTÃO DE ALTA!", "white", "on_red")
    elif position < 0.2:
        cprint("🟢 ZONA DE EXAUSTÃO DE BAIXA!", "white", "on_green")
    else:
        cprint("😐 ZONA NEUTRA", "white", "on_yellow")

def simulate_trading_session(token, periods=20):
    """Simula uma sessão de trading mostrando sinais em tempo real"""
    cprint(f"\n🎮 SIMULADOR DE TRADING - {token}", "white", "on_magenta")
    cprint("Simulando sinais em tempo real...", "white", "on_magenta")
    
    try:
        # Coletar dados
        data = collect_token_data(token, days_back=10, timeframe='3m')
        
        if data is None or len(data) < 200:
            cprint(f"❌ Dados insuficientes para {token}", "white", "on_red")
            return
        
        # Aplicar indicadores
        data = calculate_distance_mme9(data)
        data = calculate_bollinger_on_distance(data)
        data = detect_exhaustion_signals(data)
        
        # Simular últimos períodos
        start_idx = max(200, len(data) - periods)
        
        portfolio_value = 1000  # Começar com $1000 simulados
        position = 0  # 0 = sem posição, 1 = comprado, -1 = vendido
        entry_price = 0
        trades_count = 0
        winning_trades = 0
        
        cprint(f"\n💰 PORTFÓLIO INICIAL: ${portfolio_value:.2f}", "white", "on_blue")
        print("=" * 80)
        
        for i in range(start_idx, len(data)):
            current_data = data.iloc[:i+1]
            row = current_data.iloc[-1]
            
            print(f"\n⏰ Período {i+1-start_idx+1}/{periods}")
            print(f"💲 Preço: ${row['close']:.6f}")
            print(f"📊 Distância MME9: {row['distanciaMME9_pct']:+.2f}%")
            
            # Mostrar sinais
            signal_text = ""
            action_taken = False
            
            if row['reversao_alta'] and position <= 0:
                signal_text = "🟢 SINAL DE COMPRA!"
                if position == 0:  # Sem posição
                    position = 1
                    entry_price = row['close']
                    action_taken = True
                    trades_count += 1
                    cprint(f"✅ COMPRANDO a ${entry_price:.6f}", "white", "on_green")
                elif position == -1:  # Vendido, fechar posição
                    profit = (entry_price - row['close']) / entry_price * portfolio_value
                    portfolio_value += profit
                    if profit > 0:
                        winning_trades += 1
                        cprint(f"✅ FECHANDO VENDA com LUCRO: +${profit:.2f}", "white", "on_green")
                    else:
                        cprint(f"❌ FECHANDO VENDA com PREJUÍZO: ${profit:.2f}", "white", "on_red")
                    position = 1
                    entry_price = row['close']
                    trades_count += 1
                    cprint(f"✅ COMPRANDO a ${entry_price:.6f}", "white", "on_green")
                    
            elif row['reversao_baixa'] and position >= 0:
                signal_text = "🔴 SINAL DE VENDA!"
                if position == 0:  # Sem posição
                    position = -1
                    entry_price = row['close']
                    action_taken = True
                    trades_count += 1
                    cprint(f"✅ VENDENDO a ${entry_price:.6f}", "white", "on_red")
                elif position == 1:  # Comprado, fechar posição
                    profit = (row['close'] - entry_price) / entry_price * portfolio_value
                    portfolio_value += profit
                    if profit > 0:
                        winning_trades += 1
                        cprint(f"✅ FECHANDO COMPRA com LUCRO: +${profit:.2f}", "white", "on_green")
                    else:
                        cprint(f"❌ FECHANDO COMPRA com PREJUÍZO: ${profit:.2f}", "white", "on_red")
                    position = -1
                    entry_price = row['close']
                    trades_count += 1
                    cprint(f"✅ VENDENDO a ${entry_price:.6f}", "white", "on_red")
                    
            elif row['exaustao_alta']:
                signal_text = "⚠️ EXAUSTÃO DE ALTA - Aguardando reversão..."
            elif row['exaustao_baixa']:
                signal_text = "⚠️ EXAUSTÃO DE BAIXA - Aguardando reversão..."
            else:
                signal_text = "😐 Sem sinais"
            
            print(f"🎯 {signal_text}")
            
            # Status da posição
            if position == 1:
                current_profit = (row['close'] - entry_price) / entry_price * portfolio_value
                print(f"📈 POSIÇÃO: COMPRADO a ${entry_price:.6f} (P&L: ${current_profit:+.2f})")
            elif position == -1:
                current_profit = (entry_price - row['close']) / entry_price * portfolio_value
                print(f"📉 POSIÇÃO: VENDIDO a ${entry_price:.6f} (P&L: ${current_profit:+.2f})")
            else:
                print("💤 POSIÇÃO: SEM POSIÇÃO")
            
            print(f"💰 PORTFÓLIO: ${portfolio_value:.2f}")
            print("-" * 50)
            
            # Pausa para simular tempo real
            time.sleep(1)
        
        # Resumo final
        cprint(f"\n🏁 RESUMO DA SIMULAÇÃO", "white", "on_blue")
        print("=" * 50)
        print(f"💰 Portfólio Final: ${portfolio_value:.2f}")
        print(f"📈 Retorno: {((portfolio_value/1000)-1)*100:+.2f}%")
        print(f"🔄 Total de Trades: {trades_count}")
        if trades_count > 0:
            win_rate = (winning_trades / trades_count) * 100
            print(f"🎯 Taxa de Acerto: {win_rate:.1f}% ({winning_trades}/{trades_count})")
        
        # Fechar posição final se necessário
        if position != 0:
            final_row = data.iloc[-1]
            if position == 1:
                final_profit = (final_row['close'] - entry_price) / entry_price * portfolio_value
                print(f"📊 P&L da posição aberta: ${final_profit:+.2f}")
            else:
                final_profit = (entry_price - final_row['close']) / entry_price * portfolio_value
                print(f"📊 P&L da posição aberta: ${final_profit:+.2f}")
        
    except Exception as e:
        cprint(f"❌ Erro na simulação: {str(e)}", "white", "on_red")

def live_monitor(token):
    """Monitor em tempo real de um token"""
    cprint(f"\n📡 MONITOR EM TEMPO REAL - {token}", "white", "on_blue")
    cprint("Pressione Ctrl+C para parar", "white", "on_blue")
    
    try:
        while True:
            # Coletar dados atuais
            data = collect_token_data(token, days_back=5, timeframe='3m')
            
            if data is None or len(data) < 200:
                cprint(f"❌ Dados insuficientes", "white", "on_red")
                time.sleep(30)
                continue
            
            # Aplicar indicadores
            data = calculate_distance_mme9(data)
            data = calculate_bollinger_on_distance(data)
            data = detect_exhaustion_signals(data)
            
            # Limpar tela (funciona no terminal)
            os.system('clear' if os.name == 'posix' else 'cls')
            
            # Mostrar dados atuais
            last_row = data.iloc[-1]
            
            cprint(f"🎯 MONITOR LIVE - {token}", "white", "on_blue")
            print(f"⏰ Última atualização: {pd.Timestamp.now().strftime('%H:%M:%S')}")
            print("=" * 60)
            
            print(f"💲 Preço Atual: ${last_row['close']:.6f}")
            print(f"📊 MME9: ${last_row['MME9']:.6f}")
            print(f"📏 Distância: {last_row['distanciaMME9_pct']:+.2f}%")
            
            # Bollinger visual
            print_bollinger_visual(data)
            
            # Sinais atuais
            if last_row['reversao_alta']:
                cprint("\n🟢 SINAL DE COMPRA ATIVO!", "white", "on_green")
            elif last_row['reversao_baixa']:
                cprint("\n🔴 SINAL DE VENDA ATIVO!", "white", "on_red")
            elif last_row['exaustao_alta']:
                cprint("\n⚠️ EXAUSTÃO DE ALTA - Aguardando reversão", "white", "on_yellow")
            elif last_row['exaustao_baixa']:
                cprint("\n⚠️ EXAUSTÃO DE BAIXA - Aguardando reversão", "white", "on_yellow")
            else:
                cprint("\n😐 SEM SINAIS ATIVOS", "white", "on_cyan")
            
            # Aguardar próxima atualização
            print(f"\n⏳ Próxima atualização em 30 segundos...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        cprint("\n👋 Monitor interrompido pelo usuário", "white", "on_yellow")

if __name__ == "__main__":
    print("🎮 SIMULADOR VISUAL DA ESTRATÉGIA")
    print("=" * 50)
    print("1. Simulação de Trading (20 períodos)")
    print("2. Monitor em Tempo Real")
    print("3. Análise Visual Detalhada")
    
    try:
        choice = input("\nEscolha uma opção (1-3): ").strip()
        
        print(f"\nTokens disponíveis:")
        for i, token in enumerate(MONITORED_TOKENS, 1):
            print(f"{i}. {token}")
        
        token_choice = int(input("\nEscolha o número do token: ")) - 1
        if 0 <= token_choice < len(MONITORED_TOKENS):
            selected_token = MONITORED_TOKENS[token_choice]
            
            if choice == "1":
                simulate_trading_session(selected_token)
            elif choice == "2":
                live_monitor(selected_token)
            elif choice == "3":
                # Análise detalhada
                data = collect_token_data(selected_token, days_back=10, timeframe='3m')
                if data is not None and len(data) >= 200:
                    data = calculate_distance_mme9(data)
                    data = calculate_bollinger_on_distance(data)
                    data = detect_exhaustion_signals(data)
                    
                    print_chart_ascii(data)
                    print_bollinger_visual(data)
                    
                    # Estatísticas
                    cprint(f"\n📊 ESTATÍSTICAS GERAIS:", "white", "on_blue")
                    print(f"Total de períodos: {len(data)}")
                    print(f"Sinais de compra: {data['reversao_alta'].sum()}")
                    print(f"Sinais de venda: {data['reversao_baixa'].sum()}")
                    print(f"Períodos em exaustão: {(data['exaustao_alta'] | data['exaustao_baixa']).sum()}")
            else:
                print("❌ Opção inválida!")
        else:
            print("❌ Token inválido!")
            
    except KeyboardInterrupt:
        print("\n👋 Simulador interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")