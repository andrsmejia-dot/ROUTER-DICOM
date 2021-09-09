/*
Navicat MySQL Data Transfer

Source Server         : Localhost
Source Server Version : 50647
Source Host           : localhost:3306
Source Database       : dicom

Target Server Type    : MYSQL
Target Server Version : 50647
File Encoding         : 65001

Date: 2021-07-12 12:29:28
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for accounts
-- ----------------------------
DROP TABLE IF EXISTS `accounts`;
CREATE TABLE `accounts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of accounts
-- ----------------------------
INSERT INTO `accounts` VALUES ('1', 'test', 'test', 'test@test.com');
INSERT INTO `accounts` VALUES ('4', 'ricardo', '1234', 'r@gmail.com');
INSERT INTO `accounts` VALUES ('5', 'pepito', '1234', 'pepito@gmail.com');
INSERT INTO `accounts` VALUES ('6', 'noruego', '1234', 'n@gmail.com');
INSERT INTO `accounts` VALUES ('7', 'jose', '123', 'j@gmail.com');
