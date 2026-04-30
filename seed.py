from app import create_app
from models import db
from models.user import User
from models.babysitter_profile import BabysitterProfile
from models.parent_profile import ParentProfile
from utils import POSTCODE_COORDS

BABYSITTERS = [
    {"name": "Emma Sits", "email": "emma@example.com", "suburb": "Subiaco", "postcode": "6008", "bio": "Experienced nanny with a love for arts and crafts.", "hourly_rate": 22.0, "experience_years": 4, "availability": '["Mon", "Tue", "Wed"]'},
    {"name": "Liam Care", "email": "liam@example.com", "suburb": "Fremantle", "postcode": "6160", "bio": "Studying early childhood education. CPR certified.", "hourly_rate": 18.0, "experience_years": 2, "availability": '["Thu", "Fri", "Sat"]'},
    {"name": "Sofia Nanny", "email": "sofia@example.com", "suburb": "Cottesloe", "postcode": "6011", "bio": "Former kindergarten teacher. Bilingual English/Spanish.", "hourly_rate": 28.0, "experience_years": 7, "availability": '["Mon", "Wed", "Fri"]'},
    {"name": "Jack Babysits", "email": "jack@example.com", "suburb": "Osborne Park", "postcode": "6050", "bio": "Great with toddlers. Love outdoor activities and sport.", "hourly_rate": 20.0, "experience_years": 3, "availability": '["Sat", "Sun"]'},
    {"name": "Mia Childcare", "email": "mia@example.com", "suburb": "Bentley", "postcode": "6102", "bio": "Reliable and caring. First aid trained.", "hourly_rate": 25.0, "experience_years": 5, "availability": '["Mon", "Tue", "Thu", "Fri"]'},
    {"name": "Noah Sitter", "email": "noah@example.com", "suburb": "Nedlands", "postcode": "6009", "bio": "Patient and fun. Experienced with special needs children.", "hourly_rate": 30.0, "experience_years": 6, "availability": '["Wed", "Thu", "Fri"]'},
    {"name": "Ava Nanny", "email": "ava@example.com", "suburb": "Leederville", "postcode": "6007", "bio": "Music and art enthusiast. Great for creative kids.", "hourly_rate": 21.0, "experience_years": 2, "availability": '["Mon", "Sat", "Sun"]'},
    {"name": "Oliver Care", "email": "oliver@example.com", "suburb": "Claremont", "postcode": "6010", "bio": "Dad of two. Knows how to keep kids engaged and happy.", "hourly_rate": 23.0, "experience_years": 5, "availability": '["Tue", "Wed", "Sat"]'},
    {"name": "Isla Sits", "email": "isla@example.com", "suburb": "Floreat", "postcode": "6014", "bio": "Gentle and nurturing. Loves reading and storytelling.", "hourly_rate": 19.0, "experience_years": 1, "availability": '["Fri", "Sat", "Sun"]'},
    {"name": "Ethan Babysit", "email": "ethan@example.com", "suburb": "Northbridge", "postcode": "6003", "bio": "Active and energetic. Great for school-age kids.", "hourly_rate": 20.0, "experience_years": 3, "availability": '["Mon", "Tue", "Fri"]'},
]

PARENTS = [
    {"name": "Sarah Parent",  "email": "sarah@example.com",  "suburb": "Subiaco",      "postcode": "6008", "about": "Kids have nut allergy.",                      "children": [{"name": "Lily",   "age": 6}, {"name": "Max",    "age": 3}]},
    {"name": "Tom Dad",       "email": "tom@example.com",    "suburb": "Fremantle",     "postcode": "6160", "about": "",                                            "children": [{"name": "Oscar",  "age": 5}]},
    {"name": "Grace Mum",     "email": "grace@example.com",  "suburb": "Cottesloe",     "postcode": "6011", "about": "Youngest is 18 months.",                      "children": [{"name": "Ella",   "age": 4}, {"name": "Noah",   "age": 1}]},
    {"name": "Daniel Parent", "email": "daniel@example.com", "suburb": "Osborne Park",  "postcode": "6050", "about": "",                                            "children": [{"name": "Liam",   "age": 7}, {"name": "Sophie", "age": 5}, {"name": "Jack", "age": 2}]},
    {"name": "Chloe Family",  "email": "chloe@example.com",  "suburb": "Bentley",       "postcode": "6102", "about": "Child has mild asthma.",                      "children": [{"name": "Mia",    "age": 9}]},
    {"name": "James Dad",     "email": "james@example.com",  "suburb": "Nedlands",      "postcode": "6009", "about": "Experienced with large families preferred.",   "children": [{"name": "Ava",    "age": 8}, {"name": "Ethan", "age": 6}, {"name": "Ruby", "age": 4}, {"name": "Sam", "age": 1}]},
    {"name": "Lucy Mum",      "email": "lucy@example.com",   "suburb": "Leederville",   "postcode": "6007", "about": "",                                            "children": [{"name": "Isla",   "age": 3}]},
    {"name": "Ben Parent",    "email": "ben@example.com",    "suburb": "Claremont",     "postcode": "6010", "about": "Twins, both 4 years old.",                    "children": [{"name": "Oliver", "age": 4}, {"name": "Olivia", "age": 4}]},
    {"name": "Alice Family",  "email": "alice@example.com",  "suburb": "Floreat",       "postcode": "6014", "about": "",                                            "children": [{"name": "Zoe",    "age": 10}, {"name": "Harry", "age": 7}]},
    {"name": "Henry Dad",     "email": "henry@example.com",  "suburb": "Northbridge",   "postcode": "6003", "about": "One child has dietary restrictions.",          "children": [{"name": "Charlie", "age": 5}]},
]


def seed():
    app = create_app()
    with app.app_context():
        for data in BABYSITTERS:
            if User.query.filter_by(email=data["email"]).first():
                print(f"Skipping {data['email']} (already exists)")
                continue
            lat, lng = POSTCODE_COORDS.get(data["postcode"], (None, None))
            user = User(name=data["name"], email=data["email"], suburb=data["suburb"], postcode=data["postcode"], latitude=lat, longitude=lng)
            user.set_password("password123")
            db.session.add(user)
            db.session.flush()
            db.session.add(BabysitterProfile(
                user_id=user.id,
                bio=data["bio"],
                hourly_rate=data["hourly_rate"],
                experience_years=data["experience_years"],
                availability=data["availability"],
            ))
            print(f"Created babysitter: {data['name']}")

        for data in PARENTS:
            if User.query.filter_by(email=data["email"]).first():
                print(f"Skipping {data['email']} (already exists)")
                continue
            lat, lng = POSTCODE_COORDS.get(data["postcode"], (None, None))
            user = User(name=data["name"], email=data["email"], suburb=data["suburb"], postcode=data["postcode"], latitude=lat, longitude=lng)
            user.set_password("password123")
            db.session.add(user)
            db.session.flush()
            db.session.add(ParentProfile(
                user_id=user.id,
                about=data["about"] or None,
                children=data["children"],
            ))
            print(f"Created parent: {data['name']}")

        db.session.commit()
        print("\nSeed complete.")


if __name__ == "__main__":
    seed()
