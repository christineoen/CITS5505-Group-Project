"""
种子数据脚本 - 用于创建测试booking和消息数据
运行此脚本前请确保已经有用户数据
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
        # 获取一些用户
        users = User.query.all()
        
        if len(users) < 2:
            print("需要至少2个用户才能创建booking。请先运行seed.py创建用户。")
            return
        
        # 找到parent和babysitter profile
        parent_profile = ParentProfile.query.first()
        babysitter_profile = BabysitterProfile.query.first()
        
        if not parent_profile or not babysitter_profile:
            print("需要至少一个parent profile和一个babysitter profile。请先创建profile。")
            return
        
        parent = parent_profile.user
        babysitter = babysitter_profile.user
        
        print(f"创建booking: Parent={parent.username}, Babysitter={babysitter.username}")
        
        # 创建几个booking
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
            # 检查是否已存在类似的booking
            existing = Booking.query.filter_by(
                parent_id=booking_data["parent_id"],
                babysitter_id=booking_data["babysitter_id"],
                date=booking_data["date"]
            ).first()
            
            if existing:
                print(f"Booking已存在: {booking_data['date']}")
                booking = existing
            else:
                booking = Booking(**booking_data)
                db.session.add(booking)
                db.session.flush()  # 获取booking.id
                print(f"创建新booking: {booking.id}")
            
            # 计算结束时间用于显示
            start_datetime = datetime.combine(booking.date, booking.start_time)
            end_datetime = start_datetime + timedelta(hours=booking.duration_hours)
            
            # 为每个booking创建一些消息
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
            
            # 只添加不存在的消息
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
        print("✅ Booking和消息数据创建成功！")
        print(f"总共创建了 {Booking.query.count()} 个bookings")
        print(f"总共创建了 {Message.query.count()} 条消息")


if __name__ == "__main__":
    seed_bookings_and_messages()
