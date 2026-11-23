# nvme-cli 基础命令清单

将 `/dev/nvmeX` 和 `/dev/nvmeXnY` 替换为 DUT。不要对生产盘运行 destructive 命令。

## 非破坏性命令

```powershell
nvme list
nvme id-ctrl /dev/nvmeX
nvme id-ns /dev/nvmeXnY
nvme get-feature /dev/nvmeX -f 0x06
nvme smart-log /dev/nvmeX
nvme error-log /dev/nvmeX
nvme fw-log /dev/nvmeX
```

## 需要测试环境隔离的命令

```powershell
nvme reset /dev/nvmeX
nvme format /dev/nvmeXnY --lbaf=0
nvme sanitize /dev/nvmeX --sanact=2
```

## 关联测试

- T0-001
- T1-001
- T1-003
- T6-001
