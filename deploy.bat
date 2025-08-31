@echo off
REM 魔搭云端MCP自动化部署脚本 (Windows版本)
REM 用于构建和部署文档转换MCP服务器

setlocal enabledelayedexpansion

echo === 魔搭云端MCP部署脚本 ===
echo 开始部署文档转换MCP服务器...

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 需要安装Docker
    exit /b 1
)

REM 检查kubectl是否安装
kubectl version --client >nul 2>&1
if errorlevel 1 (
    echo 错误: 需要安装kubectl
    exit /b 1
)

REM 设置变量
set IMAGE_NAME=mcp-document-converter
set IMAGE_TAG=latest
set REGISTRY=registry.cn-hangzhou.aliyuncs.com/modelscope
set FULL_IMAGE_NAME=%REGISTRY%/%IMAGE_NAME%:%IMAGE_TAG%

echo 镜像名称: %FULL_IMAGE_NAME%

REM 构建Docker镜像
echo 步骤 1: 构建Docker镜像...
docker build -t %IMAGE_NAME%:%IMAGE_TAG% .
if errorlevel 1 (
    echo ❌ Docker镜像构建失败
    exit /b 1
)
echo ✅ Docker镜像构建成功

REM 标记镜像
echo 步骤 2: 标记镜像...
docker tag %IMAGE_NAME%:%IMAGE_TAG% %FULL_IMAGE_NAME%

REM 推送镜像到魔搭镜像仓库
echo 步骤 3: 推送镜像到魔搭镜像仓库...
docker push %FULL_IMAGE_NAME%
if errorlevel 1 (
    echo ❌ 镜像推送失败
    exit /b 1
)
echo ✅ 镜像推送成功

REM 更新部署配置中的镜像名称
echo 步骤 4: 更新部署配置...
powershell -Command "(Get-Content modelscope_deploy.yaml) -replace 'image: mcp-document-converter:latest', 'image: %FULL_IMAGE_NAME%' | Set-Content modelscope_deploy.yaml"

REM 部署到魔搭云端
echo 步骤 5: 部署到魔搭云端...
kubectl apply -f modelscope_deploy.yaml
if errorlevel 1 (
    echo ❌ 部署失败
    exit /b 1
)
echo ✅ 部署成功

REM 等待部署完成
echo 步骤 6: 等待部署完成...
kubectl rollout status deployment/mcp-document-converter --timeout=300s

REM 获取服务状态
echo 步骤 7: 检查服务状态...
kubectl get pods -l app=mcp-document-converter
kubectl get services mcp-document-converter-service

REM 获取外部访问地址
echo 步骤 8: 获取服务访问地址...
for /f "tokens=*" %%i in ('kubectl get service mcp-document-converter-service -o jsonpath="{.status.loadBalancer.ingress[0].ip}"') do set EXTERNAL_IP=%%i

if not "%EXTERNAL_IP%"=="" (
    echo 🌐 服务访问地址: http://%EXTERNAL_IP%
    echo 🏥 健康检查地址: http://%EXTERNAL_IP%/health
) else (
    echo ⏳ 外部IP分配中，请稍后查看服务状态
)

echo === 部署完成 ===
echo MCP文档转换服务器已成功部署到魔搭云端！

pause