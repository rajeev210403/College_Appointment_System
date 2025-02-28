import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { Calendar, LogOut } from 'lucide-react';
import { useAuthStore } from '../store/auth';
import api from '../lib/axios';

interface Availability {
  id: number;
  start_time: string;
  end_time: string;
}

interface Appointment {
  id: number;
  professor_id: number;
  start_time: string;
  status: string;
}

export default function StudentDashboard() {
  const [availabilities, setAvailabilities] = useState<Availability[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [selectedProfessor, setSelectedProfessor] = useState<number>(0);
  const { user, logout } = useAuthStore();

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      const response = await api.get('/student/appointments');
      setAppointments(response.data);
    } catch (error) {
      console.error('Failed to fetch appointments:', error);
    }
  };

  const fetchAvailabilities = async (professorId: number) => {
    try {
      const response = await api.get(`/professor/${professorId}/availability`);
      setAvailabilities(response.data);
    } catch (error) {
      console.error('Failed to fetch availabilities:', error);
    }
  };

  const handleBookAppointment = async (availabilityId: number) => {
    try {
      await api.post('/appointments', { availability_id: availabilityId });
      // Refresh both appointments and availabilities
      fetchAppointments();
      if (selectedProfessor) {
        fetchAvailabilities(selectedProfessor);
      }
    } catch (error) {
      console.error('Failed to book appointment:', error);
    }
  };

  const handleProfessorSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const professorId = parseInt(e.target.value, 10);
    setSelectedProfessor(professorId);
    if (professorId) {
      fetchAvailabilities(professorId);
    } else {
      setAvailabilities([]);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Calendar className="h-6 w-6 text-indigo-600" />
              <span className="ml-2 text-xl font-semibold">Student Dashboard</span>
            </div>
            <div className="flex items-center">
              <span className="mr-4">Welcome, {user?.name}</span>
              <button
                onClick={logout}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h2 className="text-lg font-medium mb-4">Book New Appointment</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Professor ID</label>
                <input
                  type="number"
                  value={selectedProfessor || ''}
                  onChange={handleProfessorSelect}
                  placeholder="Enter professor ID"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
              </div>

              {availabilities.length > 0 && (
                <div className="mt-4">
                  <h3 className="text-md font-medium mb-2">Available Time Slots</h3>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {availabilities.map((availability) => (
                      <div
                        key={availability.id}
                        className="border rounded-lg p-4 hover:shadow-md transition-shadow"
                      >
                        <p className="text-sm text-gray-600">
                          {format(new Date(availability.start_time), 'PPp')} -{' '}
                          {format(new Date(availability.end_time), 'p')}
                        </p>
                        <button
                          onClick={() => handleBookAppointment(availability.id)}
                          className="mt-2 w-full inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        >
                          Book
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium mb-4">My Appointments</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Time
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Professor ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {appointments.map((appointment) => (
                    <tr key={appointment.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {format(new Date(appointment.start_time), 'PPp')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {appointment.professor_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span
                          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            appointment.status === 'scheduled'
                              ? 'bg-green-100 text- green-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {appointment.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}