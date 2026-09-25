-- ========================================================
-- Hospital Management System (HMS) Database Schema
-- Compatible with MySQL 5.7+, MySQL 8.0+, MariaDB (XAMPP / phpMyAdmin)
-- ========================================================

CREATE DATABASE IF NOT EXISTS `hospital_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `hospital_db`;

-- --------------------------------------------------------
-- Table: users
-- --------------------------------------------------------
DROP TABLE IF EXISTS `billings`;
DROP TABLE IF EXISTS `medical_records`;
DROP TABLE IF EXISTS `appointments`;
DROP TABLE IF EXISTS `doctors`;
DROP TABLE IF EXISTS `patients`;
DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('admin', 'doctor', 'receptionist', 'patient') NOT NULL,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- Table: patients
-- --------------------------------------------------------
CREATE TABLE `patients` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NULL,
    `full_name` VARCHAR(100) NOT NULL,
    `dob` DATE NOT NULL,
    `gender` ENUM('Male', 'Female', 'Other') NOT NULL,
    `phone` VARCHAR(20) NOT NULL,
    `address` TEXT NULL,
    `emergency_contact` VARCHAR(100) NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_patients_user` FOREIGN KEY (`user_id`) 
        REFERENCES `users`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- Table: doctors
-- --------------------------------------------------------
CREATE TABLE `doctors` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `full_name` VARCHAR(100) NOT NULL,
    `specialization` VARCHAR(100) NOT NULL,
    `phone` VARCHAR(20) NOT NULL,
    `room_number` VARCHAR(20) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_doctors_user` FOREIGN KEY (`user_id`) 
        REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- Table: appointments
-- --------------------------------------------------------
CREATE TABLE `appointments` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `patient_id` INT NOT NULL,
    `doctor_id` INT NOT NULL,
    `appointment_date` DATETIME NOT NULL,
    `status` ENUM('Pending', 'Confirmed', 'Completed', 'Cancelled') DEFAULT 'Pending',
    `reason` TEXT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_appointments_patient` FOREIGN KEY (`patient_id`) 
        REFERENCES `patients`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_appointments_doctor` FOREIGN KEY (`doctor_id`) 
        REFERENCES `doctors`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- Table: medical_records
-- --------------------------------------------------------
CREATE TABLE `medical_records` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `patient_id` INT NOT NULL,
    `doctor_id` INT NOT NULL,
    `diagnosis` TEXT NOT NULL,
    `prescription` TEXT NOT NULL,
    `record_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_medrecords_patient` FOREIGN KEY (`patient_id`) 
        REFERENCES `patients`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_medrecords_doctor` FOREIGN KEY (`doctor_id`) 
        REFERENCES `doctors`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- Table: billings (Admin Revenue & Patient Invoicing)
