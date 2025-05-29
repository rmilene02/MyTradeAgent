"""
🤖 Moon Dev's Multi-Asset AI Tester
Testa a IA em múltiplos ativos e compara performance
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_debug_demo import AIDebugDemo
import pandas as pd
import glob
from termcolor import colored, cprint

def test_all_assets():
    """Testa todos os ativos disponíveis"""
    cprint("🌙 MOON DEV'S MULTI-ASSET AI TESTER", "white", "on_blue")
    cprint("🤖 Testando IA em todos os ativos disponíveis", "white", "on_blue")
    cprint("=" * 70, "blue")
    
    csv_files = glob.glob("*.csv")
    
    if not csv_files:
        cprint("❌ Nenhum arquivo CSV encontrado!", "red")
        return
    
    results = []
    
    for csv_file in csv_files:
        cprint(f"\n🔍 TESTANDO: {csv_file}", "white", "on_cyan")
        cprint("-" * 50, "cyan")
        
        try:
            # Carregar dados
            df = pd.read_csv(csv_file)
            df.columns = df.columns.str.lower()
            df['timestamp'] = pd.to_datetime(df['datetime'])
            df = df.dropna()
            
            # Criar demo
            demo = AIDebugDemo()
            
            # Executar (sem mostrar detalhes)
            decisions, exhaustion_count = demo.run_debug_demo(df, max_periods=500)
            
            # Calcular métricas
            if demo.trades:
                winning_trades = [t for t in demo.trades if t['pnl'] > 0]
                total_return = ((demo.balance / demo.initial_balance) - 1) * 100
                win_rate = len(winning_trades) / len(demo.trades) * 100
                
                gross_profit = sum(t['pnl'] for t in winning_trades) if winning_trades else 0
                gross_loss = abs(sum(t['pnl'] for t in demo.trades if t['pnl'] < 0))
                profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
                
                actions_on_signals = len([d for d in decisions if (d['exhaustion_buy'] or d['exhaustion_sell']) and d['action'] != 'HOLD'])
                selectivity = (actions_on_signals / exhaustion_count * 100) if exhaustion_count > 0 else 0
                
                result = {
                    'asset': csv_file.replace('.csv', '').replace('-data', ''),
                    'profit_factor': profit_factor,
                    'total_return': total_return,
                    'win_rate': win_rate,
                    'total_trades': len(demo.trades),
                    'exhaustion_signals': exhaustion_count,
                    'selectivity': selectivity,
                    'final_balance': demo.balance
                }
                
                results.append(result)
                
                # Mostrar resumo
                pf_color = "green" if profit_factor > 1.5 else "yellow" if profit_factor > 1.0 else "red"
                cprint(f"💎 Profit Factor: {profit_factor:.3f}", pf_color)
                cprint(f"💰 Retorno: {total_return:+.2f}%", "green" if total_return > 0 else "red")
                cprint(f"🎲 Taxa de acerto: {win_rate:.1f}%", "green" if win_rate > 50 else "red")
                cprint(f"🔢 Trades: {len(demo.trades)} | Sinais: {exhaustion_count} | Seletividade: {selectivity:.1f}%", "cyan")
            
            else:
                cprint("❌ Nenhum trade realizado", "red")
        
        except Exception as e:
            cprint(f"❌ Erro ao processar {csv_file}: {e}", "red")
    
    # Ranking final
    if results:
        cprint(f"\n🏆 RANKING FINAL - PROFIT FACTOR", "white", "on_green")
        cprint("=" * 70, "green")
        
        # Ordenar por profit factor
        results.sort(key=lambda x: x['profit_factor'], reverse=True)
        
        for i, result in enumerate(results, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            pf_color = "green" if result['profit_factor'] > 1.5 else "yellow" if result['profit_factor'] > 1.0 else "red"
            
            cprint(f"{medal} {result['asset']:15s} | PF: {result['profit_factor']:6.3f} | "
                   f"Ret: {result['total_return']:+6.2f}% | "
                   f"WR: {result['win_rate']:5.1f}% | "
                   f"Trades: {result['total_trades']:2d}", pf_color)
        
        # Estatísticas gerais
        profitable_strategies = len([r for r in results if r['profit_factor'] > 1.0])
        avg_profit_factor = sum(r['profit_factor'] for r in results) / len(results)
        avg_return = sum(r['total_return'] for r in results) / len(results)
        total_trades = sum(r['total_trades'] for r in results)
        
        cprint(f"\n📊 ESTATÍSTICAS GERAIS:", "white", "on_blue")
        cprint(f"💰 Estratégias lucrativas: {profitable_strategies}/{len(results)}", "green")
        cprint(f"📈 Profit Factor médio: {avg_profit_factor:.3f}", "cyan")
        cprint(f"💵 Retorno médio: {avg_return:+.2f}%", "yellow")
        cprint(f"🔢 Total de trades: {total_trades}", "white")
        
        # Melhor configuração
        best = results[0]
        cprint(f"\n🎯 MELHOR ATIVO PARA SUA ESTRATÉGIA:", "white", "on_green")
        cprint(f"🏆 {best['asset']}", "green", attrs=['bold'])
        cprint(f"💎 Profit Factor: {best['profit_factor']:.3f}", "green")
        cprint(f"💰 Retorno: {best['total_return']:+.2f}%", "green")
        cprint(f"🎲 Taxa de acerto: {best['win_rate']:.1f}%", "green")
        cprint(f"🤖 Seletividade da IA: {best['selectivity']:.1f}%", "cyan")

if __name__ == "__main__":
    test_all_assets()