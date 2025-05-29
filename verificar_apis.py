"""
🔑 Verificador de API Keys
Testa se suas APIs estão funcionando corretamente
Built with love by Moon Dev 🚀
"""

import os
import sys
from dotenv import load_dotenv
from termcolor import colored, cprint
import requests
import openai

# Carregar variáveis de ambiente
load_dotenv()

def test_deepseek_api():
    """Testa a API da DeepSeek"""
    cprint("\n🧠 Testando DeepSeek API...", "white", "on_blue")
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        cprint("❌ DEEPSEEK_API_KEY não encontrada no .env", "white", "on_red")
        return False
    
    try:
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Responda apenas: 'API funcionando!'"}
            ]
        )
        
        result = response.choices[0].message.content
        cprint(f"✅ DeepSeek API funcionando! Resposta: {result}", "white", "on_green")
        return True
        
    except Exception as e:
        cprint(f"❌ Erro na DeepSeek API: {str(e)}", "white", "on_red")
        return False

def test_birdeye_api():
    """Testa a API da Birdeye"""
    cprint("\n📊 Testando Birdeye API...", "white", "on_blue")
    
    api_key = os.getenv("BIRDEYE_API_KEY")
    if not api_key:
        cprint("❌ BIRDEYE_API_KEY não encontrada no .env", "white", "on_red")
        return False
    
    try:
        # Teste simples: buscar preço do SOL
        url = "https://public-api.birdeye.so/defi/price"
        params = {
            "address": "So11111111111111111111111111111111111111112"  # SOL address
        }
        headers = {
            "X-API-KEY": api_key
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            price = data.get('data', {}).get('value', 'N/A')
            cprint(f"✅ Birdeye API funcionando! Preço SOL: ${price}", "white", "on_green")
            return True
        else:
            cprint(f"❌ Birdeye API erro: Status {response.status_code}", "white", "on_red")
            return False
            
    except Exception as e:
        cprint(f"❌ Erro na Birdeye API: {str(e)}", "white", "on_red")
        return False

def test_solana_rpc():
    """Testa a conexão RPC Solana (opcional)"""
    cprint("\n🌐 Testando Solana RPC...", "white", "on_blue")
    
    rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
    
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getHealth"
        }
        
        response = requests.post(rpc_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('result') == 'ok':
                cprint(f"✅ Solana RPC funcionando! URL: {rpc_url}", "white", "on_green")
                return True
            else:
                cprint(f"⚠️ Solana RPC respondeu mas não está 'ok': {data}", "white", "on_yellow")
                return False
        else:
            cprint(f"❌ Solana RPC erro: Status {response.status_code}", "white", "on_red")
            return False
            
    except Exception as e:
        cprint(f"❌ Erro no Solana RPC: {str(e)}", "white", "on_red")
        return False

def check_env_file():
    """Verifica se o arquivo .env existe"""
    cprint("\n📁 Verificando arquivo .env...", "white", "on_blue")
    
    if not os.path.exists('.env'):
        cprint("❌ Arquivo .env não encontrado!", "white", "on_red")
        cprint("💡 Execute: cp .env.example .env", "white", "on_yellow")
        return False
    else:
        cprint("✅ Arquivo .env encontrado!", "white", "on_green")
        return True

def check_private_key():
    """Verifica chave privada Solana (opcional)"""
    cprint("\n🔐 Verificando chave privada Solana...", "white", "on_blue")
    
    private_key = os.getenv("SOLANA_PRIVATE_KEY")
    if not private_key:
        cprint("⚠️ SOLANA_PRIVATE_KEY não configurada (opcional para testes)", "white", "on_yellow")
        cprint("💡 Necessária apenas para trades reais", "white", "on_cyan")
        return None
    else:
        # Verificação básica do formato
        if len(private_key) > 50:  # Chave privada típica é longa
            cprint("✅ Chave privada Solana configurada!", "white", "on_green")
            return True
        else:
            cprint("⚠️ Formato da chave privada pode estar incorreto", "white", "on_yellow")
            return False

def main():
    """Função principal"""
    cprint("🔑 Moon Dev's API Key Checker", "white", "on_magenta")
    cprint("Verificando todas as APIs necessárias...\n", "white", "on_magenta")
    
    results = {}
    
    # Verificar arquivo .env
    results['env_file'] = check_env_file()
    
    if not results['env_file']:
        cprint("\n❌ Configure o arquivo .env primeiro!", "white", "on_red")
        return
    
    # Testar APIs obrigatórias
    results['deepseek'] = test_deepseek_api()
    results['birdeye'] = test_birdeye_api()
    
    # Testar APIs opcionais
    results['solana_rpc'] = test_solana_rpc()
    results['private_key'] = check_private_key()
    
    # Resumo final
    cprint("\n" + "="*60, "white")
    cprint("📋 RESUMO DOS TESTES", "white", "on_magenta")
    cprint("="*60, "white")
    
    # APIs obrigatórias
    cprint("\n🎯 APIs OBRIGATÓRIAS:", "white", "on_blue")
    status_deepseek = "✅ OK" if results['deepseek'] else "❌ ERRO"
    status_birdeye = "✅ OK" if results['birdeye'] else "❌ ERRO"
    print(f"  DeepSeek API: {status_deepseek}")
    print(f"  Birdeye API:  {status_birdeye}")
    
    # APIs opcionais
    cprint("\n⚙️ APIs OPCIONAIS:", "white", "on_cyan")
    status_rpc = "✅ OK" if results['solana_rpc'] else "❌ ERRO"
    status_key = "✅ OK" if results['private_key'] else ("⚠️ N/A" if results['private_key'] is None else "❌ ERRO")
    print(f"  Solana RPC:   {status_rpc}")
    print(f"  Private Key:  {status_key}")
    
    # Recomendações
    cprint("\n🎯 PRÓXIMOS PASSOS:", "white", "on_green")
    
    if results['deepseek'] and results['birdeye']:
        cprint("✅ Você pode testar a estratégia!", "white", "on_green")
        cprint("💡 Execute: python test_strategy.py", "white", "on_cyan")
        
        if not results['solana_rpc'] or not results['private_key']:
            cprint("⚠️ Para trades reais, configure Solana RPC e Private Key", "white", "on_yellow")
    else:
        cprint("❌ Configure as APIs obrigatórias primeiro", "white", "on_red")
        if not results['deepseek']:
            cprint("🔧 DeepSeek: https://platform.deepseek.com/", "white", "on_yellow")
        if not results['birdeye']:
            cprint("🔧 Birdeye: https://birdeye.so/", "white", "on_yellow")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Verificação interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")