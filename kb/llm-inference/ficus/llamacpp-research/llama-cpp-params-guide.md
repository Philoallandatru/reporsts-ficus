---
type: Concept
title: llama.cpp 参数完全指南（小白也能看懂）
description: 你可以把 llama.cpp 想象成一家“餐厅后厨”：
tags:
- llm
- llamacpp
- kv-cache
sources:
- c:/Users/Administrator/Documents/Code/my-code/lm-llama/research/llama-cpp-params-guide.md
createdAt: '2026-11-23'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# llama.cpp 参数完全指南（小白也能看懂）

> 基于仓库内 `llama.cpp` 源码编写（commit `f5e85d43a`，约 b10669 后 4 个提交）。
> 参数的“唯一真相来源”是 `llama.cpp/common/arg.cpp`（约 357 个 `add_opt` 定义，
> 从 ~1440 行到 ~3262 行），默认值在 `llama.cpp/common/common.h` 的
> `common_params` / `common_params_sampling` 结构体里，采样执行顺序在
> `llama.cpp/common/sampling.cpp` 的 `common_sampler_init()` 中。
> 用法：`llama cli --help` / `llama serve --help` 只显示与当前子命令相关的参数子集，
> 本文档把它们合并到一张大图里讲清楚。
>
> 阅读建议：先看第 1–2 节建立心智模型，再按需查表。第 11 节是“抄作业”速查。

---

## 1. 一句话心智模型：参数只控制 6 件事

你可以把 llama.cpp 想象成一家“餐厅后厨”：

| 控制对象 | 比喻 | 对应参数家族 |
|---|---|---|
| 1. 用哪个菜谱/食材 | 选模型文件 | `-m/-hf/-hff/-mu`，`-mmproj`（多模态） |
| 2. 桌子有多大、一次上几个菜 | 显存/内存与并发规划 | `-c/-n/-b/-ub`，`-ngl/-sm/-ts`，`-ctk/-ctv`，`-fa` |
| 3. 厨师有几个人、怎么分工 | CPU 线程亲和性 | `-t/-tb`，`-C/-Cr/--prio/--poll`，`--numa` |
| 4. 菜的口味 | 采样（随机性/重复/格式） | `--temp/--top-k/--top-p/--min-p`，惩罚项，`--grammar/-j` |
| 5. 点菜方式 | 输入输出与交互 | `-p/-f/--in-file`，`-cnv/-i`，`--chat-template` |
| 6. 开店还是摆摊 | CLI 一次性运行 vs server 常驻服务 | `--host/--port/-np`，`--cache-prompt`，`--api-key`，推测解码 `--spec-*` |

记住这 6 类，300 多个参数就不再吓人：**大部分参数是第 2/3/6 类中同一概念的“草稿模型镜像版”**（`--spec-draft-*`，约 30 个），
或“已删除但保留报错提示的兼容项”（`--draft-min` 等 5 个），或“一键预设”（`--fim-qwen-*` 等 10 个）。

### 参数的三种来源（优先级从低到高）

1. **配置文件** `config.ini`（系统级 `/etc/llama.cpp/config.ini` → 用户级 `~/.config/llama.cpp/config.ini`），后文件覆盖前者；
2. **环境变量**（如 `LLAMA_ARG_THREADS`、`LLAMA_ARG_CTX_SIZE`、`LLAMA_API_KEY`），定义在每个参数的 `.set_env(...)` 上；
3. **命令行**显式传参，优先级最高。

`common/arg.cpp` 约 716–945 行实现了这套加载顺序：先读 config，再读 env，最后解析 CLI。

---

## 2. 先跑起来：两条最小命令

```bash
# 方式 A：本地一次性问答（CLI）
llama cli -hf ggml-org/Qwen3.5-0.8B-GGUF -c 8192 -ngl 99 -n 512 -p "你好"

# 方式 B：常驻 OpenAI 兼容服务（含 WebUI）
llama serve -hf ggml-org/Qwen3.5-0.8B-GGUF -c 8192 --port 8080 -np 4
# 然后打开 http://127.0.0.1:8080，或调 POST /v1/chat/completions
```

