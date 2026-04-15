#!/bin/bash
# 测试运行脚本

echo "================================="
echo "天主教教籍管理系统 - 测试套件"
echo "================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 pytest 是否安装
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}错误: pytest 未安装${NC}"
    echo "请运行: pip install pytest pytest-cov"
    exit 1
fi

# 显示环境信息
echo -e "${YELLOW}运行环境:${NC}"
echo "Python: $(python3 --version)"
echo "pytest: $(pytest --version)"
echo "工作目录: $(pwd)"
echo ""

# 默认参数
TEST_PATH="tests/"
MARKERS=""
VERBOSE="-v"
COVERAGE=""

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            MARKERS="-m unit"
            echo -e "${GREEN}运行单元测试${NC}"
            shift
            ;;
        --integration)
            MARKERS="-m integration"
            echo -e "${GREEN}运行集成测试${NC}"
            shift
            ;;
        --no-gui)
            MARKERS="-m 'not gui'"
            echo -e "${GREEN}跳过 GUI 测试${NC}"
            shift
            ;;
        --coverage)
            COVERAGE="--cov=src --cov-report=html --cov-report=term"
            echo -e "${GREEN}生成覆盖率报告${NC}"
            shift
            ;;
        --fast)
            VERBOSE=""
            echo -e "${GREEN}快速模式（无详细输出）${NC}"
            shift
            ;;
        *)
            TEST_PATH="$1"
            shift
            ;;
    esac
done

echo ""
echo -e "${YELLOW}测试配置:${NC}"
echo "测试路径: $TEST_PATH"
echo "标记过滤: ${MARKERS:-无}"
echo "详细输出: ${VERBOSE:-否}"
echo "覆盖率: ${COVERAGE:-否}"
echo ""

# 设置 PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 运行测试
echo -e "${YELLOW}开始测试...${NC}"
echo "================================="

pytest $TEST_PATH $MARKERS $VERBOSE $COVERAGE --tb=short

# 检查测试结果
TEST_RESULT=$?

echo ""
echo "================================="
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过${NC}"
else
    echo -e "${RED}✗ 测试失败${NC}"
fi
echo "================================="

# 如果生成了覆盖率报告，显示路径
if [ ! -z "$COVERAGE" ]; then
    echo ""
    echo -e "${YELLOW}覆盖率报告已生成:${NC}"
    echo "  HTML: htmlcov/index.html"
    echo "  查看: open htmlcov/index.html  (macOS)"
    echo "      : xdg-open htmlcov/index.html  (Linux)"
fi

exit $TEST_RESULT
