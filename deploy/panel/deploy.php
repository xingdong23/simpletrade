<?php
// 简单的部署 API

// 设置响应头
header('Content-Type: application/json');

// 检查请求方法
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => '方法不允许']);
    exit;
}

// 获取请求数据
$data = json_decode(file_get_contents('php://input'), true);
$version = isset($data['version']) ? $data['version'] : '';

// 验证版本
if (empty($version)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => '版本不能为空']);
    exit;
}

// 验证版本格式
if (!preg_match('/^[a-zA-Z0-9_\-\.\/]+$/', $version)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => '版本格式不正确']);
    exit;
}

// 执行部署脚本
$output = [];
$return_var = 0;
exec('/app/deploy.sh ' . escapeshellarg($version) . ' 2>&1', $output, $return_var);

// 返回结果
if ($return_var === 0) {
    echo json_encode([
        'success' => true,
        'message' => '部署成功启动',
        'output' => implode("\n", $output)
    ]);
} else {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => '部署失败',
        'output' => implode("\n", $output)
    ]);
}
?>