- `-hf` = 从 Hugging Face 自动下载 GGUF（还要 `--hf-file` 精确到文件名时用）。
- `-ngl 99` = 尽量把层都 offload 到 GPU（99 表示“全放”，见第 4 节）。
- `-c 8192` = 上下文窗口；`-n 512` = 最多生成多少 token；`-np 4` = server 同时服务几个请求（slot 数）。

---

## 3. 选模型：`-m / -hf / -mmproj`（第 1 类）

| 参数 | 默认 | 一句话 |
|---|---|---|
| `-m, --model FNAME` | `""`（必填，server 除外可走 router） | 本地 GGUF 路径。分片模型给第一片（如 `model-00001-of-00003.gguf`）。 |
| `-mu, --model-url URL` | `""` | 从 URL 下载模型再加载。 |
| `-hf, -hfr, --hf-repo REPO` | `""` | Hugging Face 仓库（如 `ggml-org/Qwen3-8B-GGUF`），配合 `-hff` 选文件，不写则自动挑。 |
| `-hff, --hf-file FILE` | `""` | HF 仓库内的文件名。 |
| `-hft, --hf-token TOKEN` | `""` | 私有仓库/高频下载的鉴权 token。 |
| `-dr, --docker-repo` | `""` | 从 Docker 镜像式仓库拉模型（小众）。 |
| `-a, --alias` / `--tags` | 空集合 | 给模型起别名/打标签，只用于 router 多模型模式的信息展示与路由。 |
| `-mm, --mmproj FNAME` | `""` | 多模态投影模型（VLM 必备，如 Qwen-VL 的 mmproj）。`--mmproj-url` 为其 URL 版。 |
| `--mmproj-offload` / `-mmdev` | GPU 开 / 自动 | 多模态编码器放不放 GPU、放哪块卡。 |
| `--mmproj-auto`（反向开关） | 开 | 显式禁用 mmproj 自动加载。 |
| `--override-kv KEY=TYPE` | 无 | 覆盖 GGUF 元数据（如改 `tokenizer.chat_template`），调试模板时用，可重复指定。 |
| `--check-tensors` | 关 | 加载时校验张量数据完整性，怀疑文件损坏时开。 |
| `--lora FNAME [scale]` / `--lora-scaled` | 无 | 挂 LoRA 适配器；`--lora-init-without-apply` 只加载不生效（server 上稍后经 `/lora-adapters` 动态挂）。 |
| `--control-vector FNAME [scale]` | 无 | 挂 steering/control-vector；`--control-vector-layer-range s e` 限制作用层。 |

**新手三选一**：有本地文件用 `-m`；想省事用 `-hf`（可加 `--offline` 强制只用缓存、禁止联网，`common/arg.cpp` 有 `LLAMA_ARG_OFFLINE`）；
VLM（看图说话）必须再加 `-mm, --mmproj`。

---

## 4. 显存与并发规划：`-c/-n/-b/-ub` + offload（第 2 类，最重要）

### 4.1 上下文与生成长度

| 参数 | 默认（`common.h`） | 一句话 |
|---|---|---|
| `-c, --ctx-size N` | `0` = “跟模型训练时的长度” | ** prompt + 生成总共能放多少 token**。不够会截断/移位；太大则 KV cache 吃掉大量显存。 |
| `-n, --predict, --n-predict N` | `-1` = 无限制 | **最多生成多少个新 token**。CLI 常用 `-n 512`；server 端一般由 API 的 `max_tokens` 控制。 |
| `--keep N` | `0` | 开启 `--context-shift`（无限生成）时，开头保留 N 个 token 不被挤掉；`-1` = 全保留。 |
| `--context-shift` | 关 | 长对话写满 `-c` 后自动丢弃中间、保留开头+结尾继续写（会丢信息，聊天续写用）。 |
| `-kvu, --kv-unified` | 关 | 多序列共享一块统一 KV cache（server 高并发省显存，perplexity/bench 常用）。 |
| `--kv-unified-per-slot N` | `0` = 不启用 | 每个 server slot 的上下文上限；不写 `-c` 时共享池大小按 `n_parallel × N` 估算。 |
| `--swa-full` | 关 | 对滑动窗口注意力（SWA，如 Gemma/Qwen 某些）用全尺寸 cache：更准但更吃显存。 |
| `-ctxcp, --ctx-checkpoints N` | `32` | server 每个 slot 存几个“存档点”，配合 `--cache-reuse` 做前缀复用/回滚。 |
| `-cms, --checkpoint-min-step N` | `8192` | 存档点之间最少隔多少 token，防抖。 |
| `-cram, --cache-ram N`（MiB） | `8192` | server 缓存占内存上限；`-1` 不限，`0` 禁用。 |
| `--cache-idle-slots` | 开 | 新任务来了先把空闲 slot 存档清场，让复用更干净。 |

