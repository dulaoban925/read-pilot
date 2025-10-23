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
	@echo "  make diagnose    - 诊断服务状态"
	@echo "  make celery      - 启动 Celery Worker"
	@echo "  make celery-flower - 启动 Celery Flower 监控面板"
	@echo "  make celery-purge - 清空 Celery 任务队列"
	@echo "  make celery-inspect - 查看 Celery Worker 状态"
	@echo "  make celery-stats - 查看 Celery 统计信息"
	@echo ""

install:
	@echo "📦 安装依赖..."
	poetry install

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
	@poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

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
	@echo "🗄️  初始化数据库 (创建所有表)..."
	@python3 -c "import asyncio; from app.db.session import init_db; asyncio.run(init_db())" && echo "✅ 数据库初始化完成!"

db-migrate:
	@echo "🗄️  创建数据库迁移..."
	@read -p "迁移消息: " message; \
	alembic revision --autogenerate -m "$$message"

db-upgrade:
	@echo "⬆️  应用数据库迁移..."
	alembic upgrade head && echo "✅ 迁移完成!"

db-downgrade:
	@echo "⬇️  回滚数据库迁移..."
	alembic downgrade -1 && echo "✅ 回滚完成!"

db-history:
	@echo "📜 查看迁移历史..."
	alembic history

db-current:
	@echo "📍 当前数据库版本..."
	alembic current

db-reset:
	@echo "⚠️  重置数据库 (删除所有数据)..."
	@read -p "确认删除所有数据? [y/N]: " confirm; \
	if [ "$$confirm" = "y" ]; then \
		alembic downgrade base && alembic upgrade head && echo "✅ 数据库已重置!"; \
	else \
		echo "❌ 操作已取消"; \
	fi

# Redis 相关命令
redis-cli:
	@echo "🔴 连接 Redis CLI..."
	redis-cli

redis-ping:
	@echo "🔴 测试 Redis 连接..."
	@redis-cli ping && echo "✅ Redis 连接正常!"

redis-flush:
	@echo "⚠️  清空 Redis 缓存..."
	@read -p "确认清空所有缓存? [y/N]: " confirm; \
	if [ "$$confirm" = "y" ]; then \
		redis-cli FLUSHALL && echo "✅ 缓存已清空!"; \
	else \
		echo "❌ 操作已取消"; \
	fi

# 测试基础设施
test-setup:
	@echo "🧪 测试 Phase 1 基础设施..."
	python3 scripts/test_setup.py

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

# Celery 相关命令
celery:
	@echo "⚙️  启动 Celery Worker..."
	@./start_celery.sh

celery-flower:
	@echo "🌸 启动 Celery Flower 监控面板..."
	@echo "📊 访问地址: http://localhost:5555"
	@poetry run celery -A app.tasks.celery_app flower --port=5555

celery-purge:
	@echo "⚠️  清空 Celery 任务队列..."
	@read -p "确认清空所有待处理任务? [y/N]: " confirm; \
	if [ "$$confirm" = "y" ]; then \
		poetry run celery -A app.tasks.celery_app purge -f && echo "✅ 任务队列已清空!"; \
	else \
		echo "❌ 操作已取消"; \
	fi

celery-inspect:
	@echo "🔍 查看 Celery Worker 状态..."
	@poetry run celery -A app.tasks.celery_app inspect active

celery-stats:
	@echo "📊 查看 Celery 统计信息..."
	@poetry run celery -A app.tasks.celery_app inspect stats

diagnose:
	@echo "🔍 诊断服务状态..."
	@./diagnose.sh
