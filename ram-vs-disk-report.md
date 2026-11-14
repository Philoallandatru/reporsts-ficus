# Qwen3.8 小量化全RAM专家模式实测

日期：2026-11-09。工作目录：`C:\Users\Administrator\Documents\Code\tasks\strata-lab`。

**已完成 IQ2_XS 测试：同一台机器、RTX 5080 单卡，全部 24,576 个专家放入约 33.02 GiB 的 RAM arena。两次各输出 256 tokens，生成速度为 145.1、142.6 token/s；首 token 为 0.47、0.29 秒。**

按用户确认的口径，PLE / n-gram 查找表保留默认 SSD 读取。因此这次不是“全部模型字节都进RAM、零磁盘I/O”的测试。两段生成合计物理读取 **40.98 MiB**，平均 **11.57 MiB/s**；上一轮大Q5量化在相同输出上读取了 **94.95 GiB**。

## 1. 模型与驻留状态

| 项目 | 本次 IQ2_XS |
|---|---:|
| 来源 | ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF |
| 两个GGUF总量 | 68,026,093,024 bytes = 63.3542 GiB |
| 本机物理RAM | 87.35 GiB |
| 实际专家arena | 33.02 GiB，24,576个专家 |
| GPU专家缓存 | 6,554槽，8.78 GiB |
| 专家文件后备层 | 没有启用 |
| PLE查找表 | 第二分片，约26.82 GiB，默认direct读取 |
| 进程树RSS采样峰值 | 35.18 GiB |
| 主机可用RAM最低值 | 13.26 GiB |
| GPU 0显存采样峰值 | 14,902 MiB |

GPU热缓存是同一批专家的副本，不能把RAM arena与GPU缓存简单相加来计算唯一专家权重大小。

两个分片的整文件SHA-256、长度和GGUF标识已检查，且哈希同时匹配ModelScope子目录清单和安装器`setup.py`中钉住的HF LFS值。记录见 `evidence/iq2-xs-verification.json`。

启动日志的直接证据：

```text
strata generate: expert arena: locked 1 MiB via working-set minimum + VirtualLock; cudaHostRegister of the whole arena FAILED (out of memory); 48 slices pinned (33 GiB); large pages refused ...; using 4 KB pages
strata generate: loaded 33.02 GiB at 2.93 GiB/s
```

整块CUDA注册失败后，引擎使用分片固定内存完成了加载；大页申请失败后使用普通4KiB页。运行没有回退到`FileExpertSource`专家文件模式，采样脚本也在发送请求前检查了这一点。

安装路径：`data\models\IQ2_XS`。引擎、MTP草稿层和专家profile均复用了上一轮的文件。

## 2. 与上一轮的直接结果对照

| 指标 | 上一轮 UD-Q5_K_XL：24GiB专家缓存＋SSD | 本轮 IQ2_XS：全RAM专家arena |
|---|---:|---:|
| 完整GGUF体积 | 147.42 GiB | 63.35 GiB |
| 专家RAM | 24.00 GiB | 33.02 GiB |
| GPU专家槽数 | 1,946 | 6,554 |
| 请求1生成速度 | 8.5 token/s | 145.1 token/s |
| 请求2生成速度 | 10.1 token/s | 142.6 token/s |
| 请求1首token | 6.47 s | 0.47 s |
| 请求2首token | 5.89 s | 0.29 s |
| 两段生成物理读量 | 94.95 GiB | 40.98 MiB |
| 生成阶段平均物理读速 | 1,764.16 MiB/s | 11.57 MiB/s |
| 两段生成物理写量 | 47.97 MiB | 3.28 MiB |
| 进程树RSS峰值 | 28.06 GiB | 35.18 GiB |

这两轮同时改变了量化格式、专家驻留方式和能装进VRAM的专家数量；provider及部分dense / PLE tensor格式也不同。因此表中的总体加速不能全部归因于“去掉SSD读取”，也没有证明两种量化的回答质量相同。

共同设置已由 `scripts/compare_runs.py` 对文件逐项检查：

- 同一物理GPU 0（RTX 5080）与引擎0.1.58 / CUDA13。
- 相同两条提示词、temperature=0、关闭thinking、每次最多256 tokens。
- 32K上下文、INT8 KV、15个expert workers、相同MTP文件。
- `--spec 4 --spec-min-p 0.5`。
- 单请求，prompt checkpoint和conversation parking关闭。

两次流均正常结束，usage各为256输出tokens；`finish_reason=length`来自实验上限，回答片段没有写完。原始SSE及文本位于对应run目录，没有做答案准确性评测。

## 3. 全RAM专家模式的分阶段物理读写

下表来自C盘对应的PhysicalDrive2累计计数，包含同盘其他程序。首token边界按客户端接收第一个有效SSE输出划分，含少量客户端和RPC开销。

| 阶段 | 时长 s | 物理读量 | 物理写量 | 平均读 MiB/s |
|---|---:|---:|---:|---:|
| 空闲基线 | 9.92 | <1 MiB | 约12.08 MiB | 0.02 |
| 加载模型 | 40.57 | 37.03 GiB | 约69.84 MiB | 934.82 |
| 就绪空闲 | 10.02 | 约12.8 MiB | 约9.0 MiB | 1.28 |
| 请求1：首token前 | 0.51 | 约3.7 MiB | <0.1 MiB | 7.30 |
| 请求1：生成 | 1.75 | 约20.6 MiB | 约1.4 MiB | 11.74 |
| 请求2：首token前 | 0.32 | 约3.1 MiB | 约1.1 MiB | 9.75 |
| 请求2：生成 | 1.79 | 约20.4 MiB | 约1.8 MiB | 11.41 |