**比喻**：`-c` 是桌子大小，`-n` 是允许你续几个菜，`--keep/--context-shift` 是桌子满了先撤哪些盘子，
`--cache-reuse N`（server 参数，默认 `0`）是“拼桌”：新客人的前 N 个 token 若和缓存一致就免单（跳过 prefill）。

### 4.2 批处理：`-b / -ub`（prefill 快慢的关键）

| 参数 | 默认 | 一句话 |
|---|---|---|
| `-b, --batch-size N` | `2048` | **逻辑批大小**：一次 prompt 处理最多吃多少 token。大= prefill 快但瞬间显存高。 |
| `-ub, --ubatch-size N` | `512` | **物理批大小**：逻辑批再切成多小块真正执行。小= 显存平稳但调度开销大。 |

经验法则：GPU 显存充足就把 `-b` 调大（如 4096），OOM 就调小 `-ub`（如 256）。
`--fit/--fit-print`（默认开 fit）会自动按空闲显存压缩未显式设置的参数并可打印估算，`--fit-ctx 4096` 是压缩时保底的上下文。

### 4.3 模型放哪：GPU offload

| 参数 | 默认 | 一句话 |
|---|---|---|
| `-ngl, --gpu-layers N` | `-1` = 自动 | **多少层放 GPU**。`-1` 自动，`0` 纯 CPU，`99`/`999` 约等于全放。`<= -2` 也是全放的另一种写法。 |
| `-dev, --device dev1,dev2` | 自动 | 指定用哪几块后端设备（CUDA/Vulkan/Metal…），多卡必填。 |
| `-sm, --split-mode` | `layer` | 多卡切分方式：`layer` 按层切（常用） vs `row` 按行切。 |
| `-ts, --tensor-split 60,40` | `0`（自动） | 张量在多卡间按比例切（如 60%/40%）。 |
| `-mg, --main-gpu N` | `0` | 主卡（放 scratch 和小张量）。 |
| `-ot, --override-tensor "blk.0.*=CPU"` | 无 | 正则指定某些张量强制放某种 buffer（CPU/GPU），可重复。 |
| `-cmoe/--cpu-moe`，`-ncmoe N`，`-ncffn N` | 关 | MoE 模型的专家/FFN 留 CPU（显存不够跑大 MoE 的救命开关）。 |
| `-kvo, --kv-offload`（反向：`--no-kv-offload`） | 开（offload） | KV cache 放不放 GPU。关了省显存但 decode 变慢。 |
| `-ctk, --cache-type-k` / `-ctv, --cache-type-v TYPE` | `f16` | KV cache 精度：`f32/f16/q8_0/q4_0/...`。量化（如 `q8_0`）省显存、微损质量，长上下文必备。 |
| `-fa, --flash-attn on\|off\|auto` | `auto` | Flash Attention：省显存、长上下文更快；老显卡不支持会自动回退。 |
| `--repack` / `--no-host` / `--op-offload` | 开/开/开 | 权重重排与算子 offload 微调，默认别动，profiling 时再玩。 |
| `--mlock/--mmap/-dio/ -lm/--load-mode` | auto | `mlock` 锁内存防 swap、`mmap` 内存映射加载、`direct-io` 直接 IO；`--load-mode` 统一控制。SSD+大内存默认即可。 |
| `--tensor-read-lazy` | auto | 按需读张量，冷启动更快。 |
| `--rpc SERVERS` | 无 | 把计算 RPC 分发到远端机器（集群推理）。`--list-devices` 先看有哪些后端可用。 |

---