-- --------------------------------------------------------
CREATE TABLE `billings` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `patient_id` INT NOT NULL,
    `appointment_id` INT NULL,
    `amount` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `status` ENUM('Paid', 'Unpaid', 'Pending') DEFAULT 'Pending',
    `billing_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_billings_patient` FOREIGN KEY (`patient_id`) 
        REFERENCES `patients`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_billings_appointment` FOREIGN KEY (`appointment_id`) 
        REFERENCES `appointments`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================================
-- Sample Seed Data
-- Passwords:
-- admin: admin123
-- dr_sarah: doctor123
-- dr_james: doctor123
-- receptionist1: rec123
-- patient_john: patient123
-- patient_emily: patient123
-- ========================================================

INSERT INTO `users` (`id`, `username`, `password_hash`, `role`, `email`) VALUES
(1, 'admin', 'scrypt:32768:8:1$fSGn4eD9LvBQIBMj$eb025096fb7dd86b65458a76504b6b94a1b4648700d24eb121f11d84f81a1eb9b517049e6b6565fffd780f233985b544f28c8454fd8963d2b8bfbf117580efaa', 'admin', 'admin@medicare.com'),
(2, 'dr_sarah', 'scrypt:32768:8:1$IfUpP9y6hNOKpfEs$fcf08d25743827b2d254657c83cb26fd2c3e4eb0fed41f29bd6ccd4541cf8a322b51363a404556cb2b1639dd9203a06219c3af1d64e006fd8e9cee00423a6e8e', 'doctor', 'sarah.jenkins@medicare.com'),
(3, 'dr_james', 'scrypt:32768:8:1$IfUpP9y6hNOKpfEs$fcf08d25743827b2d254657c83cb26fd2c3e4eb0fed41f29bd6ccd4541cf8a322b51363a404556cb2b1639dd9203a06219c3af1d64e006fd8e9cee00423a6e8e', 'doctor', 'james.wilson@medicare.com'),
(4, 'receptionist1', 'scrypt:32768:8:1$ypRnFMzoIa9laheA$bb9400cd0d098d73ae1e8f1dba07ba4bb225604efa155b18c7ed78e46c8cc3f7555b0a2c77031ec5334bdfbf9d619dafec77c79f818a876a29e7c1c86da3775a', 'receptionist', 'frontdesk@medicare.com'),
(5, 'patient_john', 'scrypt:32768:8:1$WGBh4m6gx1njUKs0$08edd96109f1ed5f006e202a0be0af5e5144f15f74723c6f132d4d76a31844ccee67b03f166fb52e74eea622403e6cbc3e1b90fc850fd59c8ff54870273d8988', 'patient', 'john.doe@gmail.com'),
(6, 'patient_emily', 'scrypt:32768:8:1$WGBh4m6gx1njUKs0$08edd96109f1ed5f006e202a0be0af5e5144f15f74723c6f132d4d76a31844ccee67b03f166fb52e74eea622403e6cbc3e1b90fc850fd59c8ff54870273d8988', 'patient', 'emily.rose@gmail.com');

INSERT INTO `doctors` (`id`, `user_id`, `full_name`, `specialization`, `phone`, `room_number`) VALUES
(1, 2, 'Dr. Sarah Jenkins, MD', 'Cardiology', '+1 (555) 234-5678', 'Room 302-A'),
(2, 3, 'Dr. James Wilson, MD', 'General Medicine & Pediatrics', '+1 (555) 345-6789', 'Room 105-B');

INSERT INTO `patients` (`id`, `user_id`, `full_name`, `dob`, `gender`, `phone`, `address`, `emergency_contact`) VALUES
(1, 5, 'John Doe', '1988-05-14', 'Male', '+1 (555) 019-2834', '742 Evergreen Terrace, Springfield', 'Jane Doe (+1 555-019-2835)'),
(2, 6, 'Emily Rose', '1995-11-22', 'Female', '+1 (555) 829-1144', '124 Conch Street, Pacific City', 'Robert Rose (+1 555-829-9988)'),
(3, NULL, 'Michael Chang', '1976-03-30', 'Male', '+1 (555) 431-7720', '88 Maple Ave, Metroville', 'Grace Chang (+1 555-431-7721)');

INSERT INTO `appointments` (`id`, `patient_id`, `doctor_id`, `appointment_date`, `status`, `reason`) VALUES
(1, 1, 1, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 2 HOUR), 'Confirmed', 'Routine cardiology checkup and follow-up on ECG results.'),
(2, 2, 2, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 5 HOUR), 'Confirmed', 'Seasonal allergy symptoms and mild throat irritation.'),
(3, 3, 1, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY), 'Completed', 'Hypertension consultation and prescription renewal.'),
(4, 1, 2, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 2 DAY), 'Pending', 'General wellness assessment.');

INSERT INTO `medical_records` (`id`, `patient_id`, `doctor_id`, `diagnosis`, `prescription`, `record_date`) VALUES
(1, 3, 1, 'Stage 1 Hypertension. Elevated systolic pressure observed during examination.', 'Amlodipine 5mg once daily every morning. Low sodium diet and 30 minutes daily moderate walking.', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY)),
(2, 1, 1, 'Mild sinus tachycardia. Heart sounds normal with regular rhythm.', 'Metoprolol 25mg as advised. Avoid excessive caffeine intake. Follow up in 6 months.', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 20 DAY));

INSERT INTO `billings` (`id`, `patient_id`, `appointment_id`, `amount`, `status`, `billing_date`) VALUES
(1, 3, 3, 150.00, 'Paid', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY)),
(2, 1, 1, 180.00, 'Pending', CURRENT_TIMESTAMP),
(3, 2, 2, 95.00, 'Pending', CURRENT_TIMESTAMP);
