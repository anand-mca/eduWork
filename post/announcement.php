<?php
// MySQL connection configuration
$servername = "localhost";
$username = "root";
$password = "root"; // Change if different
$database = "eduwork";

// Create connection
$conn = new mysqli($servername, $username, $password, $database);

// Check connection
if ($conn->connect_error) {
    die("❌ Connection failed: " . $conn->connect_error);
}

// Handle form submission
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Get form values
    $title = $_POST['title'];
    $description = $_POST['description'];

    // Auto-generate current date and time
    $date = date('Y-m-d');
    $time = date('H:i:s');

    // Prepare SQL query
    $stmt = $conn->prepare("INSERT INTO announcement (title, description, date, time) VALUES (?, ?, ?, ?)");
    $stmt->bind_param("ssss", $title, $description, $date, $time);

    // Execute and give feedback
    if ($stmt->execute()) {
        echo "✅ Announcement posted successfully!";
    } else {
        echo "❌ Error: " . $stmt->error;
    }

    // Close resources
    $stmt->close();
    $conn->close();
}
?>
