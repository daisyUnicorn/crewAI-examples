# AgentBay SDK Integration (Code Execution Tool)

This subproject integrates `wuying-agentbay-sdk` as a CrewAI Tool, providing capabilities around "code execution" scenarios:
- Unified wrapper for session creation/deletion
- Execute Python/JavaScript code in the cloud (60s timeout limit)
- Expose as Tool for Agent usage
- Provide simple test cases

## Usage

1. Install dependencies (recommended using `uv` or `poetry`, here using `uv` as example):
```bash
uv pip install -r <(uv pip compile -q pyproject.toml)
```
Or directly:
```bash
pip install -e ./crews/agentbay_sdk
```

2. Configure credentials:

**Quick Setup** - Copy the example file and edit:
```bash
cp env.example .env
# Then edit .env with your actual API keys
```

Or manually create a `.env` file:

**Option A: Using OpenAI (Default)**
```bash
AGENTBAY_API_KEY=your_agentbay_api_key
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL_NAME=gpt-4o-mini
```

**Option B: Using Alibaba Cloud Bailian**
```bash
AGENTBAY_API_KEY=your_agentbay_api_key
OPENAI_API_KEY=your_dashscope_api_key
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL_NAME=openai/qwen-plus
```
Note: The `openai/` prefix tells LiteLLM this is an OpenAI-compatible endpoint.

**Option C: Using Azure OpenAI**
```bash
AGENTBAY_API_KEY=your_agentbay_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
```

See `env.example` for more configuration options and detailed examples.

**Troubleshooting**: If you encounter connection errors, run the diagnostic tool:
```bash
python diagnose.py
```
This will check your configuration and test connectivity.

3. Run examples/tests:
```bash
# Basic test
python -m pytest crews/agentbay_sdk/src/agentbay_sdk/tests/test_agentbay_code_flow.py -v

# Or from within the crews/agentbay_sdk directory:
cd crews/agentbay_sdk
python -m pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v

# View detailed logs (including AgentBay SDK logs)
python -m pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v -s --log-cli-level=DEBUG

# Save logs to file
python -m pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v -s --log-cli-level=DEBUG > test.log 2>&1
```

**Note**: Tests require both `AGENTBAY_API_KEY` and `OPENAI_API_KEY` environment variables. Without them, tests will be skipped.

## Key Files
- Wrapper: `agentbay_sdk/api/wuying_agentbay_wrapper.py`
- Tool: `agentbay_sdk/tools/agentbay_code_tool.py`
- Crew: `agentbay_sdk/crew.py`
- Tests: `agentbay_sdk/tests/test_agentbay_code_flow.py`
- Diagnostic: `diagnose.py`

## Troubleshooting

### Connection Errors

If you see `Connection error` or `OpenAI Exception`:

1. **Run diagnostic tool**:
   ```bash
   python diagnose.py
   ```

2. **Check API endpoint URL** (no trailing slash):
   ```bash
   # Correct
   OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1

   # Wrong
   OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1/
   ```

3. **Verify API key format**:
   - Should start with `sk-`
   - Check for extra spaces or newlines

4. **Test network connectivity**:
   ```bash
   curl -I https://dashscope.aliyuncs.com/compatible-mode/v1
   ```

### Model Provider Errors

If you see `LLM Provider NOT provided`:

- **For Bailian**, use `openai/` prefix:
  ```bash
  OPENAI_MODEL_NAME=openai/qwen-plus  # Correct
  OPENAI_MODEL_NAME=qwen-plus         # Wrong
  ```

### Authentication Errors

If you see `AuthenticationError`:

1. Verify your API keys are valid
2. Check account balance (for Bailian/OpenAI)
3. Regenerate API keys if needed

### Common Issues

- **Tests skipped**: Missing `AGENTBAY_API_KEY` or `OPENAI_API_KEY`
- **Import errors**: Run `poetry install --no-root` or `pip install -e .`
- **Module not found**: Check you're in the correct directory

