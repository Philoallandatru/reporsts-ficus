# 同一 IQ2_XS：llama.cpp 与 Strata 实机对照

> **更新（2026-11-11）：** 本文的 llama.cpp 对照用的是**默认配置**（它的 MoE 专家缓存未启用）。
> 补测 `--moe-cache-mib` 后，同一模型、同一组请求下差距从约 4 倍缩到约 2 倍，
> 见 [fair-compare-report.md](fair-compare-report.md)。本文的实测数据与口径仍然有效。

日期：2026-11-09。工作目录：`C:\Users\Administrator\Documents\Code\tasks\strata-lab`。

**llama.cpp 已跑通同一份 Qwen3.8-Flash-Next IQ2_XS。最终配置两次各生成256 tokens，生成速度28.32、29.78 token/s。配对的Strata关闭了低排名专家跳过，使用原先相同的实际6554个GPU专家槽，生成119.2、122.6 token/s。**

两边都使用物理GPU 0的RTX 5080单卡。主表来自实际HTTP响应、原生日志和同一套资源采样器；没有运行另一份重新量化的主模型。

## 1. 最终配对结果

| 指标 | Strata全路由、6554热专家槽 | llama.cpp：CPU39层专家＋GPU9层专家 |
|---|---:|---:|
| 请求1生成速度，引擎自报 | 119.2 token/s | 28.32 token/s |
| 请求2生成速度，引擎自报 | 122.6 token/s | 29.78 token/s |
| 请求1首token | 0.51 s | 1.22 s |
| 请求2首token | 0.34 s | 0.75 s |
| 请求1端到端输出速度 | 96.72 token/s | 25.04 token/s |
| 请求2端到端输出速度 | 105.87 token/s | 27.51 token/s |
| 两段生成物理读量 | 41.22 MiB | 47.14 MiB |
| 两段生成物理写量 | 1.14 MiB | 3.21 MiB |
| 生成阶段平均物理读速 | 9.79 MiB/s | 2.68 MiB/s |
| RSS采样峰值 | 35.18 GiB | 28.62 GiB |
| GPU0显存采样峰值 | 14,833 MiB | 14,731 MiB |
| 主机可用RAM最低值 | 13.85 GiB | 20.14 GiB |

以各引擎自报的生成速度计算，本次Strata配置约为llama.cpp配置的4.1–4.2倍；端到端约3.8–3.9倍。这个比值只描述本文的硬件、参数和两条短请求。

**本轮两边生成期的物理读量都只有几十MiB。** 专家权重已在RAM/GPU中，保留PLE等小量读取。不能用上一轮大Q5模型的持续SSD专家读取来解释本轮的速度差。llama.cpp的平均读带宽较低也不代表读量更少：它生成用时更长，总读量实际略高。

上轮Strata的145.1 / 142.6 token/s使用默认`STRATA_ROUTE_TAIL_SKIP=7`。这次主表额外关闭该近似项，因此使用119.2 / 122.6作为较合适的全路由参考，没有把原先约145直接当作同一计算口径。

## 2. 硬件、版本与共同设置

- RTX 5080，物理GPU 0，约16GiB显存；另一张5060 Ti未加入实验可见设备。
- Core Ultra 7 270K Plus，24物理/逻辑核；物理RAM约87.35GiB。
- 模型位于C盘，ZHITAI Ti600 NVMe，对应PhysicalDrive2。
- 主模型两分片完全复用：IQ2_XS共63.3542GiB。校验记录在`evidence/iq2-xs-verification.json`，每次原生运行前还检查文件长度和mtime没有变化。
- Strata：引擎0.1.58，CUDA13.0，发布声明提交`8a42a9457db62568d1663c8c1bcc01cfffae5355`。
- llama.cpp：官方b12211，`0.9.0-dev`，提交`7d7f0287530bc8981690f361d8c1627dbae1c99a`，Windows x86_64 CUDA13.5发布包。实际版本输出为Clang20.1.8构建。
- NVIDIA驱动616.64；CUDA包已通过设备探测和实际生成运行，没有更换系统驱动或安装系统编译工具。

共同请求与控制项已由`scripts/llama_compare.py`核对：

