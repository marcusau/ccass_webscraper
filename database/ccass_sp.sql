CREATE DATABASE IF NOT EXISTS `ccass` DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;

USE `ccass`;

DROP TABLE IF EXISTS `summary`;

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

DROP TABLE IF EXISTS `stocks`;

CREATE TABLE `stocks` (
  `stockcode` int(11) NOT NULL,
  `exchange` varchar(2) COLLATE utf8_bin NOT NULL,
  `ccass_id` int(10) DEFAULT NULL,
  `name_eng` varchar(200) COLLATE utf8_bin DEFAULT NULL,
  `name_chi` varchar(200) COLLATE utf8_bin DEFAULT NULL,
  `listing` varchar(1) COLLATE utf8_bin DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`stockcode`,`exchange`),
  KEY `idx_ccass_id` (`ccass_id`,`stockcode`,`exchange`,`listing`,`update_time`),
  KEY `idx_exchange` (`exchange`,`stockcode`,`ccass_id`,`listing`,`update_time`),
  KEY `idx_update_time` (`update_time`,`stockcode`,`exchange`,`ccass_id`,`listing`),
  KEY `idx_listing` (`listing`,`stockcode`,`exchange`,`ccass_id`,`update_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS `participants`;

CREATE TABLE `participants` (
  `pid` int(11) NOT NULL AUTO_INCREMENT,
  `ccass_id` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `name_eng` varchar(200) COLLATE utf8_bin DEFAULT NULL,
  `name_chi` varchar(200) COLLATE utf8_bin DEFAULT NULL,
  `address` varchar(400) COLLATE utf8_bin DEFAULT NULL,
  `p_type` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`pid`),
  KEY `idx_ccass_id` (`ccass_id`,`name_eng`,`pid`,`p_type`,`address`,`update_time`),
  KEY `id_p_type` (`p_type`,`ccass_id`,`pid`,`address`,`update_time`),
  KEY `idx_update_time` (`update_time`,`ccass_id`,`pid`,`name_eng`,`address`,`p_type`)
) ENGINE=InnoDB AUTO_INCREMENT=1991 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS `stock_connect`;

CREATE TABLE `stock_connect` (
  `shareholdingdate` datetime NOT NULL,
  `stockcode` int(11) NOT NULL,
  `exchange` varchar(3) COLLATE utf8_bin NOT NULL,
  `holding` bigint(15) NOT NULL,
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
  PRIMARY KEY (`shareholdingdate`,`stockcode`,`exchange`),
  KEY `idx_stockcode` (`stockcode`,`exchange`,`shareholdingdate`,`chg_pct_1lag`,`chg_pct_5lag`,`ISC_pct`),
  KEY `idx_exchange` (`exchange`,`stockcode`,`shareholdingdate`,`ISC_pct`,`chg_pct_1lag`,`chg_pct_5lag`),
  KEY `idx_ISC` (`ISC_pct`,`shareholdingdate`,`stockcode`,`exchange`,`chg_pct_1lag`,`chg_pct_5lag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS `main`;

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

DELIMITER $$

DROP PROCEDURE IF EXISTS `search_Top10NetIn`$$

CREATE DEFINER=`root`@`%` PROCEDURE `search_Top10NetIn`(
	IN `stockcode` INT,
	IN `intervalValue` VARCHAR(50),
	IN `intervalType` VARCHAR(50),
	IN `shareholdingdate` DATETIME
    )
BEGIN
	DECLARE southbound_name VARCHAR(32) CHARACTER SET utf8;
	SET southbound_name = '港股通';
	SET @stockcode = stockcode;
	SET @dateRange = CONCAT(intervalValue,intervalType);
	SET @lastDate = shareholdingdate;
	SET @sql_str = "(SELECT '0' part, DATE_FORMAT(m.shareholdingdate, '%Y-%m-%d') shareholdingdate, p.pid, p.ccass_id, p.name_eng, p.name_chi, ISC_pct, ";
	
	CASE  @dateRange
	   WHEN '1daily' THEN 
		SET @sql_str_where = " and chg_1lag>0 order by chg_1lag desc";
		SET @sql_str_from = "m.chg_1lag";
		SET @sql_str_from2 = "m.chg_pct_1lag";
		SET @sql_str_from3 = "ISC_pct-chg_pct_1lag";
	   WHEN '5daily' THEN 
		SET @sql_str_where = " and chg_5lag>0 order by chg_5lag desc";
		SET @sql_str_from = "m.chg_5lag";
		SET @sql_str_from2 = "m.chg_pct_5lag";
		SET @sql_str_from3 = "ISC_pct-chg_pct_5lag";
	   WHEN '1monthly' THEN 
		SET @sql_str_where = " and chg_1m>0 order by chg_1m desc";
		SET @sql_str_from = "m.chg_1m";
		SET @sql_str_from2 = "m.chg_pct_1m";
		SET @sql_str_from3 = "ISC_pct-chg_pct_1m";
	   WHEN '3monthly' THEN 
		SET @sql_str_where = " and chg_3m>0 order by chg_3m desc";
		SET @sql_str_from = "m.chg_3m";
		SET @sql_str_from2 = "m.chg_pct_3m";
		SET @sql_str_from3 = "ISC_pct-chg_pct_3m";
	   WHEN '6monthly' THEN 
		SET @sql_str_where = " and chg_6m>0 order by chg_6m desc";
		SET @sql_str_from = "m.chg_6m";
		SET @sql_str_from2 = "m.chg_pct_6m";
		SET @sql_str_from3 = "ISC_pct-chg_pct_6m";
	   WHEN '12monthly' THEN 
		SET @sql_str_where = " and chg_12m>0 order by chg_12m desc";
		SET @sql_str_from = "m.chg_12m";
		SET @sql_str_from2 = "m.chg_pct_12m";
		SET @sql_str_from3 = "ISC_pct-chg_pct_12m";
	END CASE;
	SET @sql_str=CONCAT(@sql_str, @sql_str_from, ' chg, ');
	SET @sql_str=CONCAT(@sql_str, @sql_str_from2, ' pct_chg, ');
	SET @sql_str=CONCAT(@sql_str, @sql_str_from3, ' nday_isc_pct ');
	SET @sql_str=CONCAT(@sql_str, " FROM main m join participants p on m.pid=p.pid WHERE m.shareholdingdate=? AND m.stockcode=? AND p.ccass_id NOT IN ('A00002', 'A00003', 'A00004', 'A00005')");
	SET @sql_str=CONCAT(@sql_str, @sql_str_where);
	SET @sql_str = CONCAT(@sql_str, " limit 10");
	SET @sql_str_union = CONCAT(") union all (SELECT '0' part, DATE_FORMAT(m.shareholdingdate, '%Y-%m-%d') shareholdingdate, '-1' pid, '' ccass_id, 'Southbound' name_eng, '", southbound_name ,"' name_chi, sum(ISC_pct) ISC_pct, sum(");
	SET @sql_str_union = CONCAT(@sql_str_union, @sql_str_from, ') chg, sum(');
	SET @sql_str_union = CONCAT(@sql_str_union, @sql_str_from2, ') pct_chg,  sum(');
	SET @sql_str_union = CONCAT(@sql_str_union, @sql_str_from3, ') nday_isc_pct ');
	SET @sql_str_union = CONCAT(@sql_str_union, " FROM main m join participants p on m.pid=p.pid WHERE m.shareholdingdate=? AND m.stockcode=? AND p.ccass_id IN ('A00002', 'A00003', 'A00004', 'A00005') group by m.shareholdingdate)");
	SET @sql_str = CONCAT(@sql_str, @sql_str_union);
	PREPARE stmt FROM @sql_str;
	EXECUTE stmt USING @lastDate, @stockcode, @lastDate, @stockcode;
	DEALLOCATE PREPARE stmt;
    END$$

DELIMITER ;


DELIMITER $$

DROP PROCEDURE IF EXISTS `search_Top10NetOut`$$

CREATE DEFINER=`root`@`%` PROCEDURE `search_Top10NetOut`(
	IN `stockcode` INT,
	IN `intervalValue` VARCHAR(50),
	IN `intervalType` VARCHAR(50),
	IN `shareholdingdate` DATETIME
    )
BEGIN
	DECLARE southbound_name VARCHAR(32) CHARACTER SET utf8;
	SET southbound_name = '港股通';
	SET @stockcode = stockcode;
	SET @dateRange = CONCAT(intervalValue,intervalType);
	SET @lastDate = shareholdingdate;
	SET @sql_str = "(SELECT '1' part, DATE_FORMAT(m.shareholdingdate, '%Y-%m-%d') shareholdingdate, p.pid, p.ccass_id, p.name_eng, p.name_chi, ISC_pct, ";
	
	CASE  @dateRange
	   WHEN '1daily' THEN 
		SET @sql_str_where = " and chg_1lag<0 order by chg_1lag asc";
		SET @sql_str_from = "m.chg_1lag";
		SET @sql_str_from2 = "m.chg_pct_1lag";
		SET @sql_str_from3 = "ISC_pct-chg_pct_1lag";
	   WHEN '5daily' THEN 
		SET @sql_str_where = " and chg_5lag<0 order by chg_5lag asc";
		SET @sql_str_from = "m.chg_5lag";
		SET @sql_str_from2 = "m.chg_pct_5lag";
		SET @sql_str_from3 = "ISC_pct-chg_pct_5lag";
	   WHEN '1monthly' THEN 
		SET @sql_str_where = " and chg_1m<0 order by chg_1m asc";
		SET @sql_str_from = "m.chg_1m";
		SET @sql_str_from2 = "m.chg_pct_1m";
		SET @sql_str_from3 = "ISC_pct-chg_pct_1m";
	   WHEN '3monthly' THEN 
		SET @sql_str_where = " and chg_3m<0 order by chg_3m asc";
		SET @sql_str_from = "m.chg_3m";
		SET @sql_str_from2 = "m.chg_pct_3m";
		SET @sql_str_from3 = "ISC_pct-chg_pct_3m";
	   WHEN '6monthly' THEN 
		SET @sql_str_where = " and chg_6m<0 order by chg_6m asc";
		SET @sql_str_from = "m.chg_6m";
		SET @sql_str_from2 = "m.chg_pct_6m";
		SET @sql_str_from3 = "ISC_pct-chg_pct_6m";
	   WHEN '12monthly' THEN 
		SET @sql_str_where = " and chg_12m<0 order by chg_12m asc";
		SET @sql_str_from = "m.chg_12m";
		SET @sql_str_from2 = "m.chg_pct_12m";
		SET @sql_str_from3 = "ISC_pct-chg_pct_12m";
	END CASE;
	SET @sql_str=CONCAT(@sql_str, @sql_str_from, ' chg, ');
	SET @sql_str=CONCAT(@sql_str, @sql_str_from2, ' pct_chg, ');
	SET @sql_str=CONCAT(@sql_str, @sql_str_from3, ' nday_isc_pct ');
	SET @sql_str=CONCAT(@sql_str, " FROM main m join participants p on m.pid=p.pid WHERE m.shareholdingdate=? AND m.stockcode=? AND p.ccass_id NOT IN ('A00002', 'A00003', 'A00004', 'A00005')");
	SET @sql_str=CONCAT(@sql_str, @sql_str_where);
	SET @sql_str = CONCAT(@sql_str, " limit 10");
	SET @sql_str_union = CONCAT(") union all (SELECT '1' part, DATE_FORMAT(m.shareholdingdate, '%Y-%m-%d') shareholdingdate, '-1' pid, '' ccass_id, 'Southbound' name_eng, '", southbound_name ,"' name_chi, sum(ISC_pct) ISC_pct, sum(");
	SET @sql_str_union = CONCAT(@sql_str_union, @sql_str_from, ') chg, sum(');
	SET @sql_str_union = CONCAT(@sql_str_union, @sql_str_from2, ') pct_chg,  sum(');
	SET @sql_str_union = CONCAT(@sql_str_union, @sql_str_from3, ') nday_isc_pct ');
	SET @sql_str_union = CONCAT(@sql_str_union, " FROM main m join participants p on m.pid=p.pid WHERE m.shareholdingdate=? AND m.stockcode=? AND p.ccass_id IN ('A00002', 'A00003', 'A00004', 'A00005') group by m.shareholdingdate)");
	SET @sql_str = CONCAT(@sql_str, @sql_str_union);
	PREPARE stmt FROM @sql_str;
	EXECUTE stmt USING @lastDate, @stockcode, @lastDate, @stockcode;
	DEALLOCATE PREPARE stmt;
    END$$

DELIMITER ;


DELIMITER $$

DROP PROCEDURE IF EXISTS `search_SouthboundStockConnect`$$

CREATE DEFINER=`root`@`%` PROCEDURE `search_SouthboundStockConnect`(
	IN `stockcode` INT
    )
BEGIN
      SET @stockcode = stockcode;
      SELECT DATE_FORMAT(sc.shareholdingdate, '%Y-%m-%d') shareholdingdate, sc.holding,sc.chg_1lag FROM stock_connect sc 
        WHERE sc.stockcode=@stockcode AND sc.exchange='HK' AND sc.shareholdingdate >DATE_SUB(NOW(),INTERVAL 6 MONTH)
        AND WEEKDAY(shareholdingdate) < 5
	ORDER BY shareholdingdate;
    END$$

DELIMITER ;


DELIMITER $$

DROP PROCEDURE IF EXISTS `search_all_participant`$$

CREATE DEFINER=`root`@`%` PROCEDURE `search_all_participant`()
BEGIN
	SELECT p.pid, p.ccass_id, p.name_eng, p.name_chi FROM participants p;
    END$$

DELIMITER ;


DELIMITER $$

DROP PROCEDURE IF EXISTS `search_Concentration`$$

CREATE DEFINER=`root`@`%` PROCEDURE `search_Concentration`(
      IN `shareholdingdate` DATETIME
    )
BEGIN
	SET @shareholdingdate = DATE_FORMAT(shareholdingdate, '%Y-%m-%d');
	SET @sql_str = 'SELECT s.stockcode, s.top5_pct, s.top10_pct, s.inter_pct, s.CIP_pct, s.nonconsenting_pct, s.ccass_pct, s.non_ccass_pct  FROM summary s WHERE s.shareholdingdate = ?';
	PREPARE stmt FROM @sql_str;
	EXECUTE stmt USING @shareholdingdate;
	DEALLOCATE PREPARE stmt;
    END$$

DELIMITER ;


DELIMITER $$

DROP PROCEDURE IF EXISTS `search_StockLatestRecord`$$

CREATE DEFINER=`root`@`%` PROCEDURE `search_StockLatestRecord`(
	IN `stockcode` INT,
	IN `shareholdingdate` DATETIME
	)
BEGIN
	SET @stockcode = stockcode;
	SET @close_price = '';
	SET @lastDate = shareholdingdate;
	SELECT s.close INTO @close_price FROM summary s WHERE s.stockcode=@stockcode AND s.shareholdingdate = @lastDate;
		SET @sql_str = "SELECT DATE_FORMAT(m.shareholdingdate, '%Y-%m-%d') shareholdingdate, p.pid, p.ccass_id, p.name_eng, p.name_chi,DATE_FORMAT(m.prev_chg_date, '%Y-%m-%d') prev_chg_date, m.holding, m.ISC_pct, m.chg_1lag,
	 m.chg_pct_1lag, m.chg_5lag, m.chg_pct_5lag, chg_1m, chg_pct_1m, chg_3m,chg_pct_3m, chg_6m, chg_pct_6m, chg_12m, chg_pct_12m, '";
	SET @sql_str = CONCAT(@sql_str, @close_price, "' close FROM main m join participants p on m.pid=p.pid where m.shareholdingdate = ? AND m.stockcode = ?");
	PREPARE stmt FROM @sql_str;
	EXECUTE stmt USING @lastDate, @stockcode;
	DEALLOCATE PREPARE stmt;
END$$

DELIMITER ;


DELIMITER $$

DROP PROCEDURE IF EXISTS `search_StockLatestRecordChart`$$

CREATE DEFINER=`root`@`%` PROCEDURE `search_StockLatestRecordChart`(
	IN `stockcode` INT,
	IN `pid` INT
    )
BEGIN
	SET @stockcode = stockcode;
	SET @pid = pid;
	SELECT DATE_FORMAT(m.shareholdingdate, '%Y-%m-%d') shareholdingdate, m.holding, m.chg_1lag
	FROM main m WHERE m.stockcode=@stockcode AND m.pid=@pid AND m.shareholdingdate >DATE_SUB(NOW(),INTERVAL 6 MONTH) 
	AND WEEKDAY(shareholdingdate) < 5
	ORDER BY m.shareholdingdate;
END$$

DELIMITER ;


DELIMITER $$

DROP PROCEDURE IF EXISTS `search_StockHoldingRecordSouthBound`$$

CREATE DEFINER=`root`@`%` PROCEDURE `search_StockHoldingRecordSouthBound`(
	IN `stockcode` INT,
	IN `shareholdingdate` DATETIME
)
BEGIN
	DECLARE southbound_name VARCHAR(32) CHARACTER SET utf8;
	SET southbound_name = '港股通';
	SET @stockcode = stockcode;
	SET @lastDate = shareholdingdate;
	SELECT '0' part,'-1' pid, '' ccass_id, 'Southbound' name_eng, southbound_name name_chi,SUM(m.holding) holding, SUM(m.ISC_pct) ISC_pct, DATE_FORMAT(m.shareholdingdate, '%Y-%m-%d') shareholdingdate,
	SUM(chg_1lag) chg_1lag ,SUM(chg_pct_1lag) chg_pct_1lag, SUM(chg_5lag) chg_5lag, SUM(chg_pct_5lag) chg_pct_5lag, SUM(chg_1m) chg_1m, SUM(chg_pct_1m) chg_pct_1m, 
	SUM(chg_3m) chg_3m, SUM(chg_pct_3m) chg_pct_3m, SUM(chg_6m) chg_6m, SUM(chg_pct_6m) chg_pct_6m, SUM(chg_12m) chg_12m, SUM(chg_pct_12m) chg_pct_12m
	FROM main m, participants p
	WHERE m.pid=p.pid AND m.stockcode = @stockcode AND m.shareholdingdate = @lastDate
	AND p.ccass_id IN ('A00002', 'A00003', 'A00004', 'A00005');
    END$$

DELIMITER ;


DELIMITER $$

DROP PROCEDURE IF EXISTS `search_StockHoldingRecord`$$

CREATE DEFINER=`root`@`%` PROCEDURE `search_StockHoldingRecord`(
      IN `stockcode` INT,
      IN `shareholdingdate` DATETIME
    )
BEGIN
	SET @stockcode = stockcode;
	SET @lastDate = shareholdingdate;
	SET @sql_str ="	SELECT '1' part, m.pid,  p.ccass_id, p.name_eng, p.name_chi, m.holding, m.ISC_pct,DATE_FORMAT(m.shareholdingdate, '%Y-%m-%d') shareholdingdate,
	chg_1lag, chg_pct_1lag, chg_5lag, chg_pct_5lag, chg_1m, chg_pct_1m, 
	chg_3m, chg_pct_3m, chg_6m, chg_pct_6m, chg_12m, chg_pct_12m
		FROM main m, participants p
		WHERE m.pid=p.pid AND m.stockcode = ? AND m.shareholdingdate = ? ";
	SET @sql_str=CONCAT(@sql_str, " order by chg_pct_1lag desc");
	
	PREPARE stmt FROM @sql_str;
	EXECUTE stmt USING @stockcode, @lastDate;
	DEALLOCATE PREPARE stmt;
    END$$

DELIMITER ;


DELIMITER $$

DROP PROCEDURE IF EXISTS `search_StockHoldingRecordChange`$$

CREATE DEFINER=`root`@`%` PROCEDURE `search_StockHoldingRecordChange`(
	IN `stockcode` INT,
	IN `intervalValue` VARCHAR(50),
	IN `intervalType` VARCHAR(50),
	IN `shareholdingdate` DATETIME
)
BEGIN
	SET @stockcode = stockcode;
	SET @dateRange = CONCAT(intervalValue,intervalType);
	SET @lastDate = shareholdingdate;
	CASE  @dateRange
	   WHEN '1daily' THEN 
		SELECT SUM(m.holding) INTO @changeHolding FROM main m WHERE m.stockcode=@stockcode AND m.shareholdingdate=@lastDate AND m.chg_1lag<>0;
		SELECT SUM(m.holding) INTO @unchangeHolding FROM main m WHERE m.stockcode=@stockcode AND m.shareholdingdate=@lastDate AND m.chg_1lag=0;
	   WHEN '5daily' THEN 
		SELECT SUM(m.holding) INTO @changeHolding FROM main m WHERE m.stockcode=@stockcode AND m.shareholdingdate=@lastDate AND m.chg_5lag<>0;
		SELECT SUM(m.holding) INTO @unchangeHolding FROM main m WHERE m.stockcode=@stockcode AND m.shareholdingdate=@lastDate AND m.chg_5lag=0;
	   WHEN '1monthly' THEN 
		SELECT SUM(m.holding) INTO @changeHolding FROM main m WHERE m.stockcode=@stockcode AND m.shareholdingdate=@lastDate AND m.chg_1m<>0;
		SELECT SUM(m.holding) INTO @unchangeHolding FROM main m WHERE m.stockcode=@stockcode AND m.shareholdingdate=@lastDate AND m.chg_1m=0;
	   WHEN '3monthly' THEN 
		SELECT SUM(m.holding) INTO @changeHolding FROM main m WHERE m.stockcode=@stockcode AND m.shareholdingdate=@lastDate AND m.chg_3m<>0;
		SELECT SUM(m.holding) INTO @unchangeHolding FROM main m WHERE m.stockcode=@stockcode AND m.shareholdingdate=@lastDate AND m.chg_3m=0;
	   WHEN '6monthly' THEN 
		SELECT SUM(m.holding) INTO @changeHolding FROM main m WHERE m.stockcode=@stockcode AND m.shareholdingdate=@lastDate AND m.chg_6m<>0;
		SELECT SUM(m.holding) INTO @unchangeHolding FROM main m WHERE m.stockcode=@stockcode AND m.shareholdingdate=@lastDate AND m.chg_6m=0;
	   WHEN '12monthly' THEN 
		SELECT SUM(m.holding) INTO @changeHolding FROM main m WHERE m.stockcode=@stockcode AND m.shareholdingdate=@lastDate AND m.chg_12m<>0;
		SELECT SUM(m.holding) INTO @unchangeHolding FROM main m WHERE m.stockcode=@stockcode AND m.shareholdingdate=@lastDate AND m.chg_12m=0;
	END CASE;
	IF @changeHolding IS NOT NULL AND @changeHolding<>'' AND @unchangeHolding IS NOT NULL AND @unchangeHolding<>'' THEN
	  SET @changeHoldingPCT = @changeHolding/(@changeHolding + @unchangeHolding);
	  SET @unchangeHoldingPCT = @unchangeHolding/(@changeHolding + @unchangeHolding);
	END IF;
	SELECT '2' part, ROUND(@changeHolding,0) holding, @changeHoldingPCT ISC_pct,DATE_FORMAT(@lastDate, '%Y-%m-%d') shareholdingdate
	UNION ALL
	SELECT '2' part, ROUND(@unchangeHolding,0) holding, @unchangeHoldingPCT ISC_pct,DATE_FORMAT(@lastDate, '%Y-%m-%d') shareholdingdate;
END$$

DELIMITER ;


DELIMITER $$

DROP PROCEDURE IF EXISTS `search_StockHoldingRecordSummary`$$

CREATE DEFINER=`root`@`%` PROCEDURE `search_StockHoldingRecordSummary`(
	IN `stockcode` INT,
	IN `shareholdingdate` DATETIME
)
BEGIN
    SET @stockcode = stockcode;
    SET @lastDate = shareholdingdate;
    SELECT '3' part, t.inter_holding + t.consenting_holding holding, t.CIP_pct ISC_pct, DATE_FORMAT(@lastDate, '%Y-%m-%d') shareholdingdate
      FROM (SELECT s.* FROM summary s WHERE s.stockcode = @stockcode AND s.shareholdingdate = @lastDate) t 
    UNION ALL
    SELECT '3' part, nonconsenting_holding holding, nonconsenting_pct ISC_pct, DATE_FORMAT(@lastDate, '%Y-%m-%d') shareholdingdate
      FROM (SELECT s.* FROM summary s WHERE s.stockcode = @stockcode AND s.shareholdingdate = @lastDate) t
    UNION ALL
    SELECT '3' part, inter_holding+ consenting_holding+ nonconsenting_holding holding, ccass_pct ISC_pct, DATE_FORMAT(@lastDate, '%Y-%m-%d') shareholdingdate
      FROM (SELECT s.* FROM summary s WHERE s.stockcode = @stockcode AND s.shareholdingdate = @lastDate) t
    UNION ALL
    SELECT '3' part, ISC-inter_holding-consenting_holding-nonconsenting_holding holding, non_ccass_pct ISC_pct, DATE_FORMAT(@lastDate, '%Y-%m-%d') shareholdingdate
      FROM (SELECT s.* FROM summary s WHERE s.stockcode = @stockcode AND s.shareholdingdate = @lastDate) t
    UNION ALL
    SELECT '3' part, ISC holding, '1' ISC_pct, DATE_FORMAT(@lastDate, '%Y-%m-%d') shareholdingdate
      FROM (SELECT s.* FROM summary s WHERE s.stockcode = @stockcode AND s.shareholdingdate = @lastDate) t ;
END$$

DELIMITER ;


DELIMITER $$

DROP PROCEDURE IF EXISTS `search_HoldingTop10`$$

CREATE DEFINER=`root`@`%` PROCEDURE `search_HoldingTop10`(
	IN `stockcode` INT,
	IN `shareholdingdate` DATETIME
    )
BEGIN
	DECLARE top10holdingname VARCHAR(32) CHARACTER SET utf8;
	SET top10holdingname = '10大持股%';
	SET @stockcode = stockcode;
	SET @lastDate = shareholdingdate;
	(SELECT  '0' part,'-1' pid, '' ccass_id,  'top 10 holding%' name_eng, top10holdingname name_chi, s.top10_pct ISC_pct
	    FROM summary s WHERE s.stockcode=@stockcode AND s.shareholdingdate=@lastDate
	    ORDER BY s.shareholdingdate DESC)
	UNION ALL
	(SELECT '1' part, m.pid, p.ccass_id, p.name_eng, p.name_chi, m.ISC_pct
	    FROM main m, participants p 
	    WHERE m.pid=p.pid
	    AND m.stockcode = @stockcode AND m.shareholdingdate=@lastDate
	    ORDER BY m.ISC_pct DESC LIMIT 10);
    END$$

DELIMITER ;