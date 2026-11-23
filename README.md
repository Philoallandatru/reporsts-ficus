# reporsts-ficus

按语义分层组织的知识库与实验评测仓库。

```text
reporsts/
├── index.md                 # OKF v0.2 总入口
├── GOVERNANCE.md            # 治理与增量更新规范
├── log.md                   # 变更日志
├── tools/                   # kb_govern.py 体检、同步与检索 CLI
├── kb/                      # 【持久知识层】按技术领域划分
│   ├── nvme/                # NVMe Base 2.1
│   ├── pcie/                # PCIe 协议栈
│   ├── pci-firmware/        # PCI Firmware 3.3
│   ├── ssd-design/          # SSD 控制器与 NAND
│   ├── llm-inference/       # LLM 推理与 KV Cache
│   └── reference-wikipedia/ # Wikipedia OKF 参考包
└── benchmarks/              # 【实测报告层】与概念知识解耦
    ├── index.md
    ├── reports/             # 评测报告与 SVG 图表
    ├── runs/                # 原始运行产物
    └── assets/              # 报告配图资源
```
