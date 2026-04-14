-- MySQL dump 10.13  Distrib 8.0.42, for Linux (x86_64)
--
-- Host: localhost    Database: pshims
-- ------------------------------------------------------
-- Server version	8.0.42-0ubuntu0.20.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `components`
--

DROP TABLE IF EXISTS `components`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `components` (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL COMMENT 'UUID 主键',
  `component_name` varchar(128) COLLATE utf8mb4_cs_0900_as_cs NOT NULL COMMENT '组件名称，可重复',
  `component_part_number` varchar(128) COLLATE utf8mb4_cs_0900_as_cs NOT NULL COMMENT '组件料号，唯一',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '逻辑删除标记，0 未删除，1 删除',
  `order_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL COMMENT '关联订单ID，外键',
  PRIMARY KEY (`id`),
  KEY `fk_order` (`order_id`),
  CONSTRAINT `fk_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_cs_0900_as_cs COMMENT='组件信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `components`
--

LOCK TABLES `components` WRITE;
/*!40000 ALTER TABLE `components` DISABLE KEYS */;
INSERT INTO `components` VALUES ('099348f1-c2d0-4ff7-8618-f05ce2f43a8e','MainBoard','COMP-X1-001','2025-08-28 14:55:32',0,'689b2e1b-9e90-48d9-9310-5b80dbe664df'),('0ad85b1a-f439-4f96-a68c-d6d6fc5f445f','MainB导出oard-V2','COMP-X1-101','2025-09-22 14:39:17',0,'aafbaf76-7e26-4490-8b70-b74aaf73c845'),('1ea27e7e-3f41-46a7-bfb9-ae73393e4e6e','I/O-Board','COMP-X1-IO-201','2025-09-22 14:39:17',0,'aafbaf76-7e26-4490-8b70-b74aaf73c845'),('42119c65-5499-4f7a-aad2-8f1f91af0538','MainBoard-V2','COMP-X1-101','2025-09-17 16:46:18',0,'94030a32-f76c-412e-b127-518407bbbf21'),('5df21d23-c135-4f58-b42e-3d5923dd5d74','PowerUnit','COMP-X2-001','2025-08-28 14:55:44',0,'8851386e-2d0d-4a28-bef9-8c52052e476a'),('89d81a69-88c9-43c6-be2d-fd153fa39c62','Component-1-Updated1','COMP001-NEW','2025-08-28 14:54:11',0,'6cb10491-bdb5-404d-aca2-6c8bcfd3542a'),('a2f3a9da-5e25-4c6f-a4e3-2b715a34d796','I/O-Board','COMP-X1-IO-201','2025-09-17 16:46:18',0,'94030a32-f76c-412e-b127-518407bbbf21'),('ee25db1c-6661-4d83-acc0-71486e8c2aa4','Component-2-NEW1','COMP002','2025-08-28 14:54:11',0,'6cb10491-bdb5-404d-aca2-6c8bcfd3542a');
/*!40000 ALTER TABLE `components` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL COMMENT 'UUID 主键',
  `order_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL COMMENT '订单号，唯一',
  `model` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL COMMENT '机型',
  `part_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL COMMENT '料号',
  `serial_number_start` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL COMMENT '序列号起始',
  `serial_number_end` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL COMMENT '序列号结束',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '逻辑删除标记，0 未删除，1 删除',
  `remark` varchar(200) COLLATE utf8mb4_cs_0900_as_cs DEFAULT NULL COMMENT '订单备注栏',
  `order_created_at` datetime DEFAULT NULL COMMENT '订单创建时间',
  `appendix` varchar(128) COLLATE utf8mb4_cs_0900_as_cs DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_number` (`order_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_cs_0900_as_cs COMMENT='订单信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES ('689b2e1b-9e90-48d9-9310-5b80dbe664df','ORDERTEST-001','Model-X1','PN-X1-001','SNX1001','SNX1100','2025-08-28 14:55:32',0,NULL,NULL,NULL),('6cb10491-bdb5-404d-aca2-6c8bcfd3542a','ORDER001-UPDATED','Model-A-Updated','PART001-UPDATED','SN010','SN150','2025-08-28 13:57:06',0,NULL,NULL,NULL),('8851386e-2d0d-4a28-bef9-8c52052e476a','ORDERTEST-002','Model-X2','PN-X2-002','SNY2001','SNY2100','2025-08-28 14:55:44',0,NULL,NULL,NULL),('94030a32-f76c-412e-b127-518407bbbf21','updatetest1','Model-X1-RevB','PN-X1-001-REV2','SNX1200','SNX1299','2025-09-15 16:10:13',0,'评论测试1','2025-09-14 16:02:43','123.rar'),('aafbaf76-7e26-4490-8b70-b74aaf73c845','导出测试1','Model-X1-RevB','PN-X1-001-REV2','SNX1200','SNX1299','2025-09-22 14:39:17',0,NULL,NULL,NULL);
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissions`
--

DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissions` (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs NOT NULL COMMENT '主键ID (UUID)',
  `permission_code` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs NOT NULL COMMENT '权限编码，程序判断用，如: user:create',
  `permission_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs NOT NULL COMMENT '权限名称，界面显示用，如: 新增用户',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs DEFAULT NULL COMMENT '权限描述',
  `is_deleted` tinyint NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_permission_code` (`permission_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs COMMENT='权限定义表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissions`
--

LOCK TABLES `permissions` WRITE;
/*!40000 ALTER TABLE `permissions` DISABLE KEYS */;
INSERT INTO `permissions` VALUES ('p1111111-1111-1111-1111-111111111111','OrderManagement','订单管理','订单管理相关权限',0),('p2222222-2222-2222-2222-222222222222','UserManagement','用户管理','用户管理相关权限',0),('p3333333-3333-3333-3333-333333333333','RoleManagement','角色管理','角色管理相关权限',0);
/*!40000 ALTER TABLE `permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role_mapping_permissions`
--

DROP TABLE IF EXISTS `role_mapping_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_mapping_permissions` (
  `role_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs NOT NULL COMMENT '角色ID',
  `permission_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs NOT NULL COMMENT '权限ID',
  `is_deleted` tinyint NOT NULL DEFAULT '0',
  PRIMARY KEY (`role_id`,`permission_id`),
  KEY `fk_rp_permission` (`permission_id`),
  CONSTRAINT `fk_rp_permission` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_rp_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs COMMENT='角色权限连接表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_mapping_permissions`
--

LOCK TABLES `role_mapping_permissions` WRITE;
/*!40000 ALTER TABLE `role_mapping_permissions` DISABLE KEYS */;
INSERT INTO `role_mapping_permissions` VALUES ('4d2f5a3b-2c61-4a5f-9e5f-b7e3f74c9e2b','p1111111-1111-1111-1111-111111111111',0),('4d2f5a3b-2c61-4a5f-9e5f-b7e3f74c9e2b','p2222222-2222-2222-2222-222222222222',0),('4d2f5a3b-2c61-4a5f-9e5f-b7e3f74c9e2b','p3333333-3333-3333-3333-333333333333',0);
/*!40000 ALTER TABLE `role_mapping_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs NOT NULL COMMENT '主键ID (UUID)',
  `role_code` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs NOT NULL COMMENT '角色编码，业务唯一',
  `role_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs NOT NULL COMMENT '角色名称',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs DEFAULT NULL COMMENT '角色描述',
  `status` enum('active','disabled') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs NOT NULL DEFAULT 'active' COMMENT '角色状态',
  `extra_data` json DEFAULT NULL COMMENT '预留扩展字段',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` tinyint NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_role_code` (`role_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs COMMENT='角色信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES ('4d2f5a3b-2c61-4a5f-9e5f-b7e3f74c9e2b','admin','admin','系统管理员角色','active',NULL,'2025-08-28 11:07:28','2025-08-28 11:07:28',0);
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `softwares`
--

DROP TABLE IF EXISTS `softwares`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `softwares` (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL COMMENT 'UUID 主键',
  `sub_component_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL COMMENT '关联子组件ID，外键',
  `software_name` varchar(128) COLLATE utf8mb4_cs_0900_as_cs NOT NULL COMMENT '软件名称，可重复',
  `software_version` varchar(128) COLLATE utf8mb4_cs_0900_as_cs DEFAULT NULL COMMENT '软件版本号，可重复',
  `attachment` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs DEFAULT NULL COMMENT '附件名称或路径，可重复',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '逻辑删除标记，0 未删除，1 删除',
  `appendix` varchar(128) COLLATE utf8mb4_cs_0900_as_cs DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_sub_component` (`sub_component_id`),
  CONSTRAINT `fk_sub_component` FOREIGN KEY (`sub_component_id`) REFERENCES `sub_components` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_cs_0900_as_cs COMMENT='软件信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `softwares`
--

LOCK TABLES `softwares` WRITE;
/*!40000 ALTER TABLE `softwares` DISABLE KEYS */;
INSERT INTO `softwares` VALUES ('28dbd6a4-f873-430c-91c1-28603c52670b','f3f359af-8f96-45f7-b920-23d228a131f8','DiagTool','0.9.0','diag_0.9.0.exe','2025-09-17 16:46:18',0,NULL),('2e1a058b-5e69-4cd8-9ded-f3e48b5ed2c2','52e41f63-7bf5-439d-93fe-b03442630e95','DiagTool','0.9.0','diag_0.9.0.exe','2025-09-22 14:39:17',0,NULL),('2e4340ca-3a5e-422e-b6e3-9e89f2627735','5fa3a76f-3d7a-4970-a169-b2a0544c8e02','Software-1-Updated','v1.1','attachment1-v2.pdf','2025-08-28 14:54:11',0,'2e4340ca-3a5e-422e-b6e3-9e89f2627735.rar'),('4eeffd1c-81c1-421b-8839-4d8429ef57c2','78fe575c-53ec-4de1-b2a7-75d8049e3019','USBFW','3.0.0','usbfw_3.0.0.bin','2025-09-22 14:39:17',0,NULL),('5a44790a-28db-49e0-9c05-8ad47cd31e4e','5528ad19-583f-41c6-a67d-4dcd2e104f98','Bootloader','1.0.0','bootloader_1.0.0.bin','2025-08-28 14:55:32',0,NULL),('5b1e0726-9be3-47cd-bf8e-d1de27e6ef90','52e41f63-7bf5-439d-93fe-b03442630e95','Bootloader','1.1.0','bootloader_1.1.0.bin','2025-09-22 14:39:17',0,NULL),('6c3e0155-824e-4ef9-a51b-869a0edb6719','8508232c-c4fb-42eb-bf23-27095d7a1f03','USBFW','3.0.0','usbfw_3.0.0.bin','2025-09-17 16:46:18',0,NULL),('9655f210-001a-4c12-b01d-ad99c7ea2434','52d8564b-9d96-492e-bf38-0348ebdfad0d','Software-2','v2.0','attachment2.pdf','2025-08-28 14:54:11',0,NULL),('de8a3464-25d9-498a-9c7b-655bcb190cbd','f3f359af-8f96-45f7-b920-23d228a131f8','Bootloader','1.1.0','bootloader_1.1.0.bin','2025-09-17 16:46:18',0,NULL),('ef7f4d11-2954-4c32-98af-becb2a464ade','88125f5d-7516-457c-893a-d0657aac296b','PowerFW','2.3.1','powerfw_2.3.1.zip','2025-08-28 14:55:44',0,NULL);
/*!40000 ALTER TABLE `softwares` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sub_components`
--

DROP TABLE IF EXISTS `sub_components`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sub_components` (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL COMMENT 'UUID 主键',
  `component_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL COMMENT '关联父组件ID，外键',
  `sub_component_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL COMMENT '子组件名称，可重复',
  `sub_component_part_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL COMMENT '子组件料号，唯一',
  `specification` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs DEFAULT NULL COMMENT '规格型号',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '逻辑删除标记，0 未删除，1 删除',
  PRIMARY KEY (`id`),
  KEY `fk_component` (`component_id`),
  CONSTRAINT `fk_component` FOREIGN KEY (`component_id`) REFERENCES `components` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_cs_0900_as_cs COMMENT='子组件信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sub_components`
--

LOCK TABLES `sub_components` WRITE;
/*!40000 ALTER TABLE `sub_components` DISABLE KEYS */;
INSERT INTO `sub_components` VALUES ('52d8564b-9d96-492e-bf38-0348ebdfad0d','ee25db1c-6661-4d83-acc0-71486e8c2aa4','Sub-Component-2','SUB002','Spec-2','2025-08-28 14:54:11',0),('52e41f63-7bf5-439d-93fe-b03442630e95','0ad85b1a-f439-4f96-a68c-d6d6fc5f445f','CPU-Module-V2','SUB-X1-CPU-101','ARMv9-A','2025-09-22 14:39:17',0),('5528ad19-583f-41c6-a67d-4dcd2e104f98','099348f1-c2d0-4ff7-8618-f05ce2f43a8e','CPU-Module','SUB-X1-CPU-001','ARMv8-A','2025-08-28 14:55:32',0),('5fa3a76f-3d7a-4970-a169-b2a0544c8e02','89d81a69-88c9-43c6-be2d-fd153fa39c62','Sub-Component-1-Updated','SUB001-NEW','Spec-1-Updated','2025-08-28 14:54:11',0),('78fe575c-53ec-4de1-b2a7-75d8049e3019','1ea27e7e-3f41-46a7-bfb9-ae73393e4e6e','USB-Controller','SUB-X1-USB-201','USB3.2','2025-09-22 14:39:17',0),('8508232c-c4fb-42eb-bf23-27095d7a1f03','a2f3a9da-5e25-4c6f-a4e3-2b715a34d796','USB-Controller','SUB-X1-USB-201','USB3.2','2025-09-17 16:46:18',0),('88125f5d-7516-457c-893a-d0657aac296b','5df21d23-c135-4f58-b42e-3d5923dd5d74','Converter','SUB-X2-CONV-001','220V-24V','2025-08-28 14:55:44',0),('f3f359af-8f96-45f7-b920-23d228a131f8','42119c65-5499-4f7a-aad2-8f1f91af0538','CPU-Module-V2','SUB-X1-CPU-101','ARMv9-A','2025-09-17 16:46:18',0);
/*!40000 ALTER TABLE `sub_components` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs NOT NULL COMMENT '主键ID (UUID)',
  `account` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs NOT NULL COMMENT '用户账号，业务唯一',
  `password_hash` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs NOT NULL COMMENT '密码哈希值 (应用层需使用Bcrypt或Argon2算法)',
  `full_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs DEFAULT NULL COMMENT '用户姓名',
  `contact_info` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs DEFAULT NULL COMMENT '联系方式',
  `address` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs DEFAULT NULL COMMENT '地址',
  `status` enum('active','disabled') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs NOT NULL DEFAULT 'active' COMMENT '状态',
  `role_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs DEFAULT NULL COMMENT '外键，关联角色表',
  `extra_data` json DEFAULT NULL COMMENT '预留扩展字段',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `gender` enum('woman','man','none','others') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs DEFAULT 'none',
  `is_deleted` tinyint NOT NULL DEFAULT '0' COMMENT '逻辑删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_account` (`account`),
  KEY `idx_role_id_users` (`role_id`),
  CONSTRAINT `fk_users_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs COMMENT='用户信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('8c7a1e7d-3f24-48d2-96b9-5b2e0c42b1b0','test','$2b$12$7qjG6SwDsS2Dvbct9xUAAeJD1UWHUHc5JSagTzQmAfL1QJtfiB48i','测试用户','13800000000','北京市海淀区','active','4d2f5a3b-2c61-4a5f-9e5f-b7e3f74c9e2b',NULL,'2025-08-28 11:09:31','2025-08-28 11:09:31','man',0),('f1560627-7e4f-43c2-b035-8307b3b225c4','admin','$2b$12$pfru2nHzUwAH9ul.GixCXuns4NlO3NUSL8LhmvKjZ9tOR1.Ty84mq',NULL,NULL,NULL,'active',NULL,NULL,'2025-09-17 14:51:40','2025-09-17 14:51:40','none',0);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-23 17:24:00
