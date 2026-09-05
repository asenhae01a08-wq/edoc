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
-- Table structure for table `aluno_disciplina_base_comum`
--

DROP TABLE IF EXISTS `aluno_disciplina_base_comum`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `aluno_disciplina_base_comum` (
  `aluno_id` int NOT NULL,
  `disciplina_id` int NOT NULL,
  PRIMARY KEY (`aluno_id`,`disciplina_id`),
  KEY `disciplina_id` (`disciplina_id`),
  CONSTRAINT `aluno_disciplina_base_comum_ibfk_1` FOREIGN KEY (`aluno_id`) REFERENCES `alunos` (`id`),
  CONSTRAINT `aluno_disciplina_base_comum_ibfk_2` FOREIGN KEY (`disciplina_id`) REFERENCES `disciplinas_anuais_base_comum` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aluno_disciplina_base_comum`
--

LOCK TABLES `aluno_disciplina_base_comum` WRITE;
/*!40000 ALTER TABLE `aluno_disciplina_base_comum` DISABLE KEYS */;
INSERT INTO `aluno_disciplina_base_comum` VALUES (15,1),(15,2),(15,3),(15,4),(15,5),(15,6),(15,7),(15,8),(15,9),(15,10),(15,11),(15,12),(15,13),(15,14),(15,15),(15,16),(15,17),(15,18),(15,19),(15,20),(15,21),(15,22),(15,23),(15,24),(15,25),(15,26),(15,27),(15,28),(15,29),(15,30),(15,31),(15,32),(15,33),(15,34),(15,35),(15,36),(18,37),(18,38),(18,39),(18,40),(18,41),(18,42),(18,43),(18,44),(18,45),(18,46),(18,47),(18,48),(18,49),(18,50),(18,51),(18,52),(18,53),(18,54),(18,55),(18,56),(18,57),(18,58),(18,59),(18,60),(18,61),(18,62),(18,63),(18,64),(18,65),(18,66),(18,67),(18,68),(18,69),(18,70),(18,71),(18,72),(19,73),(19,74),(19,75),(19,76),(19,77),(19,78),(19,79),(19,80),(19,81),(19,82),(19,83),(19,84),(19,85),(19,86),(19,87),(19,88),(19,89),(19,90),(19,91),(19,92),(19,93),(19,94),(19,95),(19,96),(19,97),(19,98),(19,99),(19,100),(19,101),(19,102),(19,103),(19,104),(19,105),(19,106),(19,107),(19,108);
/*!40000 ALTER TABLE `aluno_disciplina_base_comum` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-05 20:49:42
