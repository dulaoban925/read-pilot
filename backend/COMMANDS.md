# Backend 快捷命令使用指南

类似前端 `package.json` 的 `scripts`，后端也配置了快捷命令系统。

## 🎯 命令对比表

| 功能 | Frontend (pnpm) | Backend (make) | Backend (poetry) |
|------|----------------|----------------|------------------|
| 开发服务器 | `pnpm dev` | `make dev` | `poetry run dev` |
| 生产构建 | `pnpm build` | `make prod` | `poetry run prod` |
| 运行测试 | `pnpm test` | `make test` | `poetry run test` |
| 代码检查 | `pnpm lint` | `make lint` | `poetry run lint` |
| 代码格式化 | `pnpm format` | `make format` | `poetry run format` |
| 安装依赖 | `pnpm install` | `make install` | `poetry install` |
| 清理缓存 | `pnpm clean` | `make clean` | - |

## 🚀 常用命令

### 1. 开发流程

```bash
# 启动开发环境
cd backend
make dev              # 启动后端开发服务器 (http://localhost:8000)

# 或者使用 Poetry
poetry run dev
```

### 2. 测试流程

```bash
# 运行所有测试
make test

# 运行测试并显示覆盖率
pytest app/tests/ --cov=app --cov-report=html

# 监视模式 (文件改动自动重新测试)
make test-watch
```

### 3. 代码质量检查

```bash
# 代码检查 (Ruff)
make lint

# 代码格式化 (Ruff)
make format

# 类型检查 (mypy)
make type-check

# 一次性运行所有检查
make lint && make type-check
```

### 4. 数据库管理

```bash
# 初始化 Alembic (首次使用)
make db-init

# 创建新的数据库迁移
make db-migrate
# 输入迁移消息: "Add user table"

# 应用迁移到数据库
make db-upgrade

# 回滚上一次迁移
make db-downgrade
```

### 5. Docker 部署

```bash
# 构建 Docker 镜像
make docker-build

# 运行 Docker 容器
make docker-run

# 使用 Docker Compose 启动所有服务
make docker-compose-up

# 停止所有服务
make docker-compose-down
```

### 6. 健康检查

```bash
# 检查服务是否正常运行
make health

# 输出示例:
# ❤️  检查服务健康状态...
# {
#     "status": "healthy",
#     "environment": "development",
#     "version": "0.1.0"
# }
```

## 📚 命令详解

### `make dev`
启动开发服务器，启用热重载功能。代码修改后自动重启。

**等同于:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### `make prod`
启动生产服务器，使用 4 个 worker 进程。

**等同于:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### `make test`
运行所有测试用例。

**等同于:**
```bash
pytest app/tests/ -v
```

### `make lint`
使用 Ruff 检查代码规范。

**等同于:**
```bash
ruff check app/
```

### `make format`
使用 Ruff 自动格式化代码。

**等同于:**
```bash
ruff format app/
```

### `make clean`
清理所有 Python 缓存文件。

**清理内容:**
- `__pycache__/` 目录
- `.pytest_cache/` 目录
- `.ruff_cache/` 目录
- `*.pyc` 文件
- `*.egg-info/` 目录

## 🔧 配置文件说明

### 1. `pyproject.toml`
Poetry 配置文件，定义了：
- Python 版本要求
- 项目依赖
- Poetry scripts 映射
- Ruff、mypy、pytest 配置

### 2. `scripts.py`
Python 脚本模块，实现 Poetry scripts 的实际功能。

### 3. `Makefile`
Make 命令配置，提供跨平台的快捷命令。

## 💡 最佳实践

### 1. 推荐使用 Make 命令
Make 命令更简洁，不需要记忆 `poetry run` 前缀。

```bash
# ✅ 推荐
make dev
make test

# ⚠️ 也可以，但更长
poetry run dev
poetry run test
```

### 2. CI/CD 中使用 Poetry
在 CI/CD 管道中，使用 Poetry 命令更明确。

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: poetry run test
```

### 3. 本地开发使用 Make
本地开发时使用 Make 命令更方便快捷。

```bash
# 开发常用命令组合
make dev          # 终端 1: 启动服务器
make test-watch   # 终端 2: 监视测试
```

## 🆚 与 Frontend 对比

### Frontend (package.json)
```json
{
  "scripts": {
    "dev": "next dev --turbopack",
    "build": "next build",
    "start": "next start",
    "test": "vitest",
    "lint": "next lint"
  }
}
```

### Backend (Makefile + pyproject.toml)
```makefile
dev:
    uvicorn app.main:app --reload

test:
    pytest app/tests/ -v

lint:
    ruff check app/
```

**相同点:**
- 提供统一的命令接口
- 简化常用操作
- 团队协作一致性

**不同点:**
- Backend 使用 Make/Poetry 双系统
- Frontend 依赖 package.json
- Backend 命令更灵活可定制

## 📖 扩展阅读

- [Poetry Scripts 文档](https://python-poetry.org/docs/pyproject/#scripts)
- [Make 教程](https://makefiletutorial.com/)
- [Ruff 文档](https://docs.astral.sh/ruff/)
- [Pytest 文档](https://docs.pytest.org/)

## 🆘 常见问题

### Q: Make 命令不工作？
**A:** 确保已安装 Make 工具：
```bash
# macOS/Linux
make --version

# Windows (需要安装 Make for Windows 或使用 WSL)
```

### Q: Poetry scripts 不工作？
**A:** 确保已安装 Poetry 和项目依赖：
```bash
poetry --version
poetry install
```

### Q: 如何添加新命令？
**A:** 同时更新两个文件：

1. `Makefile`:
```makefile
my-command:
    @echo "Running my command..."
    python my_script.py
```

2. `pyproject.toml`:
```toml
[tool.poetry.scripts]
my-command = "scripts:my_command"
```

然后在 `scripts.py` 中实现：
```python
def my_command():
    print("Running my command...")
    # 实现逻辑
```
