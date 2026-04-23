"""
Simple API test script
Used to verify that the message system API endpoints are working properly
"""
import requests
from requests.auth import HTTPBasicAuth

# Configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_USERNAME = "parent1"  # Modify according to your seed data
TEST_PASSWORD = "password123"  # Modify according to your seed data

def test_api():
    """Test message API"""
    
    # Create session to maintain login state
    session = requests.Session()
    
    print("=" * 50)
    print("Testing Message System API")
    print("=" * 50)
    
    # 1. Test login
    print("\n1. Testing login...")
    login_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
    
    if response.status_code in [200, 302]:
        print("✅ Login successful")
    else:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    # 2. Test getting conversation list
    print("\n2. Testing get conversation list...")
    response = session.get(f"{BASE_URL}/messages/api/conversations")
    
    if response.status_code == 200:
        conversations = response.json()
        print(f"✅ Successfully retrieved {len(conversations)} conversations")
        
        if conversations:
            print("\nConversation list:")
            for i, conv in enumerate(conversations, 1):
                print(f"  {i}. Conversation with {conv['other_user']['username']}")
                print(f"     Status: {conv['booking_status']}")
                print(f"     Date: {conv['booking_date']} {conv['booking_time']}")
                print(f"     Unread: {conv['unread_count']}")
                if conv['last_message']:
                    print(f"     Last message: {conv['last_message']['content'][:50]}...")
    else:
        print(f"❌ Failed to get conversation list: {response.status_code}")
        return
    
    # 3. Test getting specific conversation
    if conversations:
        booking_id = conversations[0]['booking_id']
        print(f"\n3. Testing get conversation details (Booking ID: {booking_id})...")
        response = session.get(f"{BASE_URL}/messages/api/conversation/{booking_id}")
        
        if response.status_code == 200:
            conversation = response.json()
            print(f"✅ Successfully retrieved conversation details")
            print(f"   Conversation with: {conversation['other_user']['username']}")
            print(f"   Message count: {len(conversation['messages'])}")
            
            if conversation['messages']:
                print("\n   Recent messages:")
                for msg in conversation['messages'][-3:]:  # Show last 3
                    print(f"   - {msg['sender_username']}: {msg['content']}")
        else:
            print(f"❌ Failed to get conversation details: {response.status_code}")
    
    # 4. Test sending message
    if conversations:
        booking_id = conversations[0]['booking_id']
        print(f"\n4. Testing send message (Booking ID: {booking_id})...")
        
        message_data = {
            "booking_id": booking_id,
            "content": "This is a test message - Test message from API test script"
        }
        response = session.post(
            f"{BASE_URL}/messages/api/send",
            json=message_data
        )
        
        if response.status_code == 201:
            message = response.json()
            print(f"✅ Message sent successfully")
            print(f"   Message ID: {message['id']}")
            print(f"   Content: {message['content']}")
        else:
            print(f"❌ Failed to send message: {response.status_code}")
            print(f"   Response: {response.text}")
    
    print("\n" + "=" * 50)
    print("Testing complete!")
    print("=" * 50)


def check_database():
    """Check data in database"""
    import sqlite3
    
    print("\n" + "=" * 50)
    print("Checking Database")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('instance/database.db')
        cursor = conn.cursor()
        
        # Check bookings
        cursor.execute("SELECT COUNT(*) FROM bookings")
        booking_count = cursor.fetchone()[0]
        print(f"\n📊 Bookings count: {booking_count}")
        
        if booking_count > 0:
            cursor.execute("""
                SELECT b.id, pp.user_id as parent_user, bp.user_id as babysitter_user, 
                       b.status, b.date
                FROM bookings b
                JOIN parent_profiles pp ON b.parent_id = pp.id
                JOIN babysitter_profiles bp ON b.babysitter_id = bp.id
                LIMIT 5
            """)
            print("\nRecent Bookings:")
            for row in cursor.fetchall():
                print(f"  ID {row[0]}: Parent User {row[1]} -> Babysitter User {row[2]} | {row[3]} | {row[4]}")
        
        # Check messages
        cursor.execute("SELECT COUNT(*) FROM messages")
        message_count = cursor.fetchone()[0]
        print(f"\n💬 Messages count: {message_count}")
        
        if message_count > 0:
            cursor.execute("""
                SELECT m.id, u.username, m.content, m.created_at
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                ORDER BY m.created_at DESC
                LIMIT 5
            """)
            print("\nRecent Messages:")
            for row in cursor.fetchall():
                content = row[2][:50] + "..." if len(row[2]) > 50 else row[2]
                print(f"  {row[1]}: {content}")
        
        conn.close()
        
    except sqlite3.OperationalError as e:
        print(f"❌ Database error: {e}")
        print("Tip: Please run 'python app.py' first to create database tables")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys
    
    print("\n🧪 SitBuddy Message System Test Tool\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == "db":
        # Only check database
        check_database()
    else:
        # Run API tests
        print("Tip: Make sure the application is running (python app.py)")
        print("Tip: Use 'python test_messages_api.py db' to only check database\n")
        
        try:
            test_api()
        except requests.exceptions.ConnectionError:
            print("\n❌ Unable to connect to server")
            print("Please make sure the application is running: python app.py")
        except Exception as e:
            print(f"\n❌ Test error: {e}")
            import traceback
            traceback.print_exc()
