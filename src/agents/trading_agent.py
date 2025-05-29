"""
🌙 Moon Dev's AI Trading Agent
Built with love by Moon Dev 🚀
"""

# ⏰ Run Configuration
RUN_INTERVAL_MINUTES = 15  # How often the AI agent runs

# 🎯 Trading Strategy Prompt - Estratégia Distância MME9 + Bollinger Bands! 
TRADING_PROMPT = """
You are Moon Dev's AI Trading Assistant specialized in the Distance MME9 + Bollinger Bands Strategy 🌙

STRATEGY RULES:
1. **SELL Signal**: When distanciaMME9 is ABOVE upper Bollinger Band AND shows reversal (exaustão alta)
2. **BUY Signal**: When distanciaMME9 is BELOW lower Bollinger Band AND shows reversal (exaustão baixa)
3. **NOTHING**: When in exhaustion zones but no reversal yet, or in neutral territory

STOP LOSS GUIDELINES:
- For SELL: Stop above the high of the reversal candle
- For BUY: Stop below the low of the reversal candle
- Let AI decide optimal stop distance based on volatility

TARGET GUIDELINES:
- Use support/resistance levels provided
- Consider risk/reward ratio (minimum 1:2)
- Adjust based on market conditions

Analyze the strategy summary provided and respond in this exact format:
1. First line must be one of: BUY, SELL, or NOTHING (in caps)
2. Then explain your reasoning, including:
   - Distance MME9 analysis
   - Bollinger Bands position
   - Exhaustion/reversal signals
   - Suggested stop loss level
   - Suggested target level
   - Risk/reward ratio
   - Confidence level (as a percentage, e.g. 75%)

Remember: This strategy focuses on mean reversion after exhaustion! 🎯
"""

# 💰 Portfolio Allocation Prompt
ALLOCATION_PROMPT = """
You are Moon Dev's Portfolio Allocation Assistant 🌙

Given the total portfolio size and trading recommendations, allocate capital efficiently.
Consider:
1. Position sizing based on confidence levels
2. Risk distribution
3. Keep cash buffer as specified
4. Maximum allocation per position

Format your response as a Python dictionary:
{
    "token_address": allocated_amount,  # In USD
    ...
    "USDC_ADDRESS": remaining_cash  # Always use USDC_ADDRESS for cash
}

Remember:
- Total allocations must not exceed total_size
- Higher confidence should get larger allocations
- Never allocate more than {MAX_POSITION_PERCENTAGE}% to a single position
- Keep at least {CASH_PERCENTAGE}% in USDC as safety buffer
- Only allocate to BUY recommendations
- Cash must be stored as USDC using USDC_ADDRESS: {USDC_ADDRESS}
"""

import openai
import os
import pandas as pd
import json
from termcolor import colored, cprint
from dotenv import load_dotenv
from ..core.config import *
from ..core import nice_funcs as n  # Import nice_funcs as n
from ..data.ohlcv_collector import collect_all_tokens
from datetime import datetime, timedelta
import time

# Load environment variables
load_dotenv()

