-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Anamakine: 127.0.0.1
-- Üretim Zamanı: 25 Mar 2026, 01:52:29
-- Sunucu sürümü: 10.4.32-MariaDB
-- PHP Sürümü: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Veritabanı: `kooperatif_sistemi`
--

DELIMITER $$
--
-- Yordamlar
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `Yeni_Odeme_Ekle` (IN `p_uye_id` INT, IN `p_donem_id` INT, IN `p_tutar` DECIMAL(10,2), IN `p_tarih` DATE, IN `p_makbuz` VARCHAR(20))   BEGIN
    INSERT INTO Odemeler (uye_id, donem_id, odenen_tutar, odeme_tarihi, makbuz_no)
    VALUES (p_uye_id, p_donem_id, p_tutar, p_tarih, p_makbuz);
END$$

--
-- İşlevler
--
CREATE DEFINER=`root`@`localhost` FUNCTION `Toplam_Odenen` (`f_uye_id` INT) RETURNS DECIMAL(10,2) DETERMINISTIC BEGIN
    DECLARE toplam DECIMAL(10,2);
    SELECT COALESCE(SUM(odenen_tutar), 0) INTO toplam FROM Odemeler WHERE uye_id = f_uye_id;
    RETURN toplam;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Tablo için tablo yapısı `aidat_donemleri`
--

