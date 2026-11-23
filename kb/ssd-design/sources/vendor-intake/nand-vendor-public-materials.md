# NAND Vendor 公开资料 Intake

调研日期：2026-08-12。

本 intake 用于后续抽取 NAND geometry、timing、read-retry、ECC、坏块、retention、read disturb、temperature 和 packaging 信息。公开页面通常不会给出完整 datasheet；如果要做可运行控制器参数，仍需要具体 part number 的 datasheet 或厂商授权资料。

机器可读采集矩阵见 [NAND Parameter Extraction Matrix](nand-parameter-extraction-matrix.yml)。后续每次固定一个 PDF 或 datasheet，都应按该矩阵补字段、可信度和访问条件。更完整的抽取流程见 [NAND 数据采集与建模](../../wiki/concepts/nand-data-acquisition-and-modeling.md)。

## Micron

- 入口：https://www.micron.com/support/technical-notes
- 已固定公开 PDF：Micron NOR and NAND Flash Guide，官方资产 URL：https://assets.micron.com/adobe/assets/urn%3Aaaid%3Aaem%3Ae98bc653-e42d-45a7-9b8c-03cb3d488f05/renditions/original/as/nor-nand-flash-guide.pdf
- 本地 artifact：`sources/artifacts/vendors/micron/nor-nand-flash-guide.pdf`；sha256 `791d5f24f9d5fa4fcf780dd82cd330d0cd388cccaae3dbf0b17101e5bc3c788f`；页数 7。
- 可用资料：technical note、NAND flash 基础说明、managed NAND/SSD reliability 相关资料。
- 适合抽取：NAND 基础术语、program/read/erase 行为、ECC/reliability 背景、power-loss 或 endurance 相关工程语言。
- 已固定 guide 可抽取：raw NAND 与 managed NAND 边界、NOR/NAND 取舍、ECC/bad block/wear leveling 责任归属、应用场景分类。
- 局限：很多具体 NAND datasheet、read-retry table、timing mode、vendor command 需要具体产品资料；公开 technical note 可能跨代较大。
- 后续动作：为 Micron 目标 part number 建独立 intake，补 geometry、ONFI/timing、read-retry、ECC requirement 和 bad block marker 字段。

### Micron 下一批优先资料

- 具体 NAND part datasheet 或 product brief，优先选择带 parameter page、timing mode 和 read-retry 说明的版本。
- Managed NAND / SSD reliability note，用来补 retention、disturb、endurance 和 telemetry 术语。
- 若能找到官方 application note，再补坏块、factory bad block marker、feature register 和 reset 行为。

### Micron 抽取优先级

1. 先固定文档身份：part number、revision、URL、sha256、访问条件。
2. 再抽 geometry：page、OOB、block、plane、die、package。
3. 再抽 timing：tR、tPROG、tBERS、interface mode、bus width。
4. 最后抽 reliability：endurance、retention、read disturb、bad block、read retry。

## Kioxia

- 入口：https://www.kioxia.com/en-jp/business/memory/technical-resources.html
- 可用资料：BiCS FLASH、3D flash、memory technology white paper 和产品技术资源。
- 适合抽取：BiCS/3D NAND 架构背景、cell 类型、可靠性和产品族术语。
- 局限：公开 white paper 通常不包含完整 ONFI/Toggle timing、read retry 和坏块管理细节。
- 后续动作：记录目标 BiCS 代际，补公开 datasheet/app note 或联系渠道资料。

### Kioxia 下一批优先资料

- BiCS FLASH 代际白皮书。
- 对应代际的产品 brief 或参数页。
- 如果公开资料不足，至少把目标 generation 和 cell type 写清楚，避免把不同代际混用。

## Samsung Semiconductor

- 入口：https://semiconductor.samsung.com/
- 可用资料：V-NAND、SSD、memory technology、产品 brief 和 white paper。
- 适合抽取：V-NAND 代际、TLC/QLC 产品定位、企业/客户端 SSD 功能语言、controller/firmware feature 术语。
- 局限：公开页多为产品/技术介绍，缺少可直接用于 NAND controller 的命令时序表。
- 后续动作：把 Samsung 资料分成 NAND technology、SSD product brief、enterprise feature 三类，不混用。

### Samsung 下一批优先资料

- V-NAND 技术白皮书。
- SSD 产品 brief，专门摘 host-visible feature 和 endurance 术语。
- 若找到公开参数页，再补 NAND timing 和 interface 约束。

## SK hynix

