# Claude Desktop 中文汉化（zh-CN）

给 Windows 版 Claude Desktop 打中文补丁。

## 效果

核心界面汉化覆盖：聊天、设置、侧边栏导航、Cowork、Code 面板、第三方推理配置等。补丁后会注入中文字体自定义面板（右下角「字体」按钮）。

## 快速开始

1. 确保已安装 **Python 3**
2. 退出 Claude Desktop（含系统托盘）
3. 右键 `安装汉化.ps1` → **使用 PowerShell 运行**（需要管理员权限）

或者在管理员 PowerShell 中：

```powershell
.\安装汉化.ps1
```

运行完重新打开 Claude Desktop 即可。

## 目录结构

```
claude-zh-cn/
├── 安装汉化.ps1                        # 一键安装入口（中文）
├── install-windowsapps-json-only.ps1  # 一键安装入口（英文）
├── patch_windowsapps_json_only.py      # 步骤1：复制翻译 JSON + locale
├── patch_chunks_zh_cn.py               # 步骤2：locale 白名单 + JS 补丁 + 字体注入
├── restore_claude_zh_cn_windowsapps.py # 恢复脚本
├── resources/
│   ├── desktop-zh-CN.json              # 桌面壳层翻译（菜单、对话框等）
│   ├── frontend-zh-CN.json             # Web 前端翻译（主体界面）
│   └── statsig-zh-CN.json              # Statsig 功能描述翻译
├── tools/
│   ├── validate_resources.py           # JSON 合法性校验
│   ├── check_i18n_coverage.py          # 翻译覆盖率检测
│   └── test_patch_behaviors.py         # 回归测试
├── claude-zh-cn.ps1                    # 交互式菜单（安装/卸载/状态）
├── README.md
└── LICENSE.md
```

## 脚本做了什么

1. **复制翻译 JSON** — 把 `resources/*.json` 写入 Claude 的 `ion-dist/i18n/` 目录
2. **修补语言白名单** — 在 `cec18ad9a-*.js` 的 `KH` locale 数组中插入 `"zh-CN"`
3. **汉化 JS 硬编码文本** — 替换 bundle 中的英文 UI 标签（侧边栏、筛选器等）
4. **注入中文字体面板** — 运行时 CSS 字体覆盖 + 设置面板入口
5. **设置 locale** — 在 `config.json` 中写入 `"locale": "zh-CN"`

## 卸载

```powershell
python restore_claude_zh_cn_windowsapps.py
```

这会从备份还原原始文件、删除中文资源、移除 locale 设置。

## 翻译覆盖

| 文件 | 翻译量 | 当前版本 en-US 总量 | 覆盖率 |
|------|--------|-------------------|--------|
| desktop-zh-CN.json | 425 | — | — |
| frontend-zh-CN.json | 18,564 | 18,564 | 100% |
| statsig-zh-CN.json | 46 | — | — |

## 版本兼容

- **当前适配**: Claude Desktop v1.14271.0
- Claude Desktop 更新后，chunk 文件 hash 会变化，补丁脚本使用 glob 模式 (`[hash]-*.js`) 匹配，多数情况下无需修改
- JSON 语言资源不受版本影响
- 如 locale 白名单 `KH` 数组语法变化，需调整 `patch_chunks_zh_cn.py` 中 `cec18ad9a-*.js` 的替换规则

## 环境要求

- Windows 10 / 11
- Claude Desktop（Microsoft Store 安装或解压版）
- Python 3
- 管理员权限

## 参考来源

- [javaht/claude-desktop-zh-cn](https://github.com/javaht/claude-desktop-zh-cn)
- LINUX DO 社区

## 许可

非 Anthropic 官方发布，仅供个人设备使用。
