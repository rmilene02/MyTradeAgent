"""
🌙 Teste Rápido com SOL
Testa a estratégia com Solana (token conhecido)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.ohlcv_collector import collect_token_data
from src.data.custom_indicators_simple import run_complete_analysis
from termcolor import colored, cprint
import pandas as pd

def test_sol_strategy():
    """Testa estratégia com SOL"""
    cprint("🌙 TESTE RÁPIDO - ESTRATÉGIA COM SOL", "white", "on_blue")
    cprint("=" * 50, "blue")
    
    # Endereço do SOL
    sol_address = "So11111111111111111111111111111111111111112"
    
    try:
        cprint(f"📊 Coletando dados do SOL...", "cyan")
        
        # Coletar dados
        df = collect_token_data(sol_address, days_back=30, timeframe="1H")
        
        if df is None or len(df) < 200:
            cprint("❌ Dados insuficientes para SOL", "red")
            return
        
        cprint(f"✅ Dados coletados: {len(df)} períodos", "green")
        cprint(f"📈 Preço atual: ${df['close'].iloc[-1]:.2f}", "yellow")
        cprint(f"📊 Período: {df['timestamp'].iloc[0]} até {df['timestamp'].iloc[-1]}", "white")
        
        # Executar análise
        cprint("\n🔍 Executando análise da estratégia...", "cyan")
        df_result, performance = run_complete_analysis(df)
        
        # Mostrar últimos sinais
        recent_signals = df_result[df_result['signal'] != 0].tail(5)
        if len(recent_signals) > 0:
            cprint("\n🎯 ÚLTIMOS 5 SINAIS:", "white", "on_blue")
            for _, signal in recent_signals.iterrows():
                signal_type = "🟢 COMPRA" if signal['signal'] == 1 else "🔴 VENDA"
                timestamp = signal['timestamp'].strftime('%Y-%m-%d %H:%M') if 'timestamp' in signal else 'N/A'
                cprint(f"{signal_type} - {timestamp} - ${signal['close']:.2f} - Força: {signal['signal_strength']:.4f}", 
                       "green" if signal['signal'] == 1 else "red")
        
        # Estatísticas
        buy_signals = len(df_result[df_result['signal'] == 1])
        sell_signals = len(df_result[df_result['signal'] == -1])
        
        cprint(f"\n📊 RESUMO DA ANÁLISE:", "white", "on_blue")
        cprint(f"📈 Sinais de COMPRA: {buy_signals}", "green")
        cprint(f"📉 Sinais de VENDA: {sell_signals}", "red")
        cprint(f"🎯 Total de sinais: {buy_signals + sell_signals}", "yellow")
        
        if 'signal_strength' in df_result.columns:
            avg_strength = df_result[df_result['signal'] != 0]['signal_strength'].mean()
            cprint(f"💪 Força média dos sinais: {avg_strength:.4f}", "magenta")
        
        cprint("\n✅ TESTE CONCLUÍDO COM SUCESSO!", "white", "on_green")
        
    except Exception as e:
        cprint(f"❌ Erro no teste: {e}", "red")
        cprint("💡 Verifique se as APIs estão configuradas corretamente", "yellow")

if __name__ == "__main__":
    test_sol_strategy()