- 同两条提示词，输入分别44、50 tokens。
- 各输出256 tokens，temperature=0，关闭thinking。
- 32K上下文，单slot/单请求。
- 关闭prompt缓存复用和会话parking；usage中cached_tokens均为0。
- attention KV使用名义8-bit：Strata `int8`，llama.cpp K/V均`q8_0`。混合架构的循环状态等不全是INT8，不宣称缓存格式逐位相同。
- Strata15 expert workers加host共16个参与线程；llama.cpp设置16计算/批处理线程，并以CPU mask `C03FFF`选择与先前相同的一组16个逻辑处理器。各自线程调度和辅助线程仍有区别。
- 两边都启用了真实MTP，且日志/响应记录了正的草稿生成和接受计数。

## 3. 实际内存与专家放置

### Strata

- 所有24,576个专家装入约33.02GiB的RAM arena。
- 6554个热专家槽分布在各层，约8.78GiB GPU专家缓存。
- 本次完整路由运行的自报decode缓存命中率约84.1%、84.8%，另有部分专家经PCIe share处理。
- `STRATA_ROUTE_TAIL_SKIP=0`，本次不跳过该项低排名missed experts。
- PLE默认direct读取，带自己的有界行缓存。

注意，`--expert-cache N`在原生pack里表示N个最大专家blob的字节预算，不保证最终恰为N个实际槽。第一次校准请求6554，实际分配6851槽；该记录保留在`strata-iq2-fullroutes-01`。最终改用6244预算，启动日志和分析断言确认实际6554槽，见`strata-iq2-fullroutes-matched-01`。

### llama.cpp

最终参数为：

```text
-ngl 999 --n-cpu-moe 39 --fit off
--load-mode none --lazy-mode on
-c 32768 -np 1 -t 16 -tb 16
-fa on -ctk q8_0 -ctv q8_0
--cache-ram 0 --no-cache-prompt --reasoning off
```

它把前39层的routed expert权重留在CPU、后9层专家权重放GPU；attention、router、shared expert等不跟着`--n-cpu-moe`全部搬CPU。名义上GPU持久保存9×512=4608组专家权重，和Strata的跨层热专家缓存策略不同。**这里描述的是持久权重放置，不等同于所有阶段的算子执行设备；调度器仍可根据batch等条件上传选中的专家片段。**

`--load-mode none`让普通权重进入直接分配的缓冲；PLE仍保持lazy映射，并未整个读入RAM。运行日志给出：

```text
tensor per_layer_token_embd.weight (size = 27465 MiB) lazy read enabled
CUDA0 model buffer size = 9901.22 MiB
CUDA_Host model buffer size = 27497.07 MiB
CPU_Mapped model buffer size = 27465.95 MiB
```

27GiB级`CPU_Mapped`是PLE映射规模，不代表整表物理驻留。源码中`init_mappings`明确在`use_mmap || lazy.any()`时建立映射，因此普通权重关闭mmap后，lazy表仍可保留映射；lazy区间也排除在Windows预热范围之外。

