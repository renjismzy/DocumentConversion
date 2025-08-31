#!/bin/bash

# 魔搭云端MCP自动化部署脚本
# 用于构建和部署文档转换MCP服务器

set -e

echo "=== 魔搭云端MCP部署脚本 ==="
echo "开始部署文档转换MCP服务器..."

# 检查必要的工具
command -v docker >/dev/null 2>&1 || { echo "错误: 需要安装Docker" >&2; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "错误: 需要安装kubectl" >&2; exit 1; }

# 设置变量
IMAGE_NAME="mcp-document-converter"
IMAGE_TAG="latest"
REGISTRY="registry.cn-hangzhou.aliyuncs.com/modelscope"
FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "镜像名称: ${FULL_IMAGE_NAME}"

# 构建Docker镜像
echo "步骤 1: 构建Docker镜像..."
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
if [ $? -eq 0 ]; then
    echo "✅ Docker镜像构建成功"
else
    echo "❌ Docker镜像构建失败"
    exit 1
fi

# 标记镜像
echo "步骤 2: 标记镜像..."
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${FULL_IMAGE_NAME}

# 推送镜像到魔搭镜像仓库
echo "步骤 3: 推送镜像到魔搭镜像仓库..."
docker push ${FULL_IMAGE_NAME}
if [ $? -eq 0 ]; then
    echo "✅ 镜像推送成功"
else
    echo "❌ 镜像推送失败"
    exit 1
fi

# 更新部署配置中的镜像名称
echo "步骤 4: 更新部署配置..."
sed -i "s|image: mcp-document-converter:latest|image: ${FULL_IMAGE_NAME}|g" modelscope_deploy.yaml

# 部署到魔搭云端
echo "步骤 5: 部署到魔搭云端..."
kubectl apply -f modelscope_deploy.yaml
if [ $? -eq 0 ]; then
    echo "✅ 部署成功"
else
    echo "❌ 部署失败"
    exit 1
fi

# 等待部署完成
echo "步骤 6: 等待部署完成..."
kubectl rollout status deployment/mcp-document-converter --timeout=300s

# 获取服务状态
echo "步骤 7: 检查服务状态..."
kubectl get pods -l app=mcp-document-converter
kubectl get services mcp-document-converter-service

# 获取外部访问地址
echo "步骤 8: 获取服务访问地址..."
EXTERNAL_IP=$(kubectl get service mcp-document-converter-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
if [ -n "$EXTERNAL_IP" ]; then
    echo "🌐 服务访问地址: http://${EXTERNAL_IP}"
    echo "🏥 健康检查地址: http://${EXTERNAL_IP}/health"
else
    echo "⏳ 外部IP分配中，请稍后查看服务状态"
fi

echo "=== 部署完成 ==="
echo "MCP文档转换服务器已成功部署到魔搭云端！"