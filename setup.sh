#!/bin/bash

# ReadPilot Setup Script
# This script helps you quickly set up the ReadPilot development environment

set -e

echo "🚀 ReadPilot Setup Script"
echo "========================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo "ℹ️  $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip3."
    exit 1
fi

print_success "pip3 found"

# Step 1: Create .env files
echo ""
echo "📝 Step 1: Setting up environment variables"
echo "-------------------------------------------"

if [ ! -f ".env" ]; then
    cp .env.example .env
    print_success "Created root .env file"
    print_warning "Please edit .env and add your API keys"
else
    print_warning ".env already exists, skipping..."
fi

if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    print_success "Created backend/.env file"
    print_warning "Please edit backend/.env and add your API keys"
else
    print_warning "backend/.env already exists, skipping..."
fi

# Step 2: Create virtual environment
echo ""
echo "🐍 Step 2: Setting up Python virtual environment"
echo "------------------------------------------------"

if [ ! -d "backend/venv" ]; then
    print_info "Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
    print_success "Virtual environment created at backend/venv"
else
    print_warning "Virtual environment already exists, skipping..."
fi

# Step 3: Install dependencies
echo ""
echo "📦 Step 3: Installing Python dependencies"
echo "-----------------------------------------"

print_info "Activating virtual environment and installing packages..."
cd backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ..

print_success "All Python dependencies installed"

# Step 4: Check database
echo ""
echo "🗄️  Step 4: Database setup"
echo "--------------------------"

print_info "Checking PostgreSQL connection..."

# Try to connect to PostgreSQL
if command -v psql &> /dev/null; then
    DB_URL=$(grep "^DATABASE_URL=" backend/.env | cut -d'=' -f2)

    if [ -z "$DB_URL" ]; then
        print_warning "DATABASE_URL not found in backend/.env"
        print_info "Using default: postgresql://postgres:postgres@localhost:5432/readpilot"
    else
        print_success "DATABASE_URL configured: $DB_URL"
    fi

    print_info "Please ensure PostgreSQL is running and the database 'readpilot' exists"
    print_info "To create the database, run: createdb readpilot"
else
    print_warning "psql not found. Please install PostgreSQL or use Docker"
fi

# Step 5: Check vector database
echo ""
echo "🔍 Step 5: Vector database setup"
echo "--------------------------------"

VDB_CHOICE=$(grep "^DEFAULT_LLM_PROVIDER=" backend/.env | cut -d'=' -f2)

if grep -q "^PINECONE_API_KEY=" backend/.env; then
    print_info "Pinecone configuration found"
    print_warning "Make sure to add your Pinecone API key to backend/.env"
fi

if grep -q "^QDRANT_URL=" backend/.env; then
    print_info "Qdrant configuration found"
    print_info "To run Qdrant locally with Docker:"
    echo "    docker run -p 6333:6333 qdrant/qdrant"
fi

# Step 6: Summary
echo ""
echo "✨ Setup complete!"
echo "=================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit configuration files:"
echo "   - Root: .env (project-wide settings)"
echo "   - Backend: backend/.env (detailed backend config)"
echo ""
echo "2. Add your API keys:"
echo "   - OPENAI_API_KEY or ANTHROPIC_API_KEY"
echo "   - PINECONE_API_KEY (if using Pinecone)"
echo "   - SECRET_KEY (generate a random string)"
echo ""
echo "3. Start the database:"
echo "   - PostgreSQL: brew services start postgresql@15"
echo "   - Or use Docker: docker-compose up -d db"
echo ""
echo "4. (Optional) Start vector database:"
echo "   - Qdrant: docker run -p 6333:6333 qdrant/qdrant"
echo "   - Pinecone: Use cloud service (no local setup needed)"
echo ""
echo "5. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "6. Access the API:"
echo "   - API: http://localhost:8000"
echo "   - Swagger UI: http://localhost:8000/docs"
echo "   - ReDoc: http://localhost:8000/redoc"
echo ""
echo "📚 For more information, see:"
echo "   - README.md"
echo "   - PARLANT_AGENT_STRUCTURE.md"
echo "   - backend/README.md"
echo ""
print_success "Happy coding! 🎉"
