from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from flask_mysqldb import MySQL
import qrcode
import json
import os
import uuid
import random
import string
from datetime import datetime
from dotenv import load_dotenv
import io
import base64
from PIL import Image

load_dotenv()

app = Flask(__name__)

# MySQL Config
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'smart_entry_db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'smart-entry-secret-2026')

mysql = MySQL(app)

QR_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'qrcodes')
os.makedirs(QR_FOLDER, exist_ok=True)


def generate_entry_code():
    prefix = "SE"
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=8))
    return f"{prefix}-{code}"


def generate_booking_ref():
    return "BK" + str(uuid.uuid4()).replace("-", "").upper()[:12]


def generate_qr_code(data, filename):
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1a1a2e", back_color="white")
    path = os.path.join(QR_FOLDER, filename)
    img.save(path)
    return f"qrcodes/{filename}"


# ─── ROUTES ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/events')
def events():
    return render_template('events.html')


@app.route('/scan')
def scan():
    return render_template('scan.html')


@app.route('/booking/<int:event_id>')
def booking(event_id):
    return render_template('booking.html', event_id=event_id)


@app.route('/ticket/<booking_ref>')
def ticket(booking_ref):
    return render_template('ticket.html', booking_ref=booking_ref)


# ─── API ENDPOINTS ─────────────────────────────────────────────────────────────

@app.route('/api/events', methods=['GET'])
def api_events():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, title, description, venue, event_date, price,
                   capacity, tickets_sold, image_url, category, status
            FROM events
            WHERE status IN ('upcoming', 'ongoing')
            ORDER BY event_date ASC
        """)
        rows = cur.fetchall()
        cur.close()

        events_list = []
        for row in rows:
            events_list.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'venue': row[3],
                'event_date': row[4].strftime('%Y-%m-%d %H:%M') if row[4] else '',
                'price': float(row[5]) if row[5] else 0,
                'capacity': row[6],
                'tickets_sold': row[7],
                'available': row[6] - row[7],
                'image_url': row[8],
                'category': row[9],
                'status': row[10]
            })
        return jsonify({'success': True, 'events': events_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/events/<int:event_id>', methods=['GET'])
def api_event_detail(event_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, title, description, venue, event_date, price,
                   capacity, tickets_sold, image_url, category, status
            FROM events WHERE id = %s
        """, (event_id,))
        row = cur.fetchone()
        cur.close()

        if not row:
            return jsonify({'success': False, 'error': 'Event not found'}), 404

        event = {
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'venue': row[3],
            'event_date': row[4].strftime('%Y-%m-%d %H:%M') if row[4] else '',
            'price': float(row[5]) if row[5] else 0,
            'capacity': row[6],
            'tickets_sold': row[7],
            'available': row[6] - row[7],
            'image_url': row[8],
            'category': row[9],
            'status': row[10]
        }
        return jsonify({'success': True, 'event': event})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/book', methods=['POST'])
