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
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historico_escolar_anual_itinerario_formativo`
--

LOCK TABLES `historico_escolar_anual_itinerario_formativo` WRITE;
/*!40000 ALTER TABLE `historico_escolar_anual_itinerario_formativo` DISABLE KEYS */;
INSERT INTO `historico_escolar_anual_itinerario_formativo` VALUES (1,1,1,97.00,40),(2,1,2,94.00,40),(3,1,3,100.00,40),(4,1,4,100.00,20),(5,1,5,100.00,40),(6,1,6,97.00,40),(7,1,7,96.00,40),(8,1,8,94.00,40),(9,1,9,93.00,80),(10,1,10,95.00,40),(11,1,11,100.00,40),(12,1,12,94.00,80),(13,1,13,100.00,80),(14,1,14,97.00,80),(15,1,15,95.00,80),(16,1,16,97.00,40),(17,1,17,94.00,40),(18,1,18,98.00,80);
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

-- Dump completed on 2026-09-03 21:39:17
