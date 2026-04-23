from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.booking import Booking
from models.message import Message
from models.user import User
from datetime import datetime

messages_bp = Blueprint("messages", __name__, url_prefix="/messages")


@messages_bp.route("/")
@login_required
def index():
    """显示消息页面"""
    return render_template("messages.html")


@messages_bp.route("/api/conversations")
@login_required
def get_conversations():
    """获取当前用户的所有对话列表"""
    # 获取当前用户作为parent或babysitter的所有bookings
    bookings = []
    if current_user.is_parent and current_user.parent_profile:
        bookings = Booking.query.filter_by(parent_id=current_user.parent_profile.id).all()
    elif current_user.is_babysitter and current_user.babysitter_profile:
        bookings = Booking.query.filter_by(babysitter_id=current_user.babysitter_profile.id).all()
    
    if not bookings:
        return jsonify([])

    conversations = []
    for booking in bookings:
        # 确定对话的另一方
        if current_user.parent_profile and booking.parent_id == current_user.parent_profile.id:
            other_user = booking.babysitter.user
        else:
            other_user = booking.parent.user

        # 获取最后一条消息
        last_message = Message.query.filter_by(booking_id=booking.id).order_by(Message.created_at.desc()).first()
        
        # 获取未读消息数量
        unread_count = Message.query.filter_by(
            booking_id=booking.id,
            is_read=False
        ).filter(Message.sender_id != current_user.id).count()

        # 计算结束时间
        from datetime import datetime, timedelta
        start_datetime = datetime.combine(booking.date, booking.start_time)
        end_datetime = start_datetime + timedelta(hours=booking.duration_hours)

        conversations.append({
            "booking_id": booking.id,
            "other_user": {
                "id": other_user.id,
                "username": other_user.username
            },
            "booking_status": booking.status,
            "booking_date": booking.date.isoformat(),
            "booking_time": f"{booking.start_time.strftime('%H:%M')} - {end_datetime.strftime('%H:%M')}",
            "last_message": last_message.to_dict() if last_message else None,
            "unread_count": unread_count
        })

    # 按最后消息时间排序
    conversations.sort(key=lambda x: x["last_message"]["created_at"] if x["last_message"] else "", reverse=True)
    
    return jsonify(conversations)


@messages_bp.route("/api/conversation/<int:booking_id>")
@login_required
def get_conversation(booking_id):
    """获取特定booking的所有消息"""
    booking = Booking.query.get_or_404(booking_id)
    
    # 验证用户是否有权限查看此对话
    user_parent_id = current_user.parent_profile.id if current_user.parent_profile else None
    user_babysitter_id = current_user.babysitter_profile.id if current_user.babysitter_profile else None
    
    if booking.parent_id != user_parent_id and booking.babysitter_id != user_babysitter_id:
        return jsonify({"error": "Unauthorized"}), 403

    # 标记所有消息为已读
    Message.query.filter_by(booking_id=booking_id).filter(
        Message.sender_id != current_user.id,
        Message.is_read == False
    ).update({"is_read": True})
    db.session.commit()

    # 获取所有消息
    messages = Message.query.filter_by(booking_id=booking_id).order_by(Message.created_at.asc()).all()
    
    # 确定对话的另一方
    if user_parent_id and booking.parent_id == user_parent_id:
        other_user = booking.babysitter.user
    else:
        other_user = booking.parent.user

    # 计算结束时间
    from datetime import datetime, timedelta
    start_datetime = datetime.combine(booking.date, booking.start_time)
    end_datetime = start_datetime + timedelta(hours=booking.duration_hours)

    return jsonify({
        "booking": {
            "id": booking.id,
            "status": booking.status,
            "date": booking.date.isoformat(),
            "time": f"{booking.start_time.strftime('%H:%M')} - {end_datetime.strftime('%H:%M')}"
        },
        "other_user": {
            "id": other_user.id,
            "username": other_user.username
        },
        "messages": [msg.to_dict() for msg in messages]
    })


@messages_bp.route("/api/send", methods=["POST"])
@login_required
def send_message():
    """发送新消息"""
    data = request.get_json()
    booking_id = data.get("booking_id")
    content = data.get("content", "").strip()

    if not booking_id or not content:
        return jsonify({"error": "Missing booking_id or content"}), 400

    booking = Booking.query.get_or_404(booking_id)
    
    # 验证用户是否有权限发送消息
    user_parent_id = current_user.parent_profile.id if current_user.parent_profile else None
    user_babysitter_id = current_user.babysitter_profile.id if current_user.babysitter_profile else None
    
    if booking.parent_id != user_parent_id and booking.babysitter_id != user_babysitter_id:
        return jsonify({"error": "Unauthorized"}), 403

    # 创建新消息
    message = Message(
        booking_id=booking_id,
        sender_id=current_user.id,
        content=content
    )
    db.session.add(message)
    db.session.commit()

    return jsonify(message.to_dict()), 201


@messages_bp.route("/api/booking/<int:booking_id>/status", methods=["PUT"])
@login_required
def update_booking_status(booking_id):
    """更新booking状态（接受/拒绝）"""
    booking = Booking.query.get_or_404(booking_id)
    
    # 只有babysitter可以接受或拒绝booking
    user_babysitter_id = current_user.babysitter_profile.id if current_user.babysitter_profile else None
    if booking.babysitter_id != user_babysitter_id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    new_status = data.get("status")

    if new_status not in ["accepted", "rejected"]:
        return jsonify({"error": "Invalid status"}), 400

    booking.status = new_status
    booking.updated_at = datetime.now()
    db.session.commit()

    # 自动发送系统消息
    system_message_content = f"Booking has been {new_status}."
    system_message = Message(
        booking_id=booking_id,
        sender_id=current_user.id,
        content=system_message_content
    )
    db.session.add(system_message)
    db.session.commit()

    return jsonify({"status": booking.status, "message": system_message.to_dict()})
