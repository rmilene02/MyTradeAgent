"""
🤖 Moon Dev's AI Demo Rápido
Demonstração da IA decidindo sobre sinais de exaustão
Versão acelerada para testes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from termcolor import colored, cprint
from dotenv import load_dotenv
import requests
import json
import time

load_dotenv()

class AIDemoRapido:
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
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
        
        # Bollinger Bands na distância
        rolling_mean = df['distance_ema9'].rolling(window=200).mean()
        rolling_std = df['distance_ema9'].rolling(window=200).std()
        
        df['bb_upper'] = rolling_mean + (rolling_std * 2)
        df['bb_lower'] = rolling_mean - (rolling_std * 2)
        
        # Sinais de exaustão
        df['exhaustion_buy'] = df['distance_ema9'] < df['bb_lower']
        df['exhaustion_sell'] = df['distance_ema9'] > df['bb_upper']
        
        # RSI para contexto
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        df['rsi'] = df['rsi'].fillna(50)
        
        return df
    
    def ask_ai_simple(self, context):
        """Versão simplificada da consulta IA"""
        
        # Fallback inteligente se não tiver API
        if not self.api_key:
            # Lógica baseada na estratégia original + filtros
            if context['exhaustion_buy'] and not self.current_position:
                if context['rsi'] < 35 and context['distance_ema9'] < -2:
                    return {'action': 'BUY', 'confidence': 0.8, 'reason': 'Exaustão forte + RSI baixo'}
                else:
                    return {'action': 'HOLD', 'confidence': 0.6, 'reason': 'Exaustão fraca, aguardando'}
            elif context['exhaustion_sell'] and self.current_position:
                if context['rsi'] > 65 and context['distance_ema9'] > 2:
                    return {'action': 'SELL', 'confidence': 0.8, 'reason': 'Exaustão forte + RSI alto'}
                else:
                    return {'action': 'HOLD', 'confidence': 0.6, 'reason': 'Exaustão fraca, mantendo posição'}
            else:
                return {'action': 'HOLD', 'confidence': 0.5, 'reason': 'Sem sinal de exaustão'}
        
        # Prompt simplificado para IA
        prompt = f"""
Estratégia Moon Dev - Exaustão de Mercado:

SINAIS DETECTADOS:
- Exaustão VENDA (comprar): {context['exhaustion_buy']}
- Exaustão COMPRA (vender): {context['exhaustion_sell']}
- Distância EMA9: {context['distance_ema9']:.2f}%
- RSI: {context['rsi']:.1f}

SITUAÇÃO:
- Preço: ${context['price']:.2f}
- Posição atual: {context['current_position'] or 'Nenhuma'}

Decida: BUY, SELL ou HOLD

