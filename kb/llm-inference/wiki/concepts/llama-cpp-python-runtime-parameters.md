---
type: Concept
title: llama-cpp-python 参数模型
description: llama-cpp-python 是 llama.cpp 的 Python binding，同时提供 OpenAI-compatible
  FastAPI server。它的底层计算参数大多来自 llama.cpp，但入口变成了 Python `Llama(...)` 构造参数、server CLI、环境变量和
  JSON config。调参时要分清“绑定...
tags:
- llm
- inference
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# llama-cpp-python 参数模型

llama-cpp-python 是 llama.cpp 的 Python binding，同时提供 OpenAI-compatible FastAPI server。它的底层计算参数大多来自 llama.cpp，但入口变成了 Python `Llama(...)` 构造参数、server CLI、环境变量和 JSON config。调参时要分清“绑定层/服务层”和“llama.cpp runtime 层”。

## 参数面

| 参数面 | 常见字段 / 配置 | 作用 |
|---|---|---|
| Python 模型加载 | `Llama(model_path=...)`、`n_gpu_layers`、`split_mode`、`main_gpu`、`tensor_split`、`use_mmap`、`use_mlock`、`kv_overrides` | 加载 GGUF 模型并决定权重如何进入 CPU/GPU 内存 |
| 上下文 / batch | `n_ctx`、`n_batch`、`n_ubatch`、`n_threads`、`n_threads_batch` | 控制 KV cache、prompt processing 批大小和 CPU 线程 |
| KV / Attention / RoPE | `type_k`、`type_v`、`flash_attn`、`offload_kqv`、`swa_full`、`rope_scaling_type`、`rope_freq_base`、`rope_freq_scale`、YaRN 字段 | 控制 KV cache dtype、attention kernel、KQV offload 和长上下文扩展 |
| 输出能力 | `logits_all`、`embedding`、`pooling_type`、`draft_model` | 决定是否返回全 token logits、embedding 模式或 speculative decoding |
| Chat 模板 | `chat_format`、`chat_handler`、`chat_template_kwargs`、HF tokenizer path | 控制 `create_chat_completion` 和 server 的消息格式 |
| Server | `python -m llama_cpp.server`、`host`、`port`、`model_alias`、`api_key`、`root_path`、`interrupt_requests`、`disable_ping_events` | 提供 OpenAI-compatible HTTP 服务 |
| 多模型配置 | `--config_file` / `CONFIG_FILE`、`models[]`、`model_alias` | 按请求中的 `model` 字段路由到配置里的模型 |
| 缓存 | server `cache`、`cache_type`、`cache_size`、Python `set_cache` | 复用 prompt/cache，降低重复 prefill 成本 |
| 多模态 / function calling | `clip_model_path`、`chat_format=llava-*`、`chat_format=functionary-*`、HF tokenizer | 支持图像输入或 OpenAI function calling 风格接口 |

## 与 llama.cpp 的关系

llama-cpp-python 不改变 GGUF、KV cache、GPU offload、batch、RoPE 的底层原理。它改变的是使用入口：

- Python：直接实例化 `Llama`，适合嵌入应用、脚本和自定义 pipeline。
- Server：`python -m llama_cpp.server --model ...`，适合 OpenAI SDK 兼容调用。
- Config file：把多个模型写入 JSON，通过 `model_alias` 路由。
- 环境变量：server 文档说明 CLI 选项也可用环境变量设置。

因此，性能瓶颈仍然要回到 [llama.cpp 参数模型](llama-cpp-runtime-parameters.md)：`n_ctx` 对应上下文/KV cache，`n_gpu_layers` 对应 GPU offload，`n_batch` / `n_ubatch` 对应 prompt processing 分块。

## 关键参数原理

### `n_ctx`

`n_ctx` 是文本上下文窗口。值越大，单会话可容纳 token 越多，但 KV cache 也越大。API reference 中 `n_ctx=0` 表示从模型读取上下文设置；生产中仍建议显式记录，避免模型文件更新后容量和延迟突然变化。

### `n_gpu_layers`

`n_gpu_layers` 决定多少层 offload 到 GPU。`-1` 通常表示尽量全部 offload。它能提升矩阵计算速度，但会和 KV cache、temporary buffer、FlashAttention workspace 争抢显存。

### `n_batch` 与 `n_ubatch`

`n_batch` 是 prompt processing 最大 batch size，`n_ubatch` 是物理 micro-batch。长 prompt 首 token 慢时，增大 batch 可能提速；OOM 或显存峰值过高时，先降低 `n_ubatch`。

