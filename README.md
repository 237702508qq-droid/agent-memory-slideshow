# 云桌面 AI Agent「桌面记忆」方案 — 可交互网页演示（HyperFrames 版）

基于 **HyperFrames Slideshow**（hyperframes 0.8.41 standalone harness）的 7 页客户价值演示，浅色明亮商务风。
内容依据产品经理思维导图（见 `../OUTLINE.md`）。

**在线访问**：https://237702508qq-droid.github.io/agent-memory-slideshow/

## 打开方式
- 在线：直接打开上面链接
- 本地：`python3 -m http.server 8000` → http://localhost:8000/ （勿用 file:// 直开）

## 操作
| 按键/操作 | 作用 |
|---|---|
| `→` / `Space` | 下一步（fragment 逐条揭示） |
| `←` / `Backspace` | 上一步（分支内则返回主线原位） |
| 点击「深入 →」 | 进入案例对照分支页 |
| `P` | 演讲者模式（观众页 + 备注） |

## 页面结构（7 主线 + 1 分支）
P1 封面 / P2 两个典型问题（含案例+hotspot） / P3 原因分析 / P4 解决方案三步 / P5 如何解决 / P6 更多自定义功能 / P7 用户价值总结 / B1 两个案例逐条对照（分支）

## 验证
`selfcheck.py` 全绿；`hyperframes lint/check` Runtime 0 errors；浏览器实测 22/22 PASS（本地）。
