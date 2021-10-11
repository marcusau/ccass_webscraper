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
-- Table structure for table `summary`
--

DROP TABLE IF EXISTS `summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `summary` (
  `shareholdingdate` datetime NOT NULL,
  `stockcode` int(11) NOT NULL,
  `inter_holding` bigint(15) NOT NULL,
  `consenting_holding` bigint(15) NOT NULL,
  `nonconsenting_holding` bigint(15) NOT NULL,
  `inter_num` int(11) NOT NULL,
  `consenting_num` int(11) NOT NULL,
  `nonconsenting_num` int(11) NOT NULL,
  `ISC` bigint(15) NOT NULL,
  `inter_pct` float DEFAULT NULL,
  `consenting_pct` float DEFAULT NULL,
  `nonconsenting_pct` float DEFAULT NULL,
  `top5_pct` float DEFAULT NULL,
  `top10_pct` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `CIP_pct` float DEFAULT NULL,
  `ccass_pct` float DEFAULT NULL,
  `non_ccass_pct` float DEFAULT NULL,
  `close` float DEFAULT NULL,
  PRIMARY KEY (`shareholdingdate`,`stockcode`),
  KEY `idx_nonconsenting_num` (`nonconsenting_num`,`stockcode`,`shareholdingdate`,`nonconsenting_pct`,`ccass_pct`,`consenting_num`,`inter_num`),
  KEY `idx_pre_date` (`stockcode`,`shareholdingdate`,`inter_pct`,`consenting_pct`,`nonconsenting_pct`,`ccass_pct`),
  KEY `idx_stk` (`stockcode`,`shareholdingdate`,`inter_pct`,`consenting_pct`,`nonconsenting_pct`,`ccass_pct`),
  KEY `idx_inter_holding` (`inter_pct`,`shareholdingdate`,`stockcode`,`consenting_pct`,`nonconsenting_pct`,`ccass_pct`),
  KEY `idx_consenting_holding` (`consenting_pct`,`shareholdingdate`,`stockcode`,`inter_pct`,`nonconsenting_pct`,`ccass_pct`),
  KEY `idx_nonconsenting_holding` (`nonconsenting_pct`,`shareholdingdate`,`stockcode`,`consenting_pct`,`inter_pct`,`ccass_pct`),
  KEY `idx_ccass_to_ISC` (`ccass_pct`,`shareholdingdate`,`stockcode`,`inter_pct`,`consenting_pct`,`nonconsenting_pct`),
  KEY `idx_inter_num` (`inter_num`,`stockcode`,`shareholdingdate`,`consenting_num`,`nonconsenting_num`,`inter_pct`,`ccass_pct`),
  KEY `idx_consenting_num` (`consenting_num`,`stockcode`,`shareholdingdate`,`consenting_pct`,`inter_num`,`inter_pct`,`nonconsenting_num`,`ccass_pct`),
  KEY `idx_inter_pct` (`inter_pct`,`stockcode`,`shareholdingdate`,`inter_num`,`ccass_pct`),
  KEY `idx_consenting_pct` (`consenting_pct`,`stockcode`,`shareholdingdate`,`inter_pct`,`nonconsenting_pct`,`ccass_pct`),
  KEY `idx_nonconsenting_pct` (`nonconsenting_pct`,`stockcode`,`shareholdingdate`,`ccass_pct`,`inter_pct`,`consenting_pct`),
  KEY `idx_CIP_pct` (`ccass_pct`,`stockcode`,`shareholdingdate`,`inter_pct`,`CIP_pct`,`non_ccass_pct`),
  KEY `idx_top5_pct` (`top5_pct`,`shareholdingdate`,`stockcode`,`top10_pct`,`CIP_pct`,`ccass_pct`,`non_ccass_pct`),
  KEY `idx_top10_pct` (`top10_pct`,`stockcode`,`shareholdingdate`,`top5_pct`,`CIP_pct`,`ccass_pct`,`non_ccass_pct`)
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

-- Dump completed on 2021-10-11 15:59:16
