# SSD 设计论文与 BibTeX 种子

本页收录 SSD 固件、FTL、NAND 可靠性、仿真、开放通道和硬件原型相关论文。优先使用会议官方页面、ACM/IEEE/USENIX 页面、作者 PDF 或项目官方文档。

机器可读采集队列见 [paper-intake-matrix.yml](sources/paper-intake-matrix.yml)。如果你要新增或复核论文条目，先把条目放进采集矩阵，再补本地 PDF、sha256 和阅读状态。

## 使用规则

1. 设计结论必须引用“论文页面 + PDF/DOI + 本地阅读日期”。
2. 仿真实验引用必须同时固定论文、源码仓库 commit 和配置文件。
3. 研究论文中的参数不能直接当作产品参数；需要回看实验 NAND 代际、workload、simulator 和校准方式。

## 采集规则补充

- `seed_only` 表示只建立了研究入口，还没有本地 PDF 或 sha256 固定。
- `pending` 表示条目已经进入采集队列，但本地文件和版本信息还未补齐。
- `formal_version_fixed` 才表示本地阅读材料和版本信息已经稳定下来。
- 研究论文可以作为设计直觉来源，但不能直接替代 NAND 参数、NVMe 行为或产品化验证。

## FTL 与映射算法

| Key | 主题 | 来源 | 知识库用途 | 局限 |
|---|---|---|---|---|
| `lee-fast-2006-fast-ftl` | FAST log-block FTL | https://link.springer.com/chapter/10.1007/11807964_88 | hybrid mapping、log block、sector-level merge | 早期 NAND 与 workload，需和现代 TLC/QLC 重评估 |
| `gupta-asplos-2009-dftl` | DFTL page mapping cache | https://dl.acm.org/doi/10.1145/1508244.1508271 | DRAM 受限映射缓存、translation page miss、cached mapping table | FlashSim 时代模型，缺现代 NVMe 多队列和 3D NAND 细节 |
| `bjorling-fast-2017-lightnvm` | Open-channel SSD / host-managed FTL | https://www.usenix.org/conference/fast17/technical-sessions/presentation/bjorling | 解释 host 与 device 分担 FTL 的边界 | LightNVM 生态后来被 ZNS/FDP 等路径部分取代 |

## ECC、LDPC 与 NAND 可靠性

| Key | 主题 | 来源 | 知识库用途 | 局限 |
|---|---|---|---|---|
| `zhao-fast-2013-ldpc-ssd` | LDPC soft decoding in SSD | https://www.usenix.org/conference/fast13/technical-sessions/presentation/zhao | hard/soft decode、read retry、延迟/能耗/可靠性权衡 | 论文模型需映射到具体 NAND vendor retry/read-level 能力 |
| `li-fast-2016-read-write-cost` | Program/read cost regulation | https://www.usenix.org/system/files/conference/fast16/fast16-papers-li-qiao.pdf | ISPP、LDPC、read/write cost tradeoff | 研究机制不等于可公开产品实现 |
| `kim-fast-2019-reliability-tradeoffs` | SSD reliability design tradeoffs | https://www.usenix.org/system/files/fast19-kim-bryan.pdf | ECC、scrubbing、intra-SSD redundancy、寿命权衡 | 需要结合目标 UBER、DWPD、NAND 代际重算 |

## 仿真、仿真器与开放实现

| Key | 主题 | 来源 | 知识库用途 | 局限 |
|---|---|---|---|---|
| `li-fast-2018-femu` | FEMU NVMe SSD emulator | https://www.usenix.org/conference/fast18/presentation/li | QEMU-based NVMe emulator、BlackBox/WhiteBox/OpenChannel/ZNS 实验 | 仿真准确性依赖参数、host 环境和 mode |
| `tavakkol-fast-2018-mqsim` | MQSim multi-queue SSD simulator | https://www.usenix.org/conference/fast18/presentation/tavakkol | NVMe 多队列、稳态、端到端延迟建模 | 参数需要校准，不能用默认配置代表目标 SSD |
| `jung-cal-2017-simplessd` | SimpleSSD full-system simulator | https://arxiv.org/abs/1705.06419 | controller/FTL/NAND full-stack 教学和设计空间探索 | arXiv/IEEE 版本需要固定；结果依赖 full-system 配置 |
| `jung-atc-2020-openexpress` | OpenExpress hardware NVMe framework | https://www.usenix.org/conference/atc20/presentation/jung | 硬件化 NVMe queue、doorbell、PRP、CQ 管线参考 | 偏 NVMe 前端硬件，不覆盖完整 NAND/FTL 产品实现 |

## 性能、QoS、SLC Cache 与 Tail Latency

