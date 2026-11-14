# P5 预先固定的验收方法

2026-11-10。分支 feature/file-expert-store-p0-p2；原生为未修改 b12211，同一 MSVC/CUDA 配置。正式结果产生前固定以下标准。

- Q5 147.416 GiB，完整 top-10，单 5080；mmap、关闭 repack/MTP、CPU miss share=0、单序列、32K context、Q8 KV、Flash Attention、16 CPU threads。各组同一模型文件，保留文件身份与二进制哈希。
- 新进程，OS 缓存不清理。禁用特殊全专家预热；缓存自然随正式请求填充。逐 token 时间包括 llama_synchronize，完整 logits 写盘及检查点在 decode 计时之外；另报包含诊断、采样和写盘的请求墙钟时间。
- 调参：独立编译器/网络/生态提示；RAM 8/16/32 GiB、GPU 2/4/8 GiB，staging 8/32 MiB、depth 1/2。预算预检失败的组合保留记录，不启动。原生扫描 GPU 2/4/8 GiB，除 ubatch 512 外分别补测 ubatch 1/2/4，以免大图工作区挤压 GPU cache；保留最优候选。正式提示不参与选择。
- 正式性能：同一提示和 teacher-forcing token 序列，native/off/file 至少三轮，轮换顺序。原生和 file 各自使用调参得到的最优 GPU 预算，另做同预算对比；native/off 必须同配置。报告全部轮次、median 和 p50/p95/p99。功能关闭吞吐 median 退化上限 3%，存在噪声时增加轮次。
- 同预算组额外加入相同 RAM/staging 预算、depth=1 的同步控制，native/file/sync 三轮轮换；另做一次 RAM=0、depth=1 的源读取正确性控制。这样可分别观察同步与双缓冲、无 RAM 缓存与有缓存的行为。
- CUDA 原生可配置的 GGML_OP_OFFLOAD_MIN_BATCH=1 对所有正式组相同，避免小 batch 在缓存容量阈值外落入 CPU；另保留默认阈值 32 的边界回归。
- 同 GPU 算法和同 microbatch 的 logits 要求 bitwise 相同；不同 GPU cache 布局/CPU 与 GPU 路径采用 test_mul_mat_id 的 NMSE <= 5e-4，报告 max abs、RMSE、argmax 一致率，不事后放宽。固定评测文本条件 perplexity 相对差 <= 0.5%。该 PPL 是本文固定小语料回归，不是通用质量榜单。
- 长时：固定 GPU 4 GiB、RAM 8 GiB、staging 32 MiB、depth 2、PLE 64 MiB，保留 512 大 batch；同一 model/context 下先完成 8K prompt +512 输出，再完成共 8 个主题请求各 512 输出（合计 4096），清 KV 保留权重缓存；之后继续真实推理至少 1800 秒，跨请求继续淘汰。保留完整 logits，事后在原生上 teacher forcing 重放。测试忽略 EOS 以固定工作量，EOS 次数单独报告，不把后 EOS token 称为有效回答长度。
- RAM/commit：启动前额外 commit 预算为 RAM cache +14 GiB 加系统预留 8 GiB；可用 RAM 为 RAM cache +8 GiB 固定成本加预留 8 GiB。运行中 available RAM 或 commit headroom <4 GiB、D 盘可用 <12 GiB 时只停止本测试。GPU 预检留固定成本和图工作区，运行时由现有图预算检查再次约束。
- 每 0.5 秒记 working set/private/系统 RAM/commit/cache/进程 IO/整盘 IO，每约 2 秒记整卡 VRAM/利用率/温度/功耗。记录系统换页计数；区分软缺页、文件 hard fault 与匿名页换入。整盘 PhysicalDrive2 为 C 模型盘，PhysicalDrive3 为 D 输出盘，同时保留前后空闲噪声，不冒充进程独占物理 IO。
- 检查点输出 expert/PLE 实际完成逻辑与对齐字节、RAM hit/eviction/lease、读/H2D等待、GPU hit/miss、缓存路径累计去重工作集、GPU 驻留及 RAM/GPU 重复角色字节。原始日志中的 `routed decode experts` 实际统计所有经过 GPU cache lookup 的路由，包括可用缓存的小 batch prefill；一般路径的大 batch prefill 不在该计数内。
- 保留失败和修复记录。容量、正确性、默认路径性能及观测证据分别判定；没有通过硬门槛的项目不宣称完成目标。Strata 仅引用既有固定版本背景，不作为数值 oracle 或同内核性能基线。

