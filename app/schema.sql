-- -- Drop existing tables
-- DROP TABLE IF EXISTS medication_logs;
-- DROP TABLE IF EXISTS medications;
-- DROP TABLE IF EXISTS symptoms;
-- DROP TABLE IF EXISTS height_logs;
-- DROP TABLE IF EXISTS profiles;

-- -- Create medications table with new structure
-- CREATE TABLE medications (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     name TEXT NOT NULL,
--     dosage_schedule TEXT,
--     form_type TEXT,
--     stock INTEGER NOT NULL,
--     user_id INTEGER NOT NULL,
--     description TEXT,
--     next_dose DATETIME,
--     profile_id INTEGER,
--     FOREIGN KEY (user_id) REFERENCES users (id),
--     FOREIGN KEY (profile_id) REFERENCES profiles (id)
-- );

-- -- Create medication_logs table
-- CREATE TABLE medication_logs (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     medication_id INTEGER NOT NULL,
--     user_id INTEGER NOT NULL,
--     taken_at DATETIME NOT NULL,
--     status TEXT NOT NULL,
--     FOREIGN KEY (medication_id) REFERENCES medications (id),
--     FOREIGN KEY (user_id) REFERENCES users (id)
-- );

-- -- Create symptoms table
-- CREATE TABLE symptoms (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     user_id INTEGER NOT NULL,
--     profile_id INTEGER NOT NULL,
--     medication_id INTEGER,
--     description TEXT NOT NULL,
--     severity TEXT NOT NULL,
--     logged_at DATETIME NOT NULL,
--     FOREIGN KEY (user_id) REFERENCES users (id),
--     FOREIGN KEY (profile_id) REFERENCES profiles (id),
--     FOREIGN KEY (medication_id) REFERENCES medications (id)
-- );

-- -- Create height_logs table
-- CREATE TABLE height_logs (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     user_id INTEGER NOT NULL,
--     profile_id INTEGER NOT NULL,
--     height FLOAT NOT NULL,
--     logged_at DATETIME NOT NULL,
--     FOREIGN KEY (user_id) REFERENCES users (id),
--     FOREIGN KEY (profile_id) REFERENCES profiles (id)
-- );

-- -- Create profiles table
-- CREATE TABLE profiles (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     user_id INTEGER NOT NULL,
--     name TEXT NOT NULL,
--     relationship TEXT NOT NULL,
--     FOREIGN KEY (user_id) REFERENCES users (id)
-- ); 

-- new code

-- Drop existing tables
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS medication_logs;
DROP TABLE IF EXISTS medications;
DROP TABLE IF EXISTS symptoms;
DROP TABLE IF EXISTS height_logs;
DROP TABLE IF EXISTS profiles;

-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

-- Create medications table
CREATE TABLE medications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    dosage_schedule TEXT,
    form_type TEXT,
    stock INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    description TEXT,
    next_dose DATETIME,
    profile_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (profile_id) REFERENCES profiles (id)
);

-- Create medication_logs table
CREATE TABLE medication_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medication_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    taken_at DATETIME NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (medication_id) REFERENCES medications (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create symptoms table
CREATE TABLE symptoms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    profile_id INTEGER NOT NULL,
    medication_id INTEGER,
    description TEXT NOT NULL,
    severity TEXT NOT NULL,
    logged_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (profile_id) REFERENCES profiles (id),
    FOREIGN KEY (medication_id) REFERENCES medications (id)
);

-- Create height_logs table
CREATE TABLE height_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    profile_id INTEGER NOT NULL,
    height FLOAT NOT NULL,
    logged_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (profile_id) REFERENCES profiles (id)
);

-- Create profiles table
CREATE TABLE profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    relationship TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);