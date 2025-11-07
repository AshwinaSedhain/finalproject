# Multi-Model AI System Setup Guide

## Overview
The system now supports **automatic fallback** between multiple FREE AI models for maximum reliability. If one model fails, the system automatically tries the next one.

## Model Priority (Most Reliable First)

### 1. **Groq (Primary)** - Llama 3.3 70B
- **Speed**: ⚡ Very Fast
- **Reliability**: ⭐⭐⭐⭐⭐ Excellent
- **Free Tier**: Generous
- **Setup**: Get API key from https://console.groq.com

### 2. **Hugging Face (Fallback 1)** - Mistral 7B
- **Speed**: ⚡ Fast
- **Reliability**: ⭐⭐⭐⭐ Very Good
- **Free Tier**: Good
- **Setup**: Get API key from https://huggingface.co/settings/tokens

### 3. **Google Gemini (Fallback 2)** - Gemini Pro
- **Speed**: ⚡ Fast
- **Reliability**: ⭐⭐⭐⭐⭐ Excellent
- **Free Tier**: ✅ Generous free tier (60 requests/minute)
- **Setup**: Get API key from https://aistudio.google.com/app/apikey

## How It Works

```
User Request
    ↓
Try Groq (Primary)
    ↓ (if fails)
Try Hugging Face (Fallback 1)
    ↓ (if fails)
Try Together AI (Fallback 2)
    ↓ (if all fail)
Return Error
```

## Setup Instructions

### Step 1: Install Required Packages

```bash
cd ai-chatbot-module
pip install groq requests together
```

### Step 2: Get API Keys (All FREE)

1. **Groq API Key** (Required - Primary):
   - Visit: https://console.groq.com
   - Sign up (free)
   - Create API key
   - Add to `.env`: `GROQ_API_KEY=your_key_here`

2. **Hugging Face API Key** (Optional - Fallback 1):
   - Visit: https://huggingface.co/settings/tokens
   - Create access token
   - Add to `.env`: `HUGGINGFACE_API_KEY=your_key_here`

3. **Google Gemini API Key** (Optional - Fallback 2):
   - Visit: https://aistudio.google.com/app/apikey
   - Sign in with Google account (free)
   - Create API key
   - Add to `.env`: `GOOGLE_API_KEY=your_key_here` or `GEMINI_API_KEY=your_key_here`

### Step 3: Update .env File

Create or update `.env` file in `ai-chatbot-module/`:

```env
# Required (Primary Model)
GROQ_API_KEY=your_groq_key_here

# Optional (Fallback Models - Recommended for reliability)
HUGGINGFACE_API_KEY=your_hf_key_here
GOOGLE_API_KEY=your_gemini_key_here
```

## Minimum Setup

**Minimum**: Just Groq API key (system will work with single model)
**Recommended**: All 3 API keys (maximum reliability with automatic fallback)

## How Automatic Fallback Works

1. **System tries Groq first** (fastest, most reliable)
2. **If Groq fails** (rate limit, error, timeout):
   - Automatically tries Hugging Face
3. **If Hugging Face fails**:
   - Automatically tries Together AI
4. **If all fail**:
   - Returns error message

## Benefits

✅ **Maximum Reliability**: System never fails if at least one model works
✅ **Rate Limit Handling**: Automatically switches when rate limited
✅ **Error Recovery**: Handles API errors gracefully
✅ **Performance**: Uses fastest available model
✅ **Cost**: All models are FREE

## Monitoring

The system logs which model was used:
- `[Multi-Model] Trying Groq Llama 3.3 70B...`
- `✓ Groq Llama 3.3 70B succeeded in 0.45s`

If a model fails, you'll see:
- `⚠ Groq Llama 3.3 70B failed: rate limit - Trying next model...`
- `[Multi-Model] Trying Hugging Face Mistral 7B...`

## Model Statistics

The system tracks success/failure rates for each model. You can access stats via:
```python
stats = llm_manager.llm_backend.get_model_stats()
```

## Troubleshooting

### "No AI models available"
- Make sure at least `GROQ_API_KEY` is set in `.env`
- Check that API key is valid

### "Model failed"
- Check API key is correct
- Check internet connection
- Verify API service is online
- System will automatically try next model

### "All models failed"
- Check all API keys are valid
- Check internet connection
- Check API service status pages

## Notes

- The system works with just Groq (minimum setup)
- Adding more API keys increases reliability
- All models are FREE (no costs)
- Automatic fallback is transparent to users

