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
-- Table structure for table `disciplinas_anuais_itinerario_formativo`
--

DROP TABLE IF EXISTS `disciplinas_anuais_itinerario_formativo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `disciplinas_anuais_itinerario_formativo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(150) DEFAULT NULL,
  `abreviacao` varchar(20) DEFAULT NULL,
  `tipo` varchar(50) DEFAULT NULL,
  `nota` decimal(4,2) DEFAULT NULL,
  `resultado_final` varchar(30) DEFAULT NULL,
  `periodo_letivo` varchar(20) DEFAULT NULL,
  `frequencia` decimal(5,2) DEFAULT NULL,
  `carga_horaria` int DEFAULT NULL,
  `carga_horaria_horas_aula` int DEFAULT NULL,
  `carga_horaria_relogio` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `disciplinas_anuais_itinerario_formativo`
--

LOCK TABLES `disciplinas_anuais_itinerario_formativo` WRITE;
/*!40000 ALTER TABLE `disciplinas_anuais_itinerario_formativo` DISABLE KEYS */;
INSERT INTO `disciplinas_anuais_itinerario_formativo` VALUES (1,'APROFUNDAMENTO EM TCI I',NULL,'Formação Técnica',7.70,'Aprovado','2024',97.00,40,40,NULL),(2,'DESIGN THINKING',NULL,'Formação Técnica',7.40,'Aprovado','2024',94.00,40,40,NULL),(3,'INTRODUÇÃO ÀS TICs',NULL,'Formação Técnica',8.10,'Aprovado','2024',100.00,40,40,NULL),(4,'ESTUDO ORIENTADO 1',NULL,'Formação Técnica',7.80,'Aprovado','2024',100.00,20,20,NULL),(5,'NIVELAMENTO EM L.P.',NULL,'Formação Técnica',8.40,'Aprovado','2024',100.00,40,40,NULL),(6,'PROJETO DE VIDA 1',NULL,'Formação Técnica',8.20,'Aprovado','2024',97.00,40,40,NULL),(7,'BANCO DE DADOS',NULL,'Formação Técnica',8.90,'Aprovado','2024',96.00,40,40,NULL),(8,'DESIGN DE INTERFACES',NULL,'Formação Técnica',8.10,'Aprovado','2024',94.00,40,40,NULL),(9,'LÓGICA DE PROGRAMAÇÃO',NULL,'Formação Técnica',7.80,'Aprovado','2024',93.00,80,80,NULL),(10,'LETRAMENTO LINGUÍSTICO',NULL,'Formação Técnica',8.80,'Aprovado','2025',95.00,40,40,NULL),(11,'LÓGICA MATEMÁTICA',NULL,'Formação Técnica',8.10,'Aprovado','2025',100.00,40,40,NULL),(12,'TRABALHO E SOCIEDADE',NULL,'Formação Técnica',7.80,'Aprovado','2025',94.00,80,80,NULL),(13,'CRIATIVIDADE E INOVAÇÃO',NULL,'Formação Técnica',8.30,'Aprovado','2025',100.00,80,80,NULL),(14,'DESIGN THINKING',NULL,'Formação Técnica',7.40,'Aprovado','2025',97.00,80,80,NULL),(15,'INTRODUÇÃO ÀS TICs',NULL,'Formação Técnica',8.70,'Aprovado','2025',95.00,80,80,NULL),(16,'BANCO DE DADOS',NULL,'Formação Técnica',8.60,'Aprovado','2025',97.00,40,40,NULL),(17,'DESIGN DE INTERFACES',NULL,'Formação Técnica',8.70,'Aprovado','2025',94.00,40,40,NULL),(18,'PROGRAMAÇÃO DESKTOP',NULL,'Formação Técnica',7.50,'Aprovado','2025',98.00,80,80,NULL),(19,'APROFUNDAMENTO EM TCI I',NULL,'Formação Técnica',7.70,'Aprovado','2024',97.00,40,40,NULL),(20,'DESIGN THINKING',NULL,'Formação Técnica',7.40,'Aprovado','2024',94.00,40,40,NULL),(21,'INTRODUÇÃO ÀS TICs',NULL,'Formação Técnica',8.10,'Aprovado','2024',100.00,40,40,NULL),(22,'ESTUDO ORIENTADO 1',NULL,'Formação Técnica',7.80,'Aprovado','2024',100.00,20,20,NULL),(23,'NIVELAMENTO EM L.P.',NULL,'Formação Técnica',8.40,'Aprovado','2024',100.00,40,40,NULL),(24,'PROJETO DE VIDA 1',NULL,'Formação Técnica',8.20,'Aprovado','2024',97.00,40,40,NULL),(25,'BANCO DE DADOS',NULL,'Formação Técnica',8.90,'Aprovado','2024',96.00,40,40,NULL),(26,'DESIGN DE INTERFACES',NULL,'Formação Técnica',8.10,'Aprovado','2024',94.00,40,40,NULL),(27,'LÓGICA DE PROGRAMAÇÃO',NULL,'Formação Técnica',7.80,'Aprovado','2024',93.00,80,80,NULL),(28,'LETRAMENTO LINGUÍSTICO',NULL,'Formação Técnica',8.80,'Aprovado','2025',95.00,40,40,NULL),(29,'LÓGICA MATEMÁTICA',NULL,'Formação Técnica',8.10,'Aprovado','2025',100.00,40,40,NULL),(30,'TRABALHO E SOCIEDADE',NULL,'Formação Técnica',7.80,'Aprovado','2025',94.00,80,80,NULL),(31,'CRIATIVIDADE E INOVAÇÃO',NULL,'Formação Técnica',8.30,'Aprovado','2025',100.00,80,80,NULL),(32,'DESIGN THINKING',NULL,'Formação Técnica',7.40,'Aprovado','2025',97.00,80,80,NULL),(33,'INTRODUÇÃO ÀS TICs',NULL,'Formação Técnica',8.70,'Aprovado','2025',95.00,80,80,NULL),(34,'BANCO DE DADOS',NULL,'Formação Técnica',8.60,'Aprovado','2025',97.00,40,40,NULL),(35,'DESIGN DE INTERFACES',NULL,'Formação Técnica',8.70,'Aprovado','2025',94.00,40,40,NULL),(36,'PROGRAMAÇÃO DESKTOP',NULL,'Formação Técnica',7.50,'Aprovado','2025',98.00,80,80,NULL),(37,'APROFUNDAMENTO EM TCI I',NULL,'Formação Técnica',9.40,'Aprovado','2024',100.00,40,40,NULL),(38,'DESIGN THINKING',NULL,'Formação Técnica',8.50,'Aprovado','2024',99.00,40,40,NULL),(39,'INTRODUÇÃO ÀS TICs',NULL,'Formação Técnica',8.90,'Aprovado','2024',98.00,40,40,NULL),(40,'ESTUDO ORIENTADO 1',NULL,'Formação Técnica',9.30,'Aprovado','2024',98.00,20,20,NULL),(41,'NIVELAMENTO EM L.P.',NULL,'Formação Técnica',8.90,'Aprovado','2024',96.00,40,40,NULL),(42,'PROJETO DE VIDA 1',NULL,'Formação Técnica',8.80,'Aprovado','2024',95.00,40,40,NULL),(43,'BANCO DE DADOS',NULL,'Formação Técnica',9.10,'Aprovado','2024',96.00,40,40,NULL),(44,'DESIGN DE INTERFACES',NULL,'Formação Técnica',9.10,'Aprovado','2024',99.00,40,40,NULL),(45,'LÓGICA DE PROGRAMAÇÃO',NULL,'Formação Técnica',8.30,'Aprovado','2024',97.00,80,80,NULL),(46,'LETRAMENTO LINGUÍSTICO',NULL,'Formação Técnica',8.10,'Aprovado','2025',98.00,40,40,NULL),(47,'LÓGICA MATEMÁTICA',NULL,'Formação Técnica',8.30,'Aprovado','2025',96.00,40,40,NULL),(48,'TRABALHO E SOCIEDADE',NULL,'Formação Técnica',8.80,'Aprovado','2025',100.00,80,80,NULL),(49,'CRIATIVIDADE E INOVAÇÃO',NULL,'Formação Técnica',8.70,'Aprovado','2025',94.00,80,80,NULL),(50,'DESIGN THINKING',NULL,'Formação Técnica',9.10,'Aprovado','2025',96.00,80,80,NULL),(51,'INTRODUÇÃO ÀS TICs',NULL,'Formação Técnica',9.40,'Aprovado','2025',96.00,80,80,NULL),(52,'BANCO DE DADOS',NULL,'Formação Técnica',8.20,'Aprovado','2025',98.00,40,40,NULL),(53,'DESIGN DE INTERFACES',NULL,'Formação Técnica',8.20,'Aprovado','2025',97.00,40,40,NULL),(54,'PROGRAMAÇÃO DESKTOP',NULL,'Formação Técnica',8.70,'Aprovado','2025',99.00,80,80,NULL);
/*!40000 ALTER TABLE `disciplinas_anuais_itinerario_formativo` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-05 20:49:40
