from app import create_app, db
from app.models import Room

def seed_rooms():
    """Seed the database with 10 rooms of different types and statuses"""
    # Check if rooms already exist
    app = create_app()
    with app.app_context():
        existing_rooms = Room.query.count()
        if existing_rooms > 0:
            print(f"Database already has {existing_rooms} rooms. Skipping room creation.")
            return
        
        # Create 10 rooms with different types and statuses
        rooms = [
            # Private rooms
            Room(room_number='101', room_type='Private', status='available', daily_rate=500.00),
            Room(room_number='102', room_type='Private', status='available', daily_rate=500.00),
            Room(room_number='103', room_type='Private', status='available', daily_rate=500.00),
            
            # Semi-private rooms
            Room(room_number='201', room_type='Semi-Private', status='available', daily_rate=300.00),
            Room(room_number='202', room_type='Semi-Private', status='available', daily_rate=300.00),
            Room(room_number='203', room_type='Semi-Private', status='available', daily_rate=300.00),
            
            # Ward rooms
            Room(room_number='301', room_type='Ward', status='available', daily_rate=150.00),
            Room(room_number='302', room_type='Ward', status='available', daily_rate=150.00),
            Room(room_number='303', room_type='Ward', status='available', daily_rate=150.00),
            
            # ICU room
            Room(room_number='401', room_type='ICU', status='available', daily_rate=1000.00),
        ]
        
        # Add rooms to database
        db.session.add_all(rooms)
        db.session.commit()
        
        print(f"Successfully added {len(rooms)} rooms to the database.")

if __name__ == '__main__':
    seed_rooms()