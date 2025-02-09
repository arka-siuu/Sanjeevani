document.addEventListener('DOMContentLoaded', function() {
    // Sample data for doctors (you can replace it with actual data from your database)
    const doctors = [
        { name: "Dr. Neha Sharma", qualification: "MD", experience: "10 years", specialty: "Psychiatry" },
        { name: "Dr. Rahul Kapoor", qualification: "MD", experience: "8 years", specialty: "Gynecology" },
        { name: "Dr. Priya Singh", qualification: "MD", experience: "12 years", specialty: "Orthopedics" },
        { name: "Dr. Amit Patel", qualification: "MD", experience: "15 years", specialty: "Oncology" },
        { name: "Dr. Ananya Gupta", qualification: "MD", experience: "7 years", specialty: "Pediatrics" },
        { name: "Dr. Sanjay Kumar", qualification: "MD", experience: "10 years", specialty: "Pulmonology" },
        // Add more doctors for each specialty here
        { name: "Dr. Aarti Gupta", qualification: "MD", experience: "9 years", specialty: "Psychiatry" },
        { name: "Dr. Reena Sharma", qualification: "MD", experience: "11 years", specialty: "Gynecology" },
        { name: "Dr. Rakesh Singh", qualification: "MD", experience: "13 years", specialty: "Orthopedics" },
        { name: "Dr. Manoj Kumar", qualification: "MD", experience: "14 years", specialty: "Oncology" },
        { name: "Dr. Sneha Patel", qualification: "MD", experience: "8 years", specialty: "Pediatrics" },
        { name: "Dr. Mohan Sharma", qualification: "MD", experience: "12 years", specialty: "Pulmonology" }
    ];

    // Function to generate doctor listings based on specialty
    function generateDoctorList(specialty) {
        const doctorsList = document.getElementById('doctors-list');
        doctorsList.innerHTML = ''; // Clear existing list
        doctors.filter(doctor => doctor.specialty === specialty).forEach(doctor => {
            const doctorCard = document.createElement('div');
            doctorCard.classList.add('doctor');
            doctorCard.innerHTML = `
                <h2>${doctor.name}</h2>
                <p>Qualification: ${doctor.qualification}</p>
                <p>Experience: ${doctor.experience}</p>
                <label for="date">Select Date:</label>
                <input type="date" id="date-${doctor.name.replace(/\s/g, '-').toLowerCase()}" name="date">
                <br>
                <label for="time">Select Time:</label>
                <select id="time-${doctor.name.replace(/\s/g, '-').toLowerCase()}" name="time">
                    <option value="09:00">09:00 AM</option>
                    <option value="10:00">10:00 AM</option>
                    <option value="11:00">11:00 AM</option>
                    <option value="12:00">12:00 PM</option>
                    <option value="13:00">01:00 PM</option>
                    <option value="14:00">02:00 PM</option>
                    <option value="15:00">03:00 PM</option>
                    <option value="16:00">04:00 PM</option>
                    <option value="17:00">05:00 PM</option>
                </select>
                <br>
                <button class="book-btn" onclick="bookAppointment('${doctor.name}')">Book Appointment</button>
            `;
            doctorsList.appendChild(doctorCard);
        });
    }

    // Function to handle booking appointment
    window.bookAppointment = function(doctorName) {
        const selectedDate = document.getElementById(`date-${doctorName.replace(/\s/g, '-').toLowerCase()}`).value;
        const selectedTime = document.getElementById(`time-${doctorName.replace(/\s/g, '-').toLowerCase()}`).value;
        
        if (selectedDate === "" || selectedTime === "") {
            alert("Please select both date and time.");
            return;
        }

        const confirmationMessage = `You have booked an appointment with ${doctorName} on ${selectedDate} at ${selectedTime}.`;
        alert(confirmationMessage);
    }

    // Get the specialty from the ID of the section and generate doctor listings accordingly
    const specialty = document.getElementById('doctors-list').getAttribute('data-specialty');
    generateDoctorList(specialty);
});
