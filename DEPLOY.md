# 数字图像处理教学平台 — 部署文档（Cloudflare Tunnel）

> 西南交通大学希望学院 · 基础部  
> 设计：李康乐 | 技术支持：李康乐  
> 部署域名：https://dip.likangle.top  
> 应用端口：9527 → cloudflared → Cloudflare Tunnel（公网）

---

## 一、项目概述

基于 Flask + OpenCV 的数字图像处理 Web 教学平台，覆盖《数字图像处理（第四版）_冈萨雷斯》第 1-12 章，共 78 个图像处理操作。

### 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python Flask + OpenCV + NumPy + Pillow |
| 前端 | Jinja2 模板 + 原生 HTML / CSS / JavaScript |
| WSGI | Gunicorn（4 workers，120s 超时） |
| 数据库 | SQLite（文件型，挂载持久化） |
| 隧道 | Cloudflare Tunnel（cloudflared，Docker 容器） |
| 容器化 | Docker + Docker Compose |
| 部署环境 | 飞牛 NAS（fnOS，Debian 基） |

### 架构

```
用户浏览器（HTTPS）
      │
      ▼
Cloudflare Edge（SSL 终止，Flexible 模式）
      │
      ▼
Cloudflare Tunnel（cloudflared，主动出站连接）
      │
      ▼
Flask 容器（Gunicorn :9527）
      │
      ├── /app/data   ← 宿主机 ./data
      └── /app/images ← 宿主机 ./images
```

**关键优点**：无需 Nginx 中间层，cloudflared 直接指向 Flask:9527，架构极简。

---

## 二、部署文件清单

| 文件 | 用途 |
|------|------|
| `Dockerfile` | Flask 应用镜像构建指令 |
| `docker-compose.yml` | 双容器编排（dip + cloudflared） |
| `DEPLOY.md` | 本部署文档 |

---

## 三、部署步骤

### 3.1 同步项目文件

将整个项目文件夹同步到 NAS 上的 `/vol1/1000/docker/dip`（可通过 SMB、rsync 或飞牛文件管理完成）。

### 3.2 Docker Compose 部署

```bash
cd /vol1/1000/docker/dip
docker-compose up -d --build
```

> 首次构建需下载基础镜像，耗时约 2-5 分钟。  
> **注意**：每次更新代码后必须加 `--build` 参数重建镜像，否则运行的是旧代码。

### 3.3 验证内网访问

浏览器访问：`http://NAS内网IP:9527`

确认页面正常加载后，进入下一步。

### 3.4 配置 Cloudflare Tunnel 指向 Flask

登录 Cloudflare Zero Trust → Networks → Tunnels → 选择 `dip-tunnel` → 编辑 Public Hostname：

- **Subdomain**：`dip`
- **Domain**：`likangle.top`
- **Type**：`HTTP`
- **URL**：`192.168.31.185:9527`

保存后验证公网访问：**https://dip.likangle.top**

---

### 3.5 Cloudflare SSL 设置

登录 Cloudflare Dashboard → 选择域名 `likangle.top` → **SSL/TLS**：

1. SSL/TLS 加密模式设为 **"灵活（Flexible）"**
   - 含义：浏览器 ↔ Cloudflare 使用 HTTPS，Cloudflare ↔ 源站使用 HTTP
2. 开启 **"始终使用 HTTPS"**
   - 自动将 HTTP 请求 301 重定向到 HTTPS

Edge 证书会自动由 Cloudflare 颁发和续期（无需 Let's Encrypt）。

---

## 四、运维备忘

### 常用命令

```bash
cd /vol1/1000/docker/dip

# 查看容器状态
docker-compose ps

# 查看全部日志
docker-compose logs -f

# 单独查看隧道日志
docker-compose logs -f cloudflared

# 重启全部
docker-compose restart

# 停止全部
docker-compose down

# 更新应用后重建
docker-compose up -d --build dip
```

### 数据持久化

| 容器内路径 | 宿主机路径 | 内容 |
|-----------|-----------|------|
| `/app/data` | `./data` | SQLite 数据库文件 |
| `/app/images` | `./images` | 上传/生成的图片 |

### 端口说明

| 端口 | 用途 | 对内 | 对外 |
|------|------|------|------|
| 9527 | Flask 应用（Gunicorn） | 容器间通信 | 映射宿主机 9527 |
| Tunnel | cloudflared 出站 | — | 主动连接 Cloudflare |

---

## 五、给学生的使用说明

1. 打开浏览器访问 **https://dip.likangle.top**
2. 注册/登录账号
3. 选择章节浏览理论知识
4. 进入综合工程案例实操页面
5. 上传图片，拖动参数滑块实时查看处理效果
6. 各章节底部讨论区可交流提问

---

## 六、常见问题

### Q: 访问 https://dip.likangle.top 出现 502 Bad Gateway

A: Cloudflare 与源站通信失败。可能原因：
1. dip 容器未启动 → `docker-compose ps` 检查
2. 9527 端口未正确映射 → `docker-compose logs dip` 检查
3. cloudflared 容器未运行 → `docker-compose logs cloudflared` 检查
4. Public Hostname 中 URL 配置不正确 → 确认指向 `192.168.31.185:9527`

### Q: 容器反复重启

A: 检查日志：`docker-compose logs dip`

### Q: 飞牛 Docker 拉取镜像失败

A: 在飞牛 Docker 设置中添加镜像加速源：`https://docker.1ms.run`
