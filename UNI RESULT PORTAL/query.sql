--- =============================================
-- University Portal - Final Corrected Script
-- Internal<=20, Practical<=30, Theory<=50, Total<=100
-- =============================================

USE university_portal;

-- Drop and recreate tables
DROP TABLE IF EXISTS marks;
DROP TABLE IF EXISTS students;

-- Students Table
CREATE TABLE students (
    rollno VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    program VARCHAR(50) NOT NULL DEFAULT 'B.Sc. ITM',
    batch VARCHAR(20) NOT NULL DEFAULT '2024-27',
    password VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Marks Table
CREATE TABLE marks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rollno VARCHAR(20) NOT NULL,
    semester INT NOT NULL,
    subject VARCHAR(150) NOT NULL,
    internal INT NOT NULL CHECK (internal BETWEEN 0 AND 20),
    practical INT NOT NULL CHECK (practical BETWEEN 0 AND 30),
    theory INT NOT NULL CHECK (theory BETWEEN 0 AND 50),
    total INT NOT NULL CHECK (total <= 100),
    grade VARCHAR(5) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (rollno) REFERENCES students(rollno) ON DELETE CASCADE,
    UNIQUE KEY uk_student_sem_subject (rollno, semester, subject)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert 30 Students
INSERT INTO students (rollno, name, program, batch, password) VALUES
('24DIT001', 'Rahul Sharma', 'B.Sc. ITM', '2024-27', 'rahul123'),
('24DIT002', 'Priya Patel', 'B.Sc. ITM', '2024-27', 'priya456'),
('24DIT003', 'Amit Kumar', 'B.Sc. ITM', '2024-27', 'amit789'),
('24DIT004', 'Sneha Gupta', 'B.Sc. ITM', '2024-27', 'sneha101'),
('24DIT005', 'Rohan Singh', 'B.Sc. ITM', '2024-27', 'rohan202'),
('24DIT006', 'Ananya Das', 'B.Sc. ITM', '2024-27', 'ananya303'),
('24DIT007', 'Vikram Malhotra', 'B.Sc. ITM', '2024-27', 'vikram404'),
('24DIT008', 'Meera Nair', 'B.Sc. ITM', '2024-27', 'meera505'),
('24DIT009', 'Arjun Rao', 'B.Sc. ITM', '2024-27', 'arjun606'),
('24DIT010', 'Kavya Menon', 'B.Sc. ITM', '2024-27', 'kavya707'),
('24DIT011', 'Siddharth Jain', 'B.Sc. ITM', '2024-27', 'sid808'),
('24DIT012', 'Pooja Reddy', 'B.Sc. ITM', '2024-27', 'pooja909'),
('24DIT013', 'Neha Sharma', 'B.Sc. ITM', '2024-27', 'neha010'),
('24DIT014', 'Aditya Verma', 'B.Sc. ITM', '2024-27', 'aditya111'),
('24DIT015', 'Ishita Bose', 'B.Sc. ITM', '2024-27', 'ishita222'),
('24DIT016', 'Ravi Kumar', 'B.Sc. ITM', '2024-27', 'ravi333'),
('24DIT017', 'Simran Kaur', 'B.Sc. ITM', '2024-27', 'simran444'),
('24DIT018', 'Karan Malhotra', 'B.Sc. ITM', '2024-27', 'karan555'),
('24DIT019', 'Tanya Singh', 'B.Sc. ITM', '2024-27', 'tanya666'),
('24DIT020', 'Mohit Agarwal', 'B.Sc. ITM', '2024-27', 'mohit777'),
('24DIT021', 'Anika Roy', 'B.Sc. ITM', '2024-27', 'anika888'),
('24DIT022', 'Devansh Patel', 'B.Sc. ITM', '2024-27', 'devansh999'),
('24DIT023', 'Riya Sen', 'B.Sc. ITM', '2024-27', 'riya1010'),
('24DIT024', 'Saurabh Khan', 'B.Sc. ITM', '2024-27', 'saurabh1111'),
('24DIT025', 'Pallavi Joshi', 'B.Sc. ITM', '2024-27', 'pallavi1212'),
('24DIT026', 'Harsh Vardhan', 'B.Sc. ITM', '2024-27', 'harsh1313'),
('24DIT027', 'Nisha Mehta', 'B.Sc. ITM', '2024-27', 'nisha1414'),
('24DIT028', 'Aarav Gupta', 'B.Sc. ITM', '2024-27', 'aarav1515'),
('24DIT029', 'Diya Sharma', 'B.Sc. ITM', '2024-27', 'diya1616'),
('24DIT030', 'Vihaan Reddy', 'B.Sc. ITM', '2024-27', 'vihaan1717');

-- =============================================
-- Generate Marks Procedure (Final Version)
-- =============================================
DELIMITER //

DROP PROCEDURE IF EXISTS generate_marks;

CREATE PROCEDURE generate_marks()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE roll VARCHAR(20);
    DECLARE sem INT;
    DECLARE subj VARCHAR(100);
    DECLARE internal_val INT;
    DECLARE practical_val INT;
    DECLARE theory_val INT;
    DECLARE total_val INT;
    DECLARE grade_val VARCHAR(5);
    DECLARE total_inserted INT DEFAULT 0;
    DECLARE j INT;

    DECLARE subjects1 JSON DEFAULT '["Data Structure using C", "Operating Systems", "Minor", "MDC"]';
    DECLARE subjects2 JSON DEFAULT '["Data Structures", "Mathematics-II", "Business Communication"]';
    DECLARE subjects3 JSON DEFAULT '["Database Management Systems", "Web Technologies", "Computer Networks"]';
    DECLARE subjects4 JSON DEFAULT '["Software Engineering", "Business Analytics", "Java Programming"]';
    DECLARE subjects5 JSON DEFAULT '["Cloud Computing", "Machine Learning", "IT Project Management"]';
    DECLARE subjects6 JSON DEFAULT '["Internship / Project", "Cyber Security", "Entrepreneurship"]';

    WHILE i <= 30 DO
        SET roll = CONCAT('24DIT', LPAD(i, 3, '0'));
        
        SET sem = 1;
        WHILE sem <= 6 DO
            
            CASE sem
                WHEN 1 THEN SET @subj_list = subjects1;
                WHEN 2 THEN SET @subj_list = subjects2;
                WHEN 3 THEN SET @subj_list = subjects3;
                WHEN 4 THEN SET @subj_list = subjects4;
                WHEN 5 THEN SET @subj_list = subjects5;
                ELSE SET @subj_list = subjects6;
            END CASE;
            
            SET j = 0;
            WHILE j < JSON_LENGTH(@subj_list) DO
                SET subj = JSON_UNQUOTE(JSON_EXTRACT(@subj_list, CONCAT('$[', j, ']')));
                
                -- Actual Random Marks with Constraints
                SET internal_val  = FLOOR(RAND() * 21);        -- 0 to 20
                SET practical_val = FLOOR(RAND() * 31);        -- 0 to 30
                SET theory_val    = FLOOR(RAND() * 51);        -- 0 to 50
                
                SET total_val = internal_val + practical_val + theory_val;
                
                -- Ensure total <= 100
                IF total_val > 100 THEN
                    SET total_val = 100;
                    SET theory_val = total_val - internal_val - practical_val;
                END IF;
                
                -- Grade Calculation
                CASE 
                    WHEN total_val >= 90 THEN SET grade_val = 'O';
                    WHEN total_val >= 80 THEN SET grade_val = 'A+';
                    WHEN total_val >= 70 THEN SET grade_val = 'A';
                    WHEN total_val >= 60 THEN SET grade_val = 'B+';
                    ELSE SET grade_val = 'B';
                END CASE;
                
                INSERT IGNORE INTO marks 
                (rollno, semester, subject, internal, practical, theory, total, grade)
                VALUES (roll, sem, subj, internal_val, practical_val, theory_val, total_val, grade_val);
                
                IF ROW_COUNT() > 0 THEN
                    SET total_inserted = total_inserted + 1;
                END IF;
                
                SET j = j + 1;
            END WHILE;
            
            SET sem = sem + 1;
        END WHILE;
        
        SET i = i + 1;
    END WHILE;
    
    SELECT CONCAT('✅ Marks generated successfully! Total records inserted: ', total_inserted) AS status;
END //

DELIMITER ;

-- Run the procedure
CALL generate_marks();

-- =============================================
-- Verification + CGPA
-- =============================================
SELECT COUNT(*) AS total_marks_records FROM marks;

-- Sample Marks
SELECT rollno, semester, subject, internal, practical, theory, total, grade 
FROM marks 
WHERE rollno = '24DIT001' 
ORDER BY semester LIMIT 10;