# Troubleshooting Guide

This guide helps you resolve common issues when using AgentBay SDK with CrewAI.

## Quick Diagnosis

**First step**: Run the diagnostic tool to identify issues:
```bash
cd crews/agentbay_sdk
python diagnose.py
```

## Common Errors and Solutions

### 1. Connection Error

**Error Message**:
```
litellm.InternalServerError: OpenAIException - Connection error
```

**Possible Causes**:
- Network connectivity issues
- Incorrect API endpoint URL
- Firewall/proxy blocking the connection
- Invalid API key

**Solutions**:

#### A. Check Network Connectivity
```bash
# Test if you can reach Bailian endpoint
curl -I https://dashscope.aliyuncs.com/compatible-mode/v1

# Expected: HTTP status code (200, 401, 404, etc.)
# Problem: Timeout or no response
```

#### B. Verify API Endpoint URL
```bash
# Correct (no trailing slash)
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1

# Wrong (has trailing slash)
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1/

# Wrong (wrong path)
OPENAI_API_BASE=https://dashscope.aliyuncs.com/api/v1
```

#### C. Test API Key Directly
```bash
# Replace YOUR_API_KEY with your actual key
curl -X POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "qwen-plus",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

**Expected**: JSON response with content
**Problem**: Error message or timeout

#### D. Use Proxy (if needed)
```bash
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port
```

---

### 2. Model Provider Error

**Error Message**:
```
litellm.BadRequestError: LLM Provider NOT provided. You passed model=qwen-plus
```

**Cause**: Missing `openai/` prefix for Bailian models

**Solution**: Add `openai/` prefix to model name

```bash
# Correct
OPENAI_MODEL_NAME=openai/qwen-plus

# Wrong
OPENAI_MODEL_NAME=qwen-plus
```

**Available Bailian models** (all need `openai/` prefix):
- `openai/qwen-turbo` - Fast, low cost
- `openai/qwen-plus` - Recommended
- `openai/qwen-max` - Most powerful
- `openai/qwen-max-longcontext` - Long context

---

### 3. Authentication Error

**Error Message**:
```
litellm.AuthenticationError: OpenAIException - The api_key client option must be set
```

**Solutions**:

#### A. Check .env File Exists
```bash
cd crews/agentbay_sdk
ls -la .env

# If not found:
cp env.example .env
```

#### B. Verify Environment Variables
```bash
# Check if variables are loaded
python3 << 'EOF'
import os
from dotenv import load_dotenv
load_dotenv()

print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY", "NOT SET")[:20] + "...")
print("OPENAI_API_BASE:", os.getenv("OPENAI_API_BASE", "NOT SET"))
EOF
```

#### C. Verify API Key Format
- Should start with `sk-`
- Should be 40+ characters
- No extra spaces or newlines
- Not expired or disabled

#### D. Regenerate API Key
1. Visit: https://bailian.console.aliyun.com/
2. Go to "API-KEY管理"
3. Delete old key (if exists)
4. Create new API-KEY
5. Copy to `.env` file

---

### 4. Tests Skipped

**Message**:
```
SKIPPED (AGENTBAY_API_KEY or OPENAI_API_KEY not set)
```

**This is normal** if you haven't set API keys yet.

**Solutions**:

#### A. Set Required Environment Variables
```bash
# In .env file
AGENTBAY_API_KEY=your_agentbay_key
OPENAI_API_KEY=your_openai_or_bailian_key
```

#### B. Verify Variables are Set
```bash
echo $AGENTBAY_API_KEY
echo $OPENAI_API_KEY
```

---

### 5. Import Errors

**Error Message**:
```
ModuleNotFoundError: No module named 'crewai'
ModuleNotFoundError: No module named 'agentbay'
```

**Solutions**:

#### A. Install Dependencies
```bash
cd crews/agentbay_sdk

# Using poetry
poetry install --no-root

# Or using pip
pip install -e .

# Or install individually
pip install crewai wuying-agentbay-sdk python-dotenv pytest
```

#### B. Verify Installation
```bash
python3 -c "import crewai; print('CrewAI:', crewai.__version__)"
python3 -c "import agentbay; print('AgentBay SDK installed')"
```

---

### 6. Python Version Issues

**Error Message**:
```
requires-python >=3.10,<3.14
```

**Solution**: Use Python 3.10, 3.11, 3.12, or 3.13

```bash
# Check your Python version
python3 --version

# If needed, use pyenv or conda to switch versions
```

---

## Step-by-Step Troubleshooting

### For Connection Errors:

1. **Run diagnostic**:
   ```bash
   python diagnose.py
   ```

2. **Check .env file**:
   ```bash
   cat .env
   ```

3. **Verify network**:
   ```bash
   curl -I https://dashscope.aliyuncs.com/compatible-mode/v1
   ```

4. **Test API key**:
   ```bash
   curl -X POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"qwen-plus","messages":[{"role":"user","content":"Hi"}]}'
   ```

5. **Check for typos**:
   - URL has no trailing slash
   - Model name has `openai/` prefix
   - API key starts with `sk-`

6. **Try OpenAI first** (to isolate the issue):
   ```bash
   # Temporarily use OpenAI
   OPENAI_API_KEY=your_openai_key
   OPENAI_MODEL_NAME=gpt-4o-mini
   # Comment out OPENAI_API_BASE
   ```

---

## Configuration Checklist

Before running tests, verify:

- [ ] `.env` file exists in `crews/agentbay_sdk/`
- [ ] `AGENTBAY_API_KEY` is set
- [ ] `OPENAI_API_KEY` is set
- [ ] `OPENAI_API_BASE` is correct (for Bailian)
- [ ] `OPENAI_MODEL_NAME` has `openai/` prefix (for Bailian)
- [ ] API keys are valid and not expired
- [ ] Account has sufficient balance
- [ ] Network can reach API endpoints
- [ ] All dependencies are installed

---

## Getting Help

If you've tried everything and still have issues:

1. **Check the diagnostic output**:
   ```bash
   python diagnose.py > diagnostic.log 2>&1
   ```

2. **Review the error message carefully** - it often tells you exactly what's wrong

3. **Common mistake**: Forgetting the `openai/` prefix for Bailian models

4. **Try the minimal test**:
   ```python
   from openai import OpenAI
   client = OpenAI(
       api_key="your_key",
       base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
   )
   print(client.chat.completions.create(
       model="qwen-plus",
       messages=[{"role": "user", "content": "Hi"}]
   ))
   ```

5. **Contact support**:
   - AgentBay: https://agentbay.console.aliyun.com/
   - Bailian: https://bailian.console.aliyun.com/

---

## Quick Reference

### Correct Bailian Configuration

```bash
# .env file
AGENTBAY_API_KEY=sk-xxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL_NAME=openai/qwen-plus
```

### Correct OpenAI Configuration

```bash
# .env file
AGENTBAY_API_KEY=sk-xxxxxxxxxxxxx
OPENAI_API_KEY=sk-proj-xxxxxxxx
OPENAI_MODEL_NAME=gpt-4o-mini
# No OPENAI_API_BASE needed
```

### Test Commands

```bash
# Diagnostic
python diagnose.py

# Run tests
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v

# Verbose mode
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v -s
```

