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
-- Table structure for table `historico_escolar_anual_itinerario_formativo`
--

DROP TABLE IF EXISTS `historico_escolar_anual_itinerario_formativo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historico_escolar_anual_itinerario_formativo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `historico_geral_id` int DEFAULT NULL,
  `disciplina_id` int DEFAULT NULL,
  `percentual_frequencia_anual` decimal(5,2) DEFAULT NULL,
  `carga_horaria_horas_aula` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `historico_geral_id` (`historico_geral_id`),
  KEY `disciplina_id` (`disciplina_id`),
  CONSTRAINT `historico_escolar_anual_itinerario_formativo_ibfk_1` FOREIGN KEY (`historico_geral_id`) REFERENCES `historico_escolar_geral` (`id`),
  CONSTRAINT `historico_escolar_anual_itinerario_formativo_ibfk_2` FOREIGN KEY (`disciplina_id`) REFERENCES `disciplinas_anuais_itinerario_formativo` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historico_escolar_anual_itinerario_formativo`
--

LOCK TABLES `historico_escolar_anual_itinerario_formativo` WRITE;
/*!40000 ALTER TABLE `historico_escolar_anual_itinerario_formativo` DISABLE KEYS */;
INSERT INTO `historico_escolar_anual_itinerario_formativo` VALUES (1,1,1,97.00,40),(2,1,2,94.00,40),(3,1,3,100.00,40),(4,1,4,100.00,20),(5,1,5,100.00,40),(6,1,6,97.00,40),(7,1,7,96.00,40),(8,1,8,94.00,40),(9,1,9,93.00,80),(10,1,10,95.00,40),(11,1,11,100.00,40),(12,1,12,94.00,80),(13,1,13,100.00,80),(14,1,14,97.00,80),(15,1,15,95.00,80),(16,1,16,97.00,40),(17,1,17,94.00,40),(18,1,18,98.00,80),(19,2,19,97.00,40),(20,2,20,94.00,40),(21,2,21,100.00,40),(22,2,22,100.00,20),(23,2,23,100.00,40),(24,2,24,97.00,40),(25,2,25,96.00,40),(26,2,26,94.00,40),(27,2,27,93.00,80),(28,2,28,95.00,40),(29,2,29,100.00,40),(30,2,30,94.00,80),(31,2,31,100.00,80),(32,2,32,97.00,80),(33,2,33,95.00,80),(34,2,34,97.00,40),(35,2,35,94.00,40),(36,2,36,98.00,80),(37,3,37,100.00,40),(38,3,38,99.00,40),(39,3,39,98.00,40),(40,3,40,98.00,20),(41,3,41,96.00,40),(42,3,42,95.00,40),(43,3,43,96.00,40),(44,3,44,99.00,40),(45,3,45,97.00,80),(46,3,46,98.00,40),(47,3,47,96.00,40),(48,3,48,100.00,80),(49,3,49,94.00,80),(50,3,50,96.00,80),(51,3,51,96.00,80),(52,3,52,98.00,40),(53,3,53,97.00,40),(54,3,54,99.00,80);
/*!40000 ALTER TABLE `historico_escolar_anual_itinerario_formativo` ENABLE KEYS */;
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
