CREATE DATABASE  IF NOT EXISTS `ficha19` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `ficha19`;
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
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alunos`
--

LOCK TABLES `alunos` WRITE;
/*!40000 ALTER TABLE `alunos` DISABLE KEYS */;
INSERT INTO `alunos` VALUES (1,'Rodrigo de Souza Silva Junior','3674783','2008-01-05','3º TDS A',NULL,NULL,NULL,'Brasileira',NULL,NULL,NULL,NULL,NULL,NULL,'2026-09-08','2026-06-01 12:27:19','rodriguin@gmail.com','rodri12342026','Pronta para emissão','Aluno'),(2,'Ana Beatriz Oliveira','3674801','2008-03-14','3º TDS A','438.271.590-11','10234567','SSP/AL','Brasileira','Carlos Henrique Oliveira','Mariana Oliveira Santos','Rua das Palmeiras, 152 - Maceió/AL','3º Ano',1,1,'2026-09-17','2026-07-28 12:21:31','anabeatrizzinha@gmail.com','Ana12342026','Em fabricação','Aluno'),(3,'Gabriel Henrique Souza','3674802','2008-07-29','3º TDS B','527.903.146-20','10234568','SSP/AL','Brasileiro','José Henrique Souza','Luciana Pereira Souza','Rua Boa Vista, 81 - Maceió/AL','3º Ano',1,1,'2026-09-29','2026-07-28 12:21:31','gabrielzin@gmail.com','gabr12342026','Pronta para emissão','Aluno'),(4,'Maria Eduarda Lima','3674803','2007-11-08','3º MKT A','184.635.902-45','10234569','SSP/AL','Brasileira','Fernando Lima','Patrícia Lima','Av. Fernandes Lima, 245 - Maceió/AL','3º Ano',1,1,'2026-10-06','2026-07-28 12:21:31','mariaeduardazinha@gmail.com','Maria12342026','Em fabricação','Aluno'),(5,'João Pedro Santos','3674804','2009-01-17','3º MKT B','319.728.450-87','10234570','SSP/AL','Brasileiro','Roberto Santos','Eliane dos Santos','Rua São José, 48 - Maceió/AL','3º Ano',1,1,'2026-10-14','2026-07-28 12:21:31','joaozin@gmail.com','joao12342026','Pronta para emissão','Aluno'),(6,'Larissa Vitória Costa','3674805','2008-05-22','3º TDS A','768.204.513-30','10234571','SSP/AL','Brasileira','Anderson Costa','Cristina Costa','Rua do Sol, 217 - Maceió/AL','3º Ano',1,1,'2026-10-23','2026-07-28 12:21:31','larissazinha@gmail.com','Larissa12342026','Em fabricação','Aluno'),(7,'Lucas Vinicius Almeida','3674806','2007-09-10','3º TDS B','905.361.247-18','10234572','SSP/AL','Brasileiro','Márcio Almeida','Sandra Almeida','Rua Tiradentes, 95 - Maceió/AL','3º Ano',1,1,'2026-11-02','2026-07-28 12:21:31','lucaszin@gmail.com','luca12342026','Pronta para emissão','Aluno'),(8,'Isabela Fernandes Rocha','3674807','2008-12-02','3º MKT A','251.847.396-42','10234573','SSP/AL','Brasileira','Eduardo Rocha','Juliana Fernandes Rocha','Rua Santa Luzia, 430 - Maceió/AL','3º Ano',1,1,'2026-11-11','2026-07-28 12:21:31','isabelazinha@gmail.com','Isabela12342026','Pronta para emissão','Aluno'),(9,'Matheus Cavalcante Silva','3674808','2009-06-18','3º MKT B','682.945.137-54','10234574','SSP/AL','Brasileiro','Cláudio Silva','Rosângela Cavalcante','Rua do Comércio, 312 - Maceió/AL','3º Ano',1,1,'2026-11-19','2026-07-28 12:21:31','matheuszin@gmail.com','math12342026','Em fabricação','Aluno'),(10,'Camila Rodrigues Melo','3674809','2008-08-30','3º TDS A','143.690.825-76','10234575','SSP/AL','Brasileira','Ricardo Melo','Vanessa Rodrigues Melo','Rua Benedito Bentes, 170 - Maceió/AL','3º Ano',1,1,'2026-11-27','2026-07-28 12:21:31','camilazinha@gmail.com','Camila12342026','Pronta para emissão','Aluno'),(11,'Felipe Augusto Barros','3674810','2007-04-05','3º TDS B','836.417.259-69','10234576','SSP/AL','Brasileiro','Paulo Barros','Márcia Barros','Rua Pajuçara, 66 - Maceió/AL','3º Ano',1,1,'2026-12-03','2026-07-28 12:21:31','felipezin@gmail.com','feli12342026','Em fabricação','Aluno'),(12,'Deyvid Bergson Medeiros Santos','1234567','2008-09-11','3º TDS A','123.456.789-10','01234576','SDS/PE','Brasileiro','Pedro Santos','Iara Medeiros','Rua Indo e Voltando, 96 - Caruaru/PE','3º Ano',1,1,'2026-12-08','2026-07-28 12:41:11','deyvidzin@gmail.com','deyv12342026','Pronta para emissão','Aluno'),(13,'Caio Carvalho Campos','5847213','2008-04-18','3º TDS B','123.543.674-22','8456321','SDS/PE','Brasileiro','Carlos Alberto Campos','Márcia Carvalho Campos','Rua das Acácias, 245 - Boa Vista - Caruaru/PE','3º Ano',1,1,'2026-12-15','2026-08-05 13:17:38','caiozin@gmail.com','caio1232026','Em fabricação','Aluno'),(14,'Pedro Pereira Pierre','7316485','2007-11-26','3º MKT A','153.842.521-32','9124785','SDS/PE','Brasileiro','José Pereira Pierre','Patrícia Pereira Pierre','Rua São Miguel, 118 - Maurício de Nassau - Caruaru/PE','3º Ano',1,2,'2026-12-21','2026-08-05 13:17:38','pedrozin@gmail.com','pedro1232026','Pronta para emissão','Aluno');
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

-- Dump completed on 2026-08-14 20:48:39