参考：[b12211 lazy映射实现](https://github.com/ggml-org/llama.cpp/blob/7d7f0287530bc8981690f361d8c1627dbae1c99a/src/llama-model-loader.cpp#L1423)。

两边显存采样峰值接近，但同样的显存GiB不代表相同的专家覆盖和命中率。当前数据支持从专家缓存、调度、算子和MTP实现差异继续分析；没有做逐算子profiling，不能给这些因素分配精确耗时占比。

## 4. MTP对齐与剩余差异

llama.cpp使用公开Unsloth完整原生侧文件：

```text
data/native-mtp/mtp-Qwen3.8-Flash-Next-Q4_K_M.gguf
```

文件为2,786,204,800 bytes；SHA-256按ModelScope清单检查。元数据是`qwen4exp`架构、49总层、1个NextN层，具备自己的embedding和output head。

已下载的shared候选不包含这两个张量，而本次b12211的Qwen4exp MTP路径没有相应target回退；最终没有用shared文件，也没有把Strata私有的`qwen4exp-mtp`封装直接交给llama.cpp。

原生参数：

```text
--spec-type draft-mtp
--spec-draft-model <完整Q4_K_M侧文件>
--spec-draft-ngl 999 --spec-draft-n-cpu-moe 0
--spec-draft-n-max 3 --spec-draft-n-min 0 --spec-draft-p-min 0.5
```

llama.cpp的n-max3表示最多3草稿加1个target，和Strata `--spec 4`的4行验证窗口对应；两边命令行数字不能直接照抄为4。

仍存在重要差异：Strata用其Q2_0 MTP、约106,299词的缩减草稿头；llama.cpp用完整Q4_K_M MTP、248,320词的词表。主模型相同不代表草稿模型相同。MTP验证机制、接受率、GPU空间占用和数值实现也不同，因此不声称这是等质量、逐位一致的纯内核基准。

## 5. 配置校准记录

| 配置 | 生成token/s，请求1 / 2 | 首token s，请求1 / 2 | 用途 |
|---|---:|---:|---|
| llama.cpp CPU40，mmap | 25.67 / 28.30 | 4.18 / 2.56 | 初始运行 |
| llama.cpp CPU40，RAM缓冲 | 28.15 / 27.64 | 1.23 / 0.70 | 按原生日志建议改加载模式 |
| llama.cpp CPU39，RAM缓冲 | 28.32 / 29.78 | 1.22 / 0.75 | 主表采用，增加一层GPU专家 |
| Strata跳过关闭，实际6851槽 | 121.9 / 118.5 | 0.54 / 0.33 | 槽位预算校准，不作为主配对 |
| Strata跳过关闭，实际6554槽 | 119.2 / 122.6 | 0.51 / 0.34 | 主表采用 |

初始llama.cpp日志建议CPU tensor override配合`--load-mode none`；改变后，输入处理耗时明显降低，生成速度变化较小。没有穷举所有层数、线程、batch或MTP设置，不把本文配置称为llama.cpp性能上限。

旧的Strata默认145.1 / 142.6记录也保留在CSV及JSON中，标为历史参考，没有隐去。

## 6. 测量与检查范围

沿用原来的Sampler、SSE读取和阶段划分：通常约1秒采样，阶段切换取共享计数快照；Windows计时用QueryPerformanceCounter。每个完成运行均检查了：

- 两条完整结束的SSE流，正的token计数、无thinking文本，输出各256。
- 输入设置一致，prompt cache复用计数为0。
- MTP实际产生和接受草稿；不是只设置参数而未生效。
- 阶段物理读写量之和与首末累计值守恒。
- 实际GPU可见设备、模型文件、上下文和线程参数。
- Strata主配对的实际6554槽与尾部跳过关闭。

物理计数来自C盘PhysicalDrive2，包含其他程序。进程逻辑I/O另外保存且标为观测下界，不能当作物理SSD字节。各引擎生成速度采用自身原生计时，端到端速度统一用输出tokens除以客户端请求总时长；细微计数约定不同，不把两者混用。

原始生成片段因256-token上限结束，回答没有写完。没有测答案准确性、长上下文、长时间稳定性，也没有清空系统页缓存或驱动缓存来构造严格冷启动。

## 7. 本机复现

在工作目录使用一个未存在的新输出目录：

```powershell
Set-Location 'C:\Users\Administrator\Documents\Code\tasks\strata-lab'
.\Strata\.venv\Scripts\python.exe .\scripts\llama_experiment.py --output .\runs\llama-repeat --cpu-moe-layers 39 --load-mode none --draft .\data\native-mtp\mtp-Qwen3.8-Flash-Next-Q4_K_M.gguf
```

对应的Strata主配对：

```powershell
.\Strata\.venv\Scripts\python.exe .\scripts\experiment.py --config .\configs\strata-iq2-fullroutes-matched.json --output .\runs\strata-repeat-fullroutes --ram-experts --max-tokens 256
```

两条命令应顺序执行，避免同时占用5080。脚本只监听127.0.0.1，结束时清理自己启动的进程树。

`scripts/llama_compare.py`重建本文六份固定记录的对照表。原始数据在`runs/`相应目录，实际argv、版本、原生日志、SSE、usage、采样和CSV均保留。

软件位于`llama-b12211-cuda135/`，原生完整MTP位于`data/native-mtp/`；主IQ2_XS仍在`data/models/IQ2_XS/`。交付包不含庞大的软件二进制或权重，仅包含报告、脚本、配置、校验记录和实测证据。

实验完成后已检查无本次llama-server或Strata引擎残留，GPU0约224MiB、利用率0%。未修改系统驱动、页面文件设置或锁页权限。
