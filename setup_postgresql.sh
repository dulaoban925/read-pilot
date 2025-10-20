#!/bin/bash

# ReadPilot PostgreSQL 完整安装和初始化脚本
# 支持: macOS (Homebrew) 和 Linux (apt)
# 用途: 从零开始安装PostgreSQL、创建数据库、初始化表结构

set -e  # Exit on error

echo "🚀 ReadPilot PostgreSQL 完整初始化"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检测操作系统
OS="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo -e "${BLUE}🖥️  检测到操作系统: macOS${NC}"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo -e "${BLUE}🖥️  检测到操作系统: Linux${NC}"
else
    echo -e "${RED}❌ 不支持的操作系统: $OSTYPE${NC}"
    exit 1
fi

echo ""

# Step 1: 检查并安装PostgreSQL
echo "📦 Step 1: 检查PostgreSQL安装..."

if command -v psql &> /dev/null; then
    PSQL_VERSION=$(psql --version)
    echo -e "${GREEN}✅ PostgreSQL已安装: $PSQL_VERSION${NC}"
elif [[ "$OS" == "macos" ]] && [[ -f "/opt/homebrew/opt/postgresql@15/bin/psql" ]]; then
    PSQL_VERSION=$(/opt/homebrew/opt/postgresql@15/bin/psql --version)
    echo -e "${GREEN}✅ PostgreSQL已安装: $PSQL_VERSION${NC}"
    echo -e "${YELLOW}⚠️  建议将PostgreSQL添加到PATH:${NC}"
    echo '   echo '\''export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"'\'' >> ~/.zshrc'
    echo '   source ~/.zshrc'
    # 临时添加到当前session的PATH
    export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
else
    echo -e "${YELLOW}⚠️  PostgreSQL未安装，开始安装...${NC}"

    if [[ "$OS" == "macos" ]]; then
        echo "   使用Homebrew安装PostgreSQL 15..."
        brew install postgresql@15
        export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
        echo -e "${GREEN}✅ PostgreSQL 15 安装完成${NC}"
    elif [[ "$OS" == "linux" ]]; then
        echo "   使用apt安装PostgreSQL 15..."
        sudo apt update
        sudo apt install -y postgresql-15 postgresql-contrib-15
        echo -e "${GREEN}✅ PostgreSQL 15 安装完成${NC}"
    fi
fi

# Step 2: 启动PostgreSQL服务
echo ""
echo "🔄 Step 2: 启动PostgreSQL服务..."

if [[ "$OS" == "macos" ]]; then
    if brew services list | grep postgresql@15 | grep started > /dev/null; then
        echo -e "${GREEN}✅ PostgreSQL服务已运行${NC}"
    else
        brew services start postgresql@15
        echo -e "${GREEN}✅ PostgreSQL服务已启动${NC}"
        echo "   等待服务就绪..."
        sleep 3
    fi
elif [[ "$OS" == "linux" ]]; then
    if sudo systemctl is-active --quiet postgresql; then
        echo -e "${GREEN}✅ PostgreSQL服务已运行${NC}"
    else
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
        echo -e "${GREEN}✅ PostgreSQL服务已启动${NC}"
        sleep 2
    fi
fi

# Step 3: 安装Python依赖
echo ""
echo "📦 Step 3: 安装Python数据库依赖..."

if [[ ! -d "backend/venv" ]]; then
    echo -e "${YELLOW}⚠️  虚拟环境不存在，请先创建:${NC}"
    echo "   cd backend && python3 -m venv venv"
    exit 1
fi

cd backend
source venv/bin/activate

echo "   安装asyncpg, pgvector, greenlet..."
pip install asyncpg pgvector greenlet -q
echo -e "${GREEN}✅ Python依赖安装完成${NC}"

cd ..

# Step 4: 创建数据库
echo ""
echo "🗄️  Step 4: 创建readpilot数据库..."

USERNAME=$(whoami)
if [[ "$OS" == "linux" ]]; then
    # Linux通常使用postgres用户
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw readpilot; then
        echo -e "${YELLOW}⚠️  数据库'readpilot'已存在${NC}"
    else
        sudo -u postgres createdb readpilot
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE readpilot TO $USERNAME;" || true
        echo -e "${GREEN}✅ 数据库'readpilot'创建成功${NC}"
    fi
else
    # macOS
    if psql -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw readpilot; then
        echo -e "${YELLOW}⚠️  数据库'readpilot'已存在${NC}"
    else
        createdb readpilot
        echo -e "${GREEN}✅ 数据库'readpilot'创建成功${NC}"
    fi
fi

# Step 5: 安装pgvector扩展
echo ""
echo "📦 Step 5: 安装pgvector扩展..."

# 先尝试安装pgvector包 (如果未安装)
if [[ "$OS" == "macos" ]]; then
    if ! brew list pgvector &>/dev/null; then
        echo "   使用Homebrew安装pgvector..."
        brew install pgvector || echo -e "${YELLOW}⚠️  pgvector安装失败，可稍后手动安装${NC}"
    fi
elif [[ "$OS" == "linux" ]]; then
    if ! dpkg -l | grep -q postgresql-15-pgvector; then
        echo "   使用apt安装pgvector..."
        sudo apt install -y postgresql-15-pgvector || echo -e "${YELLOW}⚠️  pgvector安装失败，可稍后手动安装${NC}"
    fi
fi

# 在数据库中启用pgvector扩展
if [[ "$OS" == "linux" ]]; then
    sudo -u postgres psql readpilot -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null && \
        echo -e "${GREEN}✅ pgvector扩展已启用${NC}" || \
        echo -e "${YELLOW}⚠️  pgvector扩展不可用 (可选功能，用于向量搜索)${NC}"
