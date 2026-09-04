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
-- Table structure for table `alunos`
--

DROP TABLE IF EXISTS `alunos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alunos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) DEFAULT NULL,
  `matricula` varchar(7) NOT NULL,
  `data_nascimento` date DEFAULT NULL,
  `id_turma` varchar(50) DEFAULT NULL,
  `cpf` varchar(14) DEFAULT NULL,
  `rg` varchar(50) DEFAULT NULL,
  `orgao_expedidor` varchar(50) DEFAULT NULL,
  `nacionalidade` varchar(50) DEFAULT 'Brasileira',
  `nome_pai` varchar(100) DEFAULT NULL,
  `nome_mae` varchar(100) DEFAULT NULL,
  `endereco` varchar(255) DEFAULT NULL,
  `serie` varchar(50) DEFAULT NULL,
  `escola_id` int DEFAULT NULL,
  `curso_id` int DEFAULT NULL,
  `primeiro_login` date DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `email` varchar(100) DEFAULT NULL,
  `senha` varchar(255) DEFAULT NULL,
  `status_ficha19` enum('Pronta para emissão','Em fabricação') DEFAULT 'Em fabricação',
  `cargo_nivel` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_alunos_matricula` (`matricula`),
  UNIQUE KEY `cpf` (`cpf`),
  UNIQUE KEY `email` (`email`),
  KEY `escola_id` (`escola_id`),
  KEY `curso_id` (`curso_id`),
  CONSTRAINT `alunos_ibfk_1` FOREIGN KEY (`escola_id`) REFERENCES `escolas` (`id`),
  CONSTRAINT `alunos_ibfk_2` FOREIGN KEY (`curso_id`) REFERENCES `cursos` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alunos`
--

LOCK TABLES `alunos` WRITE;
/*!40000 ALTER TABLE `alunos` DISABLE KEYS */;
INSERT INTO `alunos` VALUES (1,'Rodrigo de Souza Silva Junior','3674783','2008-01-05','3º TDS A',NULL,NULL,NULL,'Brasileira',NULL,NULL,NULL,NULL,NULL,NULL,'2026-08-31','2026-06-01 12:27:19','rodrigoalun0.client@gmail.com','rodrigo12342026','Pronta para emissão','Aluno'),(2,'Ana Beatriz Oliveira','3674801','2008-03-14','3º TDS A','438.271.590-11','10234567','SSP/AL','Brasileira','Carlos Henrique Oliveira','Mariana Oliveira Santos','Rua das Palmeiras, 152 - Maceió/AL','3º Ano',1,1,'2026-09-17','2026-07-28 12:21:31','anaalun0.client@gmail.com','Ana12342026','Em fabricação','Aluno'),(4,'Maria Eduarda Lima','3674803','2007-11-08','3º MKT A','184.635.902-45','10234569','SSP/AL','Brasileira','Fernando Lima','Patrícia Lima','Av. Fernandes Lima, 245 - Maceió/AL','3º Ano',1,1,'2026-10-06','2026-07-28 12:21:31','mariaalun0.client@gmail.com','Maria12342026','Em fabricação','Aluno'),(5,'João Pedro Santos','3674804','2009-01-17','3º MKT B','319.728.450-87','10234570','SSP/AL','Brasileiro','Roberto Santos','Eliane dos Santos','Rua São José, 48 - Maceió/AL','3º Ano',1,1,'2026-10-14','2026-07-28 12:21:31','joaoalun0.client@gmail.com','joao12342026','Pronta para emissão','Aluno'),(6,'Larissa Vitória Costa','3674805','2008-05-22','3º TDS A','768.204.513-30','10234571','SSP/AL','Brasileira','Anderson Costa','Cristina Costa','Rua do Sol, 217 - Maceió/AL','3º Ano',1,1,'2026-10-23','2026-07-28 12:21:31','larissaalun0.client@gmail.com','Larissa12342026','Em fabricação','Aluno'),(10,'Camila Rodrigues Melo','3674809','2008-08-30','3º TDS A','143.690.825-76','10234575','SSP/AL','Brasileira','Ricardo Melo','Vanessa Rodrigues Melo','Rua Benedito Bentes, 170 - Maceió/AL','3º Ano',1,1,'2026-11-27','2026-07-28 12:21:31','camilaalun0.client@gmail.com','Camila12342026','Pronta para emissão','Aluno'),(11,'JULIA FERREIRA LIMA','3674810','2008-05-09','3º TDS A','512.384.760-22','10345678','SDS/PE','BRASILEIRA','MARCOS ANTONIO LIMA','PATRICIA FERREIRA LIMA','Rua Pajuçara, 66 - Maceió/AL','3º Ano',1,1,'2026-12-03','2026-07-28 12:21:31','felipealun0.client@gmail.com','feli12342026','Pronta para emissão','Aluno'),(12,'Deyvid Bergson Medeiros Santos','1234567','2008-09-11','3º TDS A','123.456.789-10','01234576','SDS/PE','Brasileiro','Pedro Santos','Iara Medeiros','Rua Indo e Voltando, 96 - Caruaru/PE','3º Ano',1,1,'2026-12-08','2026-07-28 12:41:11','deyvidalun0.client@gmail.com','deyv12342026','Pronta para emissão','Aluno'),(15,'HENRIQUE ALVES ROCHA','3674813','2007-11-30','3º TDS B','845.631.270-59','10678901','SDS/PE','BRASILEIRO','PAULO HENRIQUE ROCHA','MARTA ALVES ROCHA',NULL,'3º Ano',1,1,NULL,'2026-08-28 08:27:15',NULL,'3184763','Pronta para emissão','Aluno'),(16,'SOFIA MARTINS COSTA','3674814','2008-06-12','3º TDS A','956.720.340-68','10789012','SDS/PE','BRASILEIRA','EDUARDO LUIZ COSTA','RENATA MARTINS COSTA',NULL,'3º Ano',1,1,NULL,'2026-08-28 08:27:16',NULL,'4184763','Pronta para emissão','Aluno'),(17,'Joao','1232131','2013-06-02','3º TDS A','213.233.332-33',NULL,NULL,'Brasileira',NULL,NULL,NULL,NULL,1,1,NULL,'2026-09-02 13:56:26','joao@gmail.com','1312321','Em fabricação','Aluno');
/*!40000 ALTER TABLE `alunos` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-03 21:32:38
