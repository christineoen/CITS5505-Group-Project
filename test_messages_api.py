"""
简单的API测试脚本
用于验证消息系统的API端点是否正常工作
"""
import requests
from requests.auth import HTTPBasicAuth

# 配置
BASE_URL = "http://127.0.0.1:5000"
TEST_USERNAME = "parent1"  # 根据你的seed数据修改
TEST_PASSWORD = "password123"  # 根据你的seed数据修改

def test_api():
    """测试消息API"""
    
    # 创建session以保持登录状态
    session = requests.Session()
    
    print("=" * 50)
    print("测试消息系统API")
    print("=" * 50)
    
    # 1. 测试登录
    print("\n1. 测试登录...")
    login_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
    
    if response.status_code in [200, 302]:
        print("✅ 登录成功")
    else:
        print(f"❌ 登录失败: {response.status_code}")
        return
    
    # 2. 测试获取对话列表
    print("\n2. 测试获取对话列表...")
    response = session.get(f"{BASE_URL}/messages/api/conversations")
    
    if response.status_code == 200:
        conversations = response.json()
        print(f"✅ 成功获取 {len(conversations)} 个对话")
        
        if conversations:
            print("\n对话列表:")
            for i, conv in enumerate(conversations, 1):
                print(f"  {i}. 与 {conv['other_user']['username']} 的对话")
                print(f"     状态: {conv['booking_status']}")
                print(f"     日期: {conv['booking_date']} {conv['booking_time']}")
                print(f"     未读: {conv['unread_count']}")
                if conv['last_message']:
                    print(f"     最后消息: {conv['last_message']['content'][:50]}...")
    else:
        print(f"❌ 获取对话列表失败: {response.status_code}")
        return
    
    # 3. 测试获取特定对话
    if conversations:
        booking_id = conversations[0]['booking_id']
        print(f"\n3. 测试获取对话详情 (Booking ID: {booking_id})...")
        response = session.get(f"{BASE_URL}/messages/api/conversation/{booking_id}")
        
        if response.status_code == 200:
            conversation = response.json()
            print(f"✅ 成功获取对话详情")
            print(f"   对话对象: {conversation['other_user']['username']}")
            print(f"   消息数量: {len(conversation['messages'])}")
            
            if conversation['messages']:
                print("\n   最近的消息:")
                for msg in conversation['messages'][-3:]:  # 显示最后3条
                    print(f"   - {msg['sender_username']}: {msg['content']}")
        else:
            print(f"❌ 获取对话详情失败: {response.status_code}")
    
    # 4. 测试发送消息
    if conversations:
        booking_id = conversations[0]['booking_id']
        print(f"\n4. 测试发送消息 (Booking ID: {booking_id})...")
        
        message_data = {
            "booking_id": booking_id,
            "content": "这是一条测试消息 - Test message from API test script"
        }
        response = session.post(
            f"{BASE_URL}/messages/api/send",
            json=message_data
        )
        
        if response.status_code == 201:
            message = response.json()
            print(f"✅ 消息发送成功")
            print(f"   消息ID: {message['id']}")
            print(f"   内容: {message['content']}")
        else:
            print(f"❌ 发送消息失败: {response.status_code}")
            print(f"   响应: {response.text}")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)


def check_database():
    """检查数据库中的数据"""
    import sqlite3
    
    print("\n" + "=" * 50)
    print("检查数据库")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('instance/database.db')
        cursor = conn.cursor()
        
        # 检查bookings
        cursor.execute("SELECT COUNT(*) FROM bookings")
        booking_count = cursor.fetchone()[0]
        print(f"\n📊 Bookings数量: {booking_count}")
        
        if booking_count > 0:
            cursor.execute("""
                SELECT b.id, pp.user_id as parent_user, bp.user_id as babysitter_user, 
                       b.status, b.date
                FROM bookings b
                JOIN parent_profiles pp ON b.parent_id = pp.id
                JOIN babysitter_profiles bp ON b.babysitter_id = bp.id
                LIMIT 5
            """)
            print("\n最近的Bookings:")
            for row in cursor.fetchall():
                print(f"  ID {row[0]}: Parent User {row[1]} -> Babysitter User {row[2]} | {row[3]} | {row[4]}")
        
        # 检查messages
        cursor.execute("SELECT COUNT(*) FROM messages")
        message_count = cursor.fetchone()[0]
        print(f"\n💬 Messages数量: {message_count}")
        
        if message_count > 0:
            cursor.execute("""
                SELECT m.id, u.username, m.content, m.created_at
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                ORDER BY m.created_at DESC
                LIMIT 5
            """)
            print("\n最近的Messages:")
            for row in cursor.fetchall():
                content = row[2][:50] + "..." if len(row[2]) > 50 else row[2]
                print(f"  {row[1]}: {content}")
        
        conn.close()
        
    except sqlite3.OperationalError as e:
        print(f"❌ 数据库错误: {e}")
        print("提示: 请先运行 'python app.py' 创建数据库表")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    import sys
    
    print("\n🧪 SitBuddy 消息系统测试工具\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == "db":
        # 只检查数据库
        check_database()
    else:
        # 运行API测试
        print("提示: 确保应用正在运行 (python app.py)")
        print("提示: 使用 'python test_messages_api.py db' 只检查数据库\n")
        
        try:
            test_api()
        except requests.exceptions.ConnectionError:
            print("\n❌ 无法连接到服务器")
            print("请确保应用正在运行: python app.py")
        except Exception as e:
            print(f"\n❌ 测试出错: {e}")
            import traceback
            traceback.print_exc()
