CREATE DATABASE IF NOT EXISTS monitoring_db;
use monitoring_db;

CREATE TABLE  IF NOT EXISTS user (
    id INT NOT NULL AUTO_INCREMENT,
    email VARCHAR(500),
    password VARCHAR(200),
    is_admin BOOLEAN,
    PRIMARY KEY (id)
);

CREATE TABLE  IF NOT EXISTS websites (
    id INT NOT NULL AUTO_INCREMENT,
    url VARCHAR(200),
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS checks (
	id INT NOT NULL AUTO_INCREMENT,
	websites int,
	checkTime datetime,
    request_result int,
	PRIMARY KEY (id),
	FOREIGN KEY (websites) REFERENCES websites(id)
);

INSERT INTO user (email, password, is_admin) VALUES ('admin@admin.com', '$argon2i$v=19$m=512,t=2,p=2$07qXMsb4P4fQ+p9T6l3rvQ$hWU817VMNDP/E9l21rYOKQ', true);
