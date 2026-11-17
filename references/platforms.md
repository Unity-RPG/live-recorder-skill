# 支持的直播平台与链接格式规范 (Supported Platforms)

本文档列出录制引擎支持的主流平台及其推荐的直播间链接提取规范。

---

## 1. 抖音 (Douyin)
- **支持链接格式**：
  - PC 端直播间直链：`https://live.douyin.com/745964462470` 或 `https://live.douyin.com/yall1102`
  - 手机 App 分享短链：`https://v.douyin.com/iQFeBnt/`
  - 主播个人主页链接：`https://www.douyin.com/user/MS4wLjABAAAA...`
- **注意事项**：
  - 推荐优先使用网页端直播间直链（`live.douyin.com/房间号`），解析速度最快。
  - 主播开播时，主页链接会自动被引擎解析并替换为当前直播间 ID。

---

## 2. 快手 (Kuaishou)
- **支持链接格式**：
  - `https://live.kuaishou.com/u/yall1102`
  - 手机短链：`https://v.kuaishou.com/xxxxxx`

---

## 3. TikTok (国际版抖音)
- **支持链接格式**：
  - `https://www.tiktok.com/@username/live`
- **注意事项**：
  - 必须在 `config.ini` 中开启代理：
    ```ini
    是否使用代理ip(是/否) = 是
    代理地址 = 127.0.0.1:7890
    ```

---

## 4. 哔哩哔哩 (B站 / Bilibili)
- **支持链接格式**：
  - 直播间主链接：`https://live.bilibili.com/320`

---

## 5. 虎牙直播 (Huya)
- **支持链接格式**：
  - `https://www.huya.com/52333`

---

## 6. 斗鱼直播 (Douyu)
- **支持链接格式**：
  - `https://www.douyu.com/3637778`
  - 专题直播间：`https://www.douyu.com/topic/wzDBLS6?rid=4921614`

---

## 7. 其它平台
- **小红书 (Xiaohongshu)**: `https://www.xiaohongshu.com/...`
- **YY 直播**: `https://www.yy.com/22490906/22490906`
- **网易 CC 直播**: `https://cc.163.com/...`
- **Twitch**: `https://www.twitch.tv/username`（需配置代理）
- **YouTube Live**: `https://www.youtube.com/watch?v=...`（需配置代理）
