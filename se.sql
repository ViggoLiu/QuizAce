-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: se
-- ------------------------------------------------------
-- Server version	8.0.40

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
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add permission',1,'add_permission'),(2,'Can change permission',1,'change_permission'),(3,'Can delete permission',1,'delete_permission'),(4,'Can view permission',1,'view_permission'),(5,'Can add group',2,'add_group'),(6,'Can change group',2,'change_group'),(7,'Can delete group',2,'delete_group'),(8,'Can view group',2,'view_group'),(9,'Can add content type',3,'add_contenttype'),(10,'Can change content type',3,'change_contenttype'),(11,'Can delete content type',3,'delete_contenttype'),(12,'Can view content type',3,'view_contenttype'),(13,'Can add session',4,'add_session'),(14,'Can change session',4,'change_session'),(15,'Can delete session',4,'delete_session'),(16,'Can view session',4,'view_session'),(17,'Can add 系统用户',5,'add_sysuser'),(18,'Can change 系统用户',5,'change_sysuser'),(19,'Can delete 系统用户',5,'delete_sysuser'),(20,'Can view 系统用户',5,'view_sysuser'),(21,'Can add 学习资源',6,'add_learningresource'),(22,'Can change 学习资源',6,'change_learningresource'),(23,'Can delete 学习资源',6,'delete_learningresource'),(24,'Can view 学习资源',6,'view_learningresource'),(25,'Can add 资源点击记录',7,'add_resourceclickrecord'),(26,'Can change 资源点击记录',7,'change_resourceclickrecord'),(27,'Can delete 资源点击记录',7,'delete_resourceclickrecord'),(28,'Can view 资源点击记录',7,'view_resourceclickrecord'),(29,'Can add 资源收藏',8,'add_resourcefavorite'),(30,'Can change 资源收藏',8,'change_resourcefavorite'),(31,'Can delete 资源收藏',8,'delete_resourcefavorite'),(32,'Can view 资源收藏',8,'view_resourcefavorite'),(33,'Can add 教师信息',9,'add_teacherprofile'),(34,'Can change 教师信息',9,'change_teacherprofile'),(35,'Can delete 教师信息',9,'delete_teacherprofile'),(36,'Can view 教师信息',9,'view_teacherprofile'),(37,'Can add 学生信息',10,'add_studentprofile'),(38,'Can change 学生信息',10,'change_studentprofile'),(39,'Can delete 学生信息',10,'delete_studentprofile'),(40,'Can view 学生信息',10,'view_studentprofile');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (2,'auth','group'),(1,'auth','permission'),(3,'contenttypes','contenttype'),(6,'learning_resource','learningresource'),(7,'learning_resource','resourceclickrecord'),(8,'learning_resource','resourcefavorite'),(4,'sessions','session'),(10,'user','studentprofile'),(5,'user','sysuser'),(9,'user','teacherprofile');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'user','0001_initial','2025-11-27 15:40:24.977210'),(2,'contenttypes','0001_initial','2025-12-01 15:19:08.658095'),(3,'contenttypes','0002_remove_content_type_name','2025-12-01 15:19:08.810996'),(4,'auth','0001_initial','2025-12-01 15:19:09.319278'),(5,'auth','0002_alter_permission_name_max_length','2025-12-01 15:19:09.432047'),(6,'auth','0003_alter_user_email_max_length','2025-12-01 15:19:09.439848'),(7,'auth','0004_alter_user_username_opts','2025-12-01 15:19:09.448838'),(8,'auth','0005_alter_user_last_login_null','2025-12-01 15:19:09.457579'),(9,'auth','0006_require_contenttypes_0002','2025-12-01 15:19:09.462865'),(10,'auth','0007_alter_validators_add_error_messages','2025-12-01 15:19:09.472274'),(11,'auth','0008_alter_user_username_max_length','2025-12-01 15:19:09.481897'),(12,'auth','0009_alter_user_last_name_max_length','2025-12-01 15:19:09.490138'),(13,'auth','0010_alter_group_name_max_length','2025-12-01 15:19:09.515601'),(14,'auth','0011_update_proxy_permissions','2025-12-01 15:19:09.524609'),(15,'auth','0012_alter_user_first_name_max_length','2025-12-01 15:19:09.535489'),(16,'sessions','0001_initial','2025-12-01 15:19:09.597363'),(17,'user','0002_alter_sysuser_options_remove_sysuser_login_date_and_more','2025-12-01 15:22:38.793923'),(18,'learning_resource','0001_initial','2025-12-01 15:26:19.032086'),(19,'learning_resource','0002_resourceclickrecord_resourcefavorite_and_more','2025-12-02 02:45:26.606527'),(20,'learning_resource','0003_remove_learningresource_file_url_and_more','2025-12-02 02:53:31.448751'),(21,'user','0003_remove_sysuser_login_date_remove_sysuser_phonenumber_and_more','2025-12-02 02:55:56.401705');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `learning_resource`
--

