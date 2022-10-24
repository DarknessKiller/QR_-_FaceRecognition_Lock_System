<?php

// Initialize the session
session_start();
 
// Check if the user is logged in, if not then redirect him to login page
if(!isset($_SESSION["loggedin"]) || $_SESSION["loggedin"] !== true){
    header("location: login.php");
    exit;
} else {
require_once "config.php";
$user = "'".htmlspecialchars($_SESSION["username"])."'";

$sql = "SELECT roomKey, checkout_at FROM access WHERE username=$user";
$result = mysqli_query($link, $sql);

if (mysqli_num_rows($result) > 0) {
  // output data of each row
  while($row = mysqli_fetch_array($result)) {
    $roomKey = $row["roomKey"];
    $checkout_at = $row["checkout_at"];
  }
}
}
?>
 
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body{ font: 14px sans-serif; text-align: center; }
    </style>
</head>
<body>
    <h1 class="my-5">Hi, <b><?php echo htmlspecialchars($_SESSION["username"]); ?></b>. Welcome to our Door Lock System.</h1>
    <p>
        <div>
            <?php if (isset($roomKey)) echo "<img src='https://chart.googleapis.com/chart?cht=qr&chl=$roomKey&chs=300x300&chld=L|0' class='qr-code img-thumbnail img-responsive' />". "<p><b>NOTE: </b>Please Checkout Before <b>$checkout_at</b></p>"; else echo "<h1>You do not access!!.</h1>"; ?>
        </div>
        <a href="reset-password.php" class="btn btn-warning">Reset Your Password</a>
        <a href="logout.php" class="btn btn-danger ml-3">Sign Out of Your Account</a>
    </p>
</body>
</html>