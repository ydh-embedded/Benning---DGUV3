-- MySQL dump 10.13  Distrib 8.0.45, for Linux (x86_64)
--
-- Host: localhost    Database: miro_db
-- ------------------------------------------------------
-- Server version	8.0.45

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
-- Table structure for table `audit_log`
--

DROP TABLE IF EXISTS `audit_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `action` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `entity_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `entity_id` int DEFAULT NULL,
  `changes` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `idx_entity` (`entity_type`,`entity_id`),
  KEY `idx_created` (`created_at`),
  CONSTRAINT `audit_log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_log`
--

LOCK TABLES `audit_log` WRITE;
/*!40000 ALTER TABLE `audit_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `audit_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `devices`
--

DROP TABLE IF EXISTS `devices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `devices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Kundenname (optional)',
  `customer_device_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Formatierte Kunden-ID: Kunde-00001 (optional)',
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `serial_number` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `manufacturer` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `model` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `location` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `purchase_date` date DEFAULT NULL,
  `last_inspection` date DEFAULT NULL,
  `next_inspection` date DEFAULT NULL,
  `status` enum('active','inactive','maintenance','retired') COLLATE utf8mb4_unicode_ci DEFAULT 'active',
  `qr_code` longblob COMMENT 'QR-Code als PNG/Base64',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `cable_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'USB-Kabeltyp (USB-C, Lightning, etc.)',
  `test_result` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Testergebnis (bestanden, nicht_bestanden, etc.)',
  `internal_resistance` decimal(10,3) DEFAULT NULL COMMENT 'Innenwiderstand in Ohm',
  `emarker_active` tinyint(1) DEFAULT NULL COMMENT 'eMarker Status (nur USB-C)',
  `inspection_notes` text COLLATE utf8mb4_unicode_ci COMMENT 'Inspektionsnotizen',
  `r_pe` decimal(10,3) DEFAULT NULL COMMENT 'Schutzleiterwiderstand in Ohm',
  `r_iso` decimal(10,3) DEFAULT NULL COMMENT 'Isolationswiderstand in MegaOhm',
  `i_pe` decimal(10,3) DEFAULT NULL COMMENT 'Schutzleiterstrom in mA',
  `i_b` decimal(10,3) DEFAULT NULL COMMENT 'Berhrungsstrom in mA',
  PRIMARY KEY (`id`),
  UNIQUE KEY `customer_device_id` (`customer_device_id`),
  KEY `idx_customer` (`customer`),
  KEY `idx_customer_device_id` (`customer_device_id`),
  KEY `idx_name` (`name`),
  KEY `idx_serial` (`serial_number`),
  KEY `idx_status` (`status`),
  KEY `idx_created` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devices`
--

LOCK TABLES `devices` WRITE;
/*!40000 ALTER TABLE `devices` DISABLE KEYS */;
INSERT INTO `devices` VALUES (1,'Miro','Miro-00001','Kaltgeräte-Stecker','Kabel',NULL,'Kema-Keur',NULL,'Berlin','2025-01-01','2026-02-17','2027-02-17','active',NULL,NULL,'2026-02-17 16:25:14','2026-02-18 12:04:12','','',NULL,NULL,'',0.040,1999.000,NULL,NULL),(2,'Miro','Miro-00002','Power-Cabel','USB-Kabel',NULL,'Nintendo',NULL,'Berlin','2025-01-01','2026-02-17','2027-02-17','active',NULL,NULL,'2026-02-17 17:01:35','2026-02-17 17:01:35','USB-C','bestanden',0.250,NULL,'',NULL,NULL,NULL,NULL),(3,'Miro','Miro-00003','IsY Nintendo Switch Ladestation','USB-Kabel',NULL,'IsY',NULL,'Berlin','2025-01-01','2026-02-17','2027-02-17','active',NULL,NULL,'2026-02-17 17:03:49','2026-02-17 17:03:49','USB-C','bestanden',0.230,NULL,'',NULL,NULL,NULL,NULL),(4,'Miro','Miro-00004','3x Steckdose - stehend','Kabel',NULL,'Steelcase',NULL,'Berlin','2025-01-01','2026-02-17','2027-02-17','active',NULL,NULL,'2026-02-17 17:29:03','2026-02-18 12:04:12','','',NULL,NULL,'',0.070,20.000,0.020,0.020),(5,'Miro','Miro-00005','4x Steckdose','Verlängerung',NULL,'TuV',NULL,'Berlin','2025-01-01','2026-02-17','2027-02-17','active',NULL,NULL,'2026-02-17 17:33:27','2026-02-18 12:04:12','','',NULL,NULL,'',0.050,1000.000,NULL,0.005),(6,'Miro','Miro-00006','3x Stecker','Verlängerung',NULL,'Steelcase',NULL,'Berlin','2025-01-01','2026-02-17','2027-02-17','active',NULL,NULL,'2026-02-17 17:39:04','2026-02-17 17:39:04','','',NULL,NULL,'',0.230,NULL,NULL,0.020),(7,'Miro','Miro-00007','4x Stecker','Verlängerung',NULL,'TuV',NULL,'Berlin','2025-01-01','2026-02-17','2027-02-17','active',NULL,NULL,'2026-02-17 17:46:36','2026-02-18 12:04:12','','',NULL,NULL,'',0.010,20.000,NULL,0.020),(8,'Miro','Miro-00008','3x Stecker Würfel','Verlängerung',NULL,'AVOLT',NULL,'Berlin','2025-01-01','2026-02-17','2027-02-17','active',NULL,NULL,'2026-02-17 17:51:43','2026-02-18 12:04:12','','',NULL,NULL,'',0.026,20.000,NULL,0.020),(9,'Miro','Miro-00009','Monitor - Präsentation','Kabel',NULL,'neat',NULL,'Berlin','2025-01-01','2026-02-17','2027-02-17','active',NULL,NULL,'2026-02-17 17:59:29','2026-02-18 12:04:12','','',NULL,NULL,'',NULL,20.000,NULL,0.020),(10,'Miro','Miro-00010','Apple Station','Sonstiges',NULL,'Apple',NULL,'Berlin','2025-01-01','2026-02-17','2027-02-17','active',NULL,NULL,'2026-02-17 18:03:22','2026-02-18 12:04:12','','',NULL,NULL,'',NULL,20.000,NULL,0.020),(11,'Miro','Miro-00011','LogiCam','Sonstiges',NULL,'Logi - MeetUp',NULL,'Berlin','2025-01-01','2026-02-17','2027-02-17','active',NULL,'Datenkabel -> USB zum Apple PC defekt','2026-02-17 18:11:21','2026-02-18 12:04:12','','',NULL,NULL,'',NULL,20.000,NULL,0.020),(12,'Miro','Miro-00012','Apple - Ladegerät','USB-Kabel',NULL,'Apple',NULL,'Berlin','2025-01-01','2026-02-17','2027-02-17','active',NULL,'keine Beschädigung','2026-02-17 18:16:48','2026-02-18 12:04:12','Lightning','bestanden',6.900,NULL,'stabiles Gewebeband ',NULL,20.000,NULL,0.020),(13,'Miro','Miro-00013','Mikrofon - Sennheiser Station','Sonstiges',NULL,'Sennheiser',NULL,'Berlin','2025-01-01','2026-02-17','2027-02-17','active',NULL,'Dünnes Kabel -> Regelmäßig 4x im Jahr empfohlen zu prüfen!','2026-02-17 18:23:56','2026-02-18 12:04:12','','',NULL,NULL,'',NULL,20.000,NULL,0.020),(14,'Miro','Miro-00014','Mischpult','Sonstiges','Inventur-Nr.: 000002','Allen-Heath',NULL,'Berlin','2025-01-01','2026-02-17','2027-02-17','active',NULL,'Lackiertes Gehäuse -> keine Durchgang zum PE-Anschluss [amerikanisches Variante]','2026-02-17 18:37:02','2026-02-18 12:04:12','','',NULL,NULL,'',0.023,20.000,NULL,0.020),(15,'Miro','Miro-00015','Netzteil - JBL Box','Kabel','191319-11','JBL',NULL,'Berlin','2022-08-01','2026-02-17','2027-02-17','active',NULL,NULL,'2026-02-17 18:41:14','2026-02-18 12:04:12','','',NULL,NULL,'',NULL,20.000,NULL,0.020),(16,'Miro','Miro-00016','Lautsprecher - Front PA','Sonstiges','205841','JBL',NULL,'Berlin','2025-01-01','2026-02-17','2027-02-17','active',NULL,'Zuleitung iO','2026-02-17 18:44:25','2026-02-18 12:04:12','','',NULL,NULL,'',0.013,20.000,NULL,0.020),(17,'Miro','Miro-00017','Kühltruhe - TK','Sonstiges','1030054','Comfee',NULL,'Berlin - Küche','2025-08-01','2026-02-17','2027-02-17','retired',NULL,'Isolation der Zuleitung gebrochen -> muss gewechselt werden! [5m PVC-Kabel]\nGehäuse Lackiert und stark beansprucht durch Transport -> 4x Empfehlung zur Prüfung','2026-02-17 19:00:36','2026-02-18 12:04:12','','',NULL,NULL,'',0.040,20.000,NULL,0.020),(18,'Miro','Miro-00018','Induction cooker','Sonstiges','000084','HENDI',NULL,'Berlin - Küche','2025-01-01','2026-02-17','2027-02-17','active',NULL,'SKII Empfehlung die Platte zu auszuwechseln [Hygiene Vorschrift]','2026-02-17 19:04:47','2026-02-18 12:04:12','','',NULL,NULL,'',NULL,20.000,NULL,0.020),(19,'Miro','Miro-00019','Induktion - Platte','Sonstiges','000104','HENDI',NULL,'Berlin - Küche','2025-01-01','2026-02-17','2027-02-17','active',NULL,'SKII Auch hier Empfehlung: Wechsel der Platte wegen Hygiene Vorschrift','2026-02-17 19:07:21','2026-02-18 12:04:12','','',NULL,NULL,'',NULL,20.000,NULL,0.020),(20,'Miro','Miro-00020','Mixer','Sonstiges','600','Tefal',NULL,'Berlin - Küche','2025-01-01','2026-02-17','2027-02-17','active',NULL,'Gehäuse intakt -> Empfehlung 4x zu Prüfen da hohe Belastung und günstiges Küchengerät','2026-02-17 19:13:11','2026-02-18 12:04:12','','',NULL,NULL,'',NULL,20.000,NULL,0.020),(21,'Miro','Miro-00021','NK - Schrank Edelstahl Doppeltür','Elektrowerkzeug','245519','metos',NULL,'Berlin - Küche','2025-01-01','2026-02-17','2027-02-17','active',NULL,'NK - Schrank keine Mängel','2026-02-17 19:22:26','2026-02-18 12:04:12','','',NULL,NULL,'',0.010,20.000,NULL,0.020),(22,'Miro','Miro-00022','Kochplatte','Elektrowerkzeug','00006','HOELLER',NULL,'Berlin',NULL,'2026-02-17','2027-02-17','active',NULL,'Lackiertes Gehäuse RPE bis 1,23 Ohm','2026-02-17 19:31:40','2026-02-18 12:04:12','','',NULL,NULL,'',0.040,20.000,NULL,0.020),(23,'Miro','Miro-00023','Kochplatte','Elektrowerkzeug',NULL,'HOELLER',NULL,'Berlin - Küche','2025-01-01','2026-02-17','2027-02-17','active',NULL,'Gehäuse lackiert -> RPE Werte bis 1,31 Ohm','2026-02-17 19:33:54','2026-02-18 12:04:12','','',NULL,NULL,'',0.041,20.000,NULL,0.020);
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
  `device_id` int NOT NULL,
  `inspection_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `result` enum('pass','fail','pending') COLLATE utf8mb4_unicode_ci DEFAULT 'pending',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `inspector` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_device` (`device_id`),
  KEY `idx_date` (`inspection_date`),
  KEY `idx_result` (`result`),
  CONSTRAINT `inspections_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inspections`
--

LOCK TABLES `inspections` WRITE;
/*!40000 ALTER TABLE `inspections` DISABLE KEYS */;
/*!40000 ALTER TABLE `inspections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` enum('admin','inspector','viewer') COLLATE utf8mb4_unicode_ci DEFAULT 'viewer',
  `active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_username` (`username`),
  KEY `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-18 12:46:29
