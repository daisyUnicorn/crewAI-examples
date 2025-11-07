# CrewAI 沙箱执行环境详解

## 概述

CrewAI 的沙箱执行环境（Sandbox Execution Environment）是一个安全、隔离的代码执行系统，允许 Agent 自主生成并执行 Python 代码，同时保护主机系统免受潜在恶意代码的侵害。该系统主要位于 `crewai-tools` 包中的 `CodeInterpreterTool` 模块。

## 核心架构

### 1. 三层执行模式

CrewAI 提供了三种代码执行模式，按安全性从高到低排列：

#### 模式一：Docker 容器执行（推荐，最安全）

**实现位置**：`CodeInterpreterTool.run_code_in_docker()`

**特点**：
- 代码在完全隔离的 Docker 容器中执行
- 使用 Alpine Linux 基础镜像（`python:3.12-alpine`）
- 容器执行完毕后自动清理
- 支持动态安装 Python 库
- 当前工作目录映射到容器的 `/workspace`

**工作流程**：
```python
1. 验证 Docker 镜像是否存在，不存在则构建
2. 创建名为 "code-interpreter" 的容器
3. 挂载当前工作目录到容器的 /workspace
4. 安装所需的 Python 库（通过 pip）
5. 执行 Python 代码
6. 获取执行结果
7. 停止并删除容器
```

**Dockerfile 配置**：
```dockerfile
FROM python:3.12-alpine
RUN pip install requests beautifulsoup4 
WORKDIR /workspace
```

#### 模式二：受限沙箱执行（降级方案）

**实现位置**：`SandboxPython` 类和 `CodeInterpreterTool.run_code_in_restricted_sandbox()`

**触发条件**：当 Docker 不可用或无法访问时自动降级到此模式

**安全机制**：

**1. 阻止的危险模块（BLOCKED_MODULES）**：
```python
BLOCKED_MODULES = {
    "os",           # 操作系统接口
    "sys",          # 系统特定参数和函数
    "subprocess",   # 子进程管理
    "shutil",       # 高级文件操作
    "importlib",    # 导入机制
    "inspect",      # 自省功能
    "tempfile",     # 临时文件和目录
    "sysconfig",    # Python 配置信息
    "builtins",     # 内置函数和异常
}
```

**2. 阻止的不安全内置函数（UNSAFE_BUILTINS）**：
```python
UNSAFE_BUILTINS = {
    "exec",         # 动态执行代码
    "eval",         # 评估表达式
    "open",         # 文件操作
    "compile",      # 编译代码
    "input",        # 用户输入
    "globals",      # 全局变量访问
    "locals",       # 局部变量访问
    "vars",         # 对象属性字典
    "help",         # 帮助系统
    "dir",          # 目录列表
}
```

**3. 受限导入机制**：
```python
@staticmethod
def restricted_import(name: str, ...) -> ModuleType:
    """受限的导入函数，阻止导入危险模块"""
    if name in SandboxPython.BLOCKED_MODULES:
        raise ImportError(f"Importing '{name}' is not allowed.")
    return __import__(name, ...)
```

**4. 安全的内置函数字典**：
```python
@staticmethod
def safe_builtins() -> dict[str, Any]:
    """创建安全的内置函数字典，移除所有不安全的函数"""
    safe_builtins = {
        k: v for k, v in builtins.__dict__.items()
        if k not in SandboxPython.UNSAFE_BUILTINS
    }
    safe_builtins["__import__"] = SandboxPython.restricted_import
    return safe_builtins
```

**5. 受限执行环境**：
```python
@staticmethod
def exec(code: str, locals_: dict[str, Any]) -> None:
    """在受限环境中执行代码"""
    exec(code, {"__builtins__": SandboxPython.safe_builtins()}, locals_)
```

**限制说明**：
- 无法安装新的 Python 库（安全考虑）
- 无法访问文件系统
- 无法执行系统命令
- 无法访问危险的内置函数
- 代码执行结果通过 `result` 变量返回

#### 模式三：不安全模式（不推荐）

**实现位置**：`CodeInterpreterTool.run_code_unsafe()`

