<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST');
header('Access-Control-Allow-Headers: Content-Type');

$databaseFile = 'database.json';

// Đọc dữ liệu
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (file_exists($databaseFile)) {
        $data = json_decode(file_get_contents($databaseFile), true);
        echo json_encode($data);
    } else {
        echo json_encode(['error' => 'Database not found']);
    }
}

// Ghi dữ liệu
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if ($input) {
        $result = file_put_contents($databaseFile, json_encode($input, JSON_PRETTY_PRINT));
        if ($result === false) {
            echo json_encode([
                'error' => 'Failed to write to database',
                'details' => error_get_last()
            ]);
        } else {
            echo json_encode(['success' => true]);
        }
    } else {
        echo json_encode([
            'error' => 'Invalid data',
            'details' => json_last_error_msg()
        ]);
    }
}
?> 