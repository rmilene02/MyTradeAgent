"""
🤖 Moon Dev's AI Smart Trader
Estratégia: Distância EMA9 + Bollinger Bands (sua estratégia original)
IA Decide: QUANDO entrar/sair nos sinais de exaustão
Métricas: Profit Factor, Win Rate, Drawdown completo
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
from datetime import datetime
import time

load_dotenv()

class AISmartTrader:
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.trades = []
        self.current_position = None
        self.balance = 10000  # Capital inicial
        self.initial_balance = 10000
        self.equity_curve = []
        
    def calculate_strategy_indicators(self, df, ema_period=9, bb_period=200, bb_std=2):
        """Calcula sua estratégia original: Distância EMA9 + Bollinger Bands"""
        
        # EMA 9
        df['ema9'] = df['close'].ewm(span=ema_period).mean()
        
        # Distância percentual da EMA9
        df['distance_ema9'] = ((df['close'] - df['ema9']) / df['ema9']) * 100
        
        # Bollinger Bands na distância
        rolling_mean = df['distance_ema9'].rolling(window=bb_period).mean()
        rolling_std = df['distance_ema9'].rolling(window=bb_period).std()
        
        df['bb_upper'] = rolling_mean + (rolling_std * bb_std)
        df['bb_middle'] = rolling_mean
        df['bb_lower'] = rolling_mean - (rolling_std * bb_std)
        
        # Sinais de exaustão (sua estratégia original)
        df['exhaustion_buy'] = df['distance_ema9'] < df['bb_lower']  # Abaixo da banda = exaustão de venda
        df['exhaustion_sell'] = df['distance_ema9'] > df['bb_upper']  # Acima da banda = exaustão de compra
        
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
        
        # Indicadores adicionais para contexto
        df['rsi'] = self.calculate_rsi(df['close'], 14)
        df['volume_sma'] = df['volume'].rolling(20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        return df
    
    def calculate_rsi(self, prices, period=14):
        """Calcula RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    
    def prepare_ai_context(self, df, index):
        """Prepara contexto completo para a IA"""
        if index < 250:  # Precisa de histórico para Bollinger Bands
            return None
            
        current = df.iloc[index]
        recent = df.iloc[max(0, index-10):index+1]  # Últimos 10 períodos
        
        # Verificar sinais de exaustão recentes (últimos 5 períodos)
        recent_exhaustion_buy = df.iloc[max(0, index-5):index+1]['exhaustion_buy'].any()
        recent_exhaustion_sell = df.iloc[max(0, index-5):index+1]['exhaustion_sell'].any()
        
        # Contar períodos desde última exaustão
        periods_since_buy_exhaustion = 0
        periods_since_sell_exhaustion = 0
        
        for i in range(index, max(0, index-20), -1):
            if df.iloc[i]['exhaustion_buy'] and periods_since_buy_exhaustion == 0:
                periods_since_buy_exhaustion = index - i
            if df.iloc[i]['exhaustion_sell'] and periods_since_sell_exhaustion == 0:
                periods_since_sell_exhaustion = index - i
        
        # Contexto do mercado
        price_change_1 = ((current['close'] - df.iloc[index-1]['close']) / df.iloc[index-1]['close']) * 100
        price_change_5 = ((current['close'] - df.iloc[index-5]['close']) / df.iloc[index-5]['close']) * 100 if index >= 5 else 0
        
        context = {
            'timestamp': current['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'price': current['close'],
            'volume': current['volume'],
            'volume_ratio': current['volume_ratio'],
            
            # Sua estratégia original
            'ema9': current['ema9'],
            'distance_ema9': current['distance_ema9'],
            'bb_upper': current['bb_upper'],
            'bb_middle': current['bb_middle'],
            'bb_lower': current['bb_lower'],
            
            # Sinais de exaustão ATUAIS
            'exhaustion_buy_now': bool(current['exhaustion_buy']),
            'exhaustion_sell_now': bool(current['exhaustion_sell']),
            'exhaustion_strength_buy': current['exhaustion_strength_buy'],
            'exhaustion_strength_sell': current['exhaustion_strength_sell'],
            
            # Histórico de exaustão
            'recent_exhaustion_buy': recent_exhaustion_buy,
            'recent_exhaustion_sell': recent_exhaustion_sell,
            'periods_since_buy_exhaustion': periods_since_buy_exhaustion,
            'periods_since_sell_exhaustion': periods_since_sell_exhaustion,
            
            # Contexto adicional
            'rsi': current['rsi'],
            'price_change_1period': price_change_1,
            'price_change_5periods': price_change_5,
            
            # Situação atual
            'current_position': self.current_position,
            'balance': self.balance,
            'total_trades': len(self.trades)
        }
        
        return context
    
    def ask_ai_decision(self, context):
        """Pergunta para a IA se deve agir nos sinais de exaustão"""
        
        # Fallback se não tiver API
        if not self.api_key:
            # Lógica simples baseada na estratégia original
            if context['exhaustion_buy_now'] and not self.current_position and context['rsi'] < 40:
                return {'action': 'BUY', 'confidence': 0.7, 'reason': 'Exaustão de venda + RSI baixo (fallback)'}
            elif context['exhaustion_sell_now'] and self.current_position and context['rsi'] > 60:
                return {'action': 'SELL', 'confidence': 0.7, 'reason': 'Exaustão de compra + RSI alto (fallback)'}
            else:
                return {'action': 'HOLD', 'confidence': 0.5, 'reason': 'Aguardando melhor momento (fallback)'}
        
        prompt = f"""
Você é um trader expert usando a estratégia Moon Dev de exaustão de mercado.

ESTRATÉGIA BASE:
- Distância do preço da EMA9: {context['distance_ema9']:.3f}%
- Bollinger Bands: Superior {context['bb_upper']:.3f}% | Inferior {context['bb_lower']:.3f}%
- Exaustão = preço fora das Bollinger Bands da distância EMA9

SINAIS DE EXAUSTÃO DETECTADOS:
- 🔴 Exaustão de COMPRA agora: {context['exhaustion_sell_now']} (força: {context['exhaustion_strength_sell']:.3f})
- 🟢 Exaustão de VENDA agora: {context['exhaustion_buy_now']} (força: {context['exhaustion_strength_buy']:.3f})

HISTÓRICO RECENTE:
- Exaustão de venda nos últimos 5 períodos: {context['recent_exhaustion_buy']}
- Exaustão de compra nos últimos 5 períodos: {context['recent_exhaustion_sell']}
- Períodos desde última exaustão de venda: {context['periods_since_buy_exhaustion']}
- Períodos desde última exaustão de compra: {context['periods_since_sell_exhaustion']}

CONTEXTO DO MERCADO:
- Preço atual: ${context['price']:.2f}
- EMA9: ${context['ema9']:.2f}
- RSI: {context['rsi']:.1f}
- Mudança 1 período: {context['price_change_1period']:+.2f}%
- Mudança 5 períodos: {context['price_change_5periods']:+.2f}%
- Volume vs média: {context['volume_ratio']:.2f}x

SITUAÇÃO ATUAL:
- Posição: {context['current_position'] or 'Nenhuma'}
- Saldo: ${context['balance']:.2f}
- Trades: {context['total_trades']}

DECISÃO REQUERIDA:
Mesmo detectando exaustão, você decide QUANDO agir. Considere:
- Força da exaustão
- Contexto do mercado (RSI, volume, momentum)
- Timing ideal para entrada/saída
- Falsos sinais vs sinais válidos

Responda APENAS em JSON:
{{
    "action": "BUY" ou "SELL" ou "HOLD",
    "confidence": 0.0 a 1.0,
    "reason": "explicação da decisão baseada na exaustão"
}}

REGRAS:
- BUY apenas se não tiver posição E detectar boa oportunidade de exaustão de venda
- SELL apenas se tiver posição E detectar boa oportunidade de exaustão de compra
- HOLD se não for o momento ideal, mesmo com sinal de exaustão
"""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,  # Mais conservador
                "max_tokens": 300
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                # Extrair JSON
                if '{' in content and '}' in content:
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    json_str = content[json_start:json_end]
                    decision = json.loads(json_str)
                    
                    if decision.get('action') in ['BUY', 'SELL', 'HOLD']:
                        return decision
            
        except Exception as e:
            cprint(f"⚠️  Erro na API: {e}", "yellow")
        
        # Fallback
        return {'action': 'HOLD', 'confidence': 0.5, 'reason': 'API error - aguardando'}
    
    def execute_trade(self, action, price, context):
        """Executa trade e registra na equity curve"""
        timestamp = context['timestamp']
        
        if action == 'BUY' and not self.current_position:
            # Comprar
            shares = self.balance / price
            self.current_position = {
                'type': 'LONG',
                'entry_price': price,
                'shares': shares,
                'entry_time': timestamp,
                'entry_context': context.copy()
            }
            
            cprint(f"🟢 COMPRA: ${price:.2f} | Ações: {shares:.4f} | Exaustão: {context['exhaustion_buy_now']}", "green")
            
        elif action == 'SELL' and self.current_position:
            # Vender
            entry_price = self.current_position['entry_price']
            shares = self.current_position['shares']
            
            # Calcular P&L
            pnl = (price - entry_price) * shares
            pnl_pct = ((price / entry_price) - 1) * 100
            
            # Atualizar saldo
            self.balance = shares * price
            
            # Registrar trade
            trade = {
                'entry_time': self.current_position['entry_time'],
                'exit_time': timestamp,
                'entry_price': entry_price,
                'exit_price': price,
                'shares': shares,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'entry_exhaustion': self.current_position['entry_context'].get('exhaustion_buy_now', False),
                'exit_exhaustion': context.get('exhaustion_sell_now', False),
                'entry_strength': self.current_position['entry_context'].get('exhaustion_strength_buy', 0),
                'exit_strength': context.get('exhaustion_strength_sell', 0)
            }
            
            self.trades.append(trade)
            self.current_position = None
            
            color = "green" if pnl > 0 else "red"
            cprint(f"🔴 VENDA: ${price:.2f} | P&L: ${pnl:.2f} ({pnl_pct:+.2f}%) | Exaustão: {context['exhaustion_sell_now']}", color)
        
        # Registrar equity curve
        current_equity = self.balance
        if self.current_position:
            current_equity = self.current_position['shares'] * price
        
        self.equity_curve.append({
            'timestamp': timestamp,
            'equity': current_equity,
            'price': price
        })
    
    def calculate_advanced_metrics(self):
        """Calcula métricas avançadas incluindo Profit Factor"""
        if not self.trades:
            return None
        
        # Separar trades
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]
        
        # Métricas básicas
        total_trades = len(self.trades)
        win_rate = len(winning_trades) / total_trades * 100
        
        # P&L
        total_pnl = sum(t['pnl'] for t in self.trades)
        total_return = ((self.balance / self.initial_balance) - 1) * 100
        
        # PROFIT FACTOR (métrica chave!)
        gross_profit = sum(t['pnl'] for t in winning_trades) if winning_trades else 0
        gross_loss = abs(sum(t['pnl'] for t in losing_trades)) if losing_trades else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Médias
        avg_win = gross_profit / len(winning_trades) if winning_trades else 0
        avg_loss = gross_loss / len(losing_trades) if losing_trades else 0
        
        # Expectativa matemática
        expectancy = (win_rate/100 * avg_win) - ((100-win_rate)/100 * avg_loss)
        
        # Drawdown máximo
        peak_equity = self.initial_balance
        max_drawdown = 0
        max_drawdown_pct = 0
        
        for point in self.equity_curve:
            equity = point['equity']
            if equity > peak_equity:
                peak_equity = equity
            
            drawdown = peak_equity - equity
            drawdown_pct = (drawdown / peak_equity) * 100
            
            max_drawdown = max(max_drawdown, drawdown)
            max_drawdown_pct = max(max_drawdown_pct, drawdown_pct)
        
        # Análise de exaustão
        exhaustion_entry_trades = [t for t in self.trades if t.get('entry_exhaustion', False)]
        exhaustion_exit_trades = [t for t in self.trades if t.get('exit_exhaustion', False)]
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_return': total_return,
            'profit_factor': profit_factor,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'expectancy': expectancy,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown_pct,
            'final_balance': self.balance,
            'exhaustion_entry_rate': len(exhaustion_entry_trades) / total_trades * 100,
            'exhaustion_exit_rate': len(exhaustion_exit_trades) / total_trades * 100,
            'avg_entry_strength': np.mean([t.get('entry_strength', 0) for t in self.trades]),
            'avg_exit_strength': np.mean([t.get('exit_strength', 0) for t in self.trades])
        }
    
    def run_backtest(self, df, sample_size=1000):
        """Executa backtest com IA decidindo sobre sinais de exaustão"""
        cprint("🤖 BACKTEST IA SMART TRADER - ESTRATÉGIA MOON DEV", "white", "on_blue")
        cprint("📊 Distância EMA9 + Bollinger Bands + Decisão IA", "white", "on_blue")
        cprint("=" * 60, "blue")
        
        # Calcular indicadores da estratégia
        df = self.calculate_strategy_indicators(df)
        
        # Usar amostra se necessário
        if len(df) > sample_size:
            df = df.tail(sample_size)
            cprint(f"📊 Usando {len(df)} períodos (dados recentes)", "cyan")
        
        cprint(f"💰 Capital inicial: ${self.initial_balance:,.2f}", "yellow")
        cprint(f"📅 Período: {df['timestamp'].min()} até {df['timestamp'].max()}", "white")
        
        decisions_log = []
        
        # Executar backtest
        for i in range(250, len(df)):  # Começar após período de aquecimento
            context = self.prepare_ai_context(df, i)
            if not context:
                continue
            
            # IA decide sobre os sinais de exaustão
            decision = self.ask_ai_decision(context)
            
            # Log da decisão
            decisions_log.append({
                'timestamp': context['timestamp'],
                'price': context['price'],
                'action': decision['action'],
                'confidence': decision['confidence'],
                'reason': decision['reason'],
                'exhaustion_buy': context['exhaustion_buy_now'],
                'exhaustion_sell': context['exhaustion_sell_now']
            })
            
            # Executar trade
            if decision['action'] in ['BUY', 'SELL']:
                self.execute_trade(decision['action'], context['price'], context)
            else:
                # Ainda registrar na equity curve para HOLD
                current_equity = self.balance
                if self.current_position:
                    current_equity = self.current_position['shares'] * context['price']
                
                self.equity_curve.append({
                    'timestamp': context['timestamp'],
                    'equity': current_equity,
                    'price': context['price']
                })
            
            # Progresso
            if len(decisions_log) % 100 == 0:
                progress = (i / len(df)) * 100
                cprint(f"⏳ {progress:.1f}% | Decisões: {len(decisions_log)} | Trades: {len(self.trades)}", "cyan")
        
        # Fechar posição final
        if self.current_position:
            final_context = self.prepare_ai_context(df, len(df)-1)
            self.execute_trade('SELL', final_context['price'], final_context)
        
        return decisions_log
    
    def display_results(self, decisions_log):
        """Mostra resultados com foco no Profit Factor"""
        metrics = self.calculate_advanced_metrics()
        
        if not metrics:
            cprint("❌ Nenhum trade realizado", "red")
            return
        
        cprint(f"\n🏆 RESULTADOS - IA SMART TRADER", "white", "on_green")
        cprint("=" * 60, "green")
        
        # PROFIT FACTOR em destaque
        pf_color = "green" if metrics['profit_factor'] > 1.5 else "yellow" if metrics['profit_factor'] > 1.0 else "red"
        cprint(f"💎 PROFIT FACTOR: {metrics['profit_factor']:.3f}", pf_color, attrs=['bold'])
        
        if metrics['profit_factor'] > 2.0:
            cprint("🚀 EXCELENTE! Profit Factor > 2.0", "green")
        elif metrics['profit_factor'] > 1.5:
            cprint("✅ BOM! Profit Factor > 1.5", "yellow")
        elif metrics['profit_factor'] > 1.0:
            cprint("📊 POSITIVO! Profit Factor > 1.0", "white")
        else:
            cprint("❌ NEGATIVO! Profit Factor < 1.0", "red")
        
        # Performance geral
        cprint(f"\n📊 PERFORMANCE:", "white", "on_blue")
        cprint(f"💰 Retorno Total: {metrics['total_return']:+.2f}%", "green" if metrics['total_return'] > 0 else "red")
        cprint(f"💵 Saldo Final: ${metrics['final_balance']:,.2f}", "yellow")
        cprint(f"🎲 Taxa de Acerto: {metrics['win_rate']:.2f}%", "green" if metrics['win_rate'] > 50 else "red")
        
        # Análise detalhada
        cprint(f"\n💹 ANÁLISE FINANCEIRA:", "white", "on_blue")
        cprint(f"💚 Lucro Bruto: ${metrics['gross_profit']:,.2f}", "green")
        cprint(f"💔 Perda Bruta: ${metrics['gross_loss']:,.2f}", "red")
        cprint(f"📊 Ganho Médio: ${metrics['avg_win']:,.2f}", "green")
        cprint(f"📉 Perda Média: ${metrics['avg_loss']:,.2f}", "red")
        cprint(f"🎯 Expectativa: ${metrics['expectancy']:,.2f}", "green" if metrics['expectancy'] > 0 else "red")
        
        # Risco
        cprint(f"\n⚠️  GESTÃO DE RISCO:", "white", "on_blue")
        cprint(f"📉 Drawdown Máximo: ${metrics['max_drawdown']:,.2f} ({metrics['max_drawdown_pct']:.2f}%)", "red")
        
        # Análise da estratégia de exaustão
        cprint(f"\n🎯 ANÁLISE DA ESTRATÉGIA DE EXAUSTÃO:", "white", "on_blue")
        cprint(f"🟢 Entradas em exaustão: {metrics['exhaustion_entry_rate']:.1f}%", "green")
        cprint(f"🔴 Saídas em exaustão: {metrics['exhaustion_exit_rate']:.1f}%", "red")
        cprint(f"💪 Força média entrada: {metrics['avg_entry_strength']:.4f}", "cyan")
        cprint(f"💪 Força média saída: {metrics['avg_exit_strength']:.4f}", "cyan")
        
        # Trades
        cprint(f"\n🔢 ESTATÍSTICAS DE TRADES:", "white", "on_blue")
        cprint(f"📊 Total: {metrics['total_trades']}", "white")
        cprint(f"✅ Vencedores: {metrics['winning_trades']}", "green")
        cprint(f"❌ Perdedores: {metrics['losing_trades']}", "red")
        
        # Decisões da IA
        buy_decisions = len([d for d in decisions_log if d['action'] == 'BUY'])
        sell_decisions = len([d for d in decisions_log if d['action'] == 'SELL'])
        hold_decisions = len([d for d in decisions_log if d['action'] == 'HOLD'])
        
        # Análise de sinais vs ações
        exhaustion_signals = len([d for d in decisions_log if d['exhaustion_buy'] or d['exhaustion_sell']])
        actions_on_signals = len([d for d in decisions_log if (d['exhaustion_buy'] or d['exhaustion_sell']) and d['action'] != 'HOLD'])
        
        cprint(f"\n🤖 INTELIGÊNCIA DA IA:", "white", "on_blue")
        cprint(f"🎯 Sinais de exaustão detectados: {exhaustion_signals}", "yellow")
        cprint(f"⚡ Ações tomadas em sinais: {actions_on_signals}", "cyan")
        cprint(f"🧠 Taxa de seletividade: {(actions_on_signals/exhaustion_signals*100) if exhaustion_signals > 0 else 0:.1f}%", "magenta")
        cprint(f"🟢 Decisões COMPRA: {buy_decisions}", "green")
        cprint(f"🔴 Decisões VENDA: {sell_decisions}", "red")
        cprint(f"⚪ Decisões HOLD: {hold_decisions}", "white")
        
        return metrics

def test_ai_smart_trader(csv_file):
    """Testa o AI Smart Trader"""
    cprint(f"🤖 TESTANDO AI SMART TRADER: {csv_file}", "white", "on_blue")
    
    # Carregar dados
    df = pd.read_csv(csv_file)
    df.columns = df.columns.str.lower()
    df['timestamp'] = pd.to_datetime(df['datetime'])
    df = df.dropna()
    
    # Criar trader
    trader = AISmartTrader()
    
    # Executar backtest
    decisions_log = trader.run_backtest(df)
    
    # Mostrar resultados
    metrics = trader.display_results(decisions_log)
    
    return metrics

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_ai_smart_trader(sys.argv[1])
    else:
        # Testar com BTC 6h (melhor performance anterior)
        test_ai_smart_trader("BTC-6h-1000wks-data.csv")