## 5. CPU 线程：`-t/-tb` 与亲和性（第 3 类）

| 参数 | 默认 | 一句话 |
|---|---|---|
| `-t, --threads N` | 自动（`LLAMA_ARG_THREADS`） | **生成（decode）用几个 CPU 线程**。一般设为物理核心数；超线程收益递减。 |
| `-tb, --threads-batch N` | 同 `-t` | **prompt 处理（prefill）用几个线程**，可单独设更大。 |
| `-C, --cpu-mask M` / `-Cr, --cpu-range lo-hi` | 无 | 把计算绑到指定 CPU（hex mask 或区间），防 NUMA 跨节点掉速。`-Cb/-Crb` 是 batch 版。 |
| `--cpu-strict 0/1` | `0` | 严格绑定（不漂移），绑核跑分时开。batch 版 `--cpu-strict-batch` 默认跟随。 |
| `--prio N` | `0` | 进程优先级：`-1` 低，`0` 普通，`1` 中，`2` 高，`3` 实时。batch 版 `--prio-batch` 同理。 |
| `--poll 0-100` | `0` | 忙等轮询强度：`0` 最省电， latency 敏感可调高（费电）。 |
| `--numa auto\|isolate\|...` | `disabled` | NUMA 策略，多路服务器调优用。 |

> server 高并发时瓶颈多在 GPU/scheduler，CPU 线程数照抄 `nproc` 即可；真正要调的是第 8 节的 slot 数与批大小。

---

## 6. 采样：决定“口味”（第 4 类，最多也最有趣）

采样链在 `common/sampling.cpp:common_sampler_init()` 按固定顺序组装，
默认顺序（`common.h:261`）为：
`penalties → dry → top_n_sigma → top_k → typical_p → top_p → min_p → xtc → temperature`，
可用 `--samplers` / `--sampler-seq` 改顺序（用字母串，如 `d k p t`，`sampling.cpp:797` 附近定义了字母映射）。
`--temp 0`（贪心）会走特殊分支：只保留 penalties + temperature/dist。

### 6.1 随机性三件套（先调这三个）

| 参数 | 默认 | 一句话（怎么调） |
|---|---|---|
| `-s, --seed N` | `LLAMA_DEFAULT_SEED`（随机） | 固定种子可复现。`-1`/不传=每次不同。 |
| `--temp, --temperature F` | `0.8` | **温度**：`0` 贪心（最稳、做题/代码用）；`0.7–1.0` 聊天；`>1.2` 放飞自我。`<=0` 按贪心处理。 |
| `--top-k N` | `40` | 只从概率前 K 个里挑。`<=0` = 不限词表。越大越发散。 |
| `--top-p F` | `0.95` | 核采样：从累积概率 P 的最小集合里挑。`1.0` = 关闭。写作常用 `0.9–0.95`。 |
| `--min-p F` | `0.05` | 低于最优 token 概率 `P%` 的直接砍掉。`0` = 关闭。防胡言乱语比 top-p 更直接。 |
| `--top-nsigma F` | `-1` = 关 | 按 sigma 裁剪，Qwen3 等推荐试 `~1.0` 附近（先查模型卡）。 |
| `--typical F` | `1.0` = 关 | typical sampling，`1.0` 关闭；小众，一般不动。 |
| `--xtc-probability F` / `--xtc-threshold F` | `0.0` / `0.10` | XTC 采样器：降重复、增多样；阈值 `>0.5` 会禁用。默认关闭。 |
| `--dynatemp-range F` / `--dynatemp-exp F` | `0.0` / `1.0` | 动态温度：按熵自动升降温；range `0` = 关闭。 |
| `--adaptive-target F` / `--adaptive-decay F` | `-1` / `0.9` | 自适应 p：往目标概率附近选；负数关闭。实验性。 |
| `--mirostat 0/1/2`，`--mirostat-lr`，`--mirostat-ent` | `0` / `0.1` / `5.0` | Mirostat 1/2：按目标困惑度动态调温，写长文防跑偏；默认关。 |

**抄作业**：做题/抽取 `temp 0`；聊天 `temp 0.7, top-p 0.9, top-k 40, min-p 0.05, repeat-penalty 1.1`；
写小说 `temp 0.9–1.0, min-p 0.02, presence 0.3`。

