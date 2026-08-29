# coldstation — 冷站负荷与设备参数预测流水线

三个冷站（A/B/C）的 24 小时逐时预测流水线：读取 5 分钟历史数据 xlsx → 清洗（-8888 占位、非物理值）→ 小时聚合 → 负荷模型 + 设备参数模型 → 末 30 天留出回测（含极端工况分项 MAPE）→ 导出上传用 CSV（列名可配置）。

**重要：真实训练数据（xlsx）永远不进本仓库。** 代码只从本地文件夹读取，路径由环境变量 `COLD_STATION_DATA_DIR` 指定。仓库中 `tests/data/` 下只有几十行的合成样例 CSV，仅供单元测试，与真实数据无关。

## 在 Mac 上跑真实数据回测（面向非编程用户）

前提：把三个训练 xlsx 放在一个文件夹里（默认假定是 `/Users/wangtianzhi/Documents/AI冷站比赛`），文件名保持原样。

1. 打开「终端」（Terminal）应用。
2. 安装依赖（只需一次）：

    ```bash
    cd 仓库路径/coldstation
    python3 -m pip install -r requirements.txt
    ```

3. 告诉程序数据在哪（如果就在上面那个默认文件夹，这步可跳过）：

    ```bash
    export COLD_STATION_DATA_DIR="/Users/wangtianzhi/Documents/AI冷站比赛"
    ```

4. 先检查数据能不能读到、质量如何（换 `--station B` / `--station C` 看其余两站）：

    ```bash
    python3 -m coldstation inspect --station A
    ```

    会输出：文件是否找到、清洗报告（占位值/越界值/缺行数量）、小时数据覆盖率、当前设备参数目标列。

5. 跑 30 天留出回测（每站一条命令）：

    ```bash
    python3 -m coldstation backtest --station A
    python3 -m coldstation backtest --station B
    python3 -m coldstation backtest --station C
    ```

    屏幕会打印负荷整体 MAPE、四类极端工况分项 MAPE、每个设备参数列的 MAPE；同时在 `out/` 文件夹存一份 JSON 报告和逐小时预测明细 CSV。

6. 生成一份交卷格式的预测 CSV（训练全部数据、预测未来 24 小时）：

    ```bash
    python3 -m coldstation predict --station A --out out/submission_A.csv
    ```

    如有逐时天气预报文件，加 `--weather 预报.csv`（列：`timeStamp,OutdoorTdbin,OutdoorWetTemp`）；不加则用 24h 滞后天气兜底，正式交卷前务必换成真预报。

## 常用可选项

- `--model hgb|ridge`：梯度提升（默认）或线性对照基线；`seq` 是预留的序列模型插槽（未实现，会明确报错）。
- `--targets 列1,列2`：覆盖设备参数目标列（官方口径到手后用这个替换默认假设）。
- `--input 路径`：直接指定某个历史文件，绕过 `COLD_STATION_DATA_DIR`。
- 上传 CSV 的列名/时间格式/编码在 `configs/qicheng_export_template.json` 里改，不用动代码。

## 目录结构

```
coldstation/
  coldstation/        # 流水线代码（英文）
    stations.py       #   三站字段配置（76/62/56 列、各站命名差异）
    io.py             #   读 xlsx/csv（双表头：英文点名+中文说明）
    cleaning.py       #   占位值/非物理值清洗、5min 网格、小时聚合
    features.py       #   负荷/设备特征（只用 >=24h 滞后，保证24h前瞻）
    models.py         #   模型注册表：hgb / ridge / seq(插槽)
    metrics.py        #   MAPE 与极端工况判定（高温/高湿/低温/负荷突变）
    backtest.py       #   末30天留出回测 + 分项报告
    predict.py        #   全量训练 + 未来24h预测
    export.py         #   上传CSV导出（列名JSON可配）
    cli.py            #   命令行入口
  configs/            # 上传格式模板
  tests/              # 单元测试 + 合成样例CSV（几十行，纯合成）
  tools/              # 合成样例生成脚本
```

## 运行单元测试

```bash
cd 仓库路径/coldstation
python3 -m pytest -q
```

全部测试只用合成数据。测试里的 MAPE 断言仅验证代码逻辑正确，不代表真实数据上的精度水平。
