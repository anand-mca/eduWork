<?php
// Database connection details from the image
$servername = "localhost";
$username = "root";
$password = "root";
$database = "eduwork";

// Create connection
$conn = new mysqli($servername, $username, $password, $database);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Get form data
$user = $_POST['username'];
$pass = $_POST['password'];

// Prepare and execute query safely
$sql = "SELECT * FROM login WHERE username = ? AND password = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("ss", $user, $pass);
$stmt->execute();
$result = $stmt->get_result();
$_SESSION['u_id'] = $_POST['username']; // from users table after login


// Check login success
if ($result->num_rows > 0) {
    echo "Login successful! Welcome, " . htmlspecialchars($user);
} else {
    echo "Invalid username or password.";
}

// Close connection
$stmt->close();
$conn->close();
?>