### 6.2 重复惩罚（话痨/复读机治理）

| 参数 | 默认 | 一句话 |
|---|---|---|
| `--repeat-last-n N` | `64` | 看最近 N 个 token 是否重复；`0` = 关惩罚。注意它同时覆盖 `n_prev`。 |
| `--repeat-penalty F` | `1.0` = 关 | 重复词降权系数，`1.1–1.2` 常用；太大变结巴。 |
| `--presence-penalty F` | `0.0` = 关 | 出现过就罚（去重主题重复）。 |
| `--frequency-penalty F` | `0.0` = 关 | 出现越多次罚越重（压高频词）。 |
| `--dry-multiplier/--dry-base/--dry-allowed-length/--dry-penalty-last-n` | `0.0/1.75/2/64` | DRY 惩罚：专治“车轱辘话”式的长串重复；multiplier `0` = 关闭。`--dry-sequence-breaker` 可追加分隔符（默认 `\n : " *`）。 |
| `-l, --logit-bias TOKEN=BIAS` | 无 | 手动给某 token 加减分（如 `-l 1234=-5` 禁某词），可重复。 |
| `--ignore-eos` | 关 | 无视 EOS 不停（配合 `-n` 截断做“强制续写”评测）。 |

### 6.3 格式约束：grammar / JSON（要稳定输出只看这里）

| 参数 | 一句话 |
|---|---|
| `--grammar GBNF` / `--grammar-file FNAME` | 用 GBNF 文法强制输出格式（如只输出数字/枚举）。 |
| `-j, --json-schema SCHEMA` / `-jf, --json-schema-file` | 给 JSON schema 自动转文法（调 API/结构化抽取必备）。 |
| `-bs, --backend-sampling` | 把采样放后端执行（RPC/异构时有用）。 |

### 6.4 其它采样相关

`--pooling`（embedding 池化 `none/mean/cls/...`）、`--attention`、`--rope-scaling/scale/freq-base/freq-scale`、
`--yarn-*`（YaRN 超长上下文外推五件套）、`-gan/-gaw`（group-attention）——默认 `unspecified/0` 跟模型元数据走，
**玩超长上下文（RoPE/YaRN）才需要动**，否则别碰。

---

## 7. 输入输出与交互（第 5 类）

| 参数 | 默认 | 一句话 |
|---|---|---|
| `-p, --prompt TEXT` | `""` | 直接给提示词。`-f/--file` 从文件读（自动处理尾换行），`--in-file` 批量追加多个输入文件，`-bf/--binary-file` 读二进制，`--stdin` 从管道读（tokenize 工具）。 |
| `-sys, --system-prompt` / `-sysf` | `""` | 系统提示词及其文件版。 |
| `--in-prefix/--in-suffix/--in-prefix-bos` | `""` | 每轮用户输入前后缀；会禁用部分 chat template 自动处理，开了要自负。 |
| `-r, --reverse-prompt STR` | 无 | 遇到该串就停下等用户接话（人机轮转），可重复指定多个。 |
| `-sp, --special` | 关 | 允许输出特殊 token（`<think>` 这类）。 |
| `-e, --escape` | 开 | 转义 `\n\r\t\"\\` 再送模型。 |
| `--prompt-cache FNAME` | `""` | prompt 的 KV 存盘复用；`--prompt-cache-all` 连生成也存，`--prompt-cache-ro` 只读不写。 |
| `--ptc/--print-token-count N`，`--verbose-prompt`，`--display-prompt`，`-co/--color` | 见源码 | token 计数/打印 prompt/彩色区分输入与生成。 |
| `-cnv, --conversation` | 关 | 会话模板模式；`-i/--interactive` 交互式，`-if` 一启动就等输入，`-mli` 多行输入，`--single-turn` 单轮，`--spm-infill` 特殊 infill 模式，`--warmup` 预热（默认开），`--simple-io` 兼容性 IO。 |
| `--perf / --show-timings`，`--no-perf` | 开 | 打印速度（prompt tok/s、gen tok/s）。 |
| `-o/--output`，`--process-output`，`--out-freq/--save-freq` | 无 | 把结果写文件/后处理（imatrix/perplexity 工具链用）。 |

