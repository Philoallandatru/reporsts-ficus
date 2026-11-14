# Qwen3.8 超出 RAM + 显存后的 Strata 单卡实测

实测日期：2026-11-09。工作目录：`C:\Users\Administrator\Documents\Code\tasks\strata-lab`。

**已经跑通：147.42 GiB 的 Qwen3.8-Flash-Next UD-Q5_K_XL，在 RTX 5080 单卡上以 24 GiB 专家 RAM 缓存运行。两次各生成 256 tokens，生成阶段分别达到 8.5、10.1 token/s，同时持续从 SSD 读取专家。**

两段生成合计物理读取 **94.95 GiB**，平均 **1,764 MiB/s（约 1.72 GiB/s）**；57 个生成采样区间中有 56 个读取超过 1 MiB。实验结束后本次引擎已退出，5080 显存回到约 280 MiB。

## 1. 模型、硬件与容量条件

| 项目 | 本次实际值 |
|---|---:|
| 六个 GGUF 分片 | 158,286,406,650 bytes = 147.4157 GiB |
| 主机物理 RAM | 93,792,854,016 bytes ≈ 87.35 GiB |
| RTX 5080 显存 | 16,303 MiB ≈ 15.92 GiB |
| 单卡显存 + RAM | 110,887,788,544 bytes ≈ 103.27 GiB |
| 模型超过上述容量 | 约 44.14 GiB |
| CPU | Core Ultra 7 270K Plus，24 物理核 / 24 逻辑核 |
| 模型磁盘 | C:，ZHITAI Ti600 1TB NVMe，PhysicalDrive2 |
| NVIDIA 驱动 | 616.64 |

六个文件均做了整文件 SHA-256、长度和 GGUF 标识检查。记录在 `evidence/model-verification.json`；预期值来自保存的 ModelScope 清单 `evidence/modelscope-UD-Q5_K_XL.json`。ModelScope 当前文件的哈希由它自己提供，不能视为独立签名。

完整 GGUF 大小包含大型 PLE / n-gram 查找表，不能直接拿 147.42 GiB 减去 RAM 与 VRAM，推导逐 token 的 SSD 流量。本次持续读盘结论来自实际文件层日志与物理磁盘计数。

模型从 ModelScope 下载；Strata 引擎通过本机 Clash HTTP 代理 127.0.0.1:20808 下载。GitHub 代理站也测试过，但速度较低，未作为最终引擎下载路径。发布压缩包与 GitHub releases API 的 SHA-256 digest 比较一致。

## 2. 真正生效的配置

- Strata 应用版本 v0.2.12；引擎 0.1.58，CUDA 13.0，sm_120。
- 引擎 BUILD.json 声明提交 `8a42a9457db62568d1663c8c1bcc01cfffae5355`；匹配源码已保存在工作目录。
- 物理 GPU 0：RTX 5080。GPU 1 的 5060 Ti 未加入本次引擎的可见设备。
- `--resident-budget-gib 24`，32K 上下文，INT8 KV，单请求，视觉关闭。
- 15 个 CPU expert workers，host thread 也参与 drain。
- MTP 草稿层开启，`--spec 4 --spec-min-p 0.5`；请求关闭 thinking。
- 实验副本配置关闭会话 parking 和 prompt checkpoint，以便分别采样两次请求。
- 保留上游默认 `STRATA_ROUTE_TAIL_SKIP=7`。它会在特定 verify window 条件下跳过低排名的 missed expert，输出可与不跳过时不同；这些速度不能当作与另一引擎等质量的比较结果。

`engine.log` 的实际分层结果：

| 专家层 | 日志中的实际配置 |
|---|---|
| 专家总量 | 约 91.6 GiB |
| VRAM 专家缓存 | 1,946 个专家槽，约 7.25 GiB |
| page-locked RAM 专家副本 | 6,432 个专家，24.00 GiB |
| 其余专家文件层 | 约 60.4 GiB，按需无缓冲读取 |
| PLE 表 | direct read probe 正常；独立的按行读取路径 |

直接证据见本次 `engine.log`：

```text
FileExpertSource: mapped pinned cache complement ready: resident 24.00 GiB, pinned 24.00 GiB in 17 s; page-locked and mapped
strata generate: the mapped view of the experts is closed (3 GGUF shards unmapped; every expert outside RAM and VRAM is read unbuffered)
```