JSON: {{"action": "BUY/SELL/HOLD", "confidence": 0.0-1.0, "reason": "motivo"}}
"""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 150
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=8)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                if '{' in content and '}' in content:
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    json_str = content[json_start:json_end]
                    decision = json.loads(json_str)
                    
                    if decision.get('action') in ['BUY', 'SELL', 'HOLD']:
                        return decision
            
        except Exception as e:
            pass
        
        # Fallback
        return {'action': 'HOLD', 'confidence': 0.5, 'reason': 'Erro API - aguardando'}
    
    def execute_trade(self, action, price, context):
        """Executa trade"""
        if action == 'BUY' and not self.current_position:
            shares = self.balance / price
            self.current_position = {
                'entry_price': price,
                'shares': shares,
                'entry_time': context['timestamp']
            }
            cprint(f"🟢 COMPRA: ${price:.2f} | RSI: {context['rsi']:.1f} | Dist: {context['distance_ema9']:.2f}%", "green")
            
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
            cprint(f"🔴 VENDA: ${price:.2f} | P&L: ${pnl:.2f} ({pnl_pct:+.2f}%) | RSI: {context['rsi']:.1f}", color)
    
    def run_demo(self, df, max_periods=200):
        """Executa demo rápido"""
        cprint("🤖 DEMO RÁPIDO - IA SMART TRADER", "white", "on_blue")
        cprint("📊 Sua estratégia + Decisão IA", "white", "on_blue")
        cprint("=" * 50, "blue")
        
        # Calcular indicadores
        df = self.calculate_strategy_indicators(df)
        
        # Usar apenas últimos períodos
        df = df.tail(max_periods)
        
        cprint(f"📊 Analisando {len(df)} períodos", "cyan")
        cprint(f"💰 Capital inicial: ${self.initial_balance:,.2f}", "yellow")
        
        decisions = []
        
        # Processar dados
        for i in range(200, len(df)):  # Pular aquecimento
            current = df.iloc[i]
            
            context = {
                'timestamp': current['timestamp'].strftime('%Y-%m-%d %H:%M'),
                'price': current['close'],
                'distance_ema9': current['distance_ema9'],
                'exhaustion_buy': bool(current['exhaustion_buy']),
                'exhaustion_sell': bool(current['exhaustion_sell']),
                'rsi': current['rsi'],
                'current_position': self.current_position
            }
            
            # IA decide
            decision = self.ask_ai_simple(context)
            
            decisions.append({
                'timestamp': context['timestamp'],
                'action': decision['action'],
                'reason': decision['reason'],
                'exhaustion_buy': context['exhaustion_buy'],
                'exhaustion_sell': context['exhaustion_sell']
            })
            
            # Executar se necessário
            if decision['action'] in ['BUY', 'SELL']:
                self.execute_trade(decision['action'], context['price'], context)
            
            # Mostrar progresso
            if len(decisions) % 20 == 0:
                cprint(f"⏳ Processados: {len(decisions)} | Trades: {len(self.trades)}", "cyan")
        
        # Fechar posição final
        if self.current_position:
            final_price = df.iloc[-1]['close']
            final_context = {
                'timestamp': df.iloc[-1]['timestamp'].strftime('%Y-%m-%d %H:%M'),
                'price': final_price,
                'rsi': df.iloc[-1]['rsi'],
                'distance_ema9': df.iloc[-1]['distance_ema9']
            }
            self.execute_trade('SELL', final_price, final_context)
        
        return decisions
    
    def show_results(self, decisions):
        """Mostra resultados"""
        if not self.trades:
            cprint("❌ Nenhum trade realizado", "red")
            return
        
        # Calcular métricas
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]
        
        total_return = ((self.balance / self.initial_balance) - 1) * 100
        win_rate = len(winning_trades) / len(self.trades) * 100
        
        gross_profit = sum(t['pnl'] for t in winning_trades) if winning_trades else 0
        gross_loss = abs(sum(t['pnl'] for t in losing_trades)) if losing_trades else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        cprint(f"\n🏆 RESULTADOS DO DEMO", "white", "on_green")
        cprint("=" * 40, "green")
        
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
        
        exhaustion_signals = len([d for d in decisions if d['exhaustion_buy'] or d['exhaustion_sell']])
        actions_on_signals = len([d for d in decisions if (d['exhaustion_buy'] or d['exhaustion_sell']) and d['action'] != 'HOLD'])
        
        cprint(f"\n🤖 INTELIGÊNCIA DA IA:", "white", "on_blue")
        cprint(f"🎯 Sinais de exaustão: {exhaustion_signals}", "yellow")
        cprint(f"⚡ Ações em sinais: {actions_on_signals}", "cyan")
        cprint(f"🧠 Seletividade: {(actions_on_signals/exhaustion_signals*100) if exhaustion_signals > 0 else 0:.1f}%", "magenta")
        cprint(f"🟢 Compras: {buy_actions} | 🔴 Vendas: {sell_actions} | ⚪ Hold: {hold_actions}", "white")
        
        # Últimos trades
        if len(self.trades) > 0:
            cprint(f"\n📊 ÚLTIMOS TRADES:", "white", "on_blue")
            for trade in self.trades[-3:]:
                color = "green" if trade['pnl'] > 0 else "red"
                cprint(f"${trade['entry_price']:.2f} → ${trade['exit_price']:.2f} | {trade['pnl_pct']:+.2f}%", color)

def test_demo(csv_file):
    """Testa demo rápido"""
    cprint(f"🚀 DEMO RÁPIDO: {csv_file}", "white", "on_blue")
    
    # Carregar dados
    df = pd.read_csv(csv_file)
    df.columns = df.columns.str.lower()
    df['timestamp'] = pd.to_datetime(df['datetime'])
    df = df.dropna()
    
    # Criar demo
    demo = AIDemoRapido()
    
    # Executar
    decisions = demo.run_demo(df)
    
    # Mostrar resultados
    demo.show_results(decisions)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_demo(sys.argv[1])
    else:
        test_demo("BTC-6h-1000wks-data.csv")