内存口径：`GetPerformanceInfo.SystemCache` 是 standby list 与 system working set 之和；`PhysicalAvailable` 也包含 standby list，二者存在重叠，不能相加当成总占用。它们是全系统指标，并非本进程独占的文件缓存。依据：[Microsoft PERFORMANCE_INFORMATION](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-performance_information)。`QueryWorkingSetEx` 的 locked 统计仅覆盖当前枚举到的有效工作集页，不能据此宣称 CUDA 驱动未锁页；另列 backend 已分配的 CUDA_Host 字节。依据：[Microsoft PSAPI_WORKING_SET_EX_BLOCK](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-psapi_working_set_ex_block)。

ETW 统计使用 `xperf -a diskio -detail` 的逐事件十六进制 IO Size，以 Python 任意精度整数汇总并按发起 PID/文件归属；本机 `-summary` 的大文件累计字节在 4 GiB 处回绕，不能直接使用其字节汇总。主机 DiskIO 完成事件代表块设备接口读取，并不测量 SSD 内部 NAND 流量。报告追踪窗口的丢事件数、其他进程 I/O 和目标进程 pagefile hard-fault 字节，避免把全系统换页归因给模型。

## 正式长测前的观测与调整

未修改 b12211 在加载期多次触发 4 GiB commit 余量保护。核对源码后确认 `init_mappings(true)` 会预取非 lazy 的专家分片；PLE 本身标为 lazy。最后一条 PLE 日志不能证明压力来自 PLE。保留原始失败及成功的所有样本，早期同步 GPU 采样导致的间隔也单独标记；后续改为异步 GPU 采样，RAM/commit 监控不中断。

为检验热缓存能否解决加载压力，额外尝试了有限缓冲顺序读 PLE、只读 mmap 逐页触碰 PLE；二者均未解决问题。这些探索不进入正式性能统计，正式测试不预热 PLE。

另从同一原始提交建立 `native-noprefetch-bin`，仅在 `llama-model.cpp` 增加 `LLAMA_MMAP_PREFETCH=on|off` 的加载预取控制；所有 ggml DLL 保持原始二进制，推理、缓存、算子源码不变。当前开发分支提供同一环境控制，默认仍为 on。Q5 正式 native/off/file 三组都设置 off；文件模式本已禁止整段预取。报告称它为“原生推理参考（仅禁用加载预取）”，不得混称未经修改的原生二进制。Q5 原始加载失败仍属于独立验收结果。

先将参考构建的 GPU 路径与已成功运行的原始二进制作逐位 logits 校验，再用于完整长测重放。参考构建重新扫描六个 GPU cache/microbatch 组合。IQ2 默认路径回归仍尝试未经修改的原生二进制与默认 on 配置。

边界测试发现：原生默认阈值 32 在 batch 3/16 走 CPU fallback，与 GPU 路径相比超出上述 NMSE/PPL 门槛，判为失败，不放宽标准；batch 32 则逐位一致。文件路径必须把专家算子留在 GPU，其 batch 3/16/32 与未经修改原生的强制 GPU 路径逐位一致；禁用预取的原生参考也与同一原始 GPU 结果逐位一致。后续正式矩阵固定阈值 1，只能据此证明相同 GPU 执行路径的等价性，不能外推为默认 CPU fallback 也通过。