---

## 8. server 常驻服务（第 6 类，`llama serve` 必看）

### 8.1 网络与安全

| 参数 | 默认 | 一句话 |
|---|---|---|
| `--host HOST` | `127.0.0.1` | 监听地址；`0.0.0.0` 对外服务；以 `.sock` 结尾则绑 Unix socket。 |
| `--port PORT` | `8080` | 监听端口（`--fim-*` 等预设会改写）。 |
| `--reuse-port` | 关 | 多进程复用同一端口。 |
| `--api-key KEY[,KEY2]` / `--api-key-file` | 无 | 鉴权；`Authorization: Bearer KEY`。 |
| `--ssl-key-file/--ssl-cert-file` | 无 | HTTPS（PEM）。 |
| `-to, --timeout N` | `3600` | 读写超时（秒）。`--sse-ping-interval`（默认 `30`，`-1` 禁用）防流式连接被中间设备掐掉。 |
| `--threads-http N` | `-1`（自动） | HTTP 线程数。 |
| `--path PATH` / `--api-prefix PREFIX` | `""` | 静态文件目录 / API 前缀。 |
| `--cors-origins/methods/headers/credentials` | `*` 等 | 跨域；`localhost` 特殊值只反射本地 Origin。开了 MCP/agent 会自动收紧到 localhost。 |
| `--metrics/--props/--slots` | 关/关/开 | Prometheus 指标、`/props` 热改全局属性、`/slots` 监控端点三开关。 |

### 8.2 并发与缓存（server 性能就看这几个）

| 参数 | 默认 | 一句话 |
|---|---|---|
| `-np, --parallel N` | `1` | **同时跑几个 slot（并行请求数）**。每 slot 一份序列状态；KV 池按 `-c` 切分（或按 `--kv-unified-per-slot` 估）。 |
| `-cb, --cont-batching` | 开 | 连续批：decode 中途插新请求，不用等整批结束。高并发必开。 |
| `-ns, --sequences N` | `1` | 每条请求内部再开几路采样（best-of-N 式）。 |
| `--cache-prompt` | 开 | prompt KV 缓存（多轮对话/TTFT 优化总开关）。 |
| `--cache-reuse N` | `0` | ≥N token 的公共前缀尝试 KV 平移复用（F0 图里讲的那套）。 |
| `-sps, --slot-prompt-similarity F` | `0.1` | 请求与 slot 历史相似度超阈值才复用该 slot；`0` 禁用。 |
| `--defrag-thold F` | 源码默认 | KV 碎片整理阈值（server 帮助里为 `--defrag-thold`，实现侧按需整理）。 |
| `--sleep-idle-seconds N` | `-1`（不睡） | 空闲 N 秒后休眠省电/省钱。 |
| `--slot-save-path PATH` / `--media-path PATH` | 禁用 | slot KV 落盘 / 本地多媒体目录（`file://` 相对路径解析）。 |

### 8.3 聊天模板与推理（reasoning）/ 结构化

| 参数 | 默认 | 一句话 |
|---|---|---|
| `--jinja` | 开 | 用 Jinja 模板引擎渲染 chat（新模型必备）。 |
| `--chat-template STR` / `--chat-template-file` | 跟模型 | 手动覆盖模板；给了 `--in-prefix/suffix` 会禁用模板。 |
| `--reasoning-format FORMAT` | `deepseek` | 思考标签如何返回：`none/auto/deepseek/deepseek-legacy`。 |
| `-rea, --reasoning on\|off\|auto` | `auto` | 是否启用思考；`--reasoning-effort minimal/low/medium/high/max` 传给模板；`--reasoning-budget N` 为 token 预算（`-1` 不限，`0` 立刻结束），`--reasoning-budget-message` 为预算耗尽时注入的话，`--reasoning-preserve` 保留全程思考链。 |
| `--chat-template-kwargs JSON` | 无 | 透给 Jinja 的额外参数。 |
| `--skip-chat-parsing` | 关 | 强制纯 content 解析（含 tool call 也原样输出）。 |
| `--prefill-assistant` | 开 | 末尾 assistant 消息当“已说一半”续写（prefill）。 |
| `--embedding/--rerank` | 关 | 纯 embedding 模型 / 开 rerank 端点（`--rerank` 会联动 pooling）。 |
| `--lora-init-without-apply` | 关 | LoRA 只加载、稍后 `/lora-adapters` 热挂。 |

