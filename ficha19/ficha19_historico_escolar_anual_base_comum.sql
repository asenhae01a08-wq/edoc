-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: ficha19
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `historico_escolar_anual_base_comum`
--

DROP TABLE IF EXISTS `historico_escolar_anual_base_comum`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historico_escolar_anual_base_comum` (
  `id` int NOT NULL AUTO_INCREMENT,
  `historico_geral_id` int DEFAULT NULL,
  `disciplina_id` int DEFAULT NULL,
  `percentual_frequencia_anual` decimal(5,2) DEFAULT NULL,
  `carga_horaria_horas_aula` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `historico_geral_id` (`historico_geral_id`),
  KEY `disciplina_id` (`disciplina_id`),
  CONSTRAINT `historico_escolar_anual_base_comum_ibfk_1` FOREIGN KEY (`historico_geral_id`) REFERENCES `historico_escolar_geral` (`id`),
  CONSTRAINT `historico_escolar_anual_base_comum_ibfk_2` FOREIGN KEY (`disciplina_id`) REFERENCES `disciplinas_anuais_base_comum` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=109 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historico_escolar_anual_base_comum`
--

LOCK TABLES `historico_escolar_anual_base_comum` WRITE;
/*!40000 ALTER TABLE `historico_escolar_anual_base_comum` DISABLE KEYS */;
INSERT INTO `historico_escolar_anual_base_comum` VALUES (1,1,1,95.00,80),(2,1,2,93.00,80),(3,1,3,100.00,80),(4,1,4,95.00,80),(5,1,5,93.00,80),(6,1,6,100.00,80),(7,1,7,95.00,200),(8,1,8,93.00,200),(9,1,9,100.00,200),(10,1,10,95.00,80),(11,1,11,93.00,80),(12,1,12,100.00,80),(13,1,13,95.00,80),(14,1,14,93.00,40),(15,1,15,100.00,40),(16,1,16,95.00,80),(17,1,17,93.00,80),(18,1,18,100.00,80),(19,1,19,95.00,40),(20,1,20,93.00,80),(21,1,21,100.00,80),(22,1,22,95.00,40),(23,1,23,93.00,40),(24,1,24,100.00,40),(25,1,25,95.00,40),(26,1,26,93.00,40),(27,1,27,100.00,40),(28,1,28,95.00,40),(29,1,29,93.00,40),(30,1,30,100.00,40),(31,1,31,95.00,40),(32,1,32,93.00,40),(33,1,33,100.00,40),(34,1,34,95.00,200),(35,1,35,93.00,200),(36,1,36,100.00,200),(37,2,37,95.00,80),(38,2,38,93.00,80),(39,2,39,100.00,80),(40,2,40,95.00,80),(41,2,41,93.00,80),(42,2,42,100.00,80),(43,2,43,95.00,200),(44,2,44,93.00,200),(45,2,45,100.00,200),(46,2,46,95.00,80),(47,2,47,93.00,80),(48,2,48,100.00,80),(49,2,49,95.00,80),(50,2,50,93.00,40),(51,2,51,100.00,40),(52,2,52,95.00,80),(53,2,53,93.00,80),(54,2,54,100.00,80),(55,2,55,95.00,40),(56,2,56,93.00,80),(57,2,57,100.00,80),(58,2,58,95.00,40),(59,2,59,93.00,40),(60,2,60,100.00,40),(61,2,61,95.00,40),(62,2,62,93.00,40),(63,2,63,100.00,40),(64,2,64,95.00,40),(65,2,65,93.00,40),(66,2,66,100.00,40),(67,2,67,95.00,40),(68,2,68,93.00,40),(69,2,69,100.00,40),(70,2,70,95.00,200),(71,2,71,93.00,200),(72,2,72,100.00,200),(73,3,73,93.00,80),(74,3,74,99.00,80),(75,3,75,94.00,80),(76,3,76,93.00,80),(77,3,77,99.00,80),(78,3,78,94.00,80),(79,3,79,93.00,200),(80,3,80,99.00,200),(81,3,81,94.00,200),(82,3,82,93.00,80),(83,3,83,99.00,80),(84,3,84,94.00,80),(85,3,85,93.00,80),(86,3,86,99.00,40),(87,3,87,94.00,40),(88,3,88,93.00,80),(89,3,89,99.00,80),(90,3,90,94.00,80),(91,3,91,93.00,40),(92,3,92,99.00,80),(93,3,93,94.00,80),(94,3,94,93.00,40),(95,3,95,99.00,40),(96,3,96,94.00,40),(97,3,97,93.00,40),(98,3,98,99.00,40),(99,3,99,94.00,40),(100,3,100,93.00,40),(101,3,101,99.00,40),(102,3,102,94.00,40),(103,3,103,93.00,40),(104,3,104,99.00,40),(105,3,105,94.00,40),(106,3,106,93.00,200),(107,3,107,99.00,200),(108,3,108,94.00,200);
/*!40000 ALTER TABLE `historico_escolar_anual_base_comum` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-05 20:49:41
