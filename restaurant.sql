CREATE DATABASE tripadvisor
USE tripadvisor

CREATE USER 'ahmed'@'localhost' IDENTIFIED BY 'ahmed123';
GRANT ALL PRIVILEGES ON tripadvisor.* TO 'ahmed'@'localhost';
FLUSH PRIVILEGES;

CREATE TABLE restaurants (
	restaurant_name VARCHAR(255) PRIMARY KEY,
    url VARCHAR(255),
    about TEXT,
    rating FLOAT,
    price_range VARCHAR(255),
    cuisine TEXT,
    special_diet TEXT,
    meals TEXT,
    features TEXT,
    location TEXT,
    google_maps_link VARCHAR(255),
    website VARCHAR(255),
    email VARCHAR(255),
    phone_number VARCHAR(255)
);