class TradingAgent:
    def __init__(self):
        """Initialize the AI Trading Agent with Moon Dev's magic ✨"""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("🚨 DEEPSEEK_API_KEY not found in environment variables!")
            
        # Configure OpenAI client for DeepSeek
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.recommendations_df = pd.DataFrame(columns=['token', 'action', 'confidence', 'reasoning'])
        print("🤖 Moon Dev's AI Trading Agent initialized with DeepSeek!")
        
    def analyze_market_data(self, token, market_data):
        """Analyze market data using DeepSeek with custom strategy"""
        try:
            # Extrair o resumo da estratégia se disponível
            strategy_summary = market_data.get('strategy_summary', 'Resumo da estratégia não disponível')
            
            response = self.client.chat.completions.create(
                model=AI_MODEL,
                max_tokens=AI_MAX_TOKENS,
                temperature=AI_TEMPERATURE,
                messages=[
                    {
                        "role": "user", 
                        "content": f"{TRADING_PROMPT}\n\nStrategy Analysis:\n{strategy_summary}\n\nRaw Market Data:\n{str(market_data)[:1000]}..."
                    }
                ]
            )
            
            # Parse the response from DeepSeek
            content = response.choices[0].message.content
            
            lines = content.split('\n')
            action = lines[0].strip() if lines else "NOTHING"
            
            # Extract confidence from the response (assuming it's mentioned as a percentage)
            confidence = 0
            for line in lines:
                if 'confidence' in line.lower():
                    # Extract number from string like "Confidence: 75%"
                    try:
                        confidence = int(''.join(filter(str.isdigit, line)))
                    except:
                        confidence = 50  # Default if not found
            
            # Add to recommendations DataFrame with proper reasoning
            reasoning = '\n'.join(lines[1:]) if len(lines) > 1 else "No detailed reasoning provided"
            self.recommendations_df = pd.concat([
                self.recommendations_df,
                pd.DataFrame([{
                    'token': token,
                    'action': action,
                    'confidence': confidence,
                    'reasoning': reasoning
                }])
            ], ignore_index=True)
            
            print(f"🎯 Moon Dev's AI Analysis Complete for {token[:4]}!")
            return content
            
        except Exception as e:
            print(f"❌ Error in AI analysis: {str(e)}")
            # Still add to DataFrame even on error, but mark as NOTHING with 0 confidence
            self.recommendations_df = pd.concat([
                self.recommendations_df,
                pd.DataFrame([{
                    'token': token,
                    'action': "NOTHING",
                    'confidence': 0,
                    'reasoning': f"Error during analysis: {str(e)}"
                }])
            ], ignore_index=True)
            return None
    
    def allocate_portfolio(self, total_size):
        """Allocate portfolio based on recommendations"""
        try:
            # Clean and format recommendations for the allocation agent
            clean_df = self.recommendations_df.copy()
            
            # Filter to only include BUY recommendations
            buy_df = clean_df[clean_df['action'] == 'BUY'].copy()
            if buy_df.empty:
                cprint("🤔 No BUY recommendations - keeping everything in USDC", "white", "on_blue")
                return {USDC_ADDRESS: total_size}
            
            # Ensure all columns are strings and clean any TextBlock objects
            for col in buy_df.columns:
                buy_df[col] = buy_df[col].apply(lambda x: 
                    x.text if hasattr(x, 'text') else str(x))
            
            # Calculate maximum position size (30% of total)
            max_position_size = total_size * 0.30
            cprint(f"🎯 Maximum position size: ${max_position_size:.2f} (30% of ${total_size:.2f})", "white", "on_blue")
            
            recommendations_str = buy_df.to_string()
            
            response = self.client.chat.completions.create(
                model=AI_MODEL,
                max_tokens=AI_MAX_TOKENS,
                temperature=AI_TEMPERATURE,
                messages=[
                    {
                        "role": "user", 
                        "content": f"{ALLOCATION_PROMPT}\n\nTotal Size: ${total_size}\nMax Position Size: ${max_position_size}\n\nRecommendations:\n{recommendations_str}"
                    }
                ]
            )
            
            # Parse the allocation response from DeepSeek
            allocation_str = response.choices[0].message.content
            
            # Extract the dictionary string and parse it
            try:
                start_idx = allocation_str.find('{')
                end_idx = allocation_str.find('}', start_idx) + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = allocation_str[start_idx:end_idx]
                    json_str = json_str.strip()
                    allocation_dict = json.loads(json_str)
                    
                    # Ensure cash is stored with USDC_ADDRESS
                    if 'cash' in allocation_dict:
                        allocation_dict[USDC_ADDRESS] = allocation_dict.pop('cash')
                    if 'USDC_ADDRESS' in allocation_dict:
                        allocation_dict[USDC_ADDRESS] = allocation_dict.pop('USDC_ADDRESS')
                        
                    # Validate and cap allocations
                    for token, amount in list(allocation_dict.items()):
                        if token != USDC_ADDRESS and amount > max_position_size:
                            cprint(f"⚠️ Capping {token} allocation from ${amount:.2f} to ${max_position_size:.2f}", "white", "on_yellow")
                            allocation_dict[token] = max_position_size
                else:
                    raise ValueError("Could not find valid JSON in response")
                
                # Create DataFrame with allocations
                allocations_df = pd.DataFrame([
                    {"token": k, "allocation": v, "timestamp": datetime.now()}
                    for k, v in allocation_dict.items()
                ])
                
                # Save to CSV in src/data directory
                os.makedirs('src/data', exist_ok=True)
                allocations_df.to_csv('src/data/current_allocation.csv', index=False)
                cprint("💾 Portfolio allocation saved with position size limits!", "white", "on_blue")
                
                return allocation_dict
                
            except Exception as e:
                print(f"❌ Error parsing allocation response: {str(e)}")
                print(f"Raw response: {allocation_str}")
                return None
            
        except Exception as e:
            print(f"❌ Error in portfolio allocation: {str(e)}")
            return None

    def execute_allocations(self, allocation_dict):
        """Execute the allocations using AI entry for each position"""
        try:
            print("\n🚀 Moon Dev executing portfolio allocations...")
            
            for token, amount in allocation_dict.items():
                # Skip USDC - that's our cash position
                if token == USDC_ADDRESS:
                    print(f"💵 Keeping ${amount:.2f} in USDC as buffer")
                    continue
                    
                print(f"\n🎯 Checking position for {token}...")
                
                try:
                    # Get current position value
                    current_position = n.get_token_balance_usd(token)
                    target_allocation = amount  # This is the target from our portfolio calc
                    
                    # Calculate entry threshold (97% of target)
                    entry_threshold = target_allocation * 0.97
                    
                    print(f"🎯 Target allocation: ${target_allocation:.2f} USD")
                    print(f"📊 Current position: ${current_position:.2f} USD")
                    print(f"⚖️ Entry threshold: ${entry_threshold:.2f} USD")
                    
                    if current_position < entry_threshold:
                        print(f"✨ Position below threshold - executing entry for {token}")
                        n.ai_entry(token, amount)
                        print(f"✅ Entry complete for {token}")
                    else:
                        print(f"⏸️ Position already at target size for {token}")
                    
                except Exception as e:
                    print(f"❌ Error executing entry for {token}: {str(e)}")
                
                # Small delay between entries
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Error executing allocations: {str(e)}")
            print("🔧 Moon Dev suggests checking the logs and trying again!")

    def handle_exits(self):
        """Check and exit positions based on SELL or NOTHING recommendations"""
        cprint("\n🔄 Checking for positions to exit...", "white", "on_blue")
        
        for _, row in self.recommendations_df.iterrows():
            token = row['token']
            action = row['action']
            
            # Check if we have a position
            current_position = n.get_token_balance_usd(token)
            
            if current_position > 0 and action in ["SELL", "NOTHING"]:
                cprint(f"\n🚫 AI Agent recommends {action} for {token[:8]} (Current position: ${current_position:.2f})", "white", "on_yellow")
                try:
                    cprint(f"📉 Closing position for {token[:8]}...", "white", "on_blue")
                    n.chunk_kill(token, max_usd_order_size, slippage)
                    cprint(f"✅ Successfully closed position for {token[:8]}", "white", "on_green")
                except Exception as e:
                    cprint(f"❌ Error closing position for {token[:8]}: {str(e)}", "white", "on_red")
            elif current_position > 0:
                cprint(f"✨ Keeping position for {token[:8]} (${current_position:.2f}) - AI recommends {action}", "white", "on_blue")