else
    psql readpilot -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null && \
        echo -e "${GREEN}✅ pgvector扩展已启用${NC}" || \
        echo -e "${YELLOW}⚠️  pgvector扩展不可用 (可选功能，用于向量搜索)${NC}"
fi

# Step 6: 配置.env文件
echo ""
echo "⚙️  Step 6: 配置.env文件..."
ENV_FILE="backend/.env"

if [[ "$OS" == "linux" ]]; then
    # Linux通常需要密码
    DB_USER="postgres"
    echo -e "${YELLOW}⚠️  Linux环境，请在.env中配置数据库密码${NC}"
    NEW_DB_URL="DATABASE_URL=postgresql+asyncpg://$DB_USER:YOUR_PASSWORD@localhost:5432/readpilot"
else
    # macOS通常不需要密码
    DB_USER=$(whoami)
    NEW_DB_URL="DATABASE_URL=postgresql+asyncpg://$DB_USER@localhost:5432/readpilot"
fi

if [ -f "$ENV_FILE" ]; then
    # 备份.env
    cp "$ENV_FILE" "$ENV_FILE.backup"

    # 更新DATABASE_URL
    if grep -q "^DATABASE_URL=" "$ENV_FILE"; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^DATABASE_URL=.*|$NEW_DB_URL|" "$ENV_FILE"
        else
            sed -i "s|^DATABASE_URL=.*|$NEW_DB_URL|" "$ENV_FILE"
        fi
    else
        echo "" >> "$ENV_FILE"
        echo "$NEW_DB_URL" >> "$ENV_FILE"
    fi

    echo -e "${GREEN}✅ .env已更新 (备份保存为.env.backup)${NC}"
    echo "   连接字符串: postgresql://$DB_USER@localhost:5432/readpilot"
else
    echo -e "${YELLOW}⚠️  .env文件不存在，正在创建...${NC}"
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example "$ENV_FILE"
    else
        touch "$ENV_FILE"
    fi
    echo "$NEW_DB_URL" >> "$ENV_FILE"
    echo -e "${GREEN}✅ .env已创建${NC}"
fi

# Step 7: 初始化数据库表
echo ""
echo "🔨 Step 7: 初始化数据库表..."

# 优先使用SQL脚本
if [ -f "backend/scripts/init_schema.sql" ]; then
    echo "   使用SQL脚本初始化..."
    if [[ "$OS" == "linux" ]]; then
        sudo -u postgres psql readpilot < backend/scripts/init_schema.sql > /dev/null 2>&1 && \
            echo -e "${GREEN}✅ 数据库表初始化成功${NC}" || \
            echo -e "${RED}❌ SQL初始化失败，尝试Python脚本...${NC}"
    else
        psql readpilot < backend/scripts/init_schema.sql > /dev/null 2>&1 && \
            echo -e "${GREEN}✅ 数据库表初始化成功${NC}" || \
            echo -e "${RED}❌ SQL初始化失败，尝试Python脚本...${NC}"
    fi
fi

# 如果SQL失败，使用Python脚本
if [ -f "backend/scripts/init_db_simple.py" ]; then
    echo "   使用Python脚本初始化..."
    cd backend
    source venv/bin/activate
    python scripts/init_db_simple.py && \
        echo -e "${GREEN}✅ 数据库表初始化成功${NC}" || \
        echo -e "${RED}❌ 数据库初始化失败${NC}"
    cd ..
fi

# Step 8: 测试连接
echo ""
echo "🧪 Step 8: 测试数据库连接..."

# 测试表是否创建成功
EXPECTED_TABLES=("users" "documents" "document_chunks" "sessions" "messages")
TABLES_OK=true

for table in "${EXPECTED_TABLES[@]}"; do
    if [[ "$OS" == "linux" ]]; then
        if ! sudo -u postgres psql readpilot -c "\dt $table" 2>/dev/null | grep -q "$table"; then
            echo -e "${RED}   ❌ 表 $table 不存在${NC}"
            TABLES_OK=false
        fi
    else
        if ! psql readpilot -c "\dt $table" 2>/dev/null | grep -q "$table"; then
            echo -e "${RED}   ❌ 表 $table 不存在${NC}"
            TABLES_OK=false
        fi
    fi
done

if [ "$TABLES_OK" = true ]; then
    echo -e "${GREEN}✅ 所有数据表验证成功${NC}"
else
    echo -e "${YELLOW}⚠️  部分表创建失败，请检查日志${NC}"
fi

# Summary
echo ""
echo "===================================="
echo -e "${GREEN}✅ PostgreSQL完整初始化完成！${NC}"
echo ""
echo "📋 下一步操作:"
echo "   1. 启动后端服务器:"
echo "      cd backend"
echo "      source venv/bin/activate"
echo "      python main.py"
echo ""
echo "   2. 访问API文档:"
echo "      http://localhost:8000/docs"
echo ""
echo "   3. 测试健康检查:"
echo "      curl http://localhost:8000/health"
echo ""
echo "📝 数据库信息:"
echo "   - 数据库名: readpilot"
echo "   - 主机: localhost:5432"
echo "   - 用户: $DB_USER"
echo "   - 连接测试: psql readpilot"
echo ""
echo "📊 已创建的表:"
echo "   - users (用户表)"
echo "   - documents (文档表)"
echo "   - document_chunks (文档分块表)"
echo "   - sessions (会话表)"
echo "   - messages (消息表)"
echo ""
echo "🔧 常用命令:"
echo "   - 查看所有表: psql readpilot -c '\dt'"
echo "   - 查看表结构: psql readpilot -c '\d table_name'"
echo "   - 查看扩展: psql readpilot -c '\dx'"
echo "   - 备份数据库: pg_dump readpilot > backup.sql"
echo ""
