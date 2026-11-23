# Micron NOR and NAND Flash Guide 抽取记录

本页把 [Micron NOR and NAND Flash Guide](../artifacts/vendors/micron/nor-nand-flash-guide.pdf) 固定成可复用的 vendor intake。它不是具体 part number datasheet，而是一个 family-level 官方指南，适合用于术语、边界和责任划分，不适合直接填具体几何参数和时序参数。

## 来源固定

| 字段 | 值 |
|---|---|
| Source ID | `SRC-NAND-MICRON` |
| Artifact ID | `ART-MICRON-NAND-FLASH-GUIDE` |
| 官方 URL | `https://assets.micron.com/adobe/assets/urn%3Aaaid%3Aaem%3Ae98bc653-e42d-45a7-9b8c-03cb3d488f05/renditions/original/as/nor-nand-flash-guide.pdf` |
| 本地文件 | `sources/artifacts/vendors/micron/nor-nand-flash-guide.pdf` |
| sha256 | `791d5f24f9d5fa4fcf780dd82cd330d0cd388cccaae3dbf0b17101e5bc3c788f` |
| 页数 | `7` |
| 下载日期 | `2026-08-12` |
| 可信度层级 | `official_family` |

## 可直接抽取的结论

### 1. 原始 NAND 与 managed NAND 的边界

- raw NAND 需要主控或系统侧负责 ECC、坏块管理、wear leveling、地址映射和掉电恢复策略。
- managed NAND 或 SSD 会把这些复杂度封装到控制器和固件内部，对主机暴露块设备或标准协议接口。

这类结论适合流向：

- [NAND 介质参数手册](../../wiki/concepts/nand-media-parameter-guide.md)
- [控制器硬件与 NAND 接口](../../wiki/concepts/hardware-controller-and-nand.md)
- [ECC、LDPC 与可靠性管理](../../wiki/concepts/ecc-ldpc-reliability.md)

### 2. NOR 与 NAND 的工程取舍

- NOR 更适合代码存储和随机读取场景。
- NAND 更适合高密度、大容量数据存储场景。
- 这类对比可用于解释为什么 SSD 主存储介质通常是 NAND，而不是 NOR。

### 3. 责任划分语言

- ECC、bad block management、wear leveling 这几个词可以作为知识库中的标准工程语言。
- 这些词可以作为后续具体 datasheet intake 的字段分组入口，但不能替代具体参数值。

## 不应直接抽取的字段

这份 guide 不能直接用于以下字段：

- `page_size`
- `spare_or_oob_size`
- `pages_per_block`
- `blocks_per_plane`
- `planes_per_die`
- `dies_per_package`
- `interface_standard`
- `bus_width`
- `timing_mode`
- `tR_us`
- `tPROG_us`
- `tBERS_us`
- `read_retry_support`
- `bad_block_marker`
- `status_register_fail_bits`

这些字段必须回到具体 part number datasheet、parameter page 或受限 vendor 资料。

## 推荐下游映射

| 抽取结果 | 可信度 | 适合写入的位置 |
|---|---|---|
| raw NAND vs managed NAND 边界 | `official_family` | `wiki/concepts/nand-media-parameter-guide.md` |
| NOR vs NAND 应用取舍 | `official_family` | `wiki/concepts/hardware-controller-and-nand.md` |
| ECC / bad block / wear leveling 责任边界 | `official_family` | `wiki/concepts/ecc-ldpc-reliability.md` |
| 具体 geometry / timing / retry 参数 | `not_available_in_this_guide` | 等待具体 Micron datasheet intake |

## 下一步

1. 为一个具体 Micron NAND part 建独立 intake。
2. 固定 document revision、part number 和 parameter page。
3. 补 `page/block/plane/die` geometry。
4. 补 `tR/tPROG/tBERS`、interface mode 和 read-retry 抽象 hook。
5. 将可公开的 family-level 术语保留在本页，把 part-specific 参数放到后续 datasheet intake。