“mmap 专家模式”是这个 source 的入口名称；在本次运行中，建立 RAM 副本后重检确认内存不足以缓存文件层，随即关闭专家映射，改走显式无缓冲读取。因此需要看完整启动日志，而不能停在早先的 `experts via mmap` 一行。

**24 GiB 仅限制专家常驻副本。** 它不是 Windows 进程的 24 GiB 硬上限，也不包含所有 staging、KV、驱动、Python 等开销。实测进程树 RSS 采样峰值为 **28.06 GiB**；主机可用 RAM 最低为 **20.45 GiB**。

## 3. 实测读写与速度

记录共 166 份快照，通常约一秒一份，阶段边界另取共享快照。计时使用 Windows `QueryPerformanceCounter()`，本机分辨率 100 ns。GPU 查询在边界锁之外，保留独立时间戳。

下表是 **PhysicalDrive2 全盘物理计数**，包含同盘其他程序的 I/O；不是把引擎自己的逻辑读取计数冒充 SSD 流量。各阶段的物理字节之和与首末累计计数核对一致。

| 阶段 | 时长 s | 物理读 GiB | 物理写 GiB | 平均读 MiB/s |
|---|---:|---:|---:|---:|
| 启动前基线 | 9.94 | 0.016 | 0.1885 | 1.61 |
| 加载模型 | 45.00 | 35.622 | 0.4275 | 810.59 |
| 就绪空闲 | 10.02 | 0.035 | 0.0261 | 3.53 |
| 请求1：首 token 之前 | 6.50 | 12.270 | 0.0135 | 1,933.93 |
| 请求1：生成阶段 | 29.93 | 52.478 | 0.0363 | 1,795.37 |
| 请求1之后空闲 | 5.02 | <0.001 | 0.0009 | 0.04 |
| 请求2：首 token 之前 | 5.91 | 11.311 | 0.0070 | 1,961.04 |
| 请求2：生成阶段 | 25.19 | 42.477 | 0.0106 | 1,727.06 |
| 请求2之后空闲 | 5.03 | <0.001 | 0.0044 | 0.05 |
| 关闭 | 5.18 | 0.015 | 0.0076 | 2.95 |

请求阶段以客户端收到第一个有效 SSE 输出为边界，含少量 RPC / 客户端开销；它不是内核级精确的 prefill / decode tracing。引擎自己报告的请求耗时另列如下。

| 请求 | 输入 tokens | 输出 tokens | 首 token s | 请求总时长 s | 引擎生成 token/s | 含输入处理的端到端 token/s |
|---|---:|---:|---:|---:|---:|---:|
| 中文说明文件缓存、mmap、direct I/O | 44 | 256 | 6.47 | 36.40 | 8.5 | 7.03 |
| 英文说明桌面 MoE 推理 | 50 | 256 | 5.89 | 31.07 | 10.1 | 8.24 |

两次流均收到正常结束标记和正的 token 计数；`finish_reason=length` 是主动设置 256-token 上限的结果，回答没有写完。完整原始片段保存在 `response-1.sse`、`response-2.sse` 与 `requests-summary.json` 中。它们用于证明实际生成，不是准确性测试。

生成阶段的进程逻辑读取下界分别为 **52.477 GiB、42.478 GiB**，与全盘物理读取的 **52.478 GiB、42.477 GiB** 接近，支持大部分读流量来自本次引擎的判断；两套计数仍是不同口径，不应要求逐字节相等。

两次生成期间，进程 CPU 累计时间约相当于 **14.19、14.46 个逻辑核持续工作**。SSD 持续读取是明确的运行成本，CPU 也在大量计算，现有数据不支持把速度全部归结为一个设备的单一瓶颈。

5080 显存采样峰值为 **14,925 MiB（约 14.58 GiB）**；实验之后约 280 MiB。5060 Ti 的显存采样在约 5,760–5,789 MiB 之间，属于原有桌面负载；实际引擎配置与启动日志明确选择 GPU 0。

## 4. 在这一层与 llama.cpp 的区别

完整源码对照见 [source-comparison.md](source-comparison.md)，引用均固定到实际分析的提交。核心区别是专家的放置、缓存与调度：

