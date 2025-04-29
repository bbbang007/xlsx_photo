import os
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
from werkzeug.utils import secure_filename
import tempfile
import shutil
import threading
import time
import uuid
import glob
from convert_urls_to_images import download_and_insert_images

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB

# 确保上传和输出目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# 存储任务进度的字典
tasks = {}

# 最大保留的任务数量
MAX_TASKS = 10

def clean_old_tasks():
    """清理过期任务和文件"""
    global tasks
    
    # 如果任务数超过最大限制，清理最旧的任务
    if len(tasks) > MAX_TASKS:
        # 按开始时间排序
        sorted_tasks = sorted(tasks.items(), key=lambda x: x[1].get('start_time', 0))
        # 保留最新的MAX_TASKS个任务
        tasks_to_remove = sorted_tasks[:-MAX_TASKS]
        
        for task_id, task_info in tasks_to_remove:
            # 删除关联文件
            if 'input_path' in task_info and os.path.exists(task_info['input_path']):
                try:
                    os.remove(task_info['input_path'])
                except:
                    pass
            
            if 'output_path' in task_info and os.path.exists(task_info['output_path']):
                try:
                    os.remove(task_info['output_path'])
                except:
                    pass
            
            # 从任务字典中移除
            if task_id in tasks:
                del tasks[task_id]

def clean_temp_files():
    """清理临时文件"""
    # 清理uploads目录中的旧文件（保留最近1小时的文件）
    current_time = time.time()
    for file_path in glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*')):
        # 如果文件超过1小时，删除它
        if os.path.isfile(file_path) and current_time - os.path.getmtime(file_path) > 3600:
            try:
                os.remove(file_path)
            except:
                pass
    
    # 清理outputs目录中的旧文件（保留最近1小时的文件）
    for file_path in glob.glob(os.path.join(app.config['OUTPUT_FOLDER'], '*')):
        # 如果文件超过1小时，删除它
        if os.path.isfile(file_path) and current_time - os.path.getmtime(file_path) > 3600:
            try:
                os.remove(file_path)
            except:
                pass

def process_file(task_id, input_path, output_path):
    """后台处理文件并更新进度"""
    try:
        # 设置初始进度
        tasks[task_id]['status'] = 'processing'
        tasks[task_id]['progress'] = 0
        
        # 包装回调函数以更新进度
        def progress_callback(current, total, message=''):
            progress = int(current / total * 100) if total > 0 else 0
            tasks[task_id]['progress'] = progress
            tasks[task_id]['message'] = message
            print(f"Task {task_id}: {progress}% - {message}")
        
        # 处理文件
        download_and_insert_images(input_path, output_path, progress_callback)
        
        # 设置完成状态
        tasks[task_id]['status'] = 'completed'
        tasks[task_id]['progress'] = 100
        tasks[task_id]['output_path'] = output_path
        
        # 清理旧任务和临时文件
        clean_old_tasks()
        clean_temp_files()
    except Exception as e:
        # 设置错误状态
        tasks[task_id]['status'] = 'error'
        tasks[task_id]['message'] = str(e)
        print(f"Task {task_id} error: {e}")

@app.route('/')
def index():
    # 每次访问首页时清理旧任务和临时文件
    clean_old_tasks()
    clean_temp_files()
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('没有文件部分')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('未选择文件')
        return redirect(request.url)
    
    if file and file.filename.endswith('.xlsx'):
        # 生成唯一的文件名，避免文件冲突
        timestamp = int(time.time())
        filename = f"{timestamp}_{secure_filename(file.filename)}"
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_filename = f"processed_{filename}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # 保存上传的文件
        file.save(input_path)
        
        # 创建任务ID并开始处理
        task_id = str(uuid.uuid4())
        tasks[task_id] = {
            'status': 'queued',
            'progress': 0,
            'start_time': time.time(),
            'input_path': input_path,
            'filename': output_filename,
            'output_path': output_path  # 预先保存输出路径
        }
        
        # 启动后台线程进行处理
        thread = threading.Thread(target=process_file, args=(task_id, input_path, output_path))
        thread.daemon = True
        thread.start()
        
        # 返回任务ID
        return jsonify({
            'task_id': task_id,
            'status': 'queued'
        })
    else:
        flash('仅支持.xlsx文件')
        return redirect(url_for('index'))

@app.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    if task_id not in tasks:
        return jsonify({'status': 'not_found'}), 404
    
    task = tasks[task_id]
    result = {
        'status': task['status'],
        'progress': task['progress']
    }
    
    if 'message' in task:
        result['message'] = task['message']
    
    # 如果任务完成，添加下载链接
    if task['status'] == 'completed':
        result['download_url'] = url_for('download_file', task_id=task_id)
    
    return jsonify(result)

@app.route('/download/<task_id>', methods=['GET'])
def download_file(task_id):
    """下载处理完成的文件"""
    if task_id not in tasks or tasks[task_id]['status'] != 'completed':
        flash('文件未找到或处理未完成')
        return redirect(url_for('index'))
    
    output_path = tasks[task_id]['output_path']
    filename = tasks[task_id]['filename']
    
    return send_file(output_path, as_attachment=True, download_name=filename)

@app.route('/health')
def health_check():
    return 'Service is healthy', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 