def api_book():
    try:
        data = request.get_json()
        event_id = data.get('event_id')
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        age = data.get('age')
        id_proof = data.get('id_proof', '')
        num_tickets = int(data.get('num_tickets', 1))
        payment_method = data.get('payment_method', 'online')

        if not all([event_id, full_name, email, phone]):
            return jsonify({'success': False, 'error': 'Required fields missing'}), 400

        cur = mysql.connection.cursor()

        # Get event
        cur.execute("SELECT id, title, price, capacity, tickets_sold FROM events WHERE id = %s", (event_id,))
        event = cur.fetchone()
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404

        available = event[3] - event[4]
        if num_tickets > available:
            return jsonify({'success': False, 'error': f'Only {available} tickets available'}), 400

        total_amount = float(event[2]) * num_tickets
        booking_ref = generate_booking_ref()
        entry_code = generate_entry_code()

        # Generate QR
        qr_data = json.dumps({
            'booking_ref': booking_ref,
            'entry_code': entry_code,
            'event_id': event_id,
            'event': event[1],
            'name': full_name,
            'email': email,
            'tickets': num_tickets
        })
        qr_filename = f"{booking_ref}.png"
        qr_path = generate_qr_code(qr_data, qr_filename)

        # Insert booking
        cur.execute("""
            INSERT INTO bookings
            (event_id, booking_ref, full_name, email, phone, age, id_proof,
             num_tickets, total_amount, payment_status, qr_code_path, entry_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (event_id, booking_ref, full_name, email, phone, age, id_proof,
              num_tickets, total_amount, 'paid', qr_path, entry_code))

        # Update sold count
        cur.execute("UPDATE events SET tickets_sold = tickets_sold + %s WHERE id = %s",
                    (num_tickets, event_id))

        mysql.connection.commit()
        cur.close()

        return jsonify({
            'success': True,
            'booking_ref': booking_ref,
            'entry_code': entry_code,
            'qr_code': f"/static/{qr_path}",
            'total_amount': total_amount
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ticket/<booking_ref>', methods=['GET'])
def api_ticket(booking_ref):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT b.booking_ref, b.full_name, b.email, b.phone, b.age,
                   b.num_tickets, b.total_amount, b.entry_code, b.qr_code_path,
                   b.payment_status, b.checked_in, b.checked_in_at, b.created_at,
                   e.title, e.venue, e.event_date, e.category
            FROM bookings b
            JOIN events e ON b.event_id = e.id
            WHERE b.booking_ref = %s
        """, (booking_ref,))
        row = cur.fetchone()
        cur.close()

        if not row:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        return jsonify({
            'success': True,
            'ticket': {
                'booking_ref': row[0],
                'full_name': row[1],
                'email': row[2],
                'phone': row[3],
                'age': row[4],
                'num_tickets': row[5],
                'total_amount': float(row[6]) if row[6] else 0,
                'entry_code': row[7],
                'qr_code': f"/static/{row[8]}",
                'payment_status': row[9],
                'checked_in': bool(row[10]),
                'checked_in_at': row[11].strftime('%Y-%m-%d %H:%M:%S') if row[11] else None,
                'booked_at': row[12].strftime('%Y-%m-%d %H:%M:%S') if row[12] else None,
                'event_title': row[13],
                'event_venue': row[14],
                'event_date': row[15].strftime('%Y-%m-%d %H:%M') if row[15] else '',
                'event_category': row[16]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scan', methods=['POST'])
def api_scan():
    """QR scan endpoint - returns attendee details"""
    try:
        data = request.get_json()
        qr_data_raw = data.get('qr_data', '')

        # Parse QR JSON
        try:
            qr_info = json.loads(qr_data_raw)
            booking_ref = qr_info.get('booking_ref')
        except:
            booking_ref = qr_data_raw.strip()

        if not booking_ref:
            return jsonify({'success': False, 'error': 'Invalid QR code'}), 400

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT b.id, b.booking_ref, b.full_name, b.email, b.phone, b.age,
                   b.num_tickets, b.entry_code, b.checked_in, b.checked_in_at,
                   b.payment_status, b.total_amount,
                   e.title, e.venue, e.event_date, e.category
            FROM bookings b
            JOIN events e ON b.event_id = e.id
            WHERE b.booking_ref = %s
        """, (booking_ref,))
        row = cur.fetchone()

        if not row:
            cur.close()
            return jsonify({'success': False, 'error': 'Ticket not found or invalid QR code'}), 404

        already_checked = bool(row[8])

        if not already_checked:
            cur.execute("""
                UPDATE bookings SET checked_in = TRUE, checked_in_at = NOW()
                WHERE id = %s
            """, (row[0],))
            mysql.connection.commit()

        cur.close()

        return jsonify({
            'success': True,
            'already_checked_in': already_checked,
            'attendee': {
                'booking_ref': row[1],
                'full_name': row[2],
                'email': row[3],
                'phone': row[4],
                'age': row[5],
                'num_tickets': row[6],
                'entry_code': row[7],
                'checked_in': True,
                'checked_in_at': row[9].strftime('%Y-%m-%d %H:%M:%S') if row[9] else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'payment_status': row[10],
                'total_amount': float(row[11]) if row[11] else 0,
                'event_title': row[12],
                'event_venue': row[13],
                'event_date': row[14].strftime('%Y-%m-%d %H:%M') if row[14] else '',
                'event_category': row[15]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/static/qrcodes/<filename>')
def qr_file(filename):
    return send_from_directory(QR_FOLDER, filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
