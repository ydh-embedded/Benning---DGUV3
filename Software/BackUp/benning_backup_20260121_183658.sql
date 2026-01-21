-- MySQL dump 10.13  Distrib 8.0.44, for Linux (x86_64)
--
-- Host: localhost    Database: benning_device_manager
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `company_settings`
--

DROP TABLE IF EXISTS `company_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `company_settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `company_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` text COLLATE utf8mb4_unicode_ci,
  `phone` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `logo_path` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `signature_path` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `company_settings`
--

LOCK TABLES `company_settings` WRITE;
/*!40000 ALTER TABLE `company_settings` DISABLE KEYS */;
INSERT INTO `company_settings` VALUES (1,'Musterfirma GmbH','MusterstraÃŸe 123\n12345 Musterstadt','+49 123 456789','info@musterfirma.de',NULL,NULL,'2026-01-21 15:53:43','2026-01-21 15:53:43');
/*!40000 ALTER TABLE `company_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `devices`
--

DROP TABLE IF EXISTS `devices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `devices` (
  `id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `location` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `manufacturer` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `serial_number` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `purchase_date` date DEFAULT NULL,
  `last_inspection` date DEFAULT NULL,
  `next_inspection` date DEFAULT NULL,
  `status` enum('active','inactive','defect') COLLATE utf8mb4_unicode_ci DEFAULT 'active',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devices`
--

LOCK TABLES `devices` WRITE;
/*!40000 ALTER TABLE `devices` DISABLE KEYS */;
INSERT INTO `devices` VALUES ('BENNING-001','Bohrmaschine Makita','Elektrowerkzeug','Werkstatt A','Makita','MK-2024-001','2024-01-15','2024-06-15','2025-06-15','active',NULL,'2026-01-21 15:53:43','2026-01-21 15:53:43'),('BENNING-002','Winkelschleifer Bosch','Elektrowerkzeug','Werkstatt A','Bosch','BS-2024-002','2024-02-20','2024-07-20','2025-07-20','active',NULL,'2026-01-21 15:53:43','2026-01-21 15:53:43'),('BENNING-003','VerlÃ¤ngerungskabel 25m','Kabel','Lager','Brennenstuhl','BR-2023-045','2023-11-10','2024-05-10','2025-05-10','active',NULL,'2026-01-21 15:53:43','2026-01-21 15:53:43'),('BENNING-004','Staubsauger KÃ¤rcher','ReinigungsgerÃ¤t','Werkstatt B','KÃ¤rcher','KA-2024-012','2024-03-05','2024-08-05','2025-08-05','active',NULL,'2026-01-21 15:53:43','2026-01-21 15:53:43'),('BENNING-005','SchweiÃŸgerÃ¤t MIG/MAG','SchweiÃŸtechnik','Werkstatt C','Lorch','LO-2023-089','2023-09-15','2024-03-15','2025-03-15','active',NULL,'2026-01-21 15:53:43','2026-01-21 15:53:43');
/*!40000 ALTER TABLE `devices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inspections`
--

DROP TABLE IF EXISTS `inspections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inspections` (
  `id` int NOT NULL AUTO_INCREMENT,
  `device_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `inspection_date` date NOT NULL,
  `inspector_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `result` enum('passed','failed','conditional') COLLATE utf8mb4_unicode_ci DEFAULT 'passed',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `next_inspection_date` date DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_device_date` (`device_id`,`inspection_date`),
  CONSTRAINT `inspections_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inspections`
--

LOCK TABLES `inspections` WRITE;
/*!40000 ALTER TABLE `inspections` DISABLE KEYS */;
INSERT INTO `inspections` VALUES (1,'BENNING-001','2024-06-15','Max Mustermann','passed','Alle Messwerte im Normbereich','2025-06-15','2026-01-21 15:53:43');
/*!40000 ALTER TABLE `inspections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `measurements`
--

DROP TABLE IF EXISTS `measurements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `measurements` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inspection_id` int NOT NULL,
  `measurement_type` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` decimal(10,3) DEFAULT NULL,
  `unit` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `min_value` decimal(10,3) DEFAULT NULL,
  `max_value` decimal(10,3) DEFAULT NULL,
  `passed` tinyint(1) DEFAULT '1',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_inspection` (`inspection_id`),
  CONSTRAINT `measurements_ibfk_1` FOREIGN KEY (`inspection_id`) REFERENCES `inspections` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `measurements`
--

LOCK TABLES `measurements` WRITE;
/*!40000 ALTER TABLE `measurements` DISABLE KEYS */;
INSERT INTO `measurements` VALUES (1,1,'Isolationswiderstand',50.500,'MÎ©',1.000,NULL,1,NULL,'2026-01-21 15:53:43'),(2,1,'Schutzleiterwiderstand',0.150,'Î©',NULL,0.300,1,NULL,'2026-01-21 15:53:43'),(3,1,'Ableitstrom',0.250,'mA',NULL,0.500,1,NULL,'2026-01-21 15:53:43');
/*!40000 ALTER TABLE `measurements` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-21 17:36:58
