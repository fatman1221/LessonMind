-- 用户收藏表 SQL 脚本
-- 注意：如果使用 SQLAlchemy ORM，表会自动创建，此脚本仅作为参考

USE teacher_prep_system;

-- 创建用户收藏表
CREATE TABLE IF NOT EXISTS `user_favorites` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `title` VARCHAR(200) NOT NULL COMMENT '收藏标题',
  `content_type` VARCHAR(50) NOT NULL COMMENT '内容类型：teaching_design, chat, question, custom',
  `content` TEXT NOT NULL COMMENT '收藏内容（支持HTML富文本）',
  `tags` VARCHAR(500) NULL DEFAULT NULL COMMENT '标签，逗号分隔',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_content_type` (`content_type`),
  INDEX `idx_created_at` (`created_at`),
  CONSTRAINT `fk_user_favorites_user` 
    FOREIGN KEY (`user_id`) 
    REFERENCES `users` (`id`) 
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户收藏表';

-- 查看表结构
DESCRIBE user_favorites;