1. **Strata 有专门的专家常驻 RAM 副本和 VRAM 槽。** 根据 profile 与路由热度管理专家，GPU 命中由 GPU 计算，其他专家由 CPU pool 或部分 pinned PCIe share 处理。未缓存的专家才走文件后备路径。
2. **本次 Strata 文件层由引擎显式发起无缓冲读取。** Windows 路径使用 `FILE_FLAG_NO_BUFFERING | FILE_FLAG_OVERLAPPED`，按对齐范围拼批读取到主机缓冲。它不是 SSD 直接 DMA 到显存。
3. **Prefill 另有 Stager / host ring / GPU ring 流水，PLE 也有独立读取路径。** 因此加载、首 token 前与生成阶段应分别测量。
4. **llama.cpp 也支持按路由专家切片上传。** 其调度器读取 IDs，只拷贝当前用到的专家区间，不能概括成“只能整层卸载”。在所读 pin 中没有看到与 Strata 相同的跨 token 热度排名、持久专家槽和交换淘汰策略。

关键实现：[Strata open_direct](https://github.com/Niko1221/Strata/blob/8a42a9457db62568d1663c8c1bcc01cfffae5355/src/core/expert_source.cpp#L2465)、[llama.cpp 路由专家切片上传](https://github.com/ggml-org/llama.cpp/blob/3cf03257f219afbe7334045ff7c6a06ac68c627d/ggml/src/ggml-backend.cpp#L1693)。

本次没有运行 llama.cpp 的速度基线，所以没有给出两个引擎的速度倍数。

## 5. 复现

本机模型已经安装在：

```text
C:\Users\Administrator\Documents\Code\tasks\strata-lab\data\models\unsloth-UD-Q5_K_XL
```

从 PowerShell 运行以下命令；每次使用一个未存在的新输出目录，以保留原始实验。

```powershell
Set-Location 'C:\Users\Administrator\Documents\Code\tasks\strata-lab'
.\Strata\.venv\Scripts\python.exe .\scripts\experiment.py --config .\Strata\strata-unsloth-ud-q5_k_xl.json --output .\runs\repeat-5080-budget24 --port 18080 --max-tokens 256
.\Strata\.venv\Scripts\python.exe .\scripts\analyze_run.py --run .\runs\repeat-5080-budget24
```

实验脚本只监听 127.0.0.1，运行期间独占本次引擎，结束时清理自己启动的进程树。它不会停止按名称匹配到的其他程序。

如需仅启动聊天服务，安装器已生成 `Strata\run-unsloth-ud-q5_k_xl.bat`；它使用原始 8080 配置，和实验脚本的 18080 是两种启动方式。不要在实验过程中同时再启动一份模型。

`download_model.ps1` 复用上游安装器的 ModelScope 下载、断点续传、校验和打包流程；`verify_download.py` 可重新做完整权重校验。重新校验会再次读取全部模型文件，应在测量之前完成，避免混入推理 I/O。

## 6. 证据与检查范围

- `evidence/model-verification.json`：六个模型分片的整文件 SHA-256、长度和超出单卡显存加 RAM 的断言。
- `evidence/hardware.json`：硬件、设备身份与磁盘映射。
- `runs/outofcore-5080-budget24-01/config.json`：实际实验副本配置。
- 同目录 `engine.log`、`server.log`：缓存分层、读取模式和请求性能。
- `samples.jsonl`、`disk-summary.csv`、`sampling-status.json`：原始计数、分阶段结果及采样状态。
- `response-*.sse`、`requests-summary.json`：原始输出、正常流终止与 usage。
- `analysis.json`：容量以外的实测验收与统计；阶段字节守恒断言已执行。

采样脚本的回归自检覆盖阶段字节守恒、短阶段、零时长区间保留字节、计数器重置、新生进程、截断 SSE、零 token 和 GPU 查询阻塞。独立检查发现的问题已修复后再用于本次实际实验。

边界：这是同机一次运行、两段短回答；没有做长上下文、长时间稳定性或答案准确性评测。磁盘为系统盘，全盘统计包含其他程序；进程 I/O 标为观测下界，短命进程与退出尾段可能漏采。引擎日志曾提示 Windows commit 余量较小和 VRAM 余量较低，本次两次请求均正常结束，未更改系统页面文件或其他程序。

交付压缩包包含报告、脚本与本次证据，不复制 147 GiB 权重、完整引擎或源码树；这些已经留在上述本机工作目录。