### 8.4 多模型 router / 工具 / MCP（进阶）

`--models-dir`（模型目录）+ `--models-preset`（INI 预设）+ `--models-max 4` + `--models-autoload` =
一个 server 按需加载/卸载多个模型（`--stop-timeout` 预设项控制优雅下线）。
`--tools TOOL1,...`（内置工具）、`--tools-runtime`（工具沙箱）、
`--mcp-servers-config/--mcp-servers-json`（MCP 服务）、`-ag/--agent`（一键 agent）、`--ui/--webui`、`--ui-config(-file)`、`--ui-mcp-proxy` =
WebUI 与 agent 实验功能，**不要在不可信网络开**（源码注释原话）。

---

## 9. 推测解码 `--spec-*`（免费午餐：解码加速）

原理一句话：**小模型先猜 N 个 token，大模型一次验算**，猜对就白赚速度，猜错回滚重算。
类型由 `--spec-type` 指定（逗号分隔，默认 `none`），可选 `mtp/dflash/eagle3/dspark/ngram-simple/ngram-map-k/ngram-map-k4v/...`，
`--mtp/--dflash/--eagle3` 为快捷开关；`--spec-default` 是一组调好的 ngram 默认。

| 参数 | 默认 | 一句话 |
|---|---|---|
| `--spec-draft-model/-md FNAME`，`--spec-draft-hf/-hfd REPO` | 无 | 草稿小模型（本地/Hub）。不给则只用 ngram 类免草稿模型方案。 |
| `--spec-draft-n-max N` | `3` | 最多猜几个；`--spec-draft-n-min` 保底几个。老别名 `--draft/--draft-max` 已迁移。 |
| `--spec-draft-p-split/--spec-draft-p-min` | `0.1/0.0` | 推测接受概率相关阈值。 |
| `--spec-draft-ngl/--spec-draft-device/--spec-draft-type-k/-v` | 跟主模型 | 草稿模型的 GPU 层数/设备/KV 精度（镜像参数）。 |
| `--spec-draft-threads* /-cpu-mask*/-cpu-range*/-prio*/-poll*` | 跟主模型 | 草稿模型的 CPU 镜像参数（约 12 个，含义同第 5 节）。 |
| `--spec-ngram-simple-size-n/m/min-hits` 等三套（simple/map-k/map-k4v）+ `--spec-ngram-mod-n-match/min/max` | 见 `common.h:352-363` | 免草稿的 ngram 猜词：lookup 长度 N、草稿长度 M、命中阈值。`--lookup-cache-static/dynamic`（`-lcs/-lcd`）可接静态/动态查找缓存文件。 |
| `--spec-synth-len/--spec-synth-rates` | 关 | benchmark 用的合成接受率模拟，别在生产开。 |

> 注意：`--draft-min/--spec-ngram-size-n/--spec-ngram-size-m/--spec-ngram-min-hits` 已删除，
> 传了会直接报错并提示新名字（`arg.cpp` “removed params”段）。

---

## 10. 多模态、评测与“工具箱”参数

- **多模态**：`--image/--audio/--video FNAME`（可重复），`--image-min/max-tokens`，
  `--mtmd-batch-max-tokens 1024`，`--video-fps 4.0`，`--video-timestamp-interval-ms 5000`，`--video-ffmpeg-dir`。
- **评测**：`--ppl/--ppl-stride/--ppl-output-type`（困惑度），`--hellaswag/--winogrande/--multiple-choice`（榜单打分），
  `--kl-divergence/--save-all-logits/--logits-file`，`--embd-normalize/--embd-output-format/--embd-separator/--cls-separator`（embedding），
  `-npp/-ntg/-npl/-pps/-tgs/--output-format`（bench/parallel），`--chunk-size/--chunk-separator/--context-file`（retrieval），
  `--pos/--junk/--chunk`（passkey 长上下文找针）。
