#!/usr/bin/env python3
"""Patch JS chunks with Chinese UI labels.

This script applies safe string replacements to hardcoded UI labels
in Claude Desktop's JS bundle files. It backs up original files before
modifying and only replaces exact string patterns.

Run after patch_windowsapps_json_only.py.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
from pathlib import Path


BACKUP_ROOT = Path(os.environ["LOCALAPPDATA"]) / "Claude-zh-CN-official-backup" / "chunks"
CONFIG_PATH = Path(os.environ["LOCALAPPDATA"]) / "Claude-3p" / "config.json"
FONT_KEY = "claudeZhCnFont"


FONT_PRESETS = [
    {
        "id": "windows-modern",
        "label": "Windows 现代默认",
        "family": "Microsoft YaHei UI, Microsoft YaHei, Segoe UI, sans-serif",
    },
    {
        "id": "yahei",
        "label": "微软雅黑",
        "family": "Microsoft YaHei, Microsoft YaHei UI, Segoe UI, sans-serif",
    },
    {
        "id": "dengxian",
        "label": "等线",
        "family": "DengXian, Microsoft YaHei UI, Segoe UI, sans-serif",
    },
]


def font_inject_script() -> str:
    presets_json = json.dumps(FONT_PRESETS, ensure_ascii=False, separators=(",", ":"))
    body = f'''
;(()=>{{
  if (globalThis.__CLAUDE_ZH_CN_FONT_PATCH__) return;
  globalThis.__CLAUDE_ZH_CN_FONT_PATCH__ = true;
  const KEY = "{FONT_KEY}";
  const PRESETS = {presets_json};
  const DEFAULT = PRESETS[0].family;
  const STYLE_ID = "claude-zh-cn-font-style";
  const PANEL_ID = "claude-zh-cn-font-panel";
  const FLOATING_PANEL_ID = "claude-zh-cn-font-floating-panel";
  const FAB_ID = "claude-zh-cn-font-fab";
  const FALLBACK = "Microsoft YaHei UI, Microsoft YaHei, Segoe UI, Arial, sans-serif";
  const state = {{ fontFaceUrl: "" }};

  const readConfig = () => {{
    try {{
      const raw = localStorage.getItem(KEY);
      if (!raw) return {{ mode: "preset", presetId: "windows-modern", family: DEFAULT }};
      const data = JSON.parse(raw);
      return {{
        mode: data.mode || "preset",
        presetId: data.presetId || "windows-modern",
        family: data.family || DEFAULT,
        fontName: data.fontName || "",
        importedName: data.importedName || "",
        importedCss: data.importedCss || ""
      }};
    }} catch {{
      return {{ mode: "preset", presetId: "windows-modern", family: DEFAULT }};
    }}
  }};

  const saveConfig = (cfg) => {{
    const current = readConfig();
    const next = {{ ...current, ...cfg }};
    localStorage.setItem(KEY, JSON.stringify(next));
    applyFont(next);
    return next;
  }};

  const cssFamily = (cfg) => {{
    if (cfg.mode === "custom" && cfg.fontName) return `"${{cfg.fontName.replaceAll('"', '\\"')}}", ${{FALLBACK}}`;
    if (cfg.mode === "imported" && cfg.importedName) return `"${{cfg.importedName.replaceAll('"', '\\"')}}", ${{FALLBACK}}`;
    const preset = PRESETS.find((item) => item.id === cfg.presetId);
    return (preset && preset.family) || cfg.family || DEFAULT;
  }};

  function applyFont(cfg = readConfig()) {{
    let style = document.getElementById(STYLE_ID);
    if (!style) {{
      style = document.createElement("style");
      style.id = STYLE_ID;
      document.head.appendChild(style);
    }}
    const family = cssFamily(cfg);
    const importedCss = cfg.mode === "imported" && cfg.importedCss ? cfg.importedCss : "";
    style.textContent = `
${{importedCss}}
:root {{ --claude-zh-cn-font-family: ${{family}}; }}
html, body, #root, #__next, #app {{
  font-family: var(--claude-zh-cn-font-family) !important;
}}
body :is(div,span,p,h1,h2,h3,h4,h5,h6,a,button,label,legend,li,dt,dd,th,td,caption,small,strong,em,b,i,input,textarea,select,option,[role="dialog"],[role="menu"],[role="tooltip"],[role="listbox"],[role="option"],[contenteditable="true"]):not(svg):not(svg *):not([aria-hidden="true"]):not([data-icon]):not([class*="icon" i]):not([class*="lucide" i]):not([class*="codicon" i]):not([class*="material" i]):not([class*="fa-" i]) {{
  font-family: var(--claude-zh-cn-font-family) !important;
}}
pre, code, kbd, samp, .monaco-editor, .monaco-editor *, .xterm, .xterm * {{
  font-family: var(--claude-zh-cn-font-family) !important;
}}
svg text, svg tspan {{
  font-family: var(--claude-zh-cn-font-family) !important;
}}
`;
    document.documentElement.style.setProperty("--claude-zh-cn-font-family", family);
    window.dispatchEvent(new CustomEvent("claude-zh-cn-font-changed", {{ detail: cfg }}));
  }}

  const labelStyle = "display:block;margin:8px 0 4px;font-size:12px;color:var(--text-300,#666);";
  const inputStyle = "width:100%;box-sizing:border-box;border:1px solid var(--border-300,#ddd);border-radius:8px;padding:8px;background:var(--bg-000,#fff);color:inherit;";
  const buttonStyle = "border:1px solid var(--border-300,#ddd);border-radius:8px;padding:6px 9px;background:var(--bg-100,#f7f7f7);color:inherit;cursor:pointer;";
  const panelStyle = "margin:0;padding:10px;border:1px solid var(--border-200,#e6e6e6);border-radius:12px;background:var(--bg-000,#fff);box-shadow:0 12px 30px rgba(0,0,0,.13);backdrop-filter:blur(10px);";
  const mutedText = "font-size:11px;line-height:1.4;color:var(--text-300,#666);";
  const sectionStyle = "padding:9px;border:1px solid var(--border-200,#e6e6e6);border-radius:10px;background:var(--bg-050,#fafafa);";
  const sectionAltStyle = "padding:9px;border:1px solid var(--border-300,#ddd);border-radius:10px;background:var(--bg-000,#fff);";
  const previewStyle = "padding:12px;border:1px solid var(--border-300,#ddd);border-radius:12px;background:linear-gradient(180deg,var(--bg-000,#fff),var(--bg-050,#fafafa));min-height:130px;";
  const segmentBase = "flex:1;min-width:0;border:0;border-radius:7px;padding:6px 7px;background:transparent;color:var(--text-300,#666);cursor:pointer;font-size:11px;font-weight:600;text-align:center;transition:background .12s ease,color .12s ease,box-shadow .12s ease;";
  const segmentActive = "background:var(--bg-000,#fff);color:var(--text-500,#111);box-shadow:0 1px 2px rgba(0,0,0,.07),inset 0 0 0 1px var(--border-300,#ddd);";

  const VISIBLE_TEXT_FIXES = new Map([
    ["auto", "自动"],
    ["Auto", "自动"],
    ["light", "浅色"],
    ["Light", "浅色"],
    ["dark", "深色"],
    ["Dark", "深色"],
    ["sans", "无衬线"],
    ["Sans", "无衬线"],
  ]);

  function shouldFixTextNode(node) {{
    const parent = node.parentElement;
    if (!parent || parent.closest("script,style,[contenteditable='true']")) return false;
    const scope = parent.closest("[role='dialog'],[role='menu'],[role='listbox'],main,section");
    if (!scope) return false;
    const context = scope.innerText || "";
    return /(Appearance|外观|颜色模式|Color mode|聊天字体|Chat font|Font|字体)/.test(context);
  }}

  function fixVisibleText(root = document.body) {{
    if (!root) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (nodes.length < 2000) {{
      const node = walker.nextNode();
      if (!node) break;
      nodes.push(node);
    }}
    nodes.forEach((node) => {{
      const text = node.nodeValue;
      if (!text) return;
      const trimmed = text.trim();
      const replacement = VISIBLE_TEXT_FIXES.get(trimmed);
      if (!replacement) return;
      if (!shouldFixTextNode(node)) return;
      node.nodeValue = text.replace(trimmed, replacement);
    }});
  }}

  let textFixScheduled = false;
  function scheduleFixVisibleText() {{
    if (textFixScheduled) return;
    textFixScheduled = true;
    const schedule = window.requestAnimationFrame || ((callback) => window.setTimeout(callback, 16));
    schedule(() => {{
      textFixScheduled = false;
      fixVisibleText();
    }});
  }}

  function buildPanel(expanded = false, mode = "inline") {{
    const panel = document.createElement("section");
    panel.id = mode === "floating" ? FLOATING_PANEL_ID : PANEL_ID;
    panel.dataset.fontPanelMode = mode;
    panel.style.cssText = panelStyle + (mode === "floating" ? "width:min(520px,calc(100vw - 40px));" : "width:100%;box-sizing:border-box;");
    panel.innerHTML = `
      <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;">
        <div>
          <h3 style="margin:0;font-size:13px;font-weight:700;letter-spacing:-0.01em;">中文字体</h3>
          <p style="margin:4px 0 0;${{mutedText}}">调整 Claude 界面的中文字体。</p>
        </div>
        <button data-font-toggle style="${{buttonStyle}};white-space:nowrap;font-size:11px;">${{expanded ? "收起" : "字体"}}</button>
      </div>

      <div data-font-body style="display:${{expanded ? "block" : "none"}};margin-top:8px;">
      <div data-font-layout style="display:grid;grid-template-columns:minmax(0,1.25fr) minmax(150px,.75fr);gap:10px;align-items:stretch;">
      <div style="display:flex;flex-direction:column;gap:8px;">
      <div style="${{sectionStyle}}">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:5px;">
          <label style="margin:0;font-size:11px;font-weight:600;color:var(--text-400,#444);">内置推荐</label>
          <span data-font-status style="font-size:11px;color:var(--text-300,#666);"></span>
        </div>
        <div data-font-preset-group style="display:flex;gap:1px;padding:2px;border:1px solid var(--border-300,#ddd);border-radius:10px;background:var(--bg-100,#f5f5f5);box-shadow:inset 0 1px 2px rgba(0,0,0,.04);">
          ${{PRESETS.map((item) => `<button type="button" data-font-preset-btn="${{item.id}}" style="${{segmentBase}}">${{item.label}}</button>`).join("")}}
        </div>
        <p style="margin:5px 0 0;${{mutedText}}">推荐字体，直接切换。</p>
      </div>

      <div style="${{sectionAltStyle}}">
        <label style="margin:0 0 5px;display:block;font-size:11px;font-weight:600;color:var(--text-400,#444);">自定义系统字体名</label>
        <div style="display:flex;gap:5px;align-items:center;">
          <input data-font-name placeholder="已安装字体名称" style="${{inputStyle}};min-width:0;padding:6px 7px;font-size:11px;" />
          <button data-font-apply-custom style="${{buttonStyle}};white-space:nowrap;font-size:11px;">应用</button>
        </div>
        <p style="margin:5px 0 0;${{mutedText}}">输入已安装字体名。</p>
      </div>

      <div style="${{sectionStyle}}">
        <label style="margin:0 0 5px;display:block;font-size:11px;font-weight:600;color:var(--text-400,#444);">导入本地字体文件</label>
        <input data-font-file type="file" accept=".ttf,.otf,font/ttf,font/otf" style="${{inputStyle}};padding:4px 5px;font-size:11px;" />
        <p style="margin:5px 0 0;${{mutedText}}">选择本地 .ttf / .otf。</p>
      </div>
      </div>

      <div style="${{previewStyle}}">
        <div style="margin:0 0 8px;font-size:11px;font-weight:600;color:var(--text-400,#444);">预览</div>
        <div style="font-size:16px;line-height:1.45;font-weight:600;color:var(--text-500,#111);">中文字体预览</div>
        <div style="margin-top:8px;${{mutedText}}">Claude Desktop 中文补丁</div>
        <div style="margin-top:14px;font-size:11px;color:var(--text-300,#666);">Aa 你好 Claude</div>
      </div>
      </div>
      <div style="display:flex;justify-content:flex-end;margin-top:8px;">
        <button data-font-reset style="${{buttonStyle}};white-space:nowrap;font-size:11px;">恢复默认</button>
      </div>
      </div>
    `;

    const presetButtons = [...panel.querySelectorAll("[data-font-preset-btn]")];
    const fontName = panel.querySelector("[data-font-name]");
    const status = panel.querySelector("[data-font-status]");
    const updateLayout = () => {{
      const layout = panel.querySelector("[data-font-layout]");
      if (!layout) return;
      layout.style.gridTemplateColumns = panel.getBoundingClientRect().width < 430 ? "1fr" : "minmax(0,1.25fr) minmax(150px,.75fr)";
    }};
    panel.querySelector("[data-font-toggle]").addEventListener("click", () => {{
      if (panel.dataset.fontPanelMode === "floating") {{
        panel.remove();
        return;
      }}
      const body = panel.querySelector("[data-font-body]");
      const willExpand = body.style.display === "none";
      body.style.display = willExpand ? "block" : "none";
      panel.querySelector("[data-font-toggle]").textContent = willExpand ? "收起" : "字体";
      if (willExpand) updateLayout();
    }});
    const setActivePreset = (presetId) => {{
      presetButtons.forEach((button) => {{
        const active = button.getAttribute("data-font-preset-btn") === presetId;
        button.style.cssText = `${{segmentBase}}${{active ? segmentActive : ""}}`;
      }});
    }};
    const sync = () => {{
      const cfg = readConfig();
      const currentPreset = cfg.presetId || "windows-modern";
      setActivePreset(currentPreset);
      fontName.value = cfg.fontName || "";
      status.textContent = cfg.mode === "custom" ? `当前：${{cfg.fontName}}` : cfg.mode === "imported" ? `当前：${{cfg.importedName}}` : `当前：${{PRESETS.find((item) => item.id === cfg.presetId)?.label || "Windows 现代默认"}}`;
    }};
    presetButtons.forEach((button) => {{
      button.addEventListener("click", () => {{
        const item = PRESETS.find((entry) => entry.id === button.getAttribute("data-font-preset-btn")) || PRESETS[0];
        saveConfig({{ mode: "preset", presetId: item.id, family: item.family }});
        sync();
      }});
    }});
    panel.querySelector("[data-font-apply-custom]").addEventListener("click", () => {{
      const name = fontName.value.trim();
      if (!name) return;
      saveConfig({{ mode: "custom", fontName: name }});
      sync();
    }});
    panel.querySelector("[data-font-file]").addEventListener("change", async (event) => {{
      const file = event.target.files && event.target.files[0];
      if (!file) return;
      const buffer = await file.arrayBuffer();
      const bytes = new Uint8Array(buffer);
      let binary = "";
      for (let i = 0; i < bytes.length; i += 1) binary += String.fromCharCode(bytes[i]);
      const b64 = btoa(binary);
      const name = `ClaudeZhCnImported-${{Date.now()}}`;
      const format = file.name.toLowerCase().endsWith(".otf") ? "opentype" : "truetype";
      const css = `@font-face{{font-family:"${{name}}";src:url(data:font/${{format}};base64,${{b64}}) format("${{format}}");font-display:swap;}}`;
      saveConfig({{ mode: "imported", importedName: name, importedCss: css }});
      sync();
    }});
    panel.querySelector("[data-font-reset]").addEventListener("click", () => {{
      localStorage.removeItem(KEY);
      applyFont();
      sync();
    }});
    sync();
    updateLayout();
    return panel;
  }}

  function openFloatingPanel() {{
    let panel = document.getElementById(FLOATING_PANEL_ID);
    if (!panel) {{
      panel = buildPanel(true, "floating");
      panel.style.position = "fixed";
      panel.style.right = "20px";
      panel.style.bottom = "76px";
      panel.style.zIndex = "2147483647";
      panel.style.width = "min(520px, calc(100vw - 40px))";
      panel.style.boxShadow = "0 18px 60px rgba(0,0,0,.24)";
      document.body.appendChild(panel);
    }} else {{
      panel.remove();
    }}
  }}

  function mountFloatingButton() {{
    if (!document.body || document.getElementById(FAB_ID)) return;
    const button = document.createElement("button");
    button.id = FAB_ID;
    button.type = "button";
    button.textContent = "字体";
    button.title = "中文字体设置";
    button.style.cssText = "position:fixed;right:20px;bottom:20px;z-index:2147483647;border:1px solid var(--border-300,#ddd);border-radius:999px;padding:8px 12px;background:var(--bg-000,#fff);color:inherit;box-shadow:0 8px 28px rgba(0,0,0,.18);cursor:pointer;font-size:13px;";
    button.addEventListener("click", openFloatingPanel);
    document.body.appendChild(button);
  }}

  function mountPanel() {{
    return;
  }}

  const start = () => {{
    applyFont();
    mountFloatingButton();
    scheduleFixVisibleText();
    const observer = new MutationObserver(() => {{
      scheduleFixVisibleText();
    }});
    observer.observe(document.body, {{ childList: true, subtree: true }});
  }};
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, {{ once: true }});
  else start();
}})();
'''.strip()
    return "\n".join([
        "// __CLAUDE_ZH_CN_FONT_PATCH_BEGIN__",
        body,
        "// __CLAUDE_ZH_CN_FONT_PATCH_END__",
    ])


def find_claude_package() -> Path | None:
    base = Path(r"C:\Program Files\WindowsApps")
    if not base.exists():
        return None
    candidates = sorted(base.glob("Claude_*_x64__*/app/resources/en-US.json"), reverse=True)
    if candidates:
        return candidates[0].parent.parent
    return None


def backup_file(path: Path, assets_dir: Path) -> None:
    if not path.exists():
        return
    rel = path.relative_to(assets_dir)
    dst = BACKUP_ROOT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        copy2_best_effort(path, dst, context="backup file")



def _take_ownership(path: Path) -> bool:
    """Take ownership and grant write access via takeown + icacls."""
    import subprocess
    try:
        subprocess.run(["takeown", "/f", str(path), "/a"], capture_output=True, timeout=30)
        subprocess.run(["icacls", str(path), "/grant", "Administrators:F"], capture_output=True, timeout=30)
        return True
    except Exception:
        return False


def copy2_best_effort(src: Path, dst: Path, *, context: str) -> bool:
    """Copy a file and retry after taking ownership of TrustedInstaller-protected files."""
    try:
        shutil.copy2(src, dst)
        return True
    except PermissionError:
        if dst.exists():
            _take_ownership(dst)
        else:
            _take_ownership(dst.parent)
        try:
            shutil.copy2(src, dst)
            return True
        except OSError as e:
            print(f"Warning: cannot copy {context} from {src} to {dst}: {e}; skipping")
            return False
    except OSError as e:
        print(f"Warning: cannot copy {context} from {src} to {dst}: {e}; skipping")
        return False


def set_font_config_mirror() -> bool:
    """Mirror default font config into Claude config without changing app behavior."""
    if not CONFIG_PATH.exists():
        return False

    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False

    data.setdefault(
        FONT_KEY,
        {
            "mode": "preset",
            "presetId": "windows-modern",
            "family": FONT_PRESETS[0]["family"],
        },
    )
    return write_text_best_effort(
        CONFIG_PATH,
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        context="font config mirror",
    )


def write_text_best_effort(path: Path, text: str, *, context: str) -> bool:
    """Write text and degrade gracefully on Windows permission issues."""
    try:
        path.write_text(text, encoding="utf-8")
        return True
    except PermissionError:
        if path.exists():
            _take_ownership(path)
        else:
            _take_ownership(path.parent)
        try:
            path.write_text(text, encoding="utf-8")
            return True
        except OSError as e:
            print(f"Warning: cannot write {context} at {path}: {e}; skipping")
            return False
    except OSError as e:
        print(f"Warning: cannot write {context} at {path}: {e}; skipping")
        return False


def patch_font_runtime(assets_dir: Path) -> int:
    """Inject runtime font customizer into the entry bundle."""
    candidates = sorted(assets_dir.glob("index-*.js"))
    if not candidates:
        print("Warning: no index-*.js found; skipping font runtime patch")
        return 0

    script = font_inject_script()
    marker = "__CLAUDE_ZH_CN_FONT_PATCH__"
    begin_marker = "// __CLAUDE_ZH_CN_FONT_PATCH_BEGIN__"
    end_marker = "// __CLAUDE_ZH_CN_FONT_PATCH_END__"
    changed = 0
    for path in candidates:
        backup_file(path, assets_dir)
        content = path.read_text(encoding="utf-8")
        if begin_marker in content and end_marker in content:
            start = content.index(begin_marker)
            end = content.index(end_marker, start) + len(end_marker)
            new_content = content[:start].rstrip() + "\n" + script + "\n" + content[end:].lstrip()
            action = "updated font runtime"
        elif marker in content:
            marker_pos = content.index(marker)
            start = content.rfind(";(()=>{", 0, marker_pos)
            if start == -1:
                start = marker_pos
            legacy_end = content.find("})();", marker_pos)
            end = legacy_end + len("})();") if legacy_end != -1 else len(content)
            new_content = content[:start].rstrip() + "\n" + script + "\n" + content[end:].lstrip()
            action = "replaced legacy font runtime"
        else:
            new_content = content.rstrip() + "\n" + script + "\n"
            action = "injected font runtime"

        if new_content == content:
            continue
        if write_text_best_effort(path, new_content, context="font runtime patch"):
            changed += 1
            print(f"  {path.name}: {action}")
    return changed


PATCHES: dict[str, list[tuple[str, str]]] = {}

# === 3P settings page (c71860c77-*.js) — v1.14271.0 ===
# 硬编码字符串已全部迁移到 i18n JSON 系统，不再需要 JS 补丁
PATCHES["c71860c77-*.js"] = []

# === 主界面 bundle (index-*.js) — v1.14271.0 ===
# 原 cbc59a8af 侧边栏标签已移入 index-*.js

# === locale 白名单 (cec18ad9a-*.js) — v1.14271.0 ===
# zh-CN 不在 KH 数组中，需要加入才能被 app 识别
PATCHES["cec18ad9a-*.js"] = [
    # KH 变量定义中的 locale 列表
    ('KH=["en-US","de-DE"', 'KH=["zh-CN","en-US","de-DE"'),
    # GH 函数参数中的内联 locale 列表
    ('function GH(e,t=KH)', 'function GH(e,t=KH)'),  # no-op (just to match the file)
]


PATCHES["index-*.js"] = [
    # ── 侧边栏导航标签 ──
    ('label:"Chat"', 'label:"聊天"'),
    ('label:"Cowork"', 'label:"协作"'),
    ('label:"Code"', 'label:"代码"'),
    ('label:"Pull Requests"', 'label:"拉取请求"'),
    ('label:"Replay"', 'label:"回放"'),
    ('label:"Ideas"', 'label:"想法"'),
    ('label:"Status"', 'label:"状态"'),
    ('label:"Last activity"', 'label:"最近活动"'),
    ('label:"Group by"', 'label:"分组方式"'),
    # ── 筛选器下拉选项 ──
    ('["active","Active"]', '["active","活跃"]'),
    ('["archived","Archived"]', '["archived","已归档"]'),
    ('["all","All"]', '["all","全部"]'),
    ('["project","Project"]', '["project","项目"]'),
    ('["state","State"]', '["state","状态"]'),
    ('["0","All"]', '["0","全部"]'),
    ('["1","1d"]', '["1","1天"]'),
    ('["3","3d"]', '["3","3天"]'),
    ('["7","7d"]', '["7","7天"]'),
    ('["30","30d"]', '["30","30天"]'),
    ('?"All":', '?"全部":'),
    # ── 通用标签 ──
    ('"Date"', '"日期"'),
    ('"None"', '"无"'),
    ('"Older"', '"更早"'),
    ('"Ungrouped"', '"未分组"'),
    # ── 删除/拖拽 ──
    ('title:"Delete older sessions?"', 'title:"删除较旧的会话？"'),
    ('"Drop here"', '"放在这里"'),
    ('"Let go"', '"松开"'),
    # ── 筛选 ──
    ('children:"Clear filters"', 'children:"清除筛选"'),
    ('children:"All projects"', 'children:"所有项目"'),
    ('children:"Project"', 'children:"项目"'),
    ('children:"3P"', 'children:"第三方"'),
    # ── 同步源 ──
    ('label:"Documents"', 'label:"文档"'),
    ('label:"Files"', 'label:"文件"'),
    ('label:"Sync Sources"', 'label:"同步源"'),
    ('title:"Add content from GitHub"', 'title:"从 GitHub 添加内容"'),
    ('title:"Connect Claude to Google Drive"', 'title:"将 Claude 连接到 Google Drive"'),
    # ── 计划任务 (baseDescription 仍在 chunk 中) ──
    ('baseDescription:"New task"', 'baseDescription:"新建任务"'),
    # ── 通话弹窗 ──
    ('title:"End this call?"', 'title:"结束此通话？"'),
]

def main() -> int:
    parser = argparse.ArgumentParser(description="Patch Claude Desktop JS chunks with zh-CN labels")
    parser.add_argument("--app-dir", type=str, default=None)
    args = parser.parse_args()

    if args.app_dir:
        app_dir = Path(args.app_dir)
    else:
        app_dir = find_claude_package()

    if not app_dir or not app_dir.exists():
        raise SystemExit("Claude app directory not found.")

    assets_dir = app_dir / "resources" / "ion-dist" / "assets" / "v1"
    if not assets_dir.exists():
        raise SystemExit(f"Assets dir not found: {assets_dir}")

    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    total = 0

    for pattern, replacements in PATCHES.items():
        files = sorted(assets_dir.glob(pattern))
        for fpath in files:
            backup_file(fpath, assets_dir)
            content = fpath.read_text(encoding="utf-8")
            changed = 0
            for old, new in replacements:
                if old in content and old != new:
                    content = content.replace(old, new)
                    changed += 1
            if changed > 0:
                if write_text_best_effort(fpath, content, context="chunk replacement"):
                    total += changed
                    print(f"  {fpath.name}: {changed} replacements")

    font_patches = patch_font_runtime(assets_dir)
    config_mirrored = set_font_config_mirror()

    print(f"Done. Total chunk patches: {total}")
    print(f"Font runtime patches: {font_patches}")
    print(f"Font config mirrored: {config_mirrored}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
