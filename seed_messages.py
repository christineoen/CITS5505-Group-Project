"""
Seed data script - Creates test booking and message data
Make sure you have user data before running this script
"""
from app import create_app
from models import db
from models.user import User
from models.parent_profile import ParentProfile
from models.babysitter_profile import BabysitterProfile
from models.booking import Booking
from models.message import Message
from datetime import datetime, date, time, timedelta

def seed_bookings_and_messages():
    app = create_app()
    with app.app_context():
        # Get some users
        users = User.query.all()
        
        if len(users) < 2:
            print("Need at least 2 users to create bookings. Please run seed.py first to create users.")
            return
        
        # Find parent and babysitter profiles
        parent_profile = ParentProfile.query.first()
        babysitter_profile = BabysitterProfile.query.first()
        
        if not parent_profile or not babysitter_profile:
            print("Need at least one parent profile and one babysitter profile. Please create profiles first.")
            return
        
        parent = parent_profile.user
        babysitter = babysitter_profile.user
        
        print(f"Creating booking: Parent={parent.username}, Babysitter={babysitter.username}")
        
        # Create several bookings
        bookings_data = [
            {
                "parent_id": parent_profile.id,
                "babysitter_id": babysitter_profile.id,
                "date": date.today() + timedelta(days=7),
                "start_time": time(14, 0),
                "duration_hours": 4,
                "status": "pending"
            },
            {
                "parent_id": parent_profile.id,
                "babysitter_id": babysitter_profile.id,
                "date": date.today() + timedelta(days=14),
                "start_time": time(10, 0),
                "duration_hours": 6,
                "status": "accepted"
            },
            {
                "parent_id": parent_profile.id,
                "babysitter_id": babysitter_profile.id,
                "date": date.today() - timedelta(days=7),
                "start_time": time(9, 0),
                "duration_hours": 8,
                "status": "completed"
            }
        ]
        
        for booking_data in bookings_data:
            # Check if similar booking already exists
            existing = Booking.query.filter_by(
                parent_id=booking_data["parent_id"],
                babysitter_id=booking_data["babysitter_id"],
                date=booking_data["date"]
            ).first()
            
            if existing:
                print(f"Booking already exists: {booking_data['date']}")
                booking = existing
            else:
                booking = Booking(**booking_data)
                db.session.add(booking)
                db.session.flush()  # Get booking.id
                print(f"Created new booking: {booking.id}")
            
            # Calculate end time for display
            start_datetime = datetime.combine(booking.date, booking.start_time)
            end_datetime = start_datetime + timedelta(hours=booking.duration_hours)
            
            # Create some messages for each booking
            messages_data = [
                {
                    "booking_id": booking.id,
                    "sender_id": parent.id,
                    "content": "Hi! I would like to book you for babysitting.",
                    "created_at": datetime.now() - timedelta(hours=24)
                },
                {
                    "booking_id": booking.id,
                    "sender_id": babysitter.id,
                    "content": "Hello! I'd be happy to help. What time works best for you?",
                    "created_at": datetime.now() - timedelta(hours=23)
                },
                {
                    "booking_id": booking.id,
                    "sender_id": parent.id,
                    "content": f"Great! How about {booking.date} from {booking.start_time.strftime('%H:%M')} to {end_datetime.strftime('%H:%M')}?",
                    "created_at": datetime.now() - timedelta(hours=22)
                }
            ]
            
            if booking.status == "accepted":
                messages_data.append({
                    "booking_id": booking.id,
                    "sender_id": babysitter.id,
                    "content": "Booking has been accepted.",
                    "created_at": datetime.now() - timedelta(hours=21)
                })
                messages_data.append({
                    "booking_id": booking.id,
                    "sender_id": babysitter.id,
                    "content": "Perfect! I'll see you then. Looking forward to it!",
                    "created_at": datetime.now() - timedelta(hours=20)
                })
            
            # Only add messages that don't exist
            for msg_data in messages_data:
                existing_msg = Message.query.filter_by(
                    booking_id=msg_data["booking_id"],
                    sender_id=msg_data["sender_id"],
                    content=msg_data["content"]
                ).first()
                
                if not existing_msg:
                    message = Message(**msg_data)
                    db.session.add(message)
        
        db.session.commit()
        print("✅ Booking and message data created successfully!")
        print(f"Total bookings created: {Booking.query.count()}")
        print(f"Total messages created: {Message.query.count()}")


if __name__ == "__main__":
    seed_bookings_and_messages()
