from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.appointment import Availability, Appointment
from app.utils.auth import role_required

student_bp = Blueprint('student', __name__)

@student_bp.route('/api/professor/<int:professor_id>/availability', methods=['GET'])
@jwt_required()
@role_required('student')
def get_professor_availability(professor_id):
    availabilities = Availability.query.filter_by(
        professor_id=professor_id,
        is_available=True
    ).all()
    
    return jsonify([{
        'id': a.id,
        'start_time': a.start_time.isoformat(),
        'end_time': a.end_time.isoformat()
    } for a in availabilities]), 200

@student_bp.route('/api/appointments', methods=['POST'])
@jwt_required()
@role_required('student')
def book_appointment():
    data = request.get_json()
    student_id = get_jwt_identity()
    
    availability = Availability.query.filter_by(
        id=data['availability_id'],
        is_available=True
    ).first_or_404()
    
    appointment = Appointment(
        student_id=student_id,
        professor_id=availability.professor_id,
        availability_id=availability.id
    )
    
    availability.is_available = False
    db.session.add(appointment)
    db.session.commit()
    
    return jsonify({"msg": "Appointment booked successfully"}), 201

@student_bp.route('/api/student/appointments', methods=['GET'])
@jwt_required()
@role_required('student')
def get_appointments():
    student_id = get_jwt_identity()
    
    # Query the Appointment table, joining with the Availability table
    appointments = db.session.query(Appointment, Availability).join(
        Availability, Appointment.availability_id == Availability.id
    ).filter(
        Appointment.student_id == student_id
    ).all()

    # Format the appointments data for the response
    return jsonify([{
        'id': a.Appointment.id,
        'professor_id': a.Appointment.professor_id,
        'start_time': a.Availability.start_time.isoformat(),
        'status': a.Appointment.status
    } for a in appointments]), 200
