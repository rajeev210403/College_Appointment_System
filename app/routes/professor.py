from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.appointment import Availability, Appointment
from app.utils.auth import role_required
from datetime import datetime
from flask_jwt_extended import decode_token

professor_bp = Blueprint('professor', __name__)

@professor_bp.route('/api/professor/availability', methods=['POST'])
@jwt_required()
@role_required('professor')
def set_availability():
    data = request.get_json()
    print("hello")
    try:
        token = request.headers.get('Authorization').split()[1]  # Extract the token from the header
        decoded_token = decode_token(token)
        print(decoded_token)  # Check the decoded token
    except Exception as e:
        return jsonify({"error": "Token error", "message": str(e)}), 400
    
    professor_id = get_jwt_identity()
    
    availability = Availability(
        professor_id=professor_id,
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time']),  
        is_available=True
    )
    
    db.session.add(availability)
    db.session.commit()
    
    return jsonify({"msg": "Availability set successfully"}), 201


@professor_bp.route('/api/professor/appointments', methods=['GET'])
@jwt_required()
@role_required('professor')
def get_appointments():
    professor_id = get_jwt_identity()
    # jsonify(professor_id), 200
    appointments = db.session.query(Appointment, Availability).join(
        Availability, Appointment.availability_id == Availability.id
    ).filter(Appointment.professor_id == professor_id).all()

    # Return a list of appointments, including the availability details
    return jsonify([{
        'id': a.id,
        'student_id': a.student_id,
        'time_slot': av.start_time.isoformat(),  # Access the start_time from the Availability table
        'status': a.status
    } for a, av in appointments]), 200

@professor_bp.route('/api/professor/appointments/<int:appointment_id>/cancel', methods=['PUT'])
@jwt_required()
@role_required('professor')
def cancel_appointment(appointment_id):
    professor_id = get_jwt_identity()
    
    # Query the Appointment table, joining with the Availability table
    appointment = db.session.query(Appointment, Availability).join(
        Availability, Appointment.availability_id == Availability.id
    ).filter(
        Appointment.id == appointment_id,
        Appointment.professor_id == professor_id
    ).first_or_404()

    # Cancel the appointment
    appointment.Appointment.status = 'cancelled'
    
    # Set the availability to available
    appointment.Availability.is_available = True
    
    # Commit the changes to the database
    db.session.commit()
    
    return jsonify({"msg": "Appointment cancelled successfully"}), 200