- **tokenize 工具**：`--ids/--stdin/--no-bos/--no-parse-special/--show-count`。
- **diffusion（试验）**：`--diffusion-steps/algorithm/block-length/cfg-scale/alg-temp/eps/add-gumbel-noise/visual`。
- **finetune（试验）**：`-lr/-lr-min/-decay-epochs/-wd/-val-split/-epochs/-opt`。
- **TTS**：`--tts-lang/--tts-speaker-file`。
- **一键预设**：`--embd-gemma-default`，`--fim-qwen-{1.5b,3b,7b,30b}-default`，`--fim-qwen-{7b,14b}-spec`（自动配好 draft），
  `--gpt-oss-{20b,120b}-default`，`--vision-gemma-{4b,12b}-default`，`--spec-default`。
  它们只是“帮你填好 `-hf/-hff/-c/-b/--spec-*` 的宏”，可在 `--help` 看到展开。
- **日志**：`-v/--verbose`（全开），`-lv/--verbosity N`（默认 `3`=INFO），`--log-file/--log-disable/--log-colors/--log-prefix/--log-timestamps`，
  `--log-prompts-dir`（调试落盘 prompt）。

---

## 11. 抄作业：常见场景配方

```bash
# 本地聊天（显存 8GB，7B Q4 模型）
llama cli -m model.gguf -c 8192 -ngl 99 -b 2048 -ub 512 \
  --temp 0.7 --top-p 0.9 --min-p 0.05 --repeat-penalty 1.1 -n 1024 -cnv

# 做题/代码（要稳）
llama cli -m model.gguf --temp 0 -n 512 -p "用 Python 写快排，只给代码"

# 结构化抽取（只出 JSON）
llama cli -m model.gguf -j '{"type":"object","properties":{"name":{"type":"string"}}}' -n 256

# server 高并发（4 路，prompt 缓存全开）
llama serve -m model.gguf -c 16384 -np 4 --cache-prompt --cache-reuse 256 \
  --cont-batching --jinja --api-key sk-123 --port 8080

# 长上下文（32k，KV 量化省显存）
llama serve -m model.gguf -c 32768 -ctk q8_0 -ctv q8_0 -fa on -b 4096 -ub 1024 -np 2

# 推测解码加速（7B 主 + 0.5B 草稿）
llama serve -m qwen7b.gguf --spec-draft-model qwen0.5b.gguf --spec-type mtp --spec-draft-n-max 5 -ngl 99

# 私有知识库问答（RAG 数据在文件里）
llama cli -m model.gguf -f question.txt --context-file kb1.txt --context-file kb2.txt -c 16384
```

**排错三板斧**：OOM → 先降 `-ub` 再降 `-b`，再把 `-ctk/-ctv` 换 `q8_0`，最后降 `-c/-ngl`；
太慢 → `--perf` 看是 prefill（prompt toks/s）还是 decode（gen toks/s）慢，分别调 `-b` 与 `--spec-*`；
胡言乱语 → `--temp 0` + `--min-p 0.1` 先止血，再调模板 `--jinja/--chat-template`。

---

## 附：参数→源码字段速查（给想看代码的人）

- 上下文/批：`-c→n_ctx`，`-n→n_predict`，`-b→n_batch`，`-ub→n_ubatch`，`--keep→n_keep`，`-np→n_parallel`，`-ns→n_sequences`。
- 线程：`-t→cpuparams.n_threads`，`-tb→cpuparams_batch.n_threads`。
- 卸载：`-ngl→n_gpu_layers`，`-dev→devices`，`-sm→split_mode`，`-ts→tensor_split`，`-mg→main_gpu`，`-ot→tensor_buft_overrides`。
- KV：`-ctk/ctv→cache_type_k/v`，`-kvu→kv_unified`，`-fa→flash_attn_type`。
- 采样：`--temp→sampling.temp` …（`sampling.*` 全家桶，见 `common.h:224-300`）。
- 模型：`-m→model.path`，`-hf→model.hf_repo`，`-hff→model.hf_file`，`-mm→mmproj.path`。
- server：`--port→port`，`--cache-reuse→n_cache_reuse`，`--slot-save-path→slot_save_path` 等（见 `common.h:448-700`）。
