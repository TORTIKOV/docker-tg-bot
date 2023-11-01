CREATE TABLE "user" (
    tg_id BIGINT PRIMARY KEY,
    name VARCHAR(30),
    phone BIGINT,
    dorm INT,
    floor INT,
    room INT,
    start_date DATE DEFAULT '2023-09-02',
    business_test TEXT
);

CREATE TABLE deliverymen (
    tg_id BIGINT PRIMARY KEY,
    career_start DATE,
    work_until DATE,
    experience_month SMALLINT,
    complete SMALLINT,
    status BOOLEAN,
    username VARCHAR(32),
    FOREIGN KEY (tg_id) REFERENCES "user"(tg_id)
);

CREATE TABLE moderator (
    tg_id BIGINT PRIMARY KEY,
    status BOOLEAN,
    FOREIGN KEY (tg_id) REFERENCES "user"(tg_id)
);

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