加载阶段读入约37GiB，之后专家从arena取数；生成阶段保留了PLE查表等小量I/O。专家放入RAM不等于整套模型的所有部分都不再访问SSD。

两段生成的物理读请求还有一个变化：

| 运行 | 平均物理读IOPS | 平均每个物理读请求 |
|---|---:|---:|
| Q5＋SSD专家层 | 约1,579 | 约1,144 KiB |
| IQ2全RAM专家 | 约2,886 | 约4.1 KiB |

这与从大块专家读取转向小页PLE查表的现象一致。**读吞吐下降，并不意味着I/O次数也归零。** 这些是全盘计数，没有逐文件ETW或LBA追踪，不能把每个读取都精确归给PLE，也不据此宣称已测得随机地址分布。

本轮共有99份快照。阶段边界共享计数，阶段物理字节之和与首末累计值核对一致。生成窗口仅约3.54秒，包含6个有时长的采样区间；速度还使用了引擎自身的请求计时，不把这组短测当作长期稳定吞吐。

## 4. 补充：同IQ2量化，仅给8GiB应用专家缓存

为减少跨量化比较的混杂，另跑了同一IQ2_XS的8GiB应用缓存版本。GPU专家槽数仍是6,554，但运行日志自动选择了**OS文件缓存路径**：

```text
strata generate: the file tier reads through the file cache (... the file cache can keep them)
FileExpertSource: RAM budget 8.00 GiB: 5969 of the 24.24 GiB of experts the GPU cache does not hold ...
strata: prefill plan inputs: 33.0 GiB experts, 8.8 GiB in the GPU caches, 8.0 GiB RAM copy ... file tier 16.2 GiB; 19.7 GiB available for the page cache
```

| 指标 | IQ2全RAM专家 | IQ2：8GiB应用缓存＋OS文件缓存 |
|---|---:|---:|
| 请求1生成速度 | 145.1 token/s | 63.4 token/s |
| 请求2生成速度 | 142.6 token/s | 73.0 token/s |
| 两段生成物理读量 | 40.98 MiB | 3.53 GiB |
| 平均物理读速 | 11.57 MiB/s | 481.11 MiB/s |
| RSS采样峰值 | 35.18 GiB | 16.59 GiB |
| 最低可用RAM | 13.26 GiB | 30.60 GiB |

“文件缓存能容纳”不代表测试开始时全部数据已经热驻留。这次仍实测到了3.53GiB物理读取。

这项补充对照展示的是应用arena与“应用缓存＋OS文件缓存”路径的差别；没有强制禁用OS缓存，不能当作严格的RAM与SSD直读A/B。缓存温度、调度路径和自适应专家放置等也可能影响差值。它同时说明：`--resident-budget-gib 8`不是整个进程或OS文件缓存的8GiB硬上限。

## 5. 复现与文件

在工作目录运行，选择一个未存在的新输出目录：

```powershell
Set-Location 'C:\Users\Administrator\Documents\Code\tasks\strata-lab'
.\Strata\.venv\Scripts\python.exe .\scripts\experiment.py --config .\Strata\strata-iq2_xs.json --output .\runs\ram-iq2xs-repeat --ram-experts --max-tokens 256
.\Strata\.venv\Scripts\python.exe .\scripts\analyze_run.py --run .\runs\ram-iq2xs-repeat
```

复现补充版本时，将`--ram-experts`换为`--expert-budget 8`，并使用另一个新输出目录。

校验IQ2权重：

```powershell
.\Strata\.venv\Scripts\python.exe .\scripts\verify_download.py --iq2-xs
```

`scripts/compare_runs.py`汇总本文三份固定运行记录，生成根目录的 `ram-vs-disk-comparison.csv` 与 `ram-vs-disk-comparison.json`。它不会自动把新的repeat目录替换进基线。

主要证据：

- `runs/ram-iq2xs-5080-01/`：本轮全RAM专家模式。
- `runs/disk-iq2xs-5080-8g-01/`：补充的OS文件缓存模式。目录名不能代替实际模式判断，应以engine.log为准。
- `runs/outofcore-5080-budget24-01/`：前一轮Q5无缓冲文件层基线。
- 每份run中均有配置、engine.log、server.log、原始SSE、usage、samples.jsonl、disk-summary.csv和analysis.json。
- `evidence/iq2-xs-verification.json`及`modelscope-ISTA-IQ2_XS.json`：本轮权重校验值。

实验后已检查本次引擎全部退出，GPU 0回到约287MiB显存。原Q5模型与原证据包保留，没有删除或覆盖旧的原始测量数据；分析JSON是可重新生成的派生结果。

限制：各配置只做两条短请求，没有长上下文、长时间稳定性或答案质量测试；各轮之间未清空系统页缓存，不比较严格冷启动。全RAM模式日志曾提示Windows commit余量较小，整块注册后使用了分片固定内存；没有手动修改系统页面文件或锁页权限。交付包包含报告、脚本与证据，不含两套庞大权重。
