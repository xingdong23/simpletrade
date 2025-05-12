#!/bin/bash

# 修复前端路由问题的脚本
# 用于修复缺失的AIAnalysisView.vue文件引用

# 设置变量
REPO_DIR="/opt/simpletrade"
ROUTER_FILE="$REPO_DIR/web-frontend/src/router/index.js"

# 显示帮助信息
show_help() {
    echo "SimpleTrade 前端修复脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -f, --fix       修复前端路由问题"
    echo "  -h, --help      显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --fix        # 修复前端路由问题"
    echo ""
}

# 修复前端路由问题
fix_frontend() {
    echo "修复前端路由问题..."
    
    # 检查路由文件是否存在
    if [ ! -f "$ROUTER_FILE" ]; then
        echo "错误: 路由文件不存在: $ROUTER_FILE"
        exit 1
    fi
    
    # 备份原始文件
    cp "$ROUTER_FILE" "$ROUTER_FILE.bak"
    echo "已备份原始文件: $ROUTER_FILE.bak"
    
    # 检查是否包含AIAnalysisView的引用
    if grep -q "AIAnalysisView" "$ROUTER_FILE"; then
        echo "找到AIAnalysisView引用，正在修复..."
        
        # 创建临时文件
        TMP_FILE=$(mktemp)
        
        # 修改路由文件，注释掉AIAnalysisView的引用和路由配置
        cat "$ROUTER_FILE" | sed '/AIAnalysisView/s/^/\/\/ /' > "$TMP_FILE"
        
        # 再次检查是否有包含AIAnalysisView的路由配置
        if grep -q "path.*ai-analysis" "$TMP_FILE"; then
            # 注释掉包含ai-analysis路径的整个路由对象
            awk '
            BEGIN { in_ai_route = 0; ai_route_lines = ""; bracket_count = 0; }
            /path.*ai-analysis/ { in_ai_route = 1; bracket_count = 0; }
            in_ai_route == 1 { 
                ai_route_lines = ai_route_lines $0 "\n"; 
                if ($0 ~ /{/) bracket_count++; 
                if ($0 ~ /}/) bracket_count--; 
                if (bracket_count == 0) in_ai_route = 0; 
                next;
            }
            { print $0; }
            END { 
                if (ai_route_lines != "") {
                    split(ai_route_lines, lines, "\n");
                    for (i in lines) {
                        if (lines[i] != "") print "// " lines[i];
                    }
                }
            }
            ' "$TMP_FILE" > "$TMP_FILE.2"
            mv "$TMP_FILE.2" "$TMP_FILE"
        fi
        
        # 将修改后的内容写回原文件
        mv "$TMP_FILE" "$ROUTER_FILE"
        
        echo "路由文件修复完成。"
    else
        echo "未找到AIAnalysisView引用，无需修复。"
    fi
}

# 处理命令行参数
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

FIX=false

while [ "$1" != "" ]; do
    case $1 in
        -f | --fix )       FIX=true
                          ;;
        -h | --help )     show_help
                          exit 0
                          ;;
        * )               show_help
                          exit 1
    esac
    shift
done

# 执行操作
if [ "$FIX" = true ]; then
    fix_frontend
fi

exit 0