CREATE TABLE `aidat_donemleri` (
  `donem_id` int(11) NOT NULL,
  `yil` int(11) NOT NULL,
  `ay` varchar(20) NOT NULL,
  `belirlenen_tutar` decimal(10,2) NOT NULL,
  `son_odeme_tarihi` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Tablo döküm verisi `aidat_donemleri`
--

INSERT INTO `aidat_donemleri` (`donem_id`, `yil`, `ay`, `belirlenen_tutar`, `son_odeme_tarihi`) VALUES
(1, 2026, 'Ocak', 1500.00, '2026-01-31'),
(2, 2026, 'Şubat', 1500.00, '2026-02-28'),
(3, 2026, 'Mart', 1750.00, '2026-03-31');

-- --------------------------------------------------------

--
-- Tablo için tablo yapısı `iptal_edilen_odemeler`
--

CREATE TABLE `iptal_edilen_odemeler` (
  `log_id` int(11) NOT NULL,
  `eski_odeme_id` int(11) DEFAULT NULL,
  `uye_id` int(11) DEFAULT NULL,
  `silinen_tutar` decimal(10,2) DEFAULT NULL,
  `iptal_tarihi` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Tablo için tablo yapısı `odemeler`
--

CREATE TABLE `odemeler` (
  `odeme_id` int(11) NOT NULL,
  `uye_id` int(11) NOT NULL,
  `donem_id` int(11) NOT NULL,
  `odenen_tutar` decimal(10,2) NOT NULL,
  `odeme_tarihi` date NOT NULL,
  `makbuz_no` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Tablo döküm verisi `odemeler`
--

INSERT INTO `odemeler` (`odeme_id`, `uye_id`, `donem_id`, `odenen_tutar`, `odeme_tarihi`, `makbuz_no`) VALUES
(1, 1, 1, 1500.00, '2026-01-15', 'MAK2026-001'),
(3, 1, 2, 1500.00, '2026-02-10', 'MAK2026-003'),
(5, 8, 1, 1500.00, '2026-03-25', '5844'),
(6, 8, 2, 1500.00, '2026-03-25', '5555');

--
-- Tetikleyiciler `odemeler`
--
DELIMITER $$
CREATE TRIGGER `Odeme_Iptal_Log` AFTER DELETE ON `odemeler` FOR EACH ROW BEGIN
    INSERT INTO Iptal_Edilen_Odemeler (eski_odeme_id, uye_id, silinen_tutar)
    VALUES (OLD.odeme_id, OLD.uye_id, OLD.odenen_tutar);
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Tablo için tablo yapısı `uyeler`
--

CREATE TABLE `uyeler` (
  `uye_id` int(11) NOT NULL,
  `tc_no` char(11) NOT NULL,
  `ad` varchar(50) NOT NULL,
  `soyad` varchar(50) NOT NULL,
  `telefon` varchar(15) DEFAULT NULL,
  `eposta` varchar(100) DEFAULT NULL,
  `kayit_tarihi` date DEFAULT curdate(),
  `durum` enum('Aktif','Pasif') DEFAULT 'Aktif'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Tablo döküm verisi `uyeler`
--

INSERT INTO `uyeler` (`uye_id`, `tc_no`, `ad`, `soyad`, `telefon`, `eposta`, `kayit_tarihi`, `durum`) VALUES
(1, '11111111111', 'Ahmet Nusret', 'Özalp', '05321112233', 'ahmet@email.com', '2025-01-10', 'Aktif'),
(7, '22222222222', 'Ayşe', 'Kaya', '05511115587', NULL, '2026-03-25', 'Aktif'),
(8, '14878545221', 'Emirhan', 'Kaymakcı', '0554744658', NULL, '2026-03-25', 'Aktif');

-- --------------------------------------------------------

--
-- Görünüm yapısı durumu `v_odeme_gecmisi`
-- (Asıl görünüm için aşağıya bakın)
--
CREATE TABLE `v_odeme_gecmisi` (
`tc_no` char(11)
,`ad` varchar(50)
,`soyad` varchar(50)
,`yil` int(11)
,`ay` varchar(20)
,`belirlenen_tutar` decimal(10,2)
,`odenen_tutar` decimal(10,2)
,`odeme_tarihi` date
);

-- --------------------------------------------------------

--
-- Görünüm yapısı `v_odeme_gecmisi`
--
DROP TABLE IF EXISTS `v_odeme_gecmisi`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_odeme_gecmisi`  AS SELECT `u`.`tc_no` AS `tc_no`, `u`.`ad` AS `ad`, `u`.`soyad` AS `soyad`, `a`.`yil` AS `yil`, `a`.`ay` AS `ay`, `a`.`belirlenen_tutar` AS `belirlenen_tutar`, `o`.`odenen_tutar` AS `odenen_tutar`, `o`.`odeme_tarihi` AS `odeme_tarihi` FROM ((`odemeler` `o` join `uyeler` `u` on(`o`.`uye_id` = `u`.`uye_id`)) join `aidat_donemleri` `a` on(`o`.`donem_id` = `a`.`donem_id`)) ;

--
-- Dökümü yapılmış tablolar için indeksler
--

--
-- Tablo için indeksler `aidat_donemleri`
--
ALTER TABLE `aidat_donemleri`
  ADD PRIMARY KEY (`donem_id`);

--
-- Tablo için indeksler `iptal_edilen_odemeler`
--
ALTER TABLE `iptal_edilen_odemeler`
  ADD PRIMARY KEY (`log_id`);

--
-- Tablo için indeksler `odemeler`
--
ALTER TABLE `odemeler`
  ADD PRIMARY KEY (`odeme_id`),
  ADD UNIQUE KEY `makbuz_no` (`makbuz_no`),
  ADD KEY `uye_id` (`uye_id`),
  ADD KEY `donem_id` (`donem_id`);

--
-- Tablo için indeksler `uyeler`
--
ALTER TABLE `uyeler`
  ADD PRIMARY KEY (`uye_id`),
  ADD UNIQUE KEY `tc_no` (`tc_no`);

--
-- Dökümü yapılmış tablolar için AUTO_INCREMENT değeri
--

--
-- Tablo için AUTO_INCREMENT değeri `aidat_donemleri`
--
ALTER TABLE `aidat_donemleri`
  MODIFY `donem_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Tablo için AUTO_INCREMENT değeri `iptal_edilen_odemeler`
--
ALTER TABLE `iptal_edilen_odemeler`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Tablo için AUTO_INCREMENT değeri `odemeler`
--
ALTER TABLE `odemeler`
  MODIFY `odeme_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Tablo için AUTO_INCREMENT değeri `uyeler`
--
ALTER TABLE `uyeler`
  MODIFY `uye_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- Dökümü yapılmış tablolar için kısıtlamalar
--

--
-- Tablo kısıtlamaları `odemeler`
--
ALTER TABLE `odemeler`
  ADD CONSTRAINT `odemeler_ibfk_1` FOREIGN KEY (`uye_id`) REFERENCES `uyeler` (`uye_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `odemeler_ibfk_2` FOREIGN KEY (`donem_id`) REFERENCES `aidat_donemleri` (`donem_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
