# Sandbox Execution

Sandboxes run agent code in isolated environments with their own filesystem and an `execute` tool for shell commands. Use when agents need to write files, install dependencies, and run commands without affecting the host machine.

All sandbox backends implement `SandboxBackendProtocol` with an `execute()` method for shell commands. The base class automatically provides filesystem tools (`ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`) on top of this.

---

## Modal

**Use case**: ML/AI workloads, GPU access. Requires `modal setup` for authentication.

```bash
pip install langchain-modal
```

```python
import modal
from langchain_anthropic import ChatAnthropic
from deepagents import create_deep_agent
from langchain_modal import ModalSandbox

app = modal.App.lookup("your-app")
modal_sandbox = modal.Sandbox.create(app=app)
backend = ModalSandbox(sandbox=modal_sandbox)

agent = create_deep_agent(
    model=ChatAnthropic(model="claude-sonnet-4-20250514"),
    system_prompt="You are a Python coding assistant with sandbox access.",
    backend=backend,
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Create a small Python package and run pytest"}]
})

modal_sandbox.terminate()
```

---

## Runloop

**Use case**: Disposable devboxes for isolated code execution. Requires `RUNLOOP_API_KEY` environment variable.

```bash
pip install langchain-runloop
```

```python
import os
from runloop_api_client import RunloopSDK
from langchain_anthropic import ChatAnthropic
from deepagents import create_deep_agent
from langchain_runloop import RunloopSandbox

client = RunloopSDK(bearer_token=os.environ["RUNLOOP_API_KEY"])
devbox = client.devbox.create()
backend = RunloopSandbox(devbox=devbox)

agent = create_deep_agent(
    model=ChatAnthropic(model="claude-sonnet-4-20250514"),
    system_prompt="You are a Python coding assistant with sandbox access.",
    backend=backend,
)

try:
    result = agent.invoke({
        "messages": [{"role": "user", "content": "Create a small Python package and run pytest"}]
    })
finally:
    devbox.shutdown()
```

---

## Daytona

**Use case**: TypeScript/Python development, fast cold starts. Requires `DAYTONA_API_KEY` environment variable.

```bash
pip install langchain-daytona
```

```python
from daytona import Daytona
from langchain_anthropic import ChatAnthropic
from deepagents import create_deep_agent
from langchain_daytona import DaytonaSandbox

sandbox = Daytona().create()
backend = DaytonaSandbox(sandbox=sandbox)

agent = create_deep_agent(
    model=ChatAnthropic(model="claude-sonnet-4-20250514"),
    system_prompt="You are a Python coding assistant with sandbox access.",
    backend=backend,
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Create a small Python package and run pytest"}]
})

sandbox.stop()
```

---

## CLI Usage

Sandboxes can also be used via the CLI without writing Python:

```bash
uvx deepagents-cli --sandbox <provider> --sandbox-setup ./setup.sh
```

Setup scripts run inside the sandbox before the agent starts -- use them to clone repos, set env vars, or install dependencies.

---

## Common Pattern

All providers follow the same lifecycle:

1. **Create** the sandbox using the provider's SDK
2. **Wrap** it in the provider's `*Sandbox` backend class
3. **Pass** as `backend` to `create_deep_agent`
4. **Invoke** the agent
5. **Terminate** the sandbox (use `try`/`finally` for cleanup)

---

## File Operations

All providers support file transfer:

```python
# Upload files (path must be absolute)
backend.upload_files([("/app/main.py", b"print('hello')")])

# Download files (returns objects with .content and .error)
results = backend.download_files(["/app/main.py"])
```

---

## Security Model

The sandbox is the security boundary -- enforce constraints at the tool/sandbox level, not by expecting the model to self-police.

**Never put secrets inside a sandbox.** Context injection attacks can read credentials from environment variables or files. Keep secrets in external tools or use network proxies that inject credentials server-side.

---

## Documentation Links

- [Sandbox Providers (Official Docs)](https://docs.langchain.com/oss/python/deepagents/sandboxes)
- [Execute Code with Sandboxes for DeepAgents (Blog)](https://blog.langchain.com/execute-code-with-sandboxes-for-deepagents/)