DROP TABLE IF EXISTS `learning_resource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `learning_resource` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `course` varchar(100) NOT NULL,
  `college` varchar(100) NOT NULL,
  `description` longtext,
  `file_size` varchar(50) DEFAULT NULL,
  `file_type` varchar(20) DEFAULT NULL,
  `uploader_role` varchar(10) NOT NULL,
  `click_count` int NOT NULL DEFAULT '0',
  `download_count` int NOT NULL DEFAULT '0',
  `favorite_count` int NOT NULL DEFAULT '0',
  `status` int NOT NULL DEFAULT '0',
  `reject_reason` varchar(255) DEFAULT NULL,
  `create_time` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `update_time` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `uploader_id` int NOT NULL,
  `file` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `learning_resource_uploader_id_694115df_fk_sys_user_id` (`uploader_id`),
  CONSTRAINT `learning_resource_uploader_id_694115df_fk_sys_user_id` FOREIGN KEY (`uploader_id`) REFERENCES `sys_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `learning_resource`
--

LOCK TABLES `learning_resource` WRITE;
/*!40000 ALTER TABLE `learning_resource` DISABLE KEYS */;
INSERT INTO `learning_resource` VALUES (1,'高等数学期中重点总结','高等数学','信息工程学院','适合期中复习的重点公式与题型总结','0.0 MB','txt','student',5,8,1,1,NULL,'2025-12-01 23:39:52.307320','2025-12-02 07:03:12.159177',1,'learning_resource/高等数学期中重点总结.txt'),(2,'Python基础期末复习资料','Python程序设计','计算机学院','附带练习题与讲解的视频资料','0.0 MB','txt','teacher',5,0,0,1,NULL,'2025-12-01 23:39:52.307320','2025-12-02 05:53:59.423887',2,'learning_resource/Python基础期末复习资料.txt'),(3,'数据结构知识点脑图','数据结构','信息工程学院','高清思维导图版本','0.0 MB','txt','teacher',1,0,0,1,NULL,'2025-12-01 23:39:52.307320','2025-12-02 07:22:30.320437',2,'learning_resource/数据结构知识点脑图.txt'),(4,'线性代数经典例题汇总','线性代数','数理学院',NULL,'0.0 MB','txt','student',2,0,0,1,NULL,'2025-12-01 23:39:52.307320','2025-12-02 06:10:21.457145',1,'learning_resource/线性代数经典例题汇总.txt'),(5,'软件工程基础小雅资料汇总_含目录.pdf','计算机基础','计算机学院','软件工程','35.14 MB','pdf','student',2,3,0,1,NULL,'2025-12-02 04:57:03.531222','2025-12-02 07:04:19.865090',1,'learning_resource/软件工程基础小雅资料汇总_含目录_Z28iVWX.pdf'),(6,'软件工程复习.pdf','计算机基础','计算机学院','软件工程复习','0.82 MB','pdf','student',1,0,0,1,NULL,'2025-12-02 06:05:46.785864','2025-12-02 06:06:17.252669',12,'learning_resource/软件工程复习.pdf');
/*!40000 ALTER TABLE `learning_resource` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resource_click_record`
--

DROP TABLE IF EXISTS `resource_click_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resource_click_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `clicked_at` datetime(6) NOT NULL,
  `resource_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_resource_click` (`user_id`,`resource_id`),
  KEY `resource_click_recor_resource_id_ff41842e_fk_learning_` (`resource_id`),
  CONSTRAINT `resource_click_recor_resource_id_ff41842e_fk_learning_` FOREIGN KEY (`resource_id`) REFERENCES `learning_resource` (`id`),
  CONSTRAINT `resource_click_record_user_id_f701c792_fk_sys_user_id` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resource_click_record`
--

LOCK TABLES `resource_click_record` WRITE;
/*!40000 ALTER TABLE `resource_click_record` DISABLE KEYS */;
INSERT INTO `resource_click_record` VALUES (1,'2025-12-02 02:45:58.038506',1,10),(2,'2025-12-02 03:47:24.163766',1,11),(3,'2025-12-02 04:01:18.460354',2,10),(4,'2025-12-02 04:02:35.497479',1,1),(5,'2025-12-02 04:40:39.768357',4,10),(6,'2025-12-02 05:30:46.156224',5,1),(7,'2025-12-02 05:53:59.417769',2,1),(8,'2025-12-02 06:06:17.248918',6,12),(9,'2025-12-02 06:10:21.451729',4,12),(10,'2025-12-02 07:03:12.155348',1,12),(11,'2025-12-02 07:04:19.856963',5,12),(12,'2025-12-02 07:22:30.315041',3,12);
/*!40000 ALTER TABLE `resource_click_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resource_favorite`
--

DROP TABLE IF EXISTS `resource_favorite`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resource_favorite` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `favorited_at` datetime(6) NOT NULL,
  `resource_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `resource_favorite_user_id_resource_id_c911cdf2_uniq` (`user_id`,`resource_id`),
  KEY `resource_favorite_resource_id_874d2278_fk_learning_resource_id` (`resource_id`),
  CONSTRAINT `resource_favorite_resource_id_874d2278_fk_learning_resource_id` FOREIGN KEY (`resource_id`) REFERENCES `learning_resource` (`id`),
  CONSTRAINT `resource_favorite_user_id_d9f00d34_fk_sys_user_id` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resource_favorite`
--

LOCK TABLES `resource_favorite` WRITE;
/*!40000 ALTER TABLE `resource_favorite` DISABLE KEYS */;
INSERT INTO `resource_favorite` VALUES (9,'2025-12-02 04:33:43.563026',1,10);
/*!40000 ALTER TABLE `resource_favorite` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_profile`
--

DROP TABLE IF EXISTS `student_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_profile` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '对应 sys_user.id',
  `student_no` varchar(50) DEFAULT NULL COMMENT '学号',
  `college` varchar(100) DEFAULT NULL COMMENT '学院',
  `major` varchar(100) DEFAULT NULL COMMENT '专业',
  `grade` varchar(20) DEFAULT NULL COMMENT '年级',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `student_profile_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='学生信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_profile`
--

LOCK TABLES `student_profile` WRITE;
/*!40000 ALTER TABLE `student_profile` DISABLE KEYS */;
INSERT INTO `student_profile` VALUES (1,1,'202401001','信息工程学院','计算机科学与技术','大一'),(2,2,'202301002','信息工程学院','软件工程','大二'),(3,5,NULL,NULL,NULL,NULL),(4,6,NULL,NULL,NULL,NULL),(5,7,NULL,NULL,NULL,NULL),(6,9,NULL,NULL,NULL,NULL),(7,10,NULL,NULL,NULL,NULL),(8,12,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `student_profile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_user`
--

DROP TABLE IF EXISTS `sys_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(50) NOT NULL,
  `password` varchar(128) NOT NULL,
  `role` enum('student','teacher','admin') NOT NULL COMMENT '角色',
  `avatar` varchar(255) DEFAULT NULL COMMENT '头像',
  `email` varchar(100) DEFAULT NULL COMMENT '邮箱',
  `phone` varchar(20) DEFAULT NULL COMMENT '手机号',
  `status` int NOT NULL,
  `last_login` datetime DEFAULT NULL COMMENT '最后登录时间',
  `create_time` datetime(6) DEFAULT NULL,
  `update_time` datetime(6) DEFAULT NULL,
  `remark` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='系统用户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_user`
--

LOCK TABLES `sys_user` WRITE;
/*!40000 ALTER TABLE `sys_user` DISABLE KEYS */;
INSERT INTO `sys_user` VALUES (1,'student01','pbkdf2_sha256$600000$fJJ1shxpZgvmyOo5MYUOLd$/9yB/8pqKcA48bslBWmdF3AO7ahsvDPf2qxu9xR7U3c=','student',NULL,'student01@qq.com','13800000001',0,NULL,'2025-11-30 21:52:48.000000','2025-11-30 14:55:13.000000','计科大一学生'),(2,'student02','pbkdf2_sha256$600000$xWCo9jjMmoyK3b0B10Xdpz$AIMeyrT5KzVzWB9QSzlM1KDPZ1ZWCz0g6mlrSUYQq80=','student',NULL,'student02@qq.com','13800000002',0,NULL,'2025-11-30 21:52:48.000000','2025-11-30 14:55:14.000000','软工大二学生'),(3,'teacher01','pbkdf2_sha256$600000$vByEtGHnkJrGITr0ZrGqn1$LlyB4tbVJfZe4PEgd+M3z4zVWC8gDRIa74UYHnc4c40=','teacher',NULL,'teacher01@qq.com','13900000001',0,NULL,'2025-11-30 21:52:48.000000','2025-11-30 14:55:14.000000','数据结构老师'),(4,'admin01','pbkdf2_sha256$600000$pD3xhgoLWH7vZFdwXYpIcM$mWl6xs50shZGQ1Ig337vO5PQg/MmaPy8eLbYWqESOCw=','admin',NULL,'admin01@qq.com','13700000000',0,NULL,'2025-11-30 21:52:48.000000','2025-11-30 14:55:14.000000','系统管理员'),(5,'jackzhong','pbkdf2_sha256$600000$QMP6FSpuIsCiuNWUO4kMiv$T0xJAtPmsOqHpep08OfVJmVt8A4HQACqCKXz6YQp1n4=','student',NULL,'123456@qq.com',NULL,0,NULL,'2025-11-30 14:13:47.000000','2025-11-30 14:55:15.000000',NULL),(6,'Jack','pbkdf2_sha256$600000$1tOvdhXzBa73KJv9Q5XlID$8WC0RwAQzy5TfPGSeHvCXqQQS5Jwp+6155owoK9tbwM=','student',NULL,'123456@qq.com',NULL,0,NULL,'2025-11-30 14:14:17.000000','2025-11-30 14:55:15.000000',NULL),(7,'jackz','pbkdf2_sha256$600000$TLNcfvjnPLEE30z6dqOTDP$b8B7B0qJGCRdWEBnpwCgwJcuZEugLLHioJs9Z4yxUto=','student',NULL,'123456@qq.com',NULL,0,NULL,'2025-11-30 14:18:23.000000','2025-11-30 14:55:15.000000',NULL),(8,'admin','pbkdf2_sha256$600000$AHNqXInxBo77nH67wXW7ze$uo7TcAL9q+VM89vo0RQDFB27T8yPBhDRWcN1+ym2SM0=','admin',NULL,NULL,NULL,0,NULL,'2025-11-30 14:54:20.000000','2025-11-30 14:54:20.000000',NULL),(9,'man','pbkdf2_sha256$600000$b4GhndYUQzV4sIkU0gQgLu$vIejWt7aSikwbLQIZSk1gELTDwD1a4ybD6/UGS12eV8=','student',NULL,'1111@qq.com',NULL,0,NULL,'2025-12-01 15:53:19.364873','2025-12-01 15:53:19.364873',NULL),(10,'man1','pbkdf2_sha256$600000$CLhWETWvrDBpMJkKIvl1hk$RnFQsQfwaH0dAD9f5CM7UnlGQXVj8UKcxELuMazHpxc=','student',NULL,'1111@qq.com',NULL,0,NULL,'2025-12-01 15:55:43.231567','2025-12-01 15:55:43.231567',NULL),(11,'test_user','pbkdf2_sha256$600000$duvnVbgUXqVckGrgJowvcJ$TU1icIE4fMM+47tKaRvPIH+vObQHp3Wki5HO2f94WLA=','student',NULL,'test@example.com',NULL,0,NULL,'2025-12-02 03:45:00.077233','2025-12-02 03:45:00.077233',NULL),(12,'ZMC','pbkdf2_sha256$600000$RINwb5dvJPFATOYdQZBevz$S6DkW3hXyO59WG9b1zgSig9tTWmy4CYjhvCuA24Dihw=','student',NULL,'111@qq.com',NULL,0,NULL,'2025-12-02 06:04:59.456811','2025-12-02 06:04:59.456811',NULL);
/*!40000 ALTER TABLE `sys_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher_profile`
--

DROP TABLE IF EXISTS `teacher_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher_profile` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '对应 sys_user.id',
  `teacher_no` varchar(50) DEFAULT NULL COMMENT '工号',
  `college` varchar(100) DEFAULT NULL COMMENT '学院',
  `title` varchar(50) DEFAULT NULL COMMENT '职称',
  `research_area` varchar(200) DEFAULT NULL COMMENT '研究方向',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `teacher_profile_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='教师信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher_profile`
--

LOCK TABLES `teacher_profile` WRITE;
/*!40000 ALTER TABLE `teacher_profile` DISABLE KEYS */;
INSERT INTO `teacher_profile` VALUES (1,3,'T2024001','信息工程学院','讲师','数据结构、算法设计');
/*!40000 ALTER TABLE `teacher_profile` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-02 15:34:51
