-- MySQL dump 10.13  Distrib 5.7.18, for Linux (x86_64)
--
-- Host: 10.200.21.42    Database: ccass
-- ------------------------------------------------------
-- Server version	5.7.18

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `main`
--

DROP TABLE IF EXISTS `main`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main` (
  `shareholdingdate` datetime NOT NULL,
  `stockcode` int(11) NOT NULL,
  `pid` int(11) NOT NULL,
  `holding` bigint(15) DEFAULT NULL,
  `market_cap` double DEFAULT NULL,
  `chg_1lag` bigint(15) DEFAULT NULL,
  `chg_5lag` bigint(15) DEFAULT NULL,
  `chg_1m` bigint(15) DEFAULT NULL,
  `chg_3m` bigint(15) DEFAULT NULL,
  `chg_6m` bigint(15) DEFAULT NULL,
  `chg_12m` bigint(15) DEFAULT NULL,
  `chg_pct_1lag` float DEFAULT NULL,
  `chg_pct_5lag` float DEFAULT NULL,
  `chg_pct_1m` float DEFAULT NULL,
  `chg_pct_3m` float DEFAULT NULL,
  `chg_pct_6m` float DEFAULT NULL,
  `chg_pct_12m` float DEFAULT NULL,
  `ISC_pct` float DEFAULT NULL,
  `prev_chg_date` datetime DEFAULT NULL,
  PRIMARY KEY (`shareholdingdate`,`stockcode`,`pid`),
  KEY `idx_stockcode` (`stockcode`),
  KEY `idx_pid` (`pid`),
  KEY `idx_pre_chg_date` (`prev_chg_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-10-11 15:59:31
