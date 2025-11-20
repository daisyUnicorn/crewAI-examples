# CrewAI x AgentBay SDK 集成示例

本示例展示如何将 `wuying-agentbay-sdk` 封装为 CrewAI 可调用的工具（Tool），并在一个最小可运行的 Crew 中演示用法。

## 快速开始

1. 复制 `.env.example` 为 `.env`，按需填写 AgentBay 和 LLM 相关配置。
2. 安装依赖（推荐使用 `uv` 或 `poetry`）:
   - `uv pip install -e .` 或 `poetry install --no-root`（在仓库根目录或本目录执行）。
3. 运行示例：
   - `python main.py`

## 设计说明

- 将 AgentBay 运行环境（如会话、工具路由、Agent 调度等）抽象为 `AgentBayRuntime`，对外提供 `run(payload)` 方法。
- 通过 `langchain.tools.tool` 装饰器暴露为 CrewAI Tool：`AgentBayTools.run_agentbay`。
- 在 Crew 中配置普通 LLM Agent 与该 Tool，使得 Agent 能在执行 Task 时调用 AgentBay 的能力。

## 目录结构

```
agentbay_sdk/
├── main.py            # 示例 Crew
├── tools.py           # CrewAI Tool 适配
├── runtime.py         # AgentBay 运行时封装
├── pyproject.toml     # 依赖与工具链
├── README.md          # 文档
├── .env.example       # 环境变量示例
```

## 假设的使用场景

- 角色：产品调研助理（CrewAI Agent）。
- 任务：给定一个产品关键词，调用 AgentBay 的能力完成：检索（文档/网页）、提取要点、生成结构化报告。
- 流程：CrewAI Agent 在 Task 中根据描述选择是否调用 `AgentBayTools.run_agentbay`，输入为 JSON 字符串，输出为结构化 JSON 或 Markdown。

## 环境变量

详见 `.env.example`，包括：
- `AGENTBAY_API_BASE`、`AGENTBAY_API_KEY`（若 SDK 需要远程服务）。
- `OPENAI_API_KEY` 或其他 LLM 后端参数（若 Agent 需要）。

## 注意

- 若 `wuying-agentbay-sdk` 包名称或 API 与假设不一致，请根据实际 SDK 调整 `runtime.py` 和 `tools.py` 中的导入与调用。