def main():
    """Main function to run the trading agent every 15 minutes"""
    cprint("🌙 Moon Dev AI Trading System Starting Up! 🚀", "white", "on_blue")
    
    INTERVAL = RUN_INTERVAL_MINUTES * 60  # Convert minutes to seconds
    
    while True:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cprint(f"\n⏰ AI Agent Run Starting at {current_time}", "white", "on_green")
            
            # Collect OHLCV data for all tokens
            cprint("📊 Collecting market data...", "white", "on_blue")
            market_data = collect_all_tokens()
            
            # Initialize AI agent
            agent = TradingAgent()
            
            # Analyze each token's data
            for token, data in market_data.items():
                cprint(f"\n🤖 AI Agent Analyzing Token: {token}", "white", "on_green")
                
                # Mostrar resumo da estratégia primeiro
                if hasattr(data, 'attrs') and 'strategy_summary' in data.attrs:
                    cprint("\n📊 RESUMO DA ESTRATÉGIA:", "white", "on_blue")
                    print(data.attrs['strategy_summary'])
                    print("\n" + "="*50 + "\n")
                
                # Preparar dados para análise
                analysis_data = {
                    'strategy_summary': data.attrs.get('strategy_summary', 'Não disponível') if hasattr(data, 'attrs') else 'Não disponível',
                    'raw_data': data.to_dict()
                }
                
                analysis = agent.analyze_market_data(token, analysis_data)
                print(f"\n🤖 AI Analysis for contract: {token}")
                print(analysis)
                print("\n" + "="*50 + "\n")
            
            # Show recommendations summary (without reasoning)
            cprint("\n📊 Moon Dev's Trading Recommendations:", "white", "on_blue")
            summary_df = agent.recommendations_df[['token', 'action', 'confidence']].copy()
            print(summary_df.to_string(index=False))
            
            # First handle any exits based on recommendations
            cprint("\n🔄 Checking for positions to exit...", "white", "on_blue")
            
            # Handle exits first - close any positions where recommendation is SELL or NOTHING
            for _, row in agent.recommendations_df.iterrows():
                token = row['token']
                action = row['action']
                
                if action in ["SELL", "NOTHING"]:
                    current_position = n.get_token_balance_usd(token)
                    if current_position > 0:
                        cprint(f"\n🚫 AI Agent recommends {action} for {token}", "white", "on_yellow")
                        cprint(f"💰 Current position: ${current_position:.2f}", "white", "on_blue")
                        try:
                            cprint(f"📉 Closing position with chunk_kill...", "white", "on_cyan")
                            n.chunk_kill(token, max_usd_order_size, slippage)
                            cprint(f"✅ Successfully closed position", "white", "on_green")
                        except Exception as e:
                            cprint(f"❌ Error closing position: {str(e)}", "white", "on_red")
            
            # Then proceed with new allocations for BUY recommendations
            cprint("\n💰 Calculating optimal portfolio allocation...", "white", "on_blue")
            allocation = agent.allocate_portfolio(usd_size)
            
            if allocation:
                cprint("\n💼 Moon Dev's Portfolio Allocation:", "white", "on_blue")
                print(json.dumps(allocation, indent=4))
                
                cprint("\n🎯 Executing allocations...", "white", "on_blue")
                agent.execute_allocations(allocation)
                cprint("\n✨ All allocations executed!", "white", "on_blue")
            else:
                cprint("\n⚠️ No allocations to execute!", "white", "on_yellow")
            
            next_run = datetime.now() + timedelta(minutes=RUN_INTERVAL_MINUTES)
            cprint(f"\n⏳ AI Agent run complete. Next run at {next_run.strftime('%Y-%m-%d %H:%M:%S')}", "white", "on_green")
            
            # Clean up temp data before sleeping
            cprint("\n🧹 Cleaning up temporary data...", "white", "on_blue")
            try:
                for file in os.listdir('temp_data'):
                    if file.endswith('_latest.csv'):
                        os.remove(os.path.join('temp_data', file))
                cprint("✨ Temp data cleaned successfully!", "white", "on_green")
            except Exception as e:
                cprint(f"⚠️ Error cleaning temp data: {str(e)}", "white", "on_yellow")
            
            # Sleep until next interval
            time.sleep(INTERVAL)
                
        except KeyboardInterrupt:
            cprint("\n👋 Moon Dev AI Agent shutting down gracefully...", "white", "on_blue")
            break
        except Exception as e:
            cprint(f"\n❌ Error: {str(e)}", "white", "on_red")
            cprint("🔧 Moon Dev suggests checking the logs and trying again!", "white", "on_blue")
            # Still sleep and continue on error
            time.sleep(INTERVAL)

if __name__ == "__main__":
    main() 