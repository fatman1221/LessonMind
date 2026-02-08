-- 作业系统新增表 SQL 脚本
-- 注意：如果使用 SQLAlchemy ORM，表会自动创建，此脚本仅作为参考

USE teacher_prep_system;

-- 1. 更新 users 表，添加 student 角色支持
-- 注意：role 字段已经存在，只需要确保支持 'student' 值
-- ALTER TABLE `users` MODIFY COLUMN `role` VARCHAR(20) DEFAULT 'teacher' COMMENT '角色：teacher, admin, student';

-- 2. 创建班级表
CREATE TABLE IF NOT EXISTS `classes` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `teacher_id` INT NOT NULL COMMENT '教师ID',
  `name` VARCHAR(100) NOT NULL COMMENT '班级名称',
  `description` TEXT NULL DEFAULT NULL COMMENT '班级描述',
  `subject` VARCHAR(50) NULL DEFAULT NULL COMMENT '学科',
  `grade` VARCHAR(20) NULL DEFAULT NULL COMMENT '学段',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  INDEX `idx_teacher_id` (`teacher_id`),
  INDEX `idx_subject` (`subject`),
  CONSTRAINT `fk_classes_teacher` 
    FOREIGN KEY (`teacher_id`) 
    REFERENCES `users` (`id`) 
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='班级表';

-- 3. 创建班级学生关系表
CREATE TABLE IF NOT EXISTS `class_students` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `class_id` INT NOT NULL COMMENT '班级ID',
  `student_id` INT NOT NULL COMMENT '学生ID',
  `joined_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_class_student` (`class_id`, `student_id`),
  INDEX `idx_class_id` (`class_id`),
  INDEX `idx_student_id` (`student_id`),
  CONSTRAINT `fk_class_students_class` 
    FOREIGN KEY (`class_id`) 
    REFERENCES `classes` (`id`) 
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_class_students_student` 
    FOREIGN KEY (`student_id`) 
    REFERENCES `users` (`id`) 
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='班级学生关系表';

-- 4. 创建作业表
CREATE TABLE IF NOT EXISTS `assignments` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `teacher_id` INT NOT NULL COMMENT '教师ID',
  `class_id` INT NOT NULL COMMENT '班级ID',
  `title` VARCHAR(200) NOT NULL COMMENT '作业标题',
  `description` TEXT NULL DEFAULT NULL COMMENT '作业描述',
  `questions` JSON NOT NULL COMMENT '题目列表（JSON格式）',
  `deadline` DATETIME NULL DEFAULT NULL COMMENT '截止时间',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_published` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否已发布',
  PRIMARY KEY (`id`),
  INDEX `idx_teacher_id` (`teacher_id`),
  INDEX `idx_class_id` (`class_id`),
  INDEX `idx_is_published` (`is_published`),
  INDEX `idx_deadline` (`deadline`),
  CONSTRAINT `fk_assignments_teacher` 
    FOREIGN KEY (`teacher_id`) 
    REFERENCES `users` (`id`) 
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_assignments_class` 
    FOREIGN KEY (`class_id`) 
    REFERENCES `classes` (`id`) 
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='作业表';

-- 5. 创建作业提交表
CREATE TABLE IF NOT EXISTS `assignment_submissions` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `assignment_id` INT NOT NULL COMMENT '作业ID',
  `student_id` INT NOT NULL COMMENT '学生ID',
  `answers` JSON NOT NULL COMMENT '学生答案（JSON格式：{question_id: answer}）',
  `score` FLOAT NULL DEFAULT NULL COMMENT '得分',
  `total_score` FLOAT NULL DEFAULT NULL COMMENT '总分',
  `is_graded` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否已批改',
  `submitted_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
  `graded_at` DATETIME NULL DEFAULT NULL COMMENT '批改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_assignment_student` (`assignment_id`, `student_id`),
  INDEX `idx_assignment_id` (`assignment_id`),
  INDEX `idx_student_id` (`student_id`),
  INDEX `idx_submitted_at` (`submitted_at`),
  CONSTRAINT `fk_submissions_assignment` 
    FOREIGN KEY (`assignment_id`) 
    REFERENCES `assignments` (`id`) 
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_submissions_student` 
    FOREIGN KEY (`student_id`) 
    REFERENCES `users` (`id`) 
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='作业提交表';

-- 查看所有新表
SHOW TABLES LIKE '%class%';
SHOW TABLES LIKE '%assignment%';

-- 查看表结构
DESCRIBE classes;
DESCRIBE class_students;
DESCRIBE assignments;
DESCRIBE assignment_submissions;

