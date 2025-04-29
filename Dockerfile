FROM python:3.9-slim

# 安装依赖
RUN apt-get update && apt-get install -y \
    imagemagick \
    libmagickwand-dev \
    && rm -rf /var/lib/apt/lists/*

# 配置ImageMagick以支持HEIC和增加资源限制
RUN mkdir -p /etc/ImageMagick-6 && \
    echo '<policymap>\n\
  <policy domain="resource" name="memory" value="512MiB"/>\n\
  <policy domain="resource" name="map" value="512MiB"/>\n\
  <policy domain="resource" name="disk" value="2GiB"/>\n\
  <policy domain="resource" name="width" value="16KP"/>\n\
  <policy domain="resource" name="height" value="16KP"/>\n\
  <policy domain="resource" name="area" value="256MP"/>\n\
  <policy domain="resource" name="time" value="300"/>\n\
  <policy domain="resource" name="thread" value="4" />\n\
  <policy domain="coder" rights="read|write" pattern="HEIC" />\n\
  <policy domain="coder" rights="read|write" pattern="JPEG" />\n\
  <policy domain="coder" rights="read|write" pattern="PNG" />\n\
</policymap>' > /etc/ImageMagick-6/policy.xml

# 为magick命令创建软链接（某些系统上ImageMagick的命令名称不同）
RUN ln -s /usr/bin/convert /usr/bin/magick || true

WORKDIR /app

# 拷贝项目文件
COPY convert_urls_to_images.py /app/
COPY app.py /app/
COPY templates/ /app/templates/

# 创建目录
RUN mkdir -p /app/temp_images
RUN mkdir -p /app/uploads
RUN mkdir -p /app/outputs

# 安装Python依赖
RUN pip install --no-cache-dir pandas requests pillow openpyxl flask

# 暴露端口
EXPOSE 5000

# 设置入口点
CMD ["python", "app.py"] 