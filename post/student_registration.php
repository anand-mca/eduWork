<?php
// Database connection configuration
$servername = "localhost";
$username = "root";
$password = "root";
$database = "eduwork";

// Create a connection
$conn = new mysqli($servername, $username, $password, $database);

// Check for connection error
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Handle form submission
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Fetch form values
    $f_name = $_POST['firstName'];
    $l_name = $_POST['lastName'];
    $dob = $_POST['dob'];
    $age = $_POST['age'];
    $gender = $_POST['gender'];
    $address = $_POST['address'];
    $phone_no = $_POST['phone'];
    $email_id = $_POST['email'];

    // Combine skills into a comma-separated string
    $skills = isset($_POST['skills']) ? implode(', ', $_POST['skills']) : '';

    // Handle image upload
    $photo_path = "";
    if (isset($_FILES["profilePicture"]) && $_FILES["profilePicture"]["error"] == 0) {
        $upload_dir = "uploads/";
        if (!file_exists($upload_dir)) {
            mkdir($upload_dir, 0777, true);
        }
        $filename = basename($_FILES["profilePicture"]["name"]);
        $target_file = $upload_dir . time() . "_" . $filename;

        if (move_uploaded_file($_FILES["profilePicture"]["tmp_name"], $target_file)) {
            $photo_path = $target_file;
        } else {
            echo "Failed to upload photo.";
            exit;
        }
    }

    // Prepare SQL query to insert into the student table
    $stmt = $conn->prepare("INSERT INTO student (f_name, l_name, age, skill, dob, gender, address, phone_no, email_id, photo)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");

    // Bind the parameters to the query
    $stmt->bind_param("ssisssssss", $f_name, $l_name, $age, $skills, $dob, $gender, $address, $phone_no, $email_id, $photo_path);

    // Execute the query
    if ($stmt->execute()) {
        echo "✅ Registration successful. Welcome, " . htmlspecialchars($f_name) . "!";
    } else {
        echo "❌ Error: " . $stmt->error;
    }

    // Close statement and connection
    $stmt->close();
    $conn->close();
}
?>
