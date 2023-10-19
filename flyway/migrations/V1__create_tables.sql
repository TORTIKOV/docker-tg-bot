-- V1__Create_deliverymen.sql
CREATE TABLE deliverymen (
    tg_id BIGINT PRIMARY KEY NOT NULL,
    career_start DATE,
    work_until DATE,
    experience_month SMALLINT,
    complete SMALLINT,
    status BOOLEAN,
    username VARCHAR(32)
);
-- V2__Create_moderator.sql
CREATE TABLE moderator (
    tg_id BIGINT PRIMARY KEY,
    status BOOLEAN
);
-- V3__Create_order.sql
CREATE TABLE "order" (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    client_id BIGINT,
    deliveryman_id BIGINT,
    status VARCHAR(20),
    creation_date DATE,
    creation_time TIME,
    order_place VARCHAR(30),
    until_date DATE,
    until_time TIME,
    payment_method VARCHAR(50),
    comment VARCHAR(100),
    delivery_option VARCHAR(20),
    dorm INT,
    floor INT,
    room INT
);
-- V4__Create_user.sql
CREATE TABLE "user" (
    name VARCHAR(30),
    phone BIGINT,
    dorm INT,
    tgid BIGINT PRIMARY KEY,
    floor INT,
    room INT,
    start_date DATE DEFAULT '2023-09-02',
    business_test TEXT
);
