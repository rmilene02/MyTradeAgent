"""
🌙 Teste Direto da API Birdeye
Testa a API diretamente sem usar as funções internas
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from termcolor import colored, cprint

# Carregar variáveis de ambiente
load_dotenv()

def test_birdeye_direct():
    """Testa a API Birdeye diretamente"""
    cprint("🌙 TESTE DIRETO DA API BIRDEYE", "white", "on_blue")
    cprint("=" * 50, "blue")
    
    # Configurações
    api_key = os.getenv('BIRDEYE_API_KEY')
    sol_address = "So11111111111111111111111111111111111111112"
    
    if not api_key:
        cprint("❌ BIRDEYE_API_KEY não encontrada!", "red")
        return
    
    cprint(f"🔑 API Key: {api_key[:10]}...", "green")
    
    # Calcular timestamps
    time_to = int(datetime.now().timestamp())
    time_from = int((datetime.now() - timedelta(days=7)).timestamp())
    
    cprint(f"📅 Período: {datetime.fromtimestamp(time_from)} até {datetime.fromtimestamp(time_to)}", "cyan")
    
    # URL da API
    url = f"https://public-api.birdeye.so/defi/ohlcv?address={sol_address}&type=1H&time_from={time_from}&time_to={time_to}"
    
    cprint(f"🌐 URL: {url}", "white")
    
    # Headers
    headers = {"X-API-KEY": api_key}
    
    try:
        cprint("📡 Fazendo requisição...", "yellow")
        response = requests.get(url, headers=headers)
        
        cprint(f"📊 Status Code: {response.status_code}", "cyan")
        
        if response.status_code == 200:
            cprint("✅ Requisição bem-sucedida!", "green")
            
            data = response.json()
            cprint(f"📋 Estrutura da resposta: {list(data.keys())}", "white")
            
            if 'data' in data and 'items' in data['data']:
                items = data['data']['items']
                cprint(f"📈 Número de candles: {len(items)}", "green")
                
                if len(items) > 0:
                    # Mostrar primeiro e último candle
                    first = items[0]
                    last = items[-1]
                    
                    cprint(f"🕐 Primeiro candle: {datetime.fromtimestamp(first['unixTime'])}", "cyan")
                    cprint(f"💰 Preço: O:{first['o']:.2f} H:{first['h']:.2f} L:{first['l']:.2f} C:{first['c']:.2f}", "cyan")
                    
                    cprint(f"🕐 Último candle: {datetime.fromtimestamp(last['unixTime'])}", "cyan")
                    cprint(f"💰 Preço: O:{last['o']:.2f} H:{last['h']:.2f} L:{last['l']:.2f} C:{last['c']:.2f}", "cyan")
                    
                    # Criar DataFrame
                    df_data = []
                    for item in items:
                        df_data.append({
                            'timestamp': datetime.fromtimestamp(item['unixTime']),
                            'open': item['o'],
                            'high': item['h'],
                            'low': item['l'],
                            'close': item['c'],
                            'volume': item['v']
                        })
                    
                    df = pd.DataFrame(df_data)
                    cprint(f"📊 DataFrame criado: {len(df)} linhas", "green")
                    cprint(f"📈 Preço atual SOL: ${df['close'].iloc[-1]:.2f}", "yellow")
                    
                    return df
                else:
                    cprint("❌ Nenhum dado retornado", "red")
            else:
                cprint("❌ Estrutura de dados inesperada", "red")
                cprint(f"📋 Resposta: {data}", "white")
        
        elif response.status_code == 401:
            cprint("❌ Erro 401: API Key inválida ou sem permissão", "red")
            cprint("💡 Verifique se a API key está correta", "yellow")
        
        elif response.status_code == 429:
            cprint("❌ Erro 429: Rate limit excedido", "red")
            cprint("💡 Aguarde alguns minutos e tente novamente", "yellow")
        
        else:
            cprint(f"❌ Erro {response.status_code}: {response.text}", "red")
    
    except Exception as e:
        cprint(f"❌ Erro na requisição: {e}", "red")
    
    return None

def test_simple_price():
    """Testa endpoint simples de preço"""
    cprint("\n🌙 TESTE SIMPLES - PREÇO SOL", "white", "on_blue")
    
    api_key = os.getenv('BIRDEYE_API_KEY')
    sol_address = "So11111111111111111111111111111111111111112"
    
    url = f"https://public-api.birdeye.so/defi/price?address={sol_address}"
    headers = {"X-API-KEY": api_key}
    
    try:
        response = requests.get(url, headers=headers)
        cprint(f"📊 Status: {response.status_code}", "cyan")
        
        if response.status_code == 200:
            data = response.json()
            price = data.get('data', {}).get('value', 0)
            cprint(f"💰 Preço SOL: ${price:.2f}", "green")
        else:
            cprint(f"❌ Erro: {response.status_code}", "red")
    
    except Exception as e:
        cprint(f"❌ Erro: {e}", "red")

if __name__ == "__main__":
    # Teste simples primeiro
    test_simple_price()
    
    # Teste completo
    df = test_birdeye_direct()
    
    if df is not None:
        cprint("\n🎉 TESTE CONCLUÍDO COM SUCESSO!", "white", "on_green")
        cprint("✅ A API Birdeye está funcionando corretamente!", "green")
    else:
        cprint("\n❌ TESTE FALHOU", "white", "on_red")
        cprint("💡 Verifique a configuração da API", "yellow")