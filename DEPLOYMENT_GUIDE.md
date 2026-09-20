# Cloudflare Workers + GitHub Pages 钉钉免登部署指南

## 一、前置准备

### 1.1 钉钉应用凭证（已提供）
- AppKey: `dingtdwofoowl7hxbjd7`
- AppSecret: `FvEzquXDKa3UvaL9TYSntDhYzI5p0ulyjo_OPqDM1V6iNQ6J2EJ3aeiE0KHhlQrx`
- CorpId: `ding53c7b55d07974d7335c2f4657eb6378f`

### 1.2 GitHub 仓库
- 用户名: `lipengzhang123`
- 仓库: `lpz-test`
- CNAME 文件已创建并推送，GitHub Pages 将在 1-3 分钟内绑定 `hgkj.eu.cc`

---

## 二、Cloudflare KV Namespace 创建

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 左侧菜单 → **Workers & Pages** → **KV**
3. 点击 **Create namespace**
4. 名称填写: `DINGTALK_KV`
5. 点击 **Add**
6. **记录生成的 Namespace ID**（形如 `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`），后续配置需要用到

---

## 三、Cloudflare Worker 部署

### 3.1 安装 Wrangler CLI（本地开发可选）
```bash
npm install -g wrangler
wrangler login
```

### 3.2 修改 wrangler.toml
打开 `worker/wrangler.toml`，将 `YOUR_KV_NAMESPACE_ID_HERE` 替换为第二步记录的 ID：

```toml
[[kv_namespaces]]
binding = "DINGTALK_KV"
id = "你刚才记录的ID"
```

### 3.3 部署 Worker
```bash
cd worker
wrangler deploy
```

### 3.4 配置环境变量（必须！）
部署后在 Cloudflare Dashboard 中设置：

1. 进入 **Workers & Pages** → 选择你的 Worker（`dingtalk-auth-worker`）
2. 点击 **Settings** → **Variables**
3. 添加以下变量：

| Variable name | Value |
|---|---|
| `APP_KEY` | `dingtdwofoowl7hxbjd7` |
| `APP_SECRET` | `FvEzquXDKa3UvaL9TYSntDhYzI5p0ulyjo_OPqDM1V6iNQ6J2EJ3aeiE0KHhlQrx` |
| `TARGET_CORP_ID` | `ding53c7b55d07974d7335c2f4657eb6378f` |

4. 点击 **Save and Deploy**

---

## 四、Cloudflare DNS 与路由配置

### 4.1 DNS 记录
进入 **DNS** → **Records**，确认已有以下记录：

| Type | Name | Content | Proxy status |
|---|---|---|---|
| CNAME | @ | `lipengzhang123.github.io` | Proxied (橙色云) |

如果没有，手动添加。

### 4.2 Worker Route（关键！）
进入 **Workers & Pages** → 选择你的 Worker → **Triggers** → **Add route**：

- **Route**: `hgkj.eu.cc/api/*`
- **Service**: 选择 `dingtalk-auth-worker`
- **Environment**: `production`

点击 **Add route**。

> **原理**：访问 `hgkj.eu.cc/api/*` 时请求转发给 Worker；访问其他路径（如 `hgkj.eu.cc/index.html`）正常回源到 GitHub Pages。

### 4.3 SSL/TLS 设置
进入 **SSL/TLS** → 设置为 **Flexible**（调试阶段），确认页面可访问后再切换为 **Full (Strict)**。

---

## 五、钉钉开发者后台配置

### 5.1 应用首页地址
进入钉钉开发者后台 → 你的应用 → **应用信息**：

- **应用首页地址**: `https://hgkj.eu.cc/?corpid=$CORPID$`
- **PC端首页地址**: `https://hgkj.eu.cc/?corpid=$CORPID$`

### 5.2 JSAPI 安全域名（必须配置！）
进入 **权限管理** → **JSAPI 安全域名**：

- 添加: `hgkj.eu.cc`

> ⚠️ 未配置此项，钉钉 JSAPI 调用会直接失败。

---

## 六、导入案例数据到 KV（可选）

如果希望案例数据从后端读取而非前端硬编码：

1. 将 `cases.json` 内容转换为 JSON 字符串
2. 在 Cloudflare Dashboard → Workers → 你的 Worker → **KV** → `DINGTALK_KV`
3. 创建 Key: `cases_data`，Value: JSON 字符串
4. 或者使用 Wrangler 命令行：
```bash
wrangler kv:key put --namespace-id=YOUR_KV_ID cases_data "$(cat ../cases.json)"
```

---

## 七、验证清单

- [ ] 访问 `https://hgkj.eu.cc` 能看到精益改善案例平台首页（非 404）
- [ ] 钉钉工作台打开应用能正常免登
- [ ] 控制台无 CORS/OPTIONS 相关报错
- [ ] Session 过期后自动重新免登，页面不空白
- [ ] `/api/getCase` 接口返回 JSON 格式数据（非纯文本）

---

## 八、常见问题

### Q1: 访问 hgkj.eu.cc 仍然 404
A: CNAME 文件推送后 GitHub Pages 需要 1-3 分钟重新部署。检查 GitHub Pages Settings 中 Custom domain 是否显示 `hgkj.eu.cc`。

### Q2: 钉钉免登报错 "invalid corpid"
A: 确认钉钉后台 JSAPI 安全域名已配置 `hgkj.eu.cc`，且 URL 中包含 `?corpid=$CORPID$` 参数。

### Q3: OPTIONS 预检失败
A: 确认 Worker 代码中已包含 OPTIONS 处理逻辑，且 Worker Route 正确匹配 `/api/*`。

### Q4: Token 获取频繁失败
A: 检查 KV Namespace 是否正确绑定到 Worker，环境变量 APP_KEY/APP_SECRET 是否正确配置。
