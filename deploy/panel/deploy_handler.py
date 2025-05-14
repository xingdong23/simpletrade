#!/usr/bin/env python3
"""
简单的部署处理脚本，处理表单提交
"""

import os
import sys
import cgi
import subprocess
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/app/logs/deploy_handler.log',
    filemode='a'
)
logger = logging.getLogger('deploy_handler')

class DeployHandler(BaseHTTPRequestHandler):
    """处理部署请求的HTTP处理器"""

    def do_GET(self):
        """处理GET请求，重定向到部署面板"""
        self.send_response(302)
        self.send_header('Location', '/deploy/')
        self.end_headers()

    def do_POST(self):
        """处理POST请求，执行部署"""
        if self.path == '/deploy/submit':
            # 解析表单数据
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )

            # 获取分支或版本
            branch = form.getvalue('branch')
            version = form.getvalue('version')
            
            # 使用分支或版本，优先使用分支
            deploy_target = branch if branch else version
            
            if not deploy_target:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Error</h1><p>Missing branch or version parameter</p></body></html>')
                return

            # 记录部署请求
            logger.info(f"收到部署请求: {deploy_target}")
            
            try:
                # 执行部署脚本
                deploy_script = '/app/deploy.sh'
                
                # 检查脚本是否存在
                if not os.path.isfile(deploy_script):
                    raise Exception(f"部署脚本不存在: {deploy_script}")
                
                # 异步执行部署脚本
                subprocess.Popen([deploy_script, deploy_target],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
                
                # 返回成功页面
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                success_html = f"""
                <!DOCTYPE html>
                <html lang="zh-CN">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>部署已启动</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                    <meta http-equiv="refresh" content="5;url=/deploy/">
                    <style>
                        body {{ padding-top: 50px; }}
                        .container {{ max-width: 600px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="card">
                            <div class="card-header bg-success text-white">
                                <h4>部署已启动</h4>
                            </div>
                            <div class="card-body">
                                <div class="alert alert-success">
                                    <p><strong>版本 {deploy_target} 的部署已经开始。</strong></p>
                                    <p>部署过程可能需要几分钟时间，请耐心等待。</p>
                                    <p>您将在5秒后自动返回部署面板。</p>
                                </div>
                                <a href="/deploy/" class="btn btn-primary">立即返回</a>
                            </div>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                self.wfile.write(success_html.encode())
                
            except Exception as e:
                logger.error(f"部署错误: {str(e)}")
                
                # 返回错误页面
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                error_html = f"""
                <!DOCTYPE html>
                <html lang="zh-CN">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>部署错误</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                    <meta http-equiv="refresh" content="5;url=/deploy/">
                    <style>
                        body {{ padding-top: 50px; }}
                        .container {{ max-width: 600px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="card">
                            <div class="card-header bg-danger text-white">
                                <h4>部署错误</h4>
                            </div>
                            <div class="card-body">
                                <div class="alert alert-danger">
                                    <p><strong>部署过程中发生错误:</strong></p>
                                    <p>{str(e)}</p>
                                    <p>您将在5秒后自动返回部署面板。</p>
                                </div>
                                <a href="/deploy/" class="btn btn-primary">立即返回</a>
                            </div>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                self.wfile.write(error_html.encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>404 Not Found</h1></body></html>')

def run_server(port=8081):
    """运行HTTP服务器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DeployHandler)
    logger.info(f"部署处理服务器启动在端口 {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
