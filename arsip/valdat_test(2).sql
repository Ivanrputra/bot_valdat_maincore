-- phpMyAdmin SQL Dump
-- version 4.3.11
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: Aug 16, 2019 at 06:23 AM
-- Server version: 5.6.24
-- PHP Version: 5.6.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `valdat_test`
--

-- --------------------------------------------------------

--
-- Table structure for table `valdat_odpmaster`
--

CREATE TABLE IF NOT EXISTS `valdat_odpmaster` (
  `id` int(11) NOT NULL,
  `name` varchar(128) NOT NULL,
  `address` varchar(400) NOT NULL,
  `redaman` varchar(15) NOT NULL,
  `ip` varchar(128) NOT NULL,
  `qrcode_port` varchar(128) NOT NULL,
  `qrcode_odp` varchar(128) NOT NULL,
  `tray` int(11) NOT NULL,
  `distribusi` int(11) NOT NULL,
  `core_odc` int(11) NOT NULL,
  `lat` varchar(128) NOT NULL,
  `long` varchar(128) NOT NULL,
  `odc_id` int(11) DEFAULT NULL,
  `cap` varchar(7) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `valdat_validasi`
--

CREATE TABLE IF NOT EXISTS `valdat_validasi` (
  `id` int(11) NOT NULL,
  `reported_date` datetime(6) NOT NULL,
  `gpon` varchar(128) NOT NULL,
  `odp_port` varchar(128) NOT NULL,
  `is_valid` tinyint(1) NOT NULL,
  `ncli` varchar(128) NOT NULL,
  `no_internet` varchar(128) NOT NULL,
  `no_pots` varchar(128) NOT NULL,
  `qrcode_dropcore` varchar(128) NOT NULL,
  `hd_id` int(11) DEFAULT NULL,
  `odp_id` int(11) DEFAULT NULL,
  `tech1_id` int(11) DEFAULT NULL,
  `tech2_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `valdat_odpmaster`
--
ALTER TABLE `valdat_odpmaster`
  ADD PRIMARY KEY (`id`), ADD KEY `valdat_odpmaster_odc_id_bd3b8557_fk_valdat_odc_id` (`odc_id`);

--
-- Indexes for table `valdat_validasi`
--
ALTER TABLE `valdat_validasi`
  ADD PRIMARY KEY (`id`), ADD KEY `valdat_validasi_hd_id_479a4648_fk_valdat_user_id` (`hd_id`), ADD KEY `valdat_validasi_odp_id_b4d8297f_fk_valdat_odpmaster_id` (`odp_id`), ADD KEY `valdat_validasi_tech1_id_5bae0180_fk_valdat_user_id` (`tech1_id`), ADD KEY `valdat_validasi_tech2_id_3e42a745_fk_valdat_user_id` (`tech2_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `valdat_odpmaster`
--
ALTER TABLE `valdat_odpmaster`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `valdat_validasi`
--
ALTER TABLE `valdat_validasi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- Constraints for dumped tables
--

--
-- Constraints for table `valdat_odpmaster`
--
ALTER TABLE `valdat_odpmaster`
ADD CONSTRAINT `valdat_odpmaster_odc_id_bd3b8557_fk_valdat_odc_id` FOREIGN KEY (`odc_id`) REFERENCES `valdat_odc` (`id`);

--
-- Constraints for table `valdat_validasi`
--
ALTER TABLE `valdat_validasi`
ADD CONSTRAINT `valdat_validasi_hd_id_479a4648_fk_valdat_user_id` FOREIGN KEY (`hd_id`) REFERENCES `valdat_user` (`id`),
ADD CONSTRAINT `valdat_validasi_odp_id_b4d8297f_fk_valdat_odpmaster_id` FOREIGN KEY (`odp_id`) REFERENCES `valdat_odpmaster` (`id`),
ADD CONSTRAINT `valdat_validasi_tech1_id_5bae0180_fk_valdat_user_id` FOREIGN KEY (`tech1_id`) REFERENCES `valdat_user` (`id`),
ADD CONSTRAINT `valdat_validasi_tech2_id_3e42a745_fk_valdat_user_id` FOREIGN KEY (`tech2_id`) REFERENCES `valdat_user` (`id`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