| Key | 主题 | 来源 | 知识库用途 | 局限 |
|---|---|---|---|---|
| `yan-fast-2017-gc-tail-latency` | GC tail latency | https://www.usenix.org/system/files/conference/fast17/fast17-yan.pdf | GC 对尾延迟的影响、QoS-aware background task | 需要确认模拟器和目标 workload |
| `huang-fast-2017-flashblox` | Isolation and wear uniformity | https://www.usenix.org/system/files/conference/fast17/fast17_huang.pdf | 多租户隔离、channel/die wear leveling | 基于 open-channel stack，产品 SSD 需要重新映射 |
| `zhang-fast-2016-slc-stress` | SLC-mode cache write stress | https://www.usenix.org/system/files/conference/fast16/fast16-papers-zhang-xuebin.pdf | SLC cache、write stress、cache rotation | 早期 SLC-mode 模型，需结合现代 TLC/QLC |
| `yang-arxiv-2024-ips-slc-cache` | In-place Switch SLC cache | https://arxiv.org/abs/2409.14360 | SLC cache performance cliff、destage/write amplification | 预印本，需确认是否已有正式发表版本 |

## BibTeX 种子

```bibtex
@inproceedings{lee-fast-2006-fast-ftl,
  title = {A Log Buffer-based Flash Translation Layer Using Fully-associative Sector Translation},
  author = {Lee, Sang-Won and Park, Dong-Joo and Chung, Tae-Sun and Lee, Dong-Ho and Park, Sangwon and Song, Ha-Joo},
  booktitle = {Advances in Databases: Concepts, Systems and Applications},
  year = {2006},
  doi = {10.1007/11807964_88},
  url = {https://link.springer.com/chapter/10.1007/11807964_88}
}

@inproceedings{gupta-asplos-2009-dftl,
  title = {DFTL: A Flash Translation Layer Employing Demand-based Selective Caching of Page-level Address Mappings},
  author = {Gupta, Aayush and Kim, Youngjae and Urgaonkar, Bhuvan},
  booktitle = {Proceedings of the 14th International Conference on Architectural Support for Programming Languages and Operating Systems},
  year = {2009},
  doi = {10.1145/1508244.1508271},
  url = {https://dl.acm.org/doi/10.1145/1508244.1508271}
}

@inproceedings{zhao-fast-2013-ldpc-ssd,
  title = {LDPC-in-SSD: Making Advanced Error Correction Codes Work Effectively in Solid State Drives},
  author = {Zhao, Kai and Zhao, Wenzhe and Sun, Hongbin and Zhang, Tong and Zhang, Xiaodong and Zheng, Nanning},
  booktitle = {11th USENIX Conference on File and Storage Technologies},
  year = {2013},
  url = {https://www.usenix.org/conference/fast13/technical-sessions/presentation/zhao}
}

@inproceedings{bjorling-fast-2017-lightnvm,
  title = {LightNVM: The Linux Open-Channel SSD Subsystem},
  author = {Bjorling, Matias and Gonzalez, Javier and Bonnet, Philippe},
  booktitle = {15th USENIX Conference on File and Storage Technologies},
  year = {2017},
  url = {https://www.usenix.org/conference/fast17/technical-sessions/presentation/bjorling}
}

@inproceedings{li-fast-2018-femu,
  title = {The CASE of FEMU: Cheap, Accurate, Scalable and Extensible Flash Emulator},
  author = {Li, Huaicheng and Hao, Mingzhe and Tong, Michael Hao and Sundararaman, Swaminathan and Bjørling, Matias and Gunawi, Haryadi S.},
  booktitle = {16th USENIX Conference on File and Storage Technologies},
  year = {2018},
  url = {https://www.usenix.org/conference/fast18/presentation/li}
}

@inproceedings{tavakkol-fast-2018-mqsim,
  title = {MQSim: A Framework for Enabling Realistic Studies of Modern Multi-Queue SSD Devices},
  author = {Tavakkol, Arash and Gomez-Luna, Juan and Sadrosadati, Mohammad and Ghose, Saugata and Mutlu, Onur},
  booktitle = {16th USENIX Conference on File and Storage Technologies},
  year = {2018},
  url = {https://www.usenix.org/conference/fast18/presentation/tavakkol}
}

@article{jung-cal-2017-simplessd,
  title = {SimpleSSD: Modeling Solid State Drives for Holistic System Simulation},
  author = {Jung, Myoungsoo and Zhang, Jie and Abulila, Ahmed and Kwon, Miryeong and Shahidi, Narges and Shalf, John and Kim, Nam Sung and Kandemir, Mahmut},
  journal = {IEEE Computer Architecture Letters},
  year = {2017},
  url = {https://arxiv.org/abs/1705.06419}
}

@inproceedings{jung-atc-2020-openexpress,
  title = {OpenExpress: Fully Hardware Automated Open Research Framework for Future Fast NVMe Devices},
  author = {Jung, Myoungsoo},
  booktitle = {2020 USENIX Annual Technical Conference},
  year = {2020},
  url = {https://www.usenix.org/conference/atc20/presentation/jung}
}
```