长测进入第二主题后，生成文本中的 UTF-8 字符暴露了 Python Windows 默认 GBK 读取问题：附加工作集/ETW 观测器退出，原始错误保存在 `observation-first.json`；模型推理和主进程 0.5 秒资源监控未中断。研究脚本改为显式 UTF-8，并重启附加观测器。为避免中断已开始的容量试验，另保留 Windows 进程句柄记录真实退出码；若旧驱动在完成后读取结果失败，则从原始命令、采样和 UTF-8 结果恢复 summary，明确标注恢复方式。推理计时、logits 和结果文件不修改；正式后续组使用修正后的驱动。

## 原生长测资源保护触发后的参考条件

`q5-long-native`（禁用预取、工作集不限）在首个 512-token 预填充批次内触发 available RAM <4 GiB 保护：约 87.27 秒，working set 峰值 56.31 GiB，最低 available RAM 3.93 GiB，退出码 1。这次失败保留，不能称原生长测已完成。

重试 `q5-long-native-ws48` 只对本测试子进程使用 `SetProcessWorkingSetSizeEx`，硬上限 48 GiB、软下限保持原值，回读确认 flags 与上限。后续 Q5 原生调参及正式 native/off/file/sync 全部采用同一 48 GiB 上限，保留原来的 RAM/commit 保护线，不清理其他进程或全局缓存。该上限由失败时的工作集/可用 RAM 测量确定，留出约 8 GiB 以上物理余量；它改变原生 mmap 的驻留/缺页策略，因此性能结论必须标为“禁用加载预取、工作集硬上限 48 GiB 的原生推理参考”，不代表无限制原生默认路径。文件长测已完成，其 working set 峰值约 13.46 GiB，低于此参考上限。

原生组加载前要求 available RAM >=48+8 GiB。正式 Q5 性能与同预算同步对照扩为六轮，使用三种模式的全部六种顺序，平衡模式间残留 OS 缓存的前序关系；新增方法在正式性能结果产生前固定。IQ2 保留三轮、默认加载预取 on，并使用相同进程上限。依据：[Microsoft SetProcessWorkingSetSizeEx](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-setprocessworkingsetsizeex)。

默认关闭的 3% 吞吐门槛分别报告 prefill 和 decode 两项，任一未达标都不称为全部通过；另报告请求墙钟比值。若 IO 噪声使结果不稳定，保留原始结果并增加控制测量，不事后只挑通过的指标。

## 静态审查补充的 context 边界回归

长测 8192+512 尚未填满 32K context。正式计时结束后另用独立 `context_boundary_probe.exe`：ctx=512，读取实际 `llama_n_ctx_seq`；511 个提示 token 写入位置 0…510，输出 logits 后 decode 一个 token 到位置 511，再保存 logits；位置 512 的额外 decode 应返回 1（KV 无槽）。清空 KV 后在同一 context 重复，验证可恢复、两次 logits 相同，native/file 逐位一致。该变体由固定性能 probe 源码生成，只增加精确边界和拒绝检查；原性能 executable 与推理 DLL 不改动。它不参与速度统计。

## IQ2 三轮回归触发后的追加测量

初始三轮 IQ2 的 off/native decode、prefill 中位数比值为 0.94935/0.95532，未通过 0.97 门槛，保存为 `performance-initial-iq2-three-rounds.json`。按原协议的噪声处理条款，追加剩余三种反向顺序（native/file/off、file/off/native、off/native/file），合并全部六轮，不删除前三轮，不改变硬件、输入或阈值。追加测量同时检查默认路径的实际额外工作，不能用 Q5 通过替代 IQ2 的独立判定。

六轮结果仍为 0.96059/0.96373，保存为 `performance-iq2-six-rounds.json`，两项均未通过。另预先固定六组 native/off 配对（AB/BA 交替），只关闭运行期间的 `nvidia-smi` 查询；启动前 GPU 检查、0.5 秒 RAM/commit 监测和资源保护仍保留。新组名为 `quiet-*`，二进制、输入、GPU/WS 预算和加载模式不变。它用于排除每约 2 秒 GPU 查询对约 7 秒 decode 窗口的干扰，和原始带 GPU 监测组分别报告，不覆盖旧失败。生产源码未因此修改。
