#!/bin/bash
# Celery Worker 启动脚本

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 启动 ReadPilot Celery Worker"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查 Redis 是否运行
echo "🔴 检查 Redis 连接..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis 未运行!"
    echo "   请先启动 Redis:"
    echo "   - macOS: brew services start redis"
    echo "   - Linux: sudo systemctl start redis"
    echo "   - Docker: docker-compose up -d redis"
    exit 1
fi
echo "✅ Redis 连接正常"
echo ""

# 检查环境变量
echo "📋 检查环境配置..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env 文件不存在，使用 .env.example 的默认值"
fi
echo ""

# 启动 Celery Worker
echo "⚙️  启动参数:"
echo "   - App: app.tasks.celery_app"
echo "   - Log Level: INFO"
echo "   - Concurrency: 4 workers"
echo "   - Task Time Limit: 30 minutes"
echo ""
echo "🛑 按 Ctrl+C 停止 Worker"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 使用 poetry 运行 celery
if command -v poetry &> /dev/null; then
    poetry run celery -A app.tasks.celery_app worker --loglevel=info --concurrency=4
else
    celery -A app.tasks.celery_app worker --loglevel=info --concurrency=4
fi
