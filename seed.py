from app import create_app
from models import db
from models.user import User
from models.babysitter_profile import BabysitterProfile
from models.parent_profile import ParentProfile

BABYSITTERS = [
    {"username": "emma_sits", "email": "emma@example.com", "bio": "Experienced nanny with a love for arts and crafts.", "hourly_rate": 22.0, "experience_years": 4, "location": "6008", "availability": '["Mon", "Tue", "Wed"]'},
    {"username": "liam_care", "email": "liam@example.com", "bio": "Studying early childhood education. CPR certified.", "hourly_rate": 18.0, "experience_years": 2, "location": "6160", "availability": '["Thu", "Fri", "Sat"]'},
    {"username": "sofia_nanny", "email": "sofia@example.com", "bio": "Former kindergarten teacher. Bilingual English/Spanish.", "hourly_rate": 28.0, "experience_years": 7, "location": "6011", "availability": '["Mon", "Wed", "Fri"]'},
    {"username": "jack_babysits", "email": "jack@example.com", "bio": "Great with toddlers. Love outdoor activities and sport.", "hourly_rate": 20.0, "experience_years": 3, "location": "6050", "availability": '["Sat", "Sun"]'},
    {"username": "mia_childcare", "email": "mia@example.com", "bio": "Reliable and caring. First aid trained.", "hourly_rate": 25.0, "experience_years": 5, "location": "6100", "availability": '["Mon", "Tue", "Thu", "Fri"]'},
    {"username": "noah_sitter", "email": "noah@example.com", "bio": "Patient and fun. Experienced with special needs children.", "hourly_rate": 30.0, "experience_years": 6, "location": "6009", "availability": '["Wed", "Thu", "Fri"]'},
    {"username": "ava_nanny", "email": "ava@example.com", "bio": "Music and art enthusiast. Great for creative kids.", "hourly_rate": 21.0, "experience_years": 2, "location": "6007", "availability": '["Mon", "Sat", "Sun"]'},
    {"username": "oliver_care", "email": "oliver@example.com", "bio": "Dad of two. Knows how to keep kids engaged and happy.", "hourly_rate": 23.0, "experience_years": 5, "location": "6010", "availability": '["Tue", "Wed", "Sat"]'},
    {"username": "isla_sits", "email": "isla@example.com", "bio": "Gentle and nurturing. Loves reading and storytelling.", "hourly_rate": 19.0, "experience_years": 1, "location": "6019", "availability": '["Fri", "Sat", "Sun"]'},
    {"username": "ethan_babysit", "email": "ethan@example.com", "bio": "Active and energetic. Great for school-age kids.", "hourly_rate": 20.0, "experience_years": 3, "location": "6003", "availability": '["Mon", "Tue", "Fri"]'},
]

PARENTS = [
    {"username": "sarah_parent", "email": "sarah@example.com", "num_children": 2, "location": "6008", "special_requirements": "Kids have nut allergy."},
    {"username": "tom_dad", "email": "tom@example.com", "num_children": 1, "location": "6160", "special_requirements": ""},
    {"username": "grace_mum", "email": "grace@example.com", "num_children": 3, "location": "6011", "special_requirements": "Youngest is 18 months."},
    {"username": "daniel_parent", "email": "daniel@example.com", "num_children": 2, "location": "6050", "special_requirements": ""},
    {"username": "chloe_family", "email": "chloe@example.com", "num_children": 1, "location": "6100", "special_requirements": "Child has mild asthma."},
    {"username": "james_dad", "email": "james@example.com", "num_children": 4, "location": "6009", "special_requirements": "Experienced with large families preferred."},
    {"username": "lucy_mum", "email": "lucy@example.com", "num_children": 2, "location": "6007", "special_requirements": ""},
    {"username": "ben_parent", "email": "ben@example.com", "num_children": 1, "location": "6010", "special_requirements": "Twins, both 4 years old."},
    {"username": "alice_family", "email": "alice@example.com", "num_children": 2, "location": "6019", "special_requirements": ""},
    {"username": "henry_dad", "email": "henry@example.com", "num_children": 3, "location": "6003", "special_requirements": "One child has dietary restrictions."},
]


def seed():
    app = create_app()
    with app.app_context():
        for data in BABYSITTERS:
            if User.query.filter_by(email=data["email"]).first():
                print(f"Skipping {data['email']} (already exists)")
                continue
            user = User(username=data["username"], email=data["email"])
            user.set_password("password123")
            db.session.add(user)
            db.session.flush()
            db.session.add(BabysitterProfile(
                user_id=user.id,
                bio=data["bio"],
                hourly_rate=data["hourly_rate"],
                experience_years=data["experience_years"],
                location=data["location"],
                availability=data["availability"],
            ))
            print(f"Created babysitter: {data['username']}")

        for data in PARENTS:
            if User.query.filter_by(email=data["email"]).first():
                print(f"Skipping {data['email']} (already exists)")
                continue
            user = User(username=data["username"], email=data["email"])
            user.set_password("password123")
            db.session.add(user)
            db.session.flush()
            db.session.add(ParentProfile(
                user_id=user.id,
                num_children=data["num_children"],
                location=data["location"],
                special_requirements=data["special_requirements"],
            ))
            print(f"Created parent: {data['username']}")

        db.session.commit()
        print("\nSeed complete.")


if __name__ == "__main__":
    seed()
