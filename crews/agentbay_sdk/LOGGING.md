# Logging and Debug Guide

## Quick Reference

### View Different Log Levels

```bash
cd crews/agentbay_sdk

# 1. Minimal output (default)
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v

# 2. Show print statements and basic output
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v -s

# 3. Show all logs including AgentBay SDK (recommended for debugging)
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v -s --log-cli-level=DEBUG

# 4. Super verbose mode
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -vv -s --log-cli-level=DEBUG

# 5. Save logs to file
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v -s --log-cli-level=DEBUG > test_output.log 2>&1
```

## pytest Options Explained

| Option | Description |
|--------|-------------|
| `-v` | Verbose - show test names and progress |
| `-vv` | Very verbose - show more details |
| `-s` | Don't capture output - show print statements |
| `--log-cli-level=DEBUG` | Show DEBUG level logs |
| `--log-cli-level=INFO` | Show INFO level logs |
| `--log-cli-level=WARNING` | Show WARNING level logs |
| `--capture=no` | Don't capture any output |
| `--tb=short` | Short traceback format |

## Log Levels

AgentBay SDK uses Python's logging module with these levels:

- **DEBUG**: Detailed debugging info (API requests/responses, session details)
- **INFO**: General informational messages (operations start/complete)
- **WARNING**: Warning messages
- **ERROR**: Error messages

## What You'll See at Each Level

### Minimal (`-v`)
```
test_run_python_code_flow PASSED [100%]
```

### With output (`-v -s`)
```
test_run_python_code_flow
🚀 Crew: crew
└── 📋 Task: run_code_task (ID: xxx)
    Status: Executing Task...
    Result: hello from agentbay
PASSED [100%]
```

### With DEBUG logs (`-v -s --log-cli-level=DEBUG`)
```
test_run_python_code_flow
[DEBUG] agentbay: 📤 CreateMcpSessionRequest body:
{
  "Authorization": "Bearer sk-****...",
  "ImageId": "code-latest",
  ...
}
[INFO] agentbay: 🆔 Session created: session-xxxxx
[DEBUG] agentbay: 📥 Response from API
[INFO] agentbay.code: Run code response: {...}
[DEBUG] crewai: Agent starting task...
🚀 Crew: crew
└── 📋 Task: run_code_task
    Agent: Cloud Code Execution Agent
    Status: Executing Task...
    Tool: agentbay_run_code
    Input: {"code": "print('hello from agentbay')", "language": "python"}
    Output: hello from agentbay
    Result: hello from agentbay
PASSED [100%]
```

## Common Use Cases

### 1. Quick Test (Just see if it passes)
```bash
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v
```

### 2. See What's Happening (Basic debugging)
```bash
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v -s
```

### 3. Full Debug (See everything)
```bash
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v -s --log-cli-level=DEBUG
```

### 4. Save Full Logs for Analysis
```bash
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v -s --log-cli-level=DEBUG > debug.log 2>&1
cat debug.log  # View the log
```

### 5. Test Failed - Need Details
```bash
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -vv -s --log-cli-level=DEBUG --tb=long
```

## Understanding the Output

### CrewAI Output Symbols
- 🚀 - Crew starting
- 📋 - Task
- 👤 - Agent
- 🔧 - Tool
- ✅ - Success
- ❌ - Failure

### AgentBay SDK Log Prefixes
- `[DEBUG] agentbay:` - SDK internal operations
- `[INFO] agentbay:` - Important operations
- `[DEBUG] agentbay.code:` - Code execution module
- `[DEBUG] agentbay.session:` - Session management
- `📤` - Outgoing request
- `📥` - Incoming response
- `🆔` - Session ID
- `⏳` - Waiting/in progress

## Filtering Logs

### Show only specific logger
```bash
# Show only AgentBay SDK logs
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v -s \
  --log-cli-level=DEBUG \
  --log-cli-format="%(levelname)s:%(name)s:%(message)s" \
  | grep agentbay
```

### Save to separate files
```bash
# All output
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v -s --log-cli-level=DEBUG > all.log 2>&1

# Only errors
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v -s --log-cli-level=ERROR 2> errors.log
```

## Environment Variable for Logging

You can also set logging level via environment variable:

```bash
# Set log level
export PYTEST_LOG_CLI_LEVEL=DEBUG

# Run test (will use DEBUG level)
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v -s
```

## Troubleshooting with Logs

### Problem: Test passes but want to verify behavior
```bash
# Solution: View full logs
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v -s --log-cli-level=DEBUG
```

### Problem: Need to see API requests/responses
```bash
# Solution: DEBUG level shows all API calls
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v -s --log-cli-level=DEBUG | grep "📤\|📥"
```

### Problem: Want to track session lifecycle
```bash
# Solution: Watch for session creation/deletion
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v -s --log-cli-level=INFO | grep -i session
```

### Problem: Too much output, can't find what I need
```bash
# Solution: Save to file and search
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v -s --log-cli-level=DEBUG > full.log 2>&1
grep "error\|fail\|exception" full.log -i
```

## Configuration File

You can also configure logging in `pytest.ini` or `pyproject.toml`:

```toml
[tool.pytest.ini_options]
log_cli = true
log_cli_level = "INFO"
log_cli_format = "%(asctime)s [%(levelname)8s] %(name)s - %(message)s"
log_cli_date_format = "%Y-%m-%d %H:%M:%S"
```

Then just run:
```bash
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v
```

## Tips

1. **Start simple**: Begin with `-v`, then add `-s`, then `--log-cli-level=DEBUG`
2. **Save logs**: Use `> file.log 2>&1` to save everything for later analysis
3. **Use grep**: Pipe output to `grep` to filter what you need
4. **Watch live**: Use `tail -f` if saving to a file: `tail -f test.log`
5. **Compare runs**: Save logs with timestamps to compare different runs

## Quick Debug Checklist

When debugging, run with full logging and check:
- [ ] Session was created successfully (look for "Session created")
- [ ] Tool was called with correct parameters
- [ ] Code execution returned expected output
- [ ] Session was cleaned up properly
- [ ] No error messages in the log
- [ ] API requests completed successfully

## Example Debug Session

```bash
# 1. Run with full logs
pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v -s --log-cli-level=DEBUG > debug.log 2>&1

# 2. Check for errors
grep -i "error\|fail\|exception" debug.log

# 3. Check session lifecycle
grep "Session created\|Session.*delete" debug.log

# 4. Check tool execution
grep "agentbay_run_code" debug.log

# 5. Check final result
grep "hello from agentbay" debug.log
```

If all checks pass, your integration is working correctly! 🎉

