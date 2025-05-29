# 🔄 Migração para DeepSeek API

## ✅ Mudanças Realizadas

### 1. **Arquivo Principal: `src/agents/trading_agent.py`**
- ❌ Removido: `import anthropic`
- ✅ Adicionado: `import openai`
- ❌ Removido: `ANTHROPIC_KEY`
- ✅ Adicionado: `DEEPSEEK_API_KEY`
- ✅ Configurado cliente OpenAI para DeepSeek:
  ```python
  self.client = openai.OpenAI(
      api_key=api_key,
      base_url="https://api.deepseek.com"
  )
  ```
- ✅ Atualizado método de chamada da API:
  ```python
  # Antes (Anthropic)
  message = self.client.messages.create(...)
  response = message.content
  
  # Agora (DeepSeek)
  response = self.client.chat.completions.create(...)
  content = response.choices[0].message.content
  ```

### 2. **Configurações: `src/core/config.py`**
- ❌ Removido: `claude-3-haiku-20240307`
- ✅ Adicionado: `deepseek-chat`
- ✅ Comentários atualizados para DeepSeek

### 3. **Dependências: `requirements.txt`**
- ❌ Removido: `anthropic>=0.3.0`
- ✅ Adicionado: `openai>=1.0.0`

### 4. **Setup: `setup.py`**
- ❌ Removido: `"anthropic"`
- ✅ Adicionado: `"openai>=1.0.0"`

### 5. **Variáveis de Ambiente: `.env.example`**
- ❌ Removido: `ANTHROPIC_KEY`
- ✅ Adicionado: `DEEPSEEK_API_KEY`
- ✅ Atualizado link: https://platform.deepseek.com/

### 6. **Documentação: `GUIA_ESTRATEGIA.md`**
- ✅ Atualizado para mencionar DeepSeek
- ✅ Adicionado link para obter API key
- ✅ Instruções de configuração atualizadas

### 7. **Prompts: `PROMPTS.md`**
- ✅ Removida referência ao cookbook da Anthropic
- ✅ Atualizado para mencionar DeepSeek

## 🎯 Modelos Disponíveis na DeepSeek

### Principais:
- **`deepseek-chat`** - Modelo principal para conversação e análise
- **`deepseek-coder`** - Especializado em código (se precisar)

### Configuração Atual:
```python
AI_MODEL = "deepseek-chat"  # Configurado no config.py
```

## 💰 Vantagens da DeepSeek

1. **💸 Mais Barato**: Preços muito competitivos
2. **🚀 Rápido**: Latência baixa
3. **🧠 Inteligente**: Performance comparável aos melhores modelos
4. **🔧 Compatível**: API compatível com OpenAI
5. **🌍 Acessível**: Disponível globalmente

## 🔧 Como Usar Agora

### 1. Obter API Key:
```bash
# Acesse: https://platform.deepseek.com/
# Crie conta → API Keys → Copie a chave
```

### 2. Configurar:
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o .env e adicione:
DEEPSEEK_API_KEY=sua_chave_aqui
```

### 3. Instalar Dependências:
```bash
pip install -r requirements.txt
```

### 4. Testar:
```bash
python test_strategy.py
```

## ⚠️ Notas Importantes

1. **API Compatível**: DeepSeek usa API compatível com OpenAI
2. **Mesmo Formato**: Prompts e respostas funcionam igual
3. **Performance**: Pode ser até melhor que Claude em alguns casos
4. **Custo**: Significativamente mais barato
5. **Rate Limits**: Verifique os limites na documentação

## 🔄 Rollback (se necessário)

Se quiser voltar para Anthropic:
1. Mude `openai` para `anthropic` no requirements.txt
2. Mude `DEEPSEEK_API_KEY` para `ANTHROPIC_KEY` no .env
3. Mude `deepseek-chat` para `claude-3-haiku-20240307` no config.py
4. Reverta as mudanças no trading_agent.py

---
*Migração realizada com ❤️ por Moon Dev*