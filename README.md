# HEIC链接转图片服务

这个服务可以将Excel文件中的HEIC图片链接下载并转换为图片，然后插入到Excel文件中。提供了友好的Web界面，支持实时进度显示和高质量图片处理。

## 功能特点

- 支持HEIC图片链接转换
- 提供Web界面上传Excel文件
- 实时显示处理进度
- 高质量图片处理
- 自动调整图片尺寸以适应Excel

## 前提条件

- Docker
- Docker Compose

## 快速部署

### 自动部署（推荐）

1. 克隆项目并进入目录
2. 运行部署脚本：

```bash
./deploy.sh
```

3. 访问Web界面：http://服务器IP:5010

### 手动部署

1. 确保已安装Docker和Docker Compose
2. 创建必要目录：

```bash
mkdir -p data uploads outputs
```

3. 构建并启动服务：

```bash
docker-compose up -d --build
```

4. 访问Web界面：http://服务器IP:5010

## 使用方法

1. 在Web界面上传包含HEIC链接的Excel文件
2. 等待处理完成（实时显示进度）
3. 处理完成后自动下载结果文件

## 服务管理

```bash
# 查看服务日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart
```

## 高级配置

### 端口修改

如需修改服务端口，编辑`docker-compose.yml`文件，修改端口映射：

```yaml
ports:
  - "你的端口:5000"
```

### HTTPS配置

对于生产环境，建议使用Nginx作为反向代理，并配置SSL证书。

## 故障排除

- 如果图片转换失败，检查HEIC链接是否可公开访问
- 确保服务器具有足够的内存和磁盘空间
- 对于大文件处理，可能需要调整超时设置

## 注意事项

- 确保Excel文件中的HEIC链接可以公开访问
- 默认图片最大宽度为300像素，可根据需要调整
- 处理完成后，临时文件会被自动清理 