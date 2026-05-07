# Image Bed Hosting

个人局域网图床服务，支持图片上传、缩略图自动生成、直链与 Markdown 链接复制、表格化图片管理。  
后端基于 FastAPI，前端使用 Bootstrap 5 + jQuery，无需额外构建工具。

## 功能

- 管理员密码登录（JWT 鉴权）
- 图片上传（限制 10MB，自动生成 300×300 缩略图）
- 原图与缩略图分开存储
- 表格化管理：缩略图预览、文件名、大小、上传时间
- 一键复制图片直链或 Markdown 链接
- 一键下载原图
- 删除图片（同时移除文件与数据库记录）
- 响应式管理界面，移动端友好
- 支持局域网内任意设备访问

## 技术栈

| 层面 | 技术 |
|------|------|
| 后端框架 | FastAPI（Python 3.12+） |
| 数据库 | SQLite（SQLAlchemy ORM） |
| 认证 | JWT + bcrypt |
| 图片处理 | Pillow（PIL） |
| 前端 | Bootstrap 5 + jQuery 3 |
| 部署 | Uvicorn + Systemd（可选） |

## 项目结构

```text
image-bed-hosting/
├── app/ # 后端核心代码
│ ├── init.py
│ ├── main.py # FastAPI 应用入口
│ ├── database.py # 数据库连接
│ ├── models.py # 数据模型
│ ├── crud.py # CRUD 操作
│ ├── auth.py # 认证与 JWT
│ └── utils.py # 图片处理、文件保存
├── uploads/ # 文件存储（自动生成）
│ ├── originals/ # 原图
│ └── thumbnails/ # 缩略图
├── static/ # 前端静态文件
│ ├── index.html # 管理界面
│ ├── css/
│ │ └── style.css # 自定义样式
│ └── js/
│ └── app.js # 前端交互逻辑
├── .env # 环境变量（需自行创建）
├── requirements.txt # Python 依赖
└── README.md
```
## 环境要求

- Python 3.12+
- 操作系统：Linux (Ubuntu 24.04 测试通过)，其他 Linux 发行版同理
- 如需在 Windows 虚拟化环境运行，建议使用 VMware/VirtualBox + NAT/桥接网络

## 安装与运行

### 1. 克隆项目

```bash
git clone https://github.com/yourname/image-bed-hosting.git
cd image-bed-hosting
```

2. 创建虚拟环境

python3 -m venv venv
source venv/bin/activate

3. 安装依赖 
```
pip install -r requirements.txt
或者也可以使用 uv
uv pip install -r requirements.txt
若安装 bcrypt 时报错，请先降级：pip install bcrypt==3.2.2
或安装编译依赖：sudo apt install build-essential python3-dev libffi-dev
```
4. 配置环境变量
```
复制示例配置文件（首次使用需创建）：

cp .env.example .env

编辑 .env 文件，修改管理员密码和密钥：
ADMIN_PASSWORD=your_admin_password
SECRET_KEY=your_random_secret_key
DATABASE_URL=sqlite:///./image_hosting.db
UPLOAD_DIR=uploads/originals
THUMB_DIR=uploads/thumbnails
MAX_FILE_SIZE_MB=10
```

注意：SECRET_KEY 请使用随机字符串，用于 JWT 签名。

5. 初始化数据库
首次运行时数据库会自动创建，也可以手动触发：

```
python -c "from app.database import engine, Base; import app.models; Base.metadata.create_all(bind=engine)"
```

6. 启动服务
开发模式（热重载）：

```
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

生产模式（通过 systemd 或 supervisor 守护）：

```
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

7. 访问

在浏览器中访问 http://<虚拟机IP>:8000
默认用户名 admin，密码为你设置的 ADMIN_PASSWORD。

使用说明
登录
输入密码后获得管理权限。

上传图片
点击“选择文件”，只允许图片格式，文件大小不超过 10MB。上传成功后自动生成缩略图，并可立即复制直链或 Markdown 链接。

图片列表
表格展示所有已上传图片，包含缩略图、原始文件名、文件大小、上传时间。支持的操作：

复制 URL：复制图片直链（以 /uploads/originals/... 开头）

复制 Markdown：复制完整 Markdown 图片语法，已包含域名

下载：下载原始图片文件

删除：从服务器和数据库中删除图片

局域网内静态博客引用
在你的 Markdown 文档中直接粘贴生成的图片链接（例如）：

text
![示例图片](http://192.168.18.10:8000/uploads/originals/abc123.png)
只要虚拟机处于运行状态，同局域网设备均可正常加载图片。

后期公网访问（可选）
若需从外网访问，可选择：

内网穿透：使用 frp、ngrok、Cloudflare Tunnel 等

端口映射：路由器设置端口转发，绑定动态域名

请自行调整安全策略（如添加 HTTPS 反向代理、限制 IP 等）。

常见问题
Q：上传按钮没有反应？
A：检查浏览器控制台是否有报错，确认后端服务正在运行且端口未被防火墙拦截。

Q：缩略图显示为原图？
A：通常是因为原图尺寸小于 300x300，此时缩略图与原图相同。可上传大图测试。

Q：bcrypt 相关错误？
A：降级 bcrypt 到 3.2.2 或参考 passlib 文档 切换后端。

Q：SQLite 数据库文件在哪里？
A：默认在项目根目录，文件名为 image_hosting.db。

License: MIT
