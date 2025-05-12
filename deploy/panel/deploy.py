#!/usr/bin/env python3
"""
简单的部署API服务器
"""

import os
import json
import subprocess
import logging
import platform
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

# 检测系统环境
system_info = {
    'system': platform.system(),
    'release': platform.release(),
    'version': platform.version(),
    'machine': platform.machine(),
    'hostname': socket.gethostname()
}

# 检测是否为 CentOS
is_centos = False
if system_info['system'] == 'Linux':
    try:
        with open('/etc/os-release', 'r') as f:
            if 'centos' in f.read().lower():
                is_centos = True
    except:
        pass

# 创建日志目录
os.makedirs('/app/logs', exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/app/logs/deploy_api.log',
    filemode='a'
)
logger = logging.getLogger('deploy_api')

# 记录系统信息
logger.info(f"System info: {system_info}")
logger.info(f"Is CentOS: {is_centos}")

class DeployHandler(BaseHTTPRequestHandler):
    """处理部署请求的HTTP处理器"""

    def do_GET(self):
        """处理GET请求，返回当前版本信息"""
        if self.path == '/api/version':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # 获取当前版本
            try:
                with open('/app/panel/version.txt', 'r') as f:
                    version = f.read().strip()
            except:
                version = 'unknown'

            # 获取部署时间
            try:
                with open('/app/panel/deploy_time.txt', 'r') as f:
                    deploy_time = f.read().strip()
            except:
                deploy_time = 'unknown'

            response = {
                'success': True,
                'version': version,
                'deploy_time': deploy_time
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/api/branches':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            try:
                # 更新远程分支信息
                subprocess.run(['git', 'fetch'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
                
                # 获取所有分支（包括远程分支）
                output = subprocess.check_output(['git', 'branch', '-a']).decode().strip()
                
                branches = []
                for line in output.split('\n'):
                    line = line.strip()
                    # 处理本地分支
                    if line.startswith('*'):
                        # 当前分支，标记为活动
                        branches.append({
                            'name': line[2:].strip(),
                            'active': True,
                            'type': 'local'
                        })
                    elif not line.startswith('remotes/'):
                        # 其他本地分支
                        branches.append({
                            'name': line.strip(),
                            'active': False,
                            'type': 'local'
                        })
                    else:
                        # 远程分支，去除 'remotes/origin/' 前缀
                        remote_branch = line.replace('remotes/origin/', '').strip()
                        # 跳过HEAD引用和已经包含的分支
                        if 'HEAD' not in remote_branch and not any(b['name'] == remote_branch for b in branches):
                            branches.append({
                                'name': remote_branch,
                                'active': False,
                                'type': 'remote'
                            })
                
                # 按名称排序，但将main分支放在最前面
                branches.sort(key=lambda x: (0 if x['name'] == 'main' else 1, x['name']))
                
                response = {
                    'success': True,
                    'branches': branches
                }
            except Exception as e:
                logger.error(f"获取分支列表错误: {str(e)}")
                response = {
                    'success': False,
                    'message': f'获取分支列表失败: {str(e)}'
                }
            
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/api/logs':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # 获取日志文件列表
            logs_dir = '/app/logs'
            log_files = []

            try:
                for file in os.listdir(logs_dir):
                    if file.startswith('deploy_') and file.endswith('.log'):
                        log_files.append(file)
                log_files.sort(reverse=True)  # 最新的日志排在前面
            except Exception as e:
                logger.error(f"获取日志列表错误: {str(e)}")

            response = {
                'success': True,
                'logs': log_files
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path.startswith('/api/logs/'):
            log_file = self.path.split('/api/logs/')[1]
            log_path = os.path.join('/app/logs', log_file)

            # 安全检查，确保只能访问日志目录中的文件
            if not log_file or '..' in log_file or not log_file.startswith('deploy_') or not log_file.endswith('.log'):
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'success': False,
                    'message': '无效的日志文件'
                }
                self.wfile.write(json.dumps(response).encode())
                return

            try:
                with open(log_path, 'r') as f:
                    log_content = f.read()

                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(log_content.encode())
            except Exception as e:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'success': False,
                    'message': f'日志文件不存在或无法读取: {str(e)}'
                }
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'success': False,
                'message': '未找到请求的资源'
            }
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """处理POST请求，执行部署"""
        if self.path == '/api/deploy':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')

            try:
                data = json.loads(post_data)
                version = data.get('version', '')

                # 验证版本
                if not version:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {
                        'success': False,
                        'message': '版本不能为空'
                    }
                    self.wfile.write(json.dumps(response).encode())
                    return

                # 验证版本格式
                import re
                if not re.match(r'^[a-zA-Z0-9_\-\.\/]+$', version):
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {
                        'success': False,
                        'message': '版本格式不正确'
                    }
                    self.wfile.write(json.dumps(response).encode())
                    return

                # 执行部署脚本
                logger.info(f"开始部署版本: {version}")
                deploy_script = '/app/deploy.sh'

                # 异步执行部署脚本
                subprocess.Popen([deploy_script, version],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'success': True,
                    'message': f'部署版本 {version} 已启动，请查看日志获取详细信息'
                }
                self.wfile.write(json.dumps(response).encode())

            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'success': False,
                    'message': '无效的JSON数据'
                }
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                logger.error(f"部署错误: {str(e)}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'success': False,
                    'message': f'部署过程中发生错误: {str(e)}'
                }
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'success': False,
                'message': '未找到请求的资源'
            }
            self.wfile.write(json.dumps(response).encode())

def run_server(port=8080):
    """运行HTTP服务器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DeployHandler)
    logger.info(f"部署API服务器启动在端口 {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
