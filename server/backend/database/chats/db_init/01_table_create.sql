CREATE TABLE chats (
	id SERIAL,
	name VARCHAR (100) NOT NULL UNIQUE,
	user_1 INT NOT NULL,
	user_2 INT NOT NULL,
	CHECK (user_1 <> user_2),
	PRIMARY KEY (id)
);

CREATE TABLE messeges (
	date TIMESTAMP DEFAULT(current_timestamp),
	user_id INT NOT NULL,
    chat_id INT NOT NULL,
	text VARCHAR(1000) NOT NULL,
	FOREIGN KEY (chat_id) REFERENCES chats(id)
);
