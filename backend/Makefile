# ReadPilot Backend Makefile
# 快捷命令工具

.PHONY: help install dev prod test lint format clean db-init db-migrate db-upgrade

help:
	@echo "ReadPilot Backend - 可用命令:"
	@echo ""
	@echo "  make install     - 安装依赖"
	@echo "  make dev         - 启动开发服务器 (热重载)"
	@echo "  make prod        - 启动生产服务器"
	@echo "  make test        - 运行测试"
	@echo "  make lint        - 代码检查"
	@echo "  make format      - 代码格式化"
	@echo "  make clean       - 清理缓存文件"
	@echo "  make db-init     - 初始化数据库"
	@echo "  make db-migrate  - 创建数据库迁移"
	@echo "  make db-upgrade  - 应用数据库迁移"
	@echo ""

install:
	@echo "📦 安装依赖..."
	pip install -r requirements.txt || poetry install

dev:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "🚀 启动 ReadPilot Backend 开发服务器..."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "📡 服务地址:"
	@echo "   🏠 主页:        http://localhost:8000/"
	@echo "   ❤️  健康检查:    http://localhost:8000/health"
	@echo "   📚 Swagger UI:  http://localhost:8000/docs"
	@echo "   📖 ReDoc:       http://localhost:8000/redoc"
	@echo "   🔧 OpenAPI:     http://localhost:8000/api/v1/openapi.json"
	@echo ""
	@echo "⚡ 热重载已启用 - 代码修改后自动重启"
	@echo "🛑 按 Ctrl+C 停止服务器"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

prod:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "🚀 启动 ReadPilot Backend 生产服务器..."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "📡 服务地址:"
	@echo "   🏠 主页:        http://localhost:8000/"
	@echo "   ❤️  健康检查:    http://localhost:8000/health"
	@echo "   📚 Swagger UI:  http://localhost:8000/docs"
	@echo "   📖 ReDoc:       http://localhost:8000/redoc"
	@echo ""
	@echo "⚙️  Workers: 4"
	@echo "🛑 按 Ctrl+C 停止服务器"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

test:
	@echo "🧪 运行测试..."
	pytest app/tests/ -v

test-watch:
	@echo "🧪 测试监视模式..."
	pytest-watch app/tests/ -v

lint:
	@echo "🔍 代码检查..."
	ruff check app/

format:
	@echo "🎨 代码格式化..."
	ruff format app/
	@echo "✅ 格式化完成!"

type-check:
	@echo "🔍 类型检查..."
	mypy app/

clean:
	@echo "🧹 清理缓存..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ 清理完成!"

db-init:
	@echo "🗄️  初始化数据库..."
	alembic init alembic

db-migrate:
	@echo "🗄️  创建数据库迁移..."
	@read -p "迁移消息: " message; \
	alembic revision --autogenerate -m "$$message"

db-upgrade:
	@echo "⬆️  应用数据库迁移..."
	alembic upgrade head

db-downgrade:
	@echo "⬇️  回滚数据库迁移..."
	alembic downgrade -1

# Docker 相关命令
docker-build:
	@echo "🐳 构建 Docker 镜像..."
	docker build -t readpilot-backend .

docker-run:
	@echo "🐳 运行 Docker 容器..."
	docker run -p 8000:8000 readpilot-backend

docker-compose-up:
	@echo "🐳 启动 Docker Compose..."
	docker-compose up -d

docker-compose-down:
	@echo "🐳 停止 Docker Compose..."
	docker-compose down

# 健康检查
health:
	@echo "❤️  检查服务健康状态..."
	@curl -s http://localhost:8000/health | python3 -m json.tool || echo "❌ 服务未运行"
