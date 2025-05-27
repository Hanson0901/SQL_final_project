<?php
header('Content-Type: application/json; charset=utf-8');
$host = "localhost";
$user = "root";
$password = "1234";
$database = "city";
$link = mysqli_connect($host, $user, $password) or die("無法選擇資料庫");
mysqli_select_db($link, $database);
mysqli_query($link, "SET NAMES 'utf8'");

$list = array();

// 根據 GET 參數設定相關值
if (!empty($_GET['act'])) {
    $action = $_GET['act'];
}
if (!empty($_GET['val'])) {
    $val = $_GET['val'];
}
if (!empty($_GET['val2'])) {
    $val2 = $_GET['val2'];
}
if (!empty($_GET['val3'])) {
    $val3 = $_GET['val3'];
}
if (!empty($_GET['val4'])) {
    $val4 = $_GET['val4'];
}

switch ($action) {
    case 'city':
        $sql = "SELECT * FROM city WHERE 1";
        $result = mysqli_query($link, $sql);
        while ($row = mysqli_fetch_assoc($result)) {
            $list[] = $row;
        }
        break;
    case 'site_id': // 查詢地區資料
        $sql = "SELECT * FROM site WHERE city_id = '$val'";
        $result = mysqli_query($link, $sql);
        while ($row = mysqli_fetch_assoc($result)) {
            $list[] = $row;
        }
        break;
    case 'road': // 查詢道路資料
        $sql = "SELECT * FROM road WHERE site_id = '$val'";
        $result = mysqli_query($link, $sql);
        while ($row = mysqli_fetch_assoc($result)) {
            $list[] = $row;
        }
        break;
    case 'insertcity':
        $sql = "INSERT INTO city VALUES ('$val', '$val2')";
        mysqli_query($link, $sql);
        $list = ["success" => true];
        break;

    case 'insertsite':
        $sql = "INSERT INTO site VALUES ('$val', '$val2', '$val3')";
        mysqli_query($link, $sql);
        $list = ["success" => true];
        break;

    case 'insertroad':
        $sql = "INSERT INTO road VALUES ('$val', '$val2')";
        mysqli_query($link, $sql);
        $list = ["success" => true];
        break;
    case 'updatecity':
        $sql = "UPDATE city SET city_id = '$val2', city = '$val3' WHERE city_id = '$val'";
        $result = mysqli_query($link, $sql);
        $list = ["success" => true];
        break;

    // 更新地區 site 資料表
    case 'updatesite':
        $sql = "UPDATE site SET site_id = '$val2', site = '$val3' WHERE site_id = '$val'";
        mysqli_query($link, $sql);
        $list = ["success" => true];
        break;

    // 更新道路 road 資料表
    case 'updateroad':
        $list = array();
        $sql = "UPDATE road SET site_id = '$val3', road = '$val4' WHERE site_id = '$val' AND road = '$val2'";
        mysqli_query($link, $sql);
        $list = ["success" => true];
        break;
    // 刪除縣市
    case 'deletecity':
        $sql = "DELETE FROM city WHERE city_id = '$val'";
        mysqli_query($link, $sql);
        $list = ["success" => true];
        break;

    // 刪除地區
    case 'deletesite':
        $sql = "DELETE FROM site WHERE site_id = '$val'";
        mysqli_query($link, $sql);
        $list = ["success" => true];
        break;

    // 刪除道路
    case 'deleteroad':
        $list = array();  // 這行其實沒用
        $sql = "DELETE FROM road WHERE site_id = '$val' AND road = '$val2'";
        mysqli_query($link, $sql);
        $list = ["success" => true];
        break;
}


echo json_encode($list);

// mysqli_free_result($result);

mysqli_close($link);

return;
?>