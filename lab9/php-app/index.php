<?php
$mysqli = new mysqli("mysql", "appuser", "apppass", "appdb");

if ($mysqli->connect_error) {
    die("Connexion échouée : " . $mysqli->connect_error);
}

echo "<h2>Connexion réussie à MySQL via Docker Compose !</h2>";
?>

