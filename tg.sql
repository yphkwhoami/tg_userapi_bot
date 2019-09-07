-- Adminer 4.6.2 MySQL dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

SET NAMES utf8mb4;

CREATE TABLE `tg_users` (
  `batch_id` int(11) NOT NULL DEFAULT '0',
  `message_id` bigint(20) NOT NULL DEFAULT '0',
  `group_id` bigint(20) NOT NULL COMMENT 'no negative number',
  `user_id` bigint(20) NOT NULL,
  `username` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `first_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `message_count` int(11) NOT NULL,
  `bot` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `tg_whitelist` (
  `user_id` bigint(20) NOT NULL,
  `group_id` bigint(20) NOT NULL COMMENT 'no negative number',
  `name` varchar(200) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


-- 2019-09-07 13:33:37
