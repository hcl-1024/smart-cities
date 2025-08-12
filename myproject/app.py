from random import random
from flask import Flask, request, session, jsonify , render_template, redirect, url_for
import sqlite3
import time
import math
import os
import numpy as np
from sklearn.preprocessing import StandardScaler

baseurl = "/smartcities"
app = Flask(__name__, static_url_path=baseurl)
app.secret_key = 'your_secret_key_here'
DATABASE = 'gps_timer.db'

# GPS coordinates (customize these with your specific locations)
START_GPS = (37.7749, -122.4194)  # San Francisco coordinates
END_GPS = (34.0522, -118.2437)    # Los Angeles coordinates
GPS_THRESHOLD = 0.01  # Approximately 1.1 km (adjust for your needs)

# Initialize database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fingerprint TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.execute('''
        CREATE TABLE IF NOT EXISTS timer_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            elapsed_time REAL,
            temperature REAL,      -- Celsius
            precipitation REAL,    -- mm
            humidity REAL,         -- Percentage
            traffic INTEGER,       -- 1-5 scale
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        ''')
        conn.commit()

# Create database if not exists
if not os.path.exists(DATABASE):
    init_db()

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS points in kilometers"""
    R = 6371  # Earth radius in km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat/2) * math.sin(dlat/2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2) * math.sin(dlon/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def is_near_location(current_lat, current_lon, target_lat, target_lon, threshold_km):
    """Check if current location is within threshold distance of target"""
    """distance = haversine(current_lat, current_lon, target_lat, target_lon)
    return distance <= threshold_km"""
    return True # Simulate always being near the location for testing

def get_user_id(fingerprint):
    """Get or create user ID based on fingerprint"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # Try to get existing user
        cursor.execute("SELECT id FROM users WHERE fingerprint = ?", (fingerprint,))
        user = cursor.fetchone()
        
        if user:
            return user[0]
        else:
            # Create new user
            cursor.execute("INSERT INTO users (fingerprint) VALUES (?)", (fingerprint,))
            conn.commit()
            return cursor.lastrowid

#check how each url matches
@app.route(baseurl + '/check-location-starting')
def check_location_starting():
    """Endpoint to check if user is at start/end location and manage timer"""
    # Get current location from request
    """data = request.json
    current_lat = data.get('latitude')
    current_lon = data.get('longitude')"""

    
    
    """if not current_lat or not current_lon:
        return jsonify({'error': 'Missing coordinates'}), 400"""
    
    # Create fingerprint from IP + User-Agent
    fingerprint = f"{request.remote_addr}-{request.user_agent.string}"
    
    # Get or create user
    user_id = get_user_id(fingerprint)
    
    # Check if at START location
    if True: #is_near_location(0, 0, *START_GPS, GPS_THRESHOLD)
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            
            # Check for existing active timer
            cursor.execute('''
            SELECT id FROM timer_events 
            WHERE user_id = ? AND end_time IS NULL
            ''', (user_id,))
            active_timer = cursor.fetchone()
            
            if not active_timer:
                # Start new timer
                start_time = time.time()
                cursor.execute('''
                INSERT INTO timer_events (user_id, start_time)
                VALUES (?, ?)
                ''', (user_id, start_time))
                conn.commit()

                return redirect(url_for('check_location_ending'))
            else:
                response = {
                    'action': 'already_started',
                    'message': 'Timer already running'
                }
    
    return render_template("check-location-starting.html")

@app.route(baseurl + '/check-location-ending')
def check_location_ending():
    """Endpoint to check if user is at start/end location and manage timer"""
    # Get current location from request
    """data = request.json
    current_lat = data.get('latitude')
    current_lon = data.get('longitude')
    
    if not current_lat or not current_lon:
        return jsonify({'error': 'Missing coordinates'}), 400"""
    
    # Create fingerprint from IP + User-Agent
    fingerprint = f"{request.remote_addr}-{request.user_agent.string}"
    
    # Get or create user
    user_id = get_user_id(fingerprint)
    
    # Check locations
    response = {'action': 'none'}

    # Check if at END location
    if True: #is_near_location(current_lat, current_lon, *END_GPS, GPS_THRESHOLD):
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            
            # Get active timer
            cursor.execute('''
            SELECT id, start_time FROM timer_events 
            WHERE user_id = ? AND end_time IS NULL
            ORDER BY start_time DESC LIMIT 1
            ''', (user_id,))
            active_timer = cursor.fetchone()
            
            if active_timer:
                # Stop the timer
                timer_id, start_time = active_timer
                end_time = time.time()
                elapsed = math.floor(end_time - start_time)
                
                # Update database
                cursor.execute('''
                UPDATE timer_events 
                SET end_time = ?, elapsed_time = ?
                WHERE id = ?
                ''', (end_time, elapsed, timer_id))
                conn.commit()

                now = time.time()
                rank = conn.execute('''
                SELECT *
                FROM timer_events AS e1
                WHERE id = ?
                ORDER BY elapsed_time
                ''', (timer_id,)).fetchone()
                time_rank = rank[0]
                print(time_rank)
    
                if rank is None:
                    return jsonify({
                    'error': 'Ranking not available',
                    'reason': 'Not enough data or event not found'
                    }), 404
                return redirect(url_for('result_page', rank=time_rank, time=round(elapsed, 2)))
            else:
                response = {
                    'action': 'no_active_timer',
                    'message': 'No active timer to stop'
                }
    return render_template("check-location-ending.html")

    
@app.route(baseurl + '/user-history/<int:user_id>')
def user_history(user_id):
    """Get timer history for a specific user"""
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get timer events
        cursor.execute('''
        SELECT id, 
               datetime(start_time, 'unixepoch') AS start_time, 
               datetime(end_time, 'unixepoch') AS end_time,
               elapsed_time
        FROM timer_events 
        WHERE user_id = ?
        ORDER BY start_time DESC
        ''', (user_id,))
        events = cursor.fetchall()
    
    return render_template("user-history.html", entries=events)

@app.route(baseurl + '/all-history')
def all_history():
    """Get all timer events from all users"""
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT u.id AS user_id, u.created_at,
               t.id AS event_id, 
               datetime(t.start_time, 'unixepoch') AS start_time,
               datetime(t.end_time, 'unixepoch') AS end_time,
               t.elapsed_time
        FROM users u
        JOIN timer_events t ON u.id = t.user_id
        ORDER BY t.start_time DESC
        ''')
        events = cursor.fetchall()
    
    #return the template
    return render_template("all-history.html", entries=events)

@app.route(baseurl + '/result-page/<int:rank>/<int:time>')
def result_page(rank, time):
    def calculate_carbon_emissions(time_minutes):
        # Calculate distance based on time and average speed
        distance_km = (time_minutes / 60) * 30
        # Calculate carbon emissions for the trip
        carbon_emissions = distance_km * 0.2
        return carbon_emissions

    carbon = calculate_carbon_emissions(time)
    carbon = round(carbon, 0)
    return render_template('result-page.html', rank=rank, carbon=carbon, time=time)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)