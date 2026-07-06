# WeChat_Like_ChatApp

一个基于 **FastAPI + Vue 3 + WebSocket + MySQL** 实现的仿微信聊天应用，支持用户注册/登录、好友管理、实时消息收发、AI 智能分析等功能。

> 本项目为课程/个人学习项目，代码已脱敏，不包含真实的密码、API Key 和服务器地址。

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Vue Router + Axios |
| 后端 | FastAPI + Uvicorn |
| 数据库 | MySQL + SQLAlchemy（异步）|
| 实时通信 | WebSocket |
| AI 能力 | 阿里云通义千问 API |

## 主要功能

- 用户注册与登录（JWT Token 认证）
- 好友添加与好友列表管理
- 实时单聊消息（WebSocket）
- 消息已读/未读状态显示
- 个人资料修改与头像上传
- AI 智能分析（基于通义千问）

## 项目结构

```
.
├── chat_interface/          # Vue 前端项目
│   ├── src/
│   │   ├── config/api.js   # 后端 API 地址配置
│   │   ├── views/          # 页面组件
│   │   └── ...
│   └── ...
├── config/                  # 后端配置文件（数据库等）
├── crud/                    # 数据库增删改查操作
├── models/                  # SQLAlchemy 数据模型
├── router/                  # FastAPI 路由接口
├── schemas/                 # Pydantic 数据校验模型
├── util/                    # 工具函数（JWT、密码加密等）
└── main.py                  # FastAPI 入口文件
```

## 本地运行步骤

### 1. 克隆项目

```bash
git clone https://github.com/Rirking/WeChat_Like_ChatApp.git
cd WeChat_Like_ChatApp
```

### 2. 准备数据库

本地安装 MySQL 并创建数据库：

```sql
CREATE DATABASE property_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 配置后端

修改 `config/db_config.py` 中的数据库连接地址：

```python
ASYNC_MYSQL_DATABASE_URL = "mysql+aiomysql://root:your_password@localhost:3306/property_manager"
```

修改 `router/ai_analys.py` 中的通义千问 API Key：

```python
QWEN_API_KEY = "your_api_key_here"
```

### 4. 安装后端依赖并启动

```bash
# 建议使用虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
python main.py
```

后端默认运行在 `http://127.0.0.1:8000`

### 5. 配置前端

修改 `chat_interface/src/config/api.js`：

```javascript
export const apiConfig = {
  baseURL: 'http://127.0.0.1:8000',
}
```

### 6. 安装前端依赖并启动

```bash
cd chat_interface
npm install
npm run dev
```

前端默认运行在 `http://127.0.0.1:5173`

### 7. 打开浏览器访问

```
http://127.0.0.1:5173
```

## 部署说明

如需部署到服务器，可将前端 `npm run build` 生成的 `dist/` 目录通过 nginx 等 Web 服务器托管，后端使用 uvicorn 启动并配置反向代理。

## 注意

- 本项目中的数据库密码、API Key、服务器 IP 均已替换为占位符，请自行修改。
- 首次运行时，数据表会通过 SQLAlchemy 的 `create_all()` 自动创建。
- 头像上传等静态资源访问，需根据实际部署环境配置静态文件服务。

## License

MIT
