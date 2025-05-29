#!/usr/bin/env python3
"""
🔧 Instalador de Dependências - Moon Dev's Trading System
Resolve problemas de compatibilidade com Python 3.13+
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Executa um comando e mostra o resultado"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erro:")
        print(f"   {e.stderr}")
        return False

def main():
    print("🌙 Moon Dev's Trading System - Instalador de Dependências")
    print("=" * 60)
    
    # Verificar se está em um ambiente virtual
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  AVISO: Recomendamos usar um ambiente virtual!")
        print("   Execute: python -m venv .venv && source .venv/bin/activate")
        response = input("   Continuar mesmo assim? (y/N): ")
        if response.lower() != 'y':
            print("👋 Instalação cancelada.")
            return
    
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Diretório atual: {os.getcwd()}")
    print()
    
    # Lista de comandos para instalar
    commands = [
        ("pip install --upgrade pip", "Atualizando pip"),
        ("pip install setuptools>=65.0.0 wheel>=0.37.0", "Instalando setuptools e wheel"),
        ("pip install packaging>=21.0", "Instalando packaging"),
        ("pip install -r requirements.txt", "Instalando dependências do projeto"),
    ]
    
    success_count = 0
    for command, description in commands:
        if run_command(command, description):
            success_count += 1
        print()
    
    print("=" * 60)
    if success_count == len(commands):
        print("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
        print()
        print("🚀 Próximos passos:")
        print("1. Configure suas APIs no arquivo .env")
        print("2. Execute: python verificar_apis.py")
        print("3. Teste: python test_strategy.py")
        print("4. Simulador: python simulador_visual.py")
    else:
        print(f"⚠️  INSTALAÇÃO PARCIAL: {success_count}/{len(commands)} comandos executados com sucesso")
        print()
        print("🔧 Tente executar manualmente:")
        print("pip install --upgrade pip setuptools wheel")
        print("pip install -r requirements.txt")
    
    print()
    print("📚 Documentação completa em: GUIA_API_KEYS.md")

if __name__ == "__main__":
    main()