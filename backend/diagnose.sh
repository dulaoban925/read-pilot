#!/bin/bash
# ReadPilot 文档处理诊断工具
# 检查文档处理流程所需的所有服务和配置

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 ReadPilot 文档处理诊断工具"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查计数
PASSED=0
FAILED=0
WARNINGS=0

# 检查函数
check_service() {
    local name=$1
    local command=$2

    echo -n "  检查 $name... "

    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 正常${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ 未运行${NC}"
        ((FAILED++))
        return 1
    fi
}

check_file() {
    local name=$1
    local file=$2

    echo -n "  检查 $name... "

    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ 存在${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ 不存在${NC}"
        ((FAILED++))
        return 1
    fi
}

check_env_var() {
    local name=$1
    local var=$2

    echo -n "  检查 $name... "

    if [ -n "$var" ]; then
        echo -e "${GREEN}✓ 已配置${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${YELLOW}⚠ 未配置${NC}"
        ((WARNINGS++))
        return 1
    fi
}

# 1. 检查环境文件
echo "📋 1. 环境配置"
check_file ".env 文件" ".env"
echo ""

# 2. 检查 Redis
echo "🔴 2. Redis (消息队列)"
if check_service "Redis 连接" "redis-cli ping"; then
    echo "     Redis URL: redis://localhost:6379/0"

    # 检查队列长度
    QUEUE_LENGTH=$(redis-cli LLEN celery 2>/dev/null || echo "0")
    echo "     待处理任务数: $QUEUE_LENGTH"
else
    echo -e "     ${RED}⚠ Redis 未运行! 文档处理需要 Redis${NC}"
    echo "     启动方式:"
    echo "       macOS: brew services start redis"
    echo "       Linux: sudo systemctl start redis"
    echo "       Docker: docker-compose up -d redis"
fi
echo ""

# 3. 检查数据库
echo "🗄️  3. 数据库"
check_file "数据库文件" "readpilot.db"
echo ""

# 4. 检查 AI API 配置
echo "🤖 4. AI 服务配置"
if [ -f ".env" ] && grep -q "OPENAI_API_KEY=" .env && ! grep -q "OPENAI_API_KEY=$" .env && ! grep -q "OPENAI_API_KEY=your-" .env; then
    echo -e "  检查 OpenAI API Key... ${GREEN}✓ 已配置${NC}"
    ((PASSED++))
else
    echo -e "  检查 OpenAI API Key... ${YELLOW}⚠ 未配置${NC}"
    ((WARNINGS++))
fi
echo ""

# 5. 检查存储目录
echo "📁 5. 文件存储"
UPLOAD_DIR=${UPLOAD_DIR:-./data/documents}
CHROMADB_PATH=${CHROMADB_PATH:-./data/chromadb}

echo -n "  检查上传目录... "
if [ -d "$UPLOAD_DIR" ]; then
    echo -e "${GREEN}✓ $UPLOAD_DIR${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ 不存在,将自动创建${NC}"
    mkdir -p "$UPLOAD_DIR" 2>/dev/null || true
    ((WARNINGS++))
fi

echo -n "  检查向量数据库目录... "
if [ -d "$CHROMADB_PATH" ]; then
    echo -e "${GREEN}✓ $CHROMADB_PATH${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ 不存在,将自动创建${NC}"
    mkdir -p "$CHROMADB_PATH" 2>/dev/null || true
    ((WARNINGS++))
fi
echo ""

# 6. 检查 Celery Worker
echo "⚙️  6. Celery Worker"
echo -n "  检查 Celery Worker... "

# 尝试检查 Celery worker 是否运行
if command -v poetry &> /dev/null; then
    CELERY_CMD="poetry run celery"
else
    CELERY_CMD="celery"
fi

if $CELERY_CMD -A app.tasks.celery_app inspect active > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 运行中${NC}"
    ((PASSED++))

    # 显示活跃任务
    ACTIVE_TASKS=$($CELERY_CMD -A app.tasks.celery_app inspect active 2>/dev/null | grep -c "process_document\|generate_embeddings\|generate_summary" || echo "0")
    echo "     活跃任务数: $ACTIVE_TASKS"
else
    echo -e "${RED}✗ 未运行${NC}"
    ((FAILED++))
    echo -e "     ${RED}⚠ Celery Worker 未运行! 文档将无法处理${NC}"
    echo "     启动方式:"
    echo "       make celery"
    echo "       或: ./start_celery.sh"
fi
echo ""

# 7. 检查 FastAPI 后端
echo "🚀 7. FastAPI 后端"
check_service "API 服务" "curl -s http://localhost:8000/health" || true
echo ""

# 8. 检查 Python 依赖
echo "📦 8. Python 依赖"
check_service "Celery 安装" "python3 -c 'import celery'"
check_service "OpenAI SDK" "python3 -c 'import openai'"
check_service "ChromaDB" "python3 -c 'import chromadb'"
echo ""

# 总结
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 诊断结果"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "  ${GREEN}✓ 通过: $PASSED${NC}"
echo -e "  ${RED}✗ 失败: $FAILED${NC}"
echo -e "  ${YELLOW}⚠ 警告: $WARNINGS${NC}"
echo ""

# 提供建议
if [ $FAILED -gt 0 ]; then
    echo "⚠️  发现问题! 请按以下步骤修复:"
    echo ""

    # Redis 未运行
    if ! redis-cli ping > /dev/null 2>&1; then
        echo "  1. 启动 Redis:"
        echo "     cd /Users/anker/Documents/SelfWorkspace/ReadPilot"
        echo "     brew services start redis  # macOS"
        echo ""
    fi

    # Celery 未运行
    if ! $CELERY_CMD -A app.tasks.celery_app inspect active > /dev/null 2>&1; then
        echo "  2. 启动 Celery Worker:"
        echo "     cd /Users/anker/Documents/SelfWorkspace/ReadPilot/backend"
        echo "     make celery"
        echo ""
    fi

    # API 未运行
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "  3. 启动 FastAPI 后端:"
        echo "     cd /Users/anker/Documents/SelfWorkspace/ReadPilot/backend"
        echo "     make dev"
        echo ""
    fi

    echo "  4. 重新运行诊断:"
    echo "     ./diagnose.sh"
    echo ""
else
    echo "✅ 所有核心服务运行正常!"
    echo ""
    echo "📝 文档处理流程:"
    echo "  1. 用户上传文档 → API 创建记录 (status: pending)"
    echo "  2. Celery 处理文档 → 解析、分块 (status: processing → completed)"
    echo "  3. Celery 生成 embedding → 向量化 (is_indexed: true)"
    echo "  4. 用户可以生成摘要和问答"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 更多信息请查看: backend/CELERY_GUIDE.md"
echo ""