**特点**：
- 代码直接在主机上执行，无任何限制
- 可以执行任何 Python 代码，包括危险操作
- 仅应在完全信任的环境中使用
- 支持安装任意库到主机环境

**警告**：此模式会带来严重的安全风险，不应在生产环境使用。

## 执行流程决策树

```
代码执行请求
    │
    ├─ unsafe_mode == True?
    │   ├─ 是 → run_code_unsafe() [不安全模式]
    │   └─ 否 ↓
    │
    ├─ Docker 可用？
    │   ├─ 是 → run_code_in_docker() [Docker 容器模式]
    │   └─ 否 → run_code_in_restricted_sandbox() [受限沙箱模式]
```

## Agent 集成机制

### Agent 配置参数

在 `Agent` 类中，有两个关键参数控制代码执行：

```python
class Agent:
    allow_code_execution: bool = Field(
        default=False,
        description="Enable code execution for the agent."
    )
    
    code_execution_mode: Literal["safe", "unsafe"] = Field(
        default="safe",
        description="Mode for code execution: 'safe' (using Docker) or 'unsafe' (direct execution)."
    )
```

### 自动工具注入

当 `allow_code_execution=True` 时，CrewAI 会自动为 Agent 添加代码执行工具：

```python
# 在 crew.py 中
def _add_code_execution_tools(self, agent: BaseAgent, tools: list[BaseTool]):
    if hasattr(agent, "get_code_execution_tools"):
        code_tools = agent.get_code_execution_tools()
        return self._merge_tools(tools, code_tools)
    return tools

# 在 agent/core.py 中
def get_code_execution_tools(self) -> list[CodeInterpreterTool]:
    unsafe_mode = self.code_execution_mode == "unsafe"
    return [CodeInterpreterTool(unsafe_mode=unsafe_mode)]
```

### Docker 验证

在 Agent 初始化时，如果启用了代码执行，会自动验证 Docker 安装：

```python
def _validate_docker_installation(self) -> None:
    """检查 Docker 是否已安装并运行"""
    docker_path = shutil.which("docker")
    if not docker_path:
        raise RuntimeError("Docker is not installed...")
    
    # 验证 Docker 是否运行
    subprocess.run([docker_path, "info"], check=True, ...)
```

## 使用示例

### 基础用法

```python
from crewai import Agent, Task, Crew
from crewai_tools import CodeInterpreterTool

# 方式一：显式添加工具
programmer_agent = Agent(
    role="Python Programmer",
    goal="Write and execute Python code",
    backstory="Expert Python programmer",
    tools=[CodeInterpreterTool()],
    verbose=True,
)

# 方式二：使用 allow_code_execution（推荐）
programmer_agent = Agent(
    role="Python Programmer",
    goal="Write and execute Python code",
    backstory="Expert Python programmer",
    allow_code_execution=True,  # 自动添加 CodeInterpreterTool
    code_execution_mode="safe",  # 使用安全模式（Docker）
    verbose=True,
)
```

### 自定义 Docker 配置

```python
# 使用自定义 Dockerfile
code_interpreter = CodeInterpreterTool(
    user_dockerfile_path="/path/to/custom/Dockerfile"
)

# 使用自定义 Docker 守护进程 URL（适用于 macOS 等场景）
code_interpreter = CodeInterpreterTool(
    user_docker_base_url="unix://var/run/docker.sock",
    user_dockerfile_path="/path/to/Dockerfile"
)
```

### 不安全模式（仅用于开发/测试）

```python
# ⚠️ 警告：仅用于完全信任的环境
code_interpreter = CodeInterpreterTool(unsafe_mode=True)

# 或在 Agent 中
programmer_agent = Agent(
    role="Python Programmer",
    allow_code_execution=True,
    code_execution_mode="unsafe",  # 不安全模式
)
```

## 安全考虑

### Docker 模式的安全优势

1. **完全隔离**：代码在独立的容器中运行，无法访问主机系统
2. **自动清理**：容器执行完毕后立即删除，不留痕迹
3. **资源限制**：可以通过 Docker 配置限制 CPU、内存等资源
4. **网络隔离**：可以配置容器网络，限制网络访问

