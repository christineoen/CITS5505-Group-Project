"""
Seed Messages Script - Creates test booking, message, and rating data.
Ensure you have user data before running this script (run seed.py).
"""
from app import create_app
from models import db
from models.user import User
from models.parent_profile import ParentProfile
from models.babysitter_profile import BabysitterProfile
from models.booking import Booking
from models.message import Message
from models.rating import Rating
from datetime import datetime, date, time, timedelta

# (parent_email, babysitter_email, days_ago, start_hour, duration, status, notes)
# Negative days_ago = future booking
BOOKING_PAIRS = [
    ("sarah@example.com",  "emma@example.com",   60, 14, 4, "completed", "Kids love arts and crafts."),
    ("sarah@example.com",  "liam@example.com",   30, 10, 3, "completed", ""),
    ("sarah@example.com",  "noah@example.com",   -7, 14, 4, "pending",   ""),
    ("tom@example.com",    "sofia@example.com",  45,  9, 5, "completed", "Oscar loves dinosaurs."),
    ("tom@example.com",    "emma@example.com",   15, 13, 4, "completed", ""),
    ("tom@example.com",    "jack@example.com",  -14, 10, 3, "accepted",  ""),
    ("grace@example.com",  "noah@example.com",   50,  8, 6, "completed", "Youngest is 18 months, needs extra care."),
    ("grace@example.com",  "mia@example.com",    20, 14, 3, "completed", ""),
    ("grace@example.com",  "emma@example.com",  -10,  9, 5, "pending",   ""),
    ("daniel@example.com", "jack@example.com",   40, 10, 5, "completed", "Three kids, lots of energy!"),
    ("daniel@example.com", "ava@example.com",    10, 15, 4, "completed", ""),
    ("chloe@example.com",  "mia@example.com",    35,  9, 4, "completed", "Mia has mild asthma, inhaler in bag."),
    ("chloe@example.com",  "isla@example.com",   -5, 13, 4, "pending",   ""),
    ("james@example.com",  "sofia@example.com",  25, 11, 6, "completed", "Four kids, experienced sitter preferred."),
    ("james@example.com",  "noah@example.com",   55, 10, 5, "completed", ""),
    ("lucy@example.com",   "ava@example.com",    18, 13, 3, "completed", ""),
    ("lucy@example.com",   "liam@example.com",  -12, 10, 4, "accepted",  ""),
    ("ben@example.com",    "oliver@example.com", 42,  9, 5, "completed", "Twins, both 4 years old."),
    ("ben@example.com",    "ethan@example.com",  12, 14, 4, "completed", ""),
    ("alice@example.com",  "isla@example.com",   28, 14, 4, "completed", "Older kids, love reading."),
    ("alice@example.com",  "ava@example.com",    -8, 11, 3, "pending",   ""),
    ("henry@example.com",  "ethan@example.com",  12, 10, 4, "completed", "Dietary restrictions - no gluten."),
    ("henry@example.com",  "oliver@example.com", -9, 15, 3, "pending",   ""),
    ("sarah@example.com",  "emma@example.com",    2, 17, 3, "completed", "Kids had a great evening."),
]

# Ratings for each completed booking: (parent_comment, parent_score, babysitter_comment, babysitter_score)
COMPLETED_RATINGS = [
    ("Emma was fantastic with our kids — they were asking for her the next day!", 5,  "Sarah's children were a delight. Very clear instructions and welcoming home.", 5),
    ("Liam was reliable and the kids had a great time. Will book again.",          4,  "Great family, kids were well-behaved and Sarah communicated everything clearly.", 5),
    ("Sofia was brilliant — kept Oscar engaged the whole time. Highly recommend.", 5,  "Tom's son was so enthusiastic. Really enjoyable booking.",                        5),
    ("Emma handled drop-off nerves really well. Kids warmed up quickly.",          4,  "Tom's family was lovely. Kids had clear routines which made the evening easy.",    4),
    ("Noah was incredibly patient with our toddler. We felt completely at ease.",  5,  "Grace gave excellent handover notes. The little one was well cared for.",          5),
    ("Mia was calm and capable. Grace loved having her.",                          4,  "Grace's family was warm and organised. Smooth booking.",                           4),
    ("Jack kept three energetic kids happy all afternoon. Impressive!",            5,  "Daniel's kids are full of life — tiring but so fun. Great family.",                4),
    ("Ava was creative and the kids made little art projects. Loved it.",          5,  "Daniel's kids were enthusiastic and well-mannered. Would sit for them again.",    5),
    ("Mia was great with Chloe's asthma — handled it professionally.",             5,  "Chloe's family was very organised. All information about the asthma was clear.",   5),
    ("Sofia managed four kids like a pro. We came home to happy children.",        5,  "James has a wonderful family. Kids were spirited but respectful.",                 4),
    ("Noah was calm and confident. Kids adored him.",                              5,  "James gave great notes. Large family but very well structured.",                   4),
    ("Ava was warm and engaging with Isla. Highly recommend.",                     5,  "Lucy's daughter was sweet and well-settled. Easy evening.",                        5),
    ("Oliver was patient and the twins absolutely loved him.",                     5,  "Ben's twins kept me on my toes! Such fun kids.",                                  5),
    ("Ethan matched Ben's kids' energy perfectly. They were worn out by bedtime.", 4,  "Ben's family was great. Very organised household.",                               4),
    ("Isla read to the kids all afternoon. They loved it.",                        5,  "Alice's kids are well-read and great fun to be with.",                             5),
    ("Ethan was thoughtful about the dietary restrictions. Very reliable.",        4,  "Henry was thorough with all the dietary info. Appreciated the preparation.",       5),
]