### `n_threads` 与 `n_threads_batch`

`n_threads` 用于 generation，`n_threads_batch` 用于 batch/prompt processing。CPU-only 或部分 GPU offload 时很关键；过高会和 Web server、tokenizer、其他模型进程抢核。

### `type_k` / `type_v`、`flash_attn` 与 `offload_kqv`

`type_k` 和 `type_v` 控制 KV cache 的数值类型。降低 KV dtype 可以节省上下文和并发显存，但要用目标任务验证质量。`flash_attn` 依赖构建和硬件支持；`offload_kqv` 把 K/Q/V 相关计算放到 GPU，有利于性能但也会增加显存压力。

### `chat_format` / `chat_handler`

这是 llama-cpp-python 最容易和底层 llama.cpp 混淆的层。模型能加载不代表 chat 模板正确。Functionary function calling 还可能需要 Hugging Face tokenizer，因为 llama.cpp tokenizer 与 HF tokenizer 的处理存在差异。

### 多模型 server 配置

server 支持 config file 的 `models[]`，并按请求中的 `model` 字段匹配 `model_alias`。官方文档说明当前只有一个模型会被加载到内存中，server 会按需要自动 load/unload。这适合本地多模型兼容服务，但不等于多模型同时驻留。

### Server 并发与中断

`interrupt_requests`、`disable_ping_events`、`root_path`、`api_key` 等字段属于 FastAPI/Uvicorn 服务层。它们不改变模型 kernel，但会改变线上行为。尤其是 `interrupt_requests`，启用后新请求可能中断旧请求；生产环境需要配合客户端重试和 streaming 语义一起设计。

## 常见误调风险

| 风险 | 表现 | 处理 |
|---|---|---|
| 把 server 多模型当作并发多模型 | 切换模型时出现冷启动延迟 | 预期它是按需加载；高频模型单独常驻服务 |
| `chat_format` 不匹配 | system/tool 消息失效、function call JSON 异常 | 为每个模型显式记录 chat format 和 tokenizer |
| `embedding=False` 却调用 embeddings | endpoint 报错或输出不符合预期 | embedding 模型启动时启用 `embedding` / pooling 相关配置 |
| `logits_all=True` 常驻 | 显存和返回数据量增加 | 只在需要 logprobs/调试时打开 |
| `n_gpu_layers=-1` 无脑使用 | 权重占满 VRAM，长上下文 OOM | 和 `n_ctx`、`flash_attn`、KV dtype 一起压测 |
| `type_k/type_v` 过度量化 | 长上下文质量波动或兼容性问题 | 先用 f16/q8 建基线，再降到更低精度 |
| `interrupt_requests` 未审计 | streaming 请求被新请求打断 | 明确服务是交互单用户还是多用户并发 |
| 环境变量覆盖不透明 | 本地和服务部署参数不一致 | 启动日志中记录最终 server/model settings |

## 调参路径

1. 先用 Python `Llama(...)` 单模型跑通，确认 `model_path`、chat format 和 tokenizer。
2. 再迁移到 server，固定 `model_alias` 和 OpenAI-compatible endpoint。
3. 显存不足时，先降 `n_ctx` 或 `n_ubatch`，再调整 `n_gpu_layers`。
4. 多模型 config 只用于轻量路由；高并发场景按模型拆服务，再交给网关路由。
5. Function calling、multimodal、embedding 分别做兼容性测试，不要只用普通 chat 请求验收。

## 相关页面

- [llama.cpp 参数模型](llama-cpp-runtime-parameters.md)
- [OpenAI-compatible API 语义与兼容边界](openai-compatible-api-semantics.md)
- [Tokenizer、chat template 与 token 预算](tokenizer-and-chat-templates.md)
- [模型生命周期、热切换与保活](model-lifecycle-hot-swap-and-keepalive.md)
- [跨框架参数对照表](cross-framework-parameter-map.md)

## 关键来源

- llama-cpp-python documentation: https://llama-cpp-python.readthedocs.io/en/latest/
- llama-cpp-python server docs: https://llama-cpp-python.readthedocs.io/en/latest/server/
- llama-cpp-python API reference: https://llama-cpp-python.readthedocs.io/en/latest/api-reference/
- llama-cpp-python GitHub: https://github.com/abetlen/llama-cpp-python
- llama-cpp-python Llama source: https://github.com/abetlen/llama-cpp-python/blob/master/llama_cpp/llama.py
- llama-cpp-python server settings source: https://github.com/abetlen/llama-cpp-python/blob/main/llama_cpp/server/settings.py
