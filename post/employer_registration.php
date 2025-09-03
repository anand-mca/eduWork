<?php
// Database connection settings
$servername = "localhost";
$username = "root";
$password = "root";  // Change this if your MySQL password is different
$database = "eduwork";

// Create connection
$conn = new mysqli($servername, $username, $password, $database);

// Check for connection errors
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Handle POST request
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Retrieve form data
    $o_name     = $_POST['ownerName'];
    $shop_name  = $_POST['shopName'];
    $category   = $_POST['category'];
    $address    = $_POST['address'];
    $phone_no   = $_POST['phone'];
    $email_id   = $_POST['email'];
    $map_loc    = $_POST['locationLink'];

    // Handle file upload
    $photo_path = "";
    if (isset($_FILES["shopLogo"]) && $_FILES["shopLogo"]["error"] == 0) {
        $upload_dir = "uploads/";

        // Create directory if it doesn't exist
        if (!file_exists($upload_dir)) {
            mkdir($upload_dir, 0777, true);
        }

        $filename = basename($_FILES["shopLogo"]["name"]);
        $photo_path = $upload_dir . time() . "_" . $filename;

        // Move uploaded file to target directory
        if (!move_uploaded_file($_FILES["shopLogo"]["tmp_name"], $photo_path)) {
            echo "Error uploading logo.";
            exit;
        }
    }

    // Prepare SQL statement
    $stmt = $conn->prepare("INSERT INTO employer (o_name, shop_name, category, address, phone_no, email_id, photo, map_loc)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)");

    $stmt->bind_param("ssssssss", $o_name, $shop_name, $category, $address, $phone_no, $email_id, $photo_path, $map_loc);

    // Execute and check result
    if ($stmt->execute()) {
        echo "✅ Employer registration successful. Welcome, " . htmlspecialchars($shop_name) . "!";
    } else {
        echo "❌ Error: " . $stmt->error;
    }

    // Close statement and connection
    $stmt->close();
    $conn->close();
}
?>
