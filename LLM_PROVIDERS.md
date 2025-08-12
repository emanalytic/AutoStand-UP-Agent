# LLM Provider Configuration Guide

The AutoStand-UP-Agent now supports multiple LLM providers, giving you the flexibility to choose between different language models based on your needs, budget, and preferences.

## Supported Providers

### 1. Groq (Default)
- **API Key**: `GROQ_API_KEY`
- **Cost**: Generally lower cost, fast inference
- **Popular Models**: 
  - `llama3-70b-8192` (recommended)
  - `mixtral-8x7b-32768`
  - `gemma-7b-it`

### 2. OpenAI
- **API Key**: `OPENAI_API_KEY`
- **Cost**: Higher cost, high quality outputs
- **Popular Models**:
  - `gpt-3.5-turbo` (recommended for cost-effectiveness)
  - `gpt-4` (highest quality)
  - `gpt-4-turbo`
  - `gpt-4o-mini`

## Configuration

### Setting up your LLM Provider

In your `config.ini` file:

```ini
[settings]
# Choose your LLM provider
llm_provider = groq  # or "openai"
model = llama3-70b-8192  # or your preferred model
```

### Environment Variables

Set the appropriate API key based on your chosen provider:

#### For Groq:
```bash
export GROQ_API_KEY=your_groq_api_key_here
```

#### For OpenAI:
```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

### GitHub Secrets

When running via GitHub Actions, add the appropriate secret:

| Provider | Secret Name | Description |
|----------|-------------|-------------|
| Groq | `GROQ_API_KEY` | Your Groq API key |
| OpenAI | `OPENAI_API_KEY` | Your OpenAI API key |

## Example Configurations

### Groq Configuration (Cost-Effective)
```ini
[settings]
llm_provider = groq
model = llama3-70b-8192
# ... other settings
```

### OpenAI Configuration (High Quality)
```ini
[settings]
llm_provider = openai
model = gpt-3.5-turbo
# ... other settings
```

## Migration from Groq-only Setup

If you're upgrading from a previous version that only supported Groq:

1. **No changes needed**: Your existing config will continue to work
2. **Optional**: Add `llm_provider = groq` to your config for explicitness
3. **To switch to OpenAI**: 
   - Change `llm_provider = openai`
   - Update your model name
   - Add `OPENAI_API_KEY` to your environment/secrets

## Model Recommendations

### For Cost Optimization:
- **Groq**: `llama3-70b-8192` 
- **OpenAI**: `gpt-3.5-turbo`

### For Best Quality:
- **Groq**: `llama3-70b-8192`
- **OpenAI**: `gpt-4` or `gpt-4-turbo`

### For Speed:
- **Groq**: Any model (Groq specializes in fast inference)
- **OpenAI**: `gpt-3.5-turbo`

## Troubleshooting

### "API Key not found" Error
- Make sure you've set the correct environment variable for your chosen provider
- Check that the variable name matches exactly (`GROQ_API_KEY` or `OPENAI_API_KEY`)
- Verify the API key is valid and has sufficient credits

### "Unsupported LLM provider" Error
- Check that `llm_provider` in config.ini is set to either `groq` or `openai`
- Case matters: use lowercase

### Model Not Found Error
- Verify your model name is correct for your chosen provider
- Check the provider's documentation for available models
- Some models may require special access or have regional restrictions