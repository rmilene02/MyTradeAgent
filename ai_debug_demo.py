"""
🤖 Moon Dev's AI Debug Demo
Mostra exatamente o que a IA está vendo e decidindo
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from termcolor import colored, cprint

class AIDebugDemo:
    def __init__(self):
        self.trades = []
        self.current_position = None
        self.balance = 10000
        self.initial_balance = 10000
        
    def calculate_strategy_indicators(self, df):
        """Calcula indicadores da estratégia Moon Dev"""
        # EMA 9
        df['ema9'] = df['close'].ewm(span=9).mean()
        
        # Distância percentual
        df['distance_ema9'] = ((df['close'] - df['ema9']) / df['ema9']) * 100
        
        # Bollinger Bands na distância (período menor para mais sinais)
        rolling_mean = df['distance_ema9'].rolling(window=50).mean()
        rolling_std = df['distance_ema9'].rolling(window=50).std()
        
        df['bb_upper'] = rolling_mean + (rolling_std * 2)
        df['bb_lower'] = rolling_mean - (rolling_std * 2)
        
        # Sinais de exaustão
        df['exhaustion_buy'] = df['distance_ema9'] < df['bb_lower']
        df['exhaustion_sell'] = df['distance_ema9'] > df['bb_upper']
        
        # Força da exaustão
        df['exhaustion_strength_buy'] = np.where(
            df['exhaustion_buy'], 
            abs((df['distance_ema9'] - df['bb_lower']) / df['bb_lower']), 
            0
        )
        
        df['exhaustion_strength_sell'] = np.where(
            df['exhaustion_sell'], 
            abs((df['distance_ema9'] - df['bb_upper']) / df['bb_upper']), 
            0
        )
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        df['rsi'] = df['rsi'].fillna(50)
        
        return df
    
    def ai_decision_logic(self, context):
        """Lógica de decisão da IA (simulada)"""
        
        # Regras inteligentes baseadas na estratégia
        if context['exhaustion_buy'] and not self.current_position:
            # Filtros para compra
            if (context['rsi'] < 40 and 
                context['distance_ema9'] < -1.5 and 
                context['exhaustion_strength_buy'] > 0.1):
                return {'action': 'BUY', 'confidence': 0.8, 'reason': 'Exaustão forte de venda + RSI baixo'}
            elif context['exhaustion_strength_buy'] > 0.05:
                return {'action': 'BUY', 'confidence': 0.6, 'reason': 'Exaustão moderada de venda'}
            else:
                return {'action': 'HOLD', 'confidence': 0.4, 'reason': 'Exaustão fraca, aguardando'}
                
        elif context['exhaustion_sell'] and self.current_position:
            # Filtros para venda
            if (context['rsi'] > 60 and 
                context['distance_ema9'] > 1.5 and 
                context['exhaustion_strength_sell'] > 0.1):
                return {'action': 'SELL', 'confidence': 0.8, 'reason': 'Exaustão forte de compra + RSI alto'}
            elif context['exhaustion_strength_sell'] > 0.05:
                return {'action': 'SELL', 'confidence': 0.6, 'reason': 'Exaustão moderada de compra'}
            else:
                return {'action': 'HOLD', 'confidence': 0.4, 'reason': 'Exaustão fraca, mantendo posição'}
        
        else:
            return {'action': 'HOLD', 'confidence': 0.3, 'reason': 'Sem sinal de exaustão'}
    
    def execute_trade(self, action, price, context):
        """Executa trade"""
        if action == 'BUY' and not self.current_position:
            shares = self.balance / price
            self.current_position = {
                'entry_price': price,
                'shares': shares,
                'entry_time': context['timestamp']
            }
            cprint(f"🟢 COMPRA: ${price:.2f} | Força: {context['exhaustion_strength_buy']:.3f} | RSI: {context['rsi']:.1f}", "green")
            
        elif action == 'SELL' and self.current_position:
            entry_price = self.current_position['entry_price']
            shares = self.current_position['shares']
            
            pnl = (price - entry_price) * shares
            pnl_pct = ((price / entry_price) - 1) * 100
            
            self.balance = shares * price
            
            trade = {
                'entry_price': entry_price,
                'exit_price': price,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'entry_time': self.current_position['entry_time'],
                'exit_time': context['timestamp']
            }
            
            self.trades.append(trade)
            self.current_position = None
            
            color = "green" if pnl > 0 else "red"
            cprint(f"🔴 VENDA: ${price:.2f} | P&L: ${pnl:.2f} ({pnl_pct:+.2f}%) | Força: {context['exhaustion_strength_sell']:.3f}", color)
    
    def run_debug_demo(self, df, max_periods=500):
        """Executa demo com debug detalhado"""
        cprint("🤖 DEBUG DEMO - IA ANALISANDO EXAUSTÃO", "white", "on_blue")
        cprint("=" * 60, "blue")
        
        # Calcular indicadores
        df = self.calculate_strategy_indicators(df)
        
        # Usar últimos períodos
        df = df.tail(max_periods)
        
        cprint(f"📊 Analisando {len(df)} períodos", "cyan")
        cprint(f"💰 Capital inicial: ${self.initial_balance:,.2f}", "yellow")
        
        decisions = []
        exhaustion_count = 0
        
        # Processar dados
        for i in range(60, len(df)):  # Período de aquecimento menor
            current = df.iloc[i]
            
            # Verificar se há dados válidos
            if pd.isna(current['bb_upper']) or pd.isna(current['bb_lower']):
                continue
            
            context = {
                'timestamp': current['timestamp'].strftime('%Y-%m-%d %H:%M'),
                'price': current['close'],
                'distance_ema9': current['distance_ema9'],
                'bb_upper': current['bb_upper'],
                'bb_lower': current['bb_lower'],
                'exhaustion_buy': bool(current['exhaustion_buy']),
                'exhaustion_sell': bool(current['exhaustion_sell']),
                'exhaustion_strength_buy': current['exhaustion_strength_buy'],
                'exhaustion_strength_sell': current['exhaustion_strength_sell'],
                'rsi': current['rsi'],
                'current_position': self.current_position
            }
            
            # Contar sinais de exaustão
            if context['exhaustion_buy'] or context['exhaustion_sell']:
                exhaustion_count += 1
                
                # Mostrar detalhes dos sinais
                if exhaustion_count <= 10:  # Mostrar primeiros 10
                    signal_type = "🟢 EXAUSTÃO VENDA" if context['exhaustion_buy'] else "🔴 EXAUSTÃO COMPRA"
                    strength = context['exhaustion_strength_buy'] if context['exhaustion_buy'] else context['exhaustion_strength_sell']
                    cprint(f"{signal_type} | ${context['price']:.2f} | Dist: {context['distance_ema9']:.2f}% | Força: {strength:.3f} | RSI: {context['rsi']:.1f}", 
                           "cyan")
            
            # IA decide
            decision = self.ai_decision_logic(context)
            
            decisions.append({
                'timestamp': context['timestamp'],
                'action': decision['action'],
                'reason': decision['reason'],
                'confidence': decision['confidence'],
                'exhaustion_buy': context['exhaustion_buy'],
                'exhaustion_sell': context['exhaustion_sell']
            })
            
            # Executar trade
            if decision['action'] in ['BUY', 'SELL']:
                self.execute_trade(decision['action'], context['price'], context)
                cprint(f"   └─ Decisão IA: {decision['action']} (Conf: {decision['confidence']:.1f}) - {decision['reason']}", "yellow")
        
        # Fechar posição final
        if self.current_position:
            final_price = df.iloc[-1]['close']
            final_context = {
                'timestamp': df.iloc[-1]['timestamp'].strftime('%Y-%m-%d %H:%M'),
                'price': final_price,
                'rsi': df.iloc[-1]['rsi'],
                'exhaustion_strength_sell': df.iloc[-1]['exhaustion_strength_sell']
            }
            self.execute_trade('SELL', final_price, final_context)
            cprint("🔄 Posição fechada ao final do período", "yellow")
        
        return decisions, exhaustion_count
    
    def show_results(self, decisions, exhaustion_count):
        """Mostra resultados detalhados"""
        cprint(f"\n🏆 RESULTADOS DO DEBUG DEMO", "white", "on_green")
        cprint("=" * 50, "green")
        
        # Estatísticas de sinais
        cprint(f"🎯 Sinais de exaustão detectados: {exhaustion_count}", "yellow")
        
        if not self.trades:
            cprint("❌ Nenhum trade executado", "red")
            
            # Analisar por que não houve trades
            buy_signals = len([d for d in decisions if d['exhaustion_buy']])
            sell_signals = len([d for d in decisions if d['exhaustion_sell']])
            
            cprint(f"\n📊 ANÁLISE DOS SINAIS:", "white", "on_blue")
            cprint(f"🟢 Sinais de compra (exaustão venda): {buy_signals}", "green")
            cprint(f"🔴 Sinais de venda (exaustão compra): {sell_signals}", "red")
            
            # Mostrar algumas decisões
            cprint(f"\n🤖 ÚLTIMAS DECISÕES DA IA:", "white", "on_blue")
            for decision in decisions[-5:]:
                action_color = "green" if decision['action'] == 'BUY' else "red" if decision['action'] == 'SELL' else "white"
                cprint(f"{decision['action']:4s} | Conf: {decision['confidence']:.1f} | {decision['reason']}", action_color)
            
            return
        
        # Calcular métricas
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]
        
        total_return = ((self.balance / self.initial_balance) - 1) * 100
        win_rate = len(winning_trades) / len(self.trades) * 100
        
        gross_profit = sum(t['pnl'] for t in winning_trades) if winning_trades else 0
        gross_loss = abs(sum(t['pnl'] for t in losing_trades)) if losing_trades else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Profit Factor em destaque
        pf_color = "green" if profit_factor > 1.5 else "yellow" if profit_factor > 1.0 else "red"
        cprint(f"💎 PROFIT FACTOR: {profit_factor:.3f}", pf_color, attrs=['bold'])
        
        cprint(f"💰 Retorno: {total_return:+.2f}%", "green" if total_return > 0 else "red")
        cprint(f"💵 Saldo final: ${self.balance:,.2f}", "yellow")
        cprint(f"🎲 Taxa de acerto: {win_rate:.1f}%", "green" if win_rate > 50 else "red")
        cprint(f"🔢 Total de trades: {len(self.trades)}", "white")
        
        # Análise de decisões
        buy_actions = len([d for d in decisions if d['action'] == 'BUY'])
        sell_actions = len([d for d in decisions if d['action'] == 'SELL'])
        hold_actions = len([d for d in decisions if d['action'] == 'HOLD'])
        
        actions_on_signals = len([d for d in decisions if (d['exhaustion_buy'] or d['exhaustion_sell']) and d['action'] != 'HOLD'])
        
        cprint(f"\n🤖 INTELIGÊNCIA DA IA:", "white", "on_blue")
        cprint(f"⚡ Ações em sinais de exaustão: {actions_on_signals}/{exhaustion_count}", "cyan")
        cprint(f"🧠 Taxa de seletividade: {(actions_on_signals/exhaustion_count*100) if exhaustion_count > 0 else 0:.1f}%", "magenta")
        cprint(f"🟢 Compras: {buy_actions} | 🔴 Vendas: {sell_actions} | ⚪ Hold: {hold_actions}", "white")
        
        # Todos os trades
        if len(self.trades) > 0:
            cprint(f"\n📊 TODOS OS TRADES:", "white", "on_blue")
            for i, trade in enumerate(self.trades, 1):
                color = "green" if trade['pnl'] > 0 else "red"
                cprint(f"{i}. ${trade['entry_price']:.2f} → ${trade['exit_price']:.2f} | {trade['pnl_pct']:+.2f}% | ${trade['pnl']:+.2f}", color)

def test_debug_demo(csv_file):
    """Testa demo com debug"""
    cprint(f"🔍 DEBUG DEMO: {csv_file}", "white", "on_blue")
    
    # Carregar dados
    df = pd.read_csv(csv_file)
    df.columns = df.columns.str.lower()
    df['timestamp'] = pd.to_datetime(df['datetime'])
    df = df.dropna()
    
    # Criar demo
    demo = AIDebugDemo()
    
    # Executar
    decisions, exhaustion_count = demo.run_debug_demo(df)
    
    # Mostrar resultados
    demo.show_results(decisions, exhaustion_count)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_debug_demo(sys.argv[1])
    else:
        test_debug_demo("BTC-5m-30wks-data.csv")