CREATE DATABASE `iargus` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
DROP TABLE IF EXISTS `car_details`;
CREATE TABLE `car_details` (
  `id` int NOT NULL AUTO_INCREMENT,
  `state` varchar(2) NOT NULL,
  `model` varchar(100) NOT NULL,
  `make` varchar(100) NOT NULL,
  `year` int NOT NULL,
  `mileage` float NOT NULL,
  `price` float NOT NULL,
  `date_added` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=300001 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;