MESSAGES = {
    "pending": [
        ("parent",     "Hi! I'd love to book you for babysitting on {date}."),
        ("babysitter", "Hi! Thanks for reaching out. I'd be happy to help — I'll check my availability."),
        ("parent",     "Great, looking forward to hearing from you!"),
    ],
    "accepted": [
        ("parent",     "Hi! I'd love to book you for babysitting on {date}."),
        ("babysitter", "Hi! That works for me — I'll confirm the booking."),
        ("parent",     "Perfect, see you then! I'll send through the details."),
        ("babysitter", "Sounds great, looking forward to it!"),
    ],
    "completed": [
        ("parent",     "Hi! I'd love to book you for babysitting on {date}."),
        ("babysitter", "Hi! That works perfectly. What time should I arrive?"),
        ("parent",     "Could you come at {start_time}? The kids will be so excited to meet you."),
        ("babysitter", "I'll be there at {start_time}. See you then!"),
        ("parent",     "Thanks again for today — the kids had a wonderful time!"),
        ("babysitter", "It was my pleasure. They were wonderful!"),
    ],
}


def seed_bookings_and_messages():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        if len(users) < 2:
            print("Need at least 2 users. Please run seed.py first.")
            return

        completed_index = 0

        for pair in BOOKING_PAIRS:
            parent_email, sitter_email, days_ago, start_hour, duration, status, notes = pair

            parent_user = User.query.filter_by(email=parent_email).first()
            sitter_user = User.query.filter_by(email=sitter_email).first()
            if not parent_user or not sitter_user:
                print(f"Skipping: could not find {parent_email} or {sitter_email}")
                continue

            parent_profile = ParentProfile.query.filter_by(user_id=parent_user.id).first()
            sitter_profile = BabysitterProfile.query.filter_by(user_id=sitter_user.id).first()
            if not parent_profile or not sitter_profile:
                print(f"Skipping: missing profile for {parent_email} or {sitter_email}")
                continue

            booking_date = date.today() - timedelta(days=days_ago) if days_ago >= 0 else date.today() + timedelta(days=abs(days_ago))
            booking_start = time(start_hour, 0)

            booking = Booking.query.filter_by(
                parent_id=parent_profile.id,
                babysitter_id=sitter_profile.id,
                date=booking_date,
            ).first()

            if not booking:
                booking = Booking(
                    parent_id=parent_profile.id,
                    babysitter_id=sitter_profile.id,
                    date=booking_date,
                    start_time=booking_start,
                    duration_hours=duration,
                    status=status,
                    notes=notes or None,
                )
                db.session.add(booking)
                db.session.flush()
                print(f"Created booking: {parent_user.name} + {sitter_user.name} ({status})")
            else:
                print(f"Skipping existing booking: {parent_user.name} + {sitter_user.name}")

            # Messages
            template_key = status if status in MESSAGES else "pending"
            msg_templates = MESSAGES[template_key]
            base_time = datetime.now() - timedelta(days=max(days_ago, 1), hours=len(msg_templates))

            for i, (sender_role, template) in enumerate(msg_templates):
                sender = parent_user if sender_role == "parent" else sitter_user
                content = template.format(
                    date=booking_date.strftime("%A, %d %B"),
                    start_time=booking_start.strftime("%H:%M"),
                )
                existing_msg = Message.query.filter_by(
                    booking_id=booking.id,
                    sender_id=sender.id,
                    content=content,
                ).first()
                if not existing_msg:
                    db.session.add(Message(
                        booking_id=booking.id,
                        sender_id=sender.id,
                        content=content,
                        created_at=base_time + timedelta(hours=i),
                    ))

            # Ratings for completed bookings
            if status == "completed" and completed_index < len(COMPLETED_RATINGS):
                p_comment, p_score, s_comment, s_score = COMPLETED_RATINGS[completed_index]
                completed_index += 1

                for rater, ratee, score, comment in [
                    (parent_user, sitter_user, p_score, p_comment),
                    (sitter_user, parent_user, s_score, s_comment),
                ]:
                    existing_rating = Rating.query.filter_by(
                        booking_id=booking.id,
                        rater_id=rater.id,
                    ).first()
                    if not existing_rating:
                        db.session.add(Rating(
                            booking_id=booking.id,
                            rater_id=rater.id,
                            ratee_id=ratee.id,
                            score=score,
                            comment=comment,
                        ))

        db.session.commit()
        print(f"\nTotal bookings:  {Booking.query.count()}")
        print(f"Total messages:  {Message.query.count()}")
        print(f"Total ratings:   {Rating.query.count()}")
        print("Seed complete.")


if __name__ == "__main__":
    seed_bookings_and_messages()
