import pytest
from app import create_app, db
from app.models.user import User
from datetime import datetime, timedelta
import json

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_appointment_flow(client):
    # 1. Register users
    student_a1 = {
        'email': 'student_a1@test.com',
        'password': 'password123',
        'name': 'Student A1',
        'role': 'student'
    }
    client.post('/api/auth/register', json=student_a1)
    
    student_a2 = {
        'email': 'student_a2@test.com',
        'password': 'password123',
        'name': 'Student A2',
        'role': 'student'
    }
    client.post('/api/auth/register', json=student_a2)
    
    professor = {
        'email': 'professor@test.com',
        'password': 'password123',
        'name': 'Professor P1',
        'role': 'professor'
    }
    client.post('/api/auth/register', json=professor)
    
    # 2. Login users
    response = client.post('/api/auth/login', json={
        'email': student_a1['email'],
        'password': student_a1['password']
    })
    student_a1_token = json.loads(response.data)['token']
    
    response = client.post('/api/auth/login', json={
        'email': student_a2['email'],
        'password': student_a2['password']
    })
    student_a2_token = json.loads(response.data)['token']
    
    response = client.post('/api/auth/login', json={
        'email': professor['email'],
        'password': professor['password']
    })
    professor_token = json.loads(response.data)['token']
    
    # 3. Professor sets availability
    now = datetime.utcnow()
    availability_data = {
        'start_time': (now + timedelta(days=1)).isoformat(),
        'end_time': (now + timedelta(days=1, hours=1)).isoformat()
    }
    response = client.post(
        '/api/professor/availability',
        json=availability_data,
        headers={'Authorization': f'Bearer {professor_token}'}
    )
    assert response.status_code == 201
    
    # 4. Student A1 views available slots
    response = client.get(
        '/api/professor/1/availability',
        headers={'Authorization': f'Bearer {student_a1_token}'}
    )
    assert response.status_code == 200
    availabilities = json.loads(response.data)
    assert len(availabilities) == 1
    
    # 5. Student A1 books appointment
    response = client.post(
        '/api/appointments',
        json={'availability_id': availabilities[0]['id']},
        headers={'Authorization': f'Bearer {student_a1_token}'}
    )
    assert response.status_code == 201
    
    # 6. Professor cancels appointment
    response = client.get(
        '/api/professor/appointments',
        headers={'Authorization': f'Bearer {professor_token}'}
    )
    appointments = json.loads(response.data)
    
    response = client.put(
        f'/api/professor/appointments/{appointments[0]["id"]}/cancel',
        headers={'Authorization': f'Bearer {professor_token}'}
    )
    assert response.status_code == 200
    
    # 7. Student A1 checks appointments
    response = client.get(
        '/api/student/appointments',
        headers={'Authorization': f'Bearer {student_a1_token}'}
    )
    appointments = json.loads(response.data)
    assert len(appointments) == 1
    assert appointments[0]['status'] == 'cancelled'