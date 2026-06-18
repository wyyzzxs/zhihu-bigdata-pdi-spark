USE zhihu_bigdata;

DROP TABLE IF EXISTS zhihu_user;

CREATE TABLE zhihu_user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    url_token VARCHAR(255) NULL,
    name VARCHAR(255) NULL,
    gender INT DEFAULT -1,
    gender_label VARCHAR(20) DEFAULT '未知',
    answer_count INT DEFAULT 0,
    articles_count INT DEFAULT 0,
    follower_count INT DEFAULT 0,
    following_count INT DEFAULT 0,
    headline VARCHAR(1000) NULL,
    location VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_gender (gender),
    INDEX idx_answer_count (answer_count),
    INDEX idx_articles_count (articles_count),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
