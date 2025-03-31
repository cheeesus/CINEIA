INSERT INTO users (id, email, password_hash) VALUES
(1, 'massyl.ouldyounes@gmail.com', 'hash1'),
(2, 'bourezghiba@gmail.com', 'hash2'),
(3, 'yann.rospars@icloud.com', 'hash3'),
(4, 'mariaitferhat@gmail.com', 'hash4');



INSERT INTO view_history (user_id, movie_id) VALUES
-- MrDreamer watched Toy Story and 8844
(1, 862),
(1, 8844),

-- Fraujaz watched Toy Story and 15602
(2, 862),
(2, 15602),

-- Yann Rospars watched 8844 and 31357
(3, 8844),
(3, 31357),

-- Maria watched Toy Story and 11862
(4, 862),
(4, 11862);


SELECT * FROM view_history ORDER BY user_id;
