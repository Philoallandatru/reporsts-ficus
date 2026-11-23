# 掉电恢复流程图

```mermaid
flowchart TD
  A["Power-on / reset"] --> B["Initialize minimal hardware"]
  B --> C["Scan superblock copies"]
  C --> D{"Valid superblock<br/>CRC and generation?"}
  D -- "No" --> E["Enter safe mode / require factory recovery"]
  D -- "Yes" --> F["Load active checkpoint"]
  F --> G{"Checkpoint valid?"}
  G -- "No" --> H["Try previous checkpoint generation"]
  H --> G
  G -- "Yes" --> I["Replay journal by sequence"]
  I --> J{"Entry complete<br/>CRC and commit marker?"}
  J -- "No" --> K["Stop replay at tail"]
  J -- "Yes" --> L["Apply mapping/block-state delta"]
  L --> I
  K --> M["Validate page metadata and versions"]
  M --> N["Rebuild free block pool and open blocks"]
  N --> O["Resolve interrupted GC / erase / firmware update"]
  O --> P["Run consistency checks"]
  P --> Q{"Ready to expose namespaces?"}
  Q -- "No" --> E
  Q -- "Yes" --> R["Set controller ready"]
```

## 阅读入口

- [掉电保护与恢复](../wiki/concepts/power-loss-recovery.md)
- [FTL 元数据格式与恢复约定](../wiki/concepts/ftl-metadata-format-and-recovery-conventions.md)
- [故障注入目录](../wiki/concepts/fault-injection-catalog.md)
- [Power-loss State Table](../tests/faults/power-loss-state-table.yml)