- 入口：https://www.skhynix.com/
- 可用资料：NAND、SSD、product brief、技术新闻和 sustainability/quality 资料。
- 适合抽取：产品族、3D NAND 技术方向、企业 SSD 功能和可靠性术语。
- 局限：公开技术深度通常低于具体 datasheet；新闻稿不能作为参数来源。
- 后续动作：只把新闻/产品页作为入口；参数必须来自 datasheet、presentation 或标准接口资料。

### SK hynix 下一批优先资料

- NAND technology brief。
- enterprise SSD product brief。
- 公开技术文档中与 temperature、retention、power-loss 相关的段落。

## YMTC

- 入口：https://www.ymtc.com/
- 可用资料：Xtacking、3D NAND 技术介绍、产品族说明。
- 适合抽取：Xtacking 架构背景、die 与 CMOS 逻辑分离的技术术语、产品定位。
- 局限：公开资料通常不足以抽取 NAND timing、read-retry、电压表或坏块规则。
- 后续动作：将 YMTC 作为 NAND vendor landscape 条目，等待具体公开 datasheet 或渠道资料。

### YMTC 下一批优先资料

- Xtacking 技术说明。
- 产品族说明或公开 brief。
- 任何可公开的 parameter page 或可靠性说明。

## Western Digital / SanDisk

- 入口：https://documents.westerndigital.com/
- ECC/DSP white paper：https://documents.westerndigital.com/content/dam/doc-library/en_us/assets/public/western-digital/collateral/white-paper/white-paper-the-application-of-ecc-dsp-to-flash-memory.pdf
- 可用资料：flash memory ECC/DSP、SSD white paper、data center SSD 资料。
- 适合抽取：ECC/DSP、NAND channel、LDPC/retry、enterprise SSD reliability 和 telemetry 背景。
- 局限：厂商白皮书会省略 decoder 细节、read retry 表和产品固件策略。
- 后续动作：优先把 ECC/DSP 白皮书纳入 [ECC、LDPC 与可靠性管理](../../wiki/concepts/ecc-ldpc-reliability.md) 的来源。

### Western Digital 下一批优先资料

- ECC/DSP 白皮书。
- enterprise SSD reliability 或 field debug 资料。
- 如果能找到产品 brief，再补 telemetry、power-loss 和 read-retry 的语言。

## 参数抽取模板

| 字段 | 示例 | 是否必须 |
|---|---|---|
| Vendor / part family | Micron 3D TLC NAND | yes |
| Source URL / file | PDF URL, filename, sha256 | yes |
| Geometry | page size, OOB/spare, pages/block, blocks/die, planes/die, dies/package | yes |
| Interface | ONFI/Toggle version, bus width, timing mode | yes |
| Latency | tR, tPROG, tBERS, cache read/program support | yes |
| Reliability | P/E cycle target, retention, read disturb, bad block policy | yes |
| ECC requirement | bits/KB, LDPC/BCH expectation, read retry hooks | yes |
| Vendor commands | read retry, OTP, unique ID, feature register | optional |
| Temperature / power | operating temp, standby/current, thermal guidance | optional |

## 公开资料到参数字段的映射

| Vendor | 公开资料通常能支持 | 必须等待 datasheet/授权资料 | 适合先填的字段 |
|---|---|---|---|
| Micron | technical note、NAND 行为、ECC/可靠性术语 | 目标 part 的 read-retry table、timing mode、status/feature register 细节 | source URL、family、cell type、基础可靠性术语 |
| Kioxia | BiCS/3D NAND 技术背景、产品族语言 | 具体 geometry、tR/tPROG/tBERS、vendor command | generation、cell type、公开 white paper 摘要 |
| Samsung | V-NAND 代际、产品/SSD 功能语言 | NAND command/timing、read retry、ECC requirement | technology generation、产品族边界 |
| SK hynix | 产品族、技术新闻、企业 SSD 功能 | 可运行 NAND 模型参数 | vendor landscape、目标资料队列 |
| YMTC | Xtacking 架构和产品定位 | NAND interface timing、read retry、bad block rule | architecture terms、family notes |
| Western Digital / SanDisk | ECC/DSP、LDPC/read-retry 背景、可靠性语言 | 具体 die geometry、voltage table、vendor command sequence | ECC/read retry 设计解释、telemetry 字段 |

## 结论

公开 vendor 页面适合作为路线图和术语入口；真正用于控制器模型的参数必须落到具体 PDF、part number、版本号和 sha256。下一步应先做 Micron/Western Digital 的公开 technical note intake，因为它们最容易补 ECC、NAND 行为和可靠性解释。
