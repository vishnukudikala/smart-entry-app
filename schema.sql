-- Smart Entry App - MySQL Schema
-- Run this in your MySQL database

CREATE DATABASE IF NOT EXISTS smart_entry_db;
USE smart_entry_db;

CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    venue VARCHAR(255),
    event_date DATETIME NOT NULL,
    price DECIMAL(10, 2) DEFAULT 0.00,
    capacity INT DEFAULT 100,
    tickets_sold INT DEFAULT 0,
    image_url VARCHAR(500),
    category VARCHAR(100),
    status ENUM('upcoming', 'ongoing', 'completed', 'cancelled') DEFAULT 'upcoming',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    booking_ref VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    age INT,
    id_proof VARCHAR(100),
    num_tickets INT DEFAULT 1,
    total_amount DECIMAL(10, 2),
    payment_status ENUM('pending', 'paid', 'failed') DEFAULT 'pending',
    payment_id VARCHAR(255),
    qr_code_path VARCHAR(500),
    entry_code VARCHAR(20) UNIQUE NOT NULL,
    checked_in BOOLEAN DEFAULT FALSE,
    checked_in_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

-- Sample Events
INSERT INTO events (title, description, venue, event_date, price, capacity, category, image_url) VALUES
('Neon Nights Music Festival', 'A spectacular night of electronic music featuring top DJs from around the world. Immerse yourself in lights, sounds, and an unforgettable atmosphere.', 'Grand Arena, Mumbai', '2026-05-15 20:00:00', 1299.00, 500, 'Music', 'https://images.unsplash.com/photo-1540039155733-5bb30b53aa14?w=800'),
('Tech Summit 2026', 'Annual technology conference bringing together innovators, entrepreneurs and tech leaders. Keynotes, workshops, and networking opportunities.', 'Convention Center, Bangalore', '2026-05-22 09:00:00', 2499.00, 1000, 'Conference', 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800'),
('Comedy Gala Night', 'An evening of non-stop laughter featuring the country best stand-up comedians. Family-friendly fun for everyone!', 'City Auditorium, Delhi', '2026-06-01 19:30:00', 799.00, 300, 'Entertainment', 'https://images.unsplash.com/photo-1585699324551-f6c309eedeca?w=800'),
('Art & Culture Expo', 'Explore breathtaking artworks from 200+ artists. Live painting, sculpture demos, and cultural performances throughout the day.', 'Heritage Gallery, Chennai', '2026-06-10 10:00:00', 499.00, 800, 'Art', 'https://images.unsplash.com/photo-1578926288207-a90a5366759d?w=800'),
('Startup Pitch Fest', 'Watch 50 startups compete for ₹1 crore in funding. Network with investors, mentors, and fellow entrepreneurs.', 'Innovation Hub, Hyderabad', '2026-06-20 10:00:00', 999.00, 400, 'Business', 'https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=800'),
('Bollywood Dance Night', 'Dance to the hottest Bollywood hits with live performances and DJ sets. Costume contest with prizes!', 'The Grand Ballroom, Pune', '2026-07-04 21:00:00', 599.00, 600, 'Music', 'https://images.unsplash.com/photo-1547153760-18fc86324498?w=800');
