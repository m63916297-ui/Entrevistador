# Secrets Management for Streamlit Cloud

## Environment Variables

To deploy this app on Streamlit Cloud, you need to configure the following secrets:

### Required Secrets

1. **OPENAI_API_KEY**: Your OpenAI API key for GPT-4 access

## How to Configure

1. Go to your Streamlit Cloud dashboard
2. Select your app repository
3. Click on "Settings" → "Secrets"
4. Add the following:

```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```

## Local Development

For local development, create a `.env` file:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

Then install python-dotenv and update app.py to load from .env.

## Security Notes

- Never commit your API keys to version control
- Use Streamlit secrets for production deployments
- Rotate your API keys periodically
