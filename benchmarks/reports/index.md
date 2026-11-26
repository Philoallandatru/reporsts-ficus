# 实验与评测报告索引

- [本地大模型推理栈终极技术报告：llama.cpp vs Strata、KVMem 实证与源码优化路线](llama-strata-kvmem-master-report.md) — 综合 22 组受控实测、Nsight Systems 显微剖面、ETW/SMART 设备计数与源码锚点，并经 `codex-cli` 交叉审核订正（附 [5-Tab 交互式仪表盘](../assets/llama-strata-kvmem/llama-strata-kvmem-dashboard.html)）。
- [NInfer + KVMem v0.19.1 (RTX 5080) 实测、PI Agent 闭环与边界总结](ninfer-kvmem-rtx5080-experiments.md) — 7 组 RTX 5080 控制变量实验（准入/5-Needle/SSD 溢出/gen_reserve/MTP4/8K 负税）、PI Agent 闭环与 7 组 Nsight 显微收敛总结。
- [NVMe 门铃槽位恢复与通知分支回归](ssd-doorbell-regression.md) — 三道合成回归题、可导入报告和 Pi/MCP 复跑命令。
- [Qwen3.8 超出 RAM + 显存后的 Strata 单卡实测](experiment-report.md) — 实测日期：2026-11-09。工作目录：`C:\Users\Administrator\Documents\Code\tasks\strata-lab`。
- [公平对比：llama.cpp 的 MoE 缓存到底能补多少（2026-11-11）](fair-compare-report.md) — 同一份 IQ2_XS、同一台 RTX 5080（GPU0）、同一组 4 条请求、16 计算线程与同一 CPU 亲和掩码、
- [KVMem 实测：提升在哪里（本机，2026-11-11）](kvmem-report.md) — 安装对象：[kvmem/kvmem](https://github.com/kvmem/kvmem) v0.19.1，Windows x64 / RTX 50 统一包。
- [Strata 与 llama.cpp 图片索引](llama-vs-strata-image-gallery.md) — 同步日期：2026-11-14。共 42 张图：图解文档 35 张、源码分析 4 张、既有 Q5 内存曲线 3 张。
- [同一 IQ2_XS：llama.cpp 与 Strata 实机对照](llama-vs-strata-report.md) — 日期：2026-11-09。工作目录：`C:\Users\Administrator\Documents\Code\tasks\strata-lab`。
- [Strata 与 llama.cpp 综合源码区别分析](llama-vs-strata-source-analysis.md) — 分析日期：2026-11-12。本文面向需要阅读、修改推理引擎和评估分层缓存的开发者。范围包括模型加载、执行图、MoE 权重、prefill、KV/会话状态、投机解码、服务调度、后端和本工作区的实验补丁。
- [Strata 与 llama.cpp 源码区别图解（新手向）](llama-vs-strata-visual-guide.md) — 日期：2026-11-13。定位：从问答看懂计算、权重与状态。
- [Q5 专家读队列：深度 1、2、4、8 的隔离实验](q5-io-depth-report.md) — 2026-11-11。续 [Q5 三方对照](../runs/q5-strata-compare-20261111/REPORT.zh-CN.md)。这次只筛选 P6 读取端的在途槽容量。Q5 仍使用原来的 GPU MoE、完整路由、缓存策略和 Windows 文件读取路径。
- [Strata 相对 llama.cpp 提升了什么：Q5 同工作量对照与改造路线](q5-strata-compare-report.md) — 日期：2026-11-11。范围：本机 Windows、单张 RTX 5080、Qwen3.8-Flash-Next UD-Q5_K_XL（147.42 GiB），以及冻结的 llama.cpp b12211、P6 和 Strata 0.1.58。这里比较的是本机已验证的三条推理路径，不代表其他模型、操作系统或版本。
- [Qwen3.8 小量化全RAM专家模式实测](ram-vs-disk-report.md) — 日期：2026-11-09。工作目录：`C:\Users\Administrator\Documents\Code\tasks\strata-lab`。