### 受限沙箱的限制

1. **无法安装库**：出于安全考虑，不允许安装新的 Python 包
2. **功能受限**：许多常用功能（如文件操作）被禁用
3. **仅适用于简单计算**：适合执行纯计算任务，不适合复杂操作

### 最佳实践

1. **优先使用 Docker 模式**：确保 Docker 已安装并运行
2. **避免不安全模式**：除非在完全受控的开发环境中
3. **限制库安装**：谨慎允许 Agent 安装任意库
4. **监控执行**：在生产环境中监控代码执行情况
5. **审查代码**：对于敏感任务，考虑审查 Agent 生成的代码

## 技术实现细节

### 容器管理

```python
def _init_docker_container(self) -> Container:
    """初始化 Docker 容器"""
    container_name = "code-interpreter"
    client = docker_from_env()
    current_path = os.getcwd()
    
    # 清理已存在的容器
    try:
        existing_container = client.containers.get(container_name)
        existing_container.stop()
        existing_container.remove()
    except NotFound:
        pass
    
    # 创建新容器
    return client.containers.run(
        self.default_image_tag,
        detach=True,
        tty=True,
        working_dir="/workspace",
        name=container_name,
        volumes={current_path: {"bind": "/workspace", "mode": "rw"}},
    )
```

### 库安装机制

```python
@staticmethod
def _install_libraries(container: Container, libraries: list[str]) -> None:
    """在容器中安装 Python 库"""
    for library in libraries:
        container.exec_run(["pip", "install", library])
```

### Docker 可用性检查

```python
@staticmethod
def _check_docker_available() -> bool:
    """检查 Docker 是否可用"""
    try:
        subprocess.run(
            ["docker", "info"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=1,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        Printer.print("Docker is installed but not running...", color="bold_purple")
        return False
    except FileNotFoundError:
        Printer.print("Docker is not installed", color="bold_purple")
        return False
```

## 错误处理

### 常见错误场景

1. **Docker 未安装**：系统会降级到受限沙箱模式
2. **Docker 未运行**：系统会降级到受限沙箱模式
3. **代码执行错误**：返回错误信息，不会崩溃
4. **导入被阻止的模块**：抛出 `ImportError`
5. **使用被阻止的内置函数**：抛出 `NameError`

### 错误消息示例

```python
# Docker 不可用时的降级提示
"Running code in restricted sandbox"  # 黄色输出

# 不安全模式警告
"WARNING: Running code in unsafe mode"  # 紫色加粗输出

# Docker 模式提示
"Running code in Docker environment"  # 蓝色加粗输出

# 代码执行错误
"Something went wrong while running the code: \n{error_message}"
```

## 扩展和自定义

### 自定义 Dockerfile

可以创建自定义 Dockerfile 来预装特定的库或配置：

```dockerfile
FROM python:3.12-alpine

# 预装常用库
RUN pip install numpy pandas matplotlib scikit-learn

# 设置工作目录
WORKDIR /workspace
```

### 扩展 SandboxPython

如果需要修改受限沙箱的行为，可以继承 `SandboxPython` 类：

```python
class CustomSandbox(SandboxPython):
    BLOCKED_MODULES = SandboxPython.BLOCKED_MODULES | {"custom_module"}
    UNSAFE_BUILTINS = SandboxPython.UNSAFE_BUILTINS | {"custom_function"}
```

## 总结

CrewAI 的沙箱执行环境提供了三层安全机制：

1. **Docker 容器模式**（最安全）：完全隔离的执行环境
2. **受限沙箱模式**（降级方案）：通过限制模块和函数提供基本安全
3. **不安全模式**（不推荐）：无限制执行，仅用于开发

对于 Agent 开发者来说，理解这些机制有助于：
- 选择合适的执行模式
- 理解安全限制和权衡
- 调试代码执行问题
- 扩展和自定义执行环境

建议在生产环境中始终使用 Docker 模式，确保 Agent 生成的代码不会对系统造成安全威胁。
