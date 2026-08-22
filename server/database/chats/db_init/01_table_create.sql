CREATE TABLE chats (
	id SERIAL PRIMARY KEY,
	name VARCHAR (100),
	user_1 INT NOT NULL,
	user_2 INT NOT NULL
);

CREATE TABLE messages (
	date TIMESTAMP DEFAULT(current_timestamp),
    chat_id INT REFERENCES chats(id) NOT NULL,
	user_id INT NOT NULL,
	text VARCHAR(1000) NOT NULL
);
