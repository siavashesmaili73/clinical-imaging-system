// Email configuration
const EMAIL_CONFIG = {
    recipientEmail: 'siavash.esmaili73@gmail.com',
    senderEmail: 'clinic@example.com',
    reminderDays: 2
};

// DOM Elements
const navItems = document.querySelectorAll('.nav-item');
const profileUpload = document.getElementById('profile-upload');
const profileInput = document.getElementById('profile-input');
const profileImg = document.getElementById('profile-img');
const xrayUpload = document.getElementById('xray-upload');
const xrayInput = document.getElementById('xray-input');
const addTreatmentBtn = document.querySelector('.add-treatment');

// Patient data management
let patients = [
    { 
        id: 1, 
        name: 'John Smith', 
        email: 'siavash.esmaili73@gmail.com',
        nextAppointment: '2024-12-20', 
        appointments: [
            { date: '2024-12-20', time: '09:00', treatment: 'Dental Cleaning' }
        ]
    },
    { 
        id: 2, 
        name: 'Sarah Johnson', 
        email: 'siavash.esmaili73@gmail.com',
        nextAppointment: '2024-12-22', 
        appointments: [
            { date: '2024-12-20', time: '11:30', treatment: 'Root Canal' }
        ]
    },
    { 
        id: 3, 
        name: 'Michael Brown', 
        email: 'siavash.esmaili73@gmail.com',
        nextAppointment: '2024-12-23', 
        appointments: [
            { date: '2024-12-23', time: '14:00', treatment: 'Teeth Whitening' }
        ]
    }
];

// Email reminder functionality
function sendEmailReminder(patient, appointment) {
    const emailBody = `
        Dear ${patient.name},

        This is a reminder that you have a dental appointment scheduled for:
        Date: ${appointment.date}
        Time: ${appointment.time}
        Treatment: ${appointment.treatment}

        Location: NYU College of Dentistry
        Contact: (123) 456-7890

        Please arrive 10 minutes before your appointment time.
        If you need to reschedule, please call us at least 24 hours in advance.

        Best regards,
        Ms. Mitra Esmaili Dental Clinic
    `;

    // In a real application, this would use a server-side email service
    // For demonstration, we'll log the email content
    console.log('Sending email reminder to:', patient.email);
    console.log('Email content:', emailBody);

    // Simulate email sending
    return new Promise((resolve) => {
        setTimeout(() => {
            console.log('Email sent successfully');
            resolve();
        }, 1000);
    });
}

// Check for upcoming appointments and send reminders
function checkUpcomingAppointments() {
    const today = new Date();
    const twoDaysFromNow = new Date(today);
    twoDaysFromNow.setDate(today.getDate() + EMAIL_CONFIG.reminderDays);

    patients.forEach(patient => {
        patient.appointments.forEach(appointment => {
            const appointmentDate = new Date(appointment.date);
            
            // Check if appointment is in 2 days
            if (appointmentDate.toDateString() === twoDaysFromNow.toDateString()) {
                sendEmailReminder(patient, appointment);
            }
        });
    });
}

// Add new appointment with email reminder
function addAppointment(patientId, date, time, treatment) {
    const patient = patients.find(p => p.id === patientId);
    if (patient) {
        const appointment = { date, time, treatment };
        patient.appointments.push(appointment);
        patient.nextAppointment = date;

        // Schedule email reminder
        const appointmentDate = new Date(date);
        const reminderDate = new Date(appointmentDate);
        reminderDate.setDate(appointmentDate.getDate() - EMAIL_CONFIG.reminderDays);

        // Set up reminder check
        const timeUntilReminder = reminderDate.getTime() - new Date().getTime();
        if (timeUntilReminder > 0) {
            setTimeout(() => {
                sendEmailReminder(patient, appointment);
            }, timeUntilReminder);
        }
    }
}

// Navigation
navItems.forEach(item => {
    item.addEventListener('click', () => {
        navItems.forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');
        const view = item.getAttribute('data-view');
        switchView(view);
    });
});

function switchView(view) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(`${view}-view`).classList.add('active');
    
    switch(view) {
        case 'calendar':
            initializeCalendar();
            break;
        case 'notes':
            initializeNotes();
            break;
        case 'reminders':
            initializeReminders();
            break;
    }
}

// Calendar functionality
function initializeCalendar() {
    const daysContainer = document.querySelector('.days');
    const currentMonthElement = document.querySelector('.current-month');
    const prevButton = document.querySelector('.calendar-nav.prev');
    const nextButton = document.querySelector('.calendar-nav.next');
    const dayDetails = document.querySelector('.day-details');
    
    let currentDate = new Date();
    
    function updateCalendar() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 
                          'July', 'August', 'September', 'October', 'November', 'December'];
        currentMonthElement.textContent = `${monthNames[month]} ${year}`;
        
        daysContainer.innerHTML = '';
        
        const firstDay = new Date(year, month, 1).getDay();
        const totalDays = new Date(year, month + 1, 0).getDate();
        
        for(let i = 0; i < firstDay; i++) {
            const emptyDay = document.createElement('div');
            daysContainer.appendChild(emptyDay);
        }
        
        for(let day = 1; day <= totalDays; day++) {
            const dayElement = document.createElement('div');
            dayElement.textContent = day;
            
            const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            
            const hasAppointments = patients.some(patient => 
                patient.appointments.some(apt => apt.date === dateStr)
            );
            
            if(hasAppointments) {
                dayElement.classList.add('has-appointments');
            }
            
            if(year === new Date().getFullYear() && 
               month === new Date().getMonth() && 
               day === new Date().getDate()) {
                dayElement.classList.add('today');
            }
            
            dayElement.addEventListener('click', () => {
                showDayDetails(dateStr);
            });
            
            daysContainer.appendChild(dayElement);
        }
    }
    
    function showDayDetails(dateStr) {
        const date = new Date(dateStr);
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 
                          'July', 'August', 'September', 'October', 'November', 'December'];
        
        dayDetails.querySelector('h3').textContent = `${monthNames[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`;
        
        const appointmentsContainer = dayDetails.querySelector('.appointments');
        appointmentsContainer.innerHTML = '';
        
        const dayAppointments = [];
        patients.forEach(patient => {
            patient.appointments.forEach(apt => {
                if(apt.date === dateStr) {
                    dayAppointments.push({
                        ...apt,
                        patientName: patient.name
                    });
                }
            });
        });
        
        dayAppointments.sort((a, b) => a.time.localeCompare(b.time));
        
        dayAppointments.forEach(apt => {
            const appointmentElement = document.createElement('div');
            appointmentElement.className = 'appointment';
            appointmentElement.innerHTML = `
                <div class="time">${apt.time}</div>
                <div class="patient-info">
                    <strong>${apt.patientName}</strong>
                    <p>Treatment: ${apt.treatment}</p>
                </div>
            `;
            appointmentsContainer.appendChild(appointmentElement);
        });
    }
    
    prevButton.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        updateCalendar();
    });
    
    nextButton.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        updateCalendar();
    });
    
    updateCalendar();
}

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    initializePatientList();
    switchView('home');
    
    // Check for appointments requiring reminders
    checkUpcomingAppointments();
    
    // Set up daily reminder check
    setInterval(checkUpcomingAppointments, 24 * 60 * 60 * 1000); // Check every 24 hours
});

// Notes functionality
function initializeNotes() {
    const addNoteBtn = document.querySelector('.add-note');
    const saveNoteBtn = document.querySelector('.save-note');
    const notesList = document.querySelector('.notes');
    const noteTitle = document.querySelector('.note-title');
    const noteContent = document.querySelector('.note-content');
    
    let notes = JSON.parse(localStorage.getItem('notes') || '[]');
    
    function updateNotesList() {
        notesList.innerHTML = '';
        notes.forEach((note, index) => {
            const noteElement = document.createElement('div');
            noteElement.className = 'note-item';
            noteElement.innerHTML = `
                <h3>${note.title}</h3>
                <p>${note.content.substring(0, 50)}${note.content.length > 50 ? '...' : ''}</p>
            `;
            noteElement.addEventListener('click', () => {
                noteTitle.value = note.title;
                noteContent.value = note.content;
            });
            notesList.appendChild(noteElement);
        });
    }
    
    addNoteBtn.addEventListener('click', () => {
        noteTitle.value = '';
        noteContent.value = '';
    });
    
    saveNoteBtn.addEventListener('click', () => {
        const title = noteTitle.value.trim();
        const content = noteContent.value.trim();
        
        if(title && content) {
            notes.push({ title, content, date: new Date().toISOString() });
            localStorage.setItem('notes', JSON.stringify(notes));
            updateNotesList();
            noteTitle.value = '';
            noteContent.value = '';
        }
    });
    
    updateNotesList();
}

// Reminders functionality
function initializeReminders() {
    const saveReminderBtn = document.querySelector('.save-reminder');
    const remindersList = document.querySelector('.reminders');
    const reminderTitle = document.querySelector('.reminder-title');
    const reminderDateTime = document.querySelector('.reminder-datetime');
    
    let reminders = JSON.parse(localStorage.getItem('reminders') || '[]');
    
    function updateRemindersList() {
        remindersList.innerHTML = '';
        reminders.sort((a, b) => new Date(a.datetime) - new Date(b.datetime))
                .forEach((reminder, index) => {
            const reminderElement = document.createElement('div');
            reminderElement.className = 'reminder-item';
            reminderElement.innerHTML = `
                <h4>${reminder.title}</h4>
                <p>${new Date(reminder.datetime).toLocaleString()}</p>
            `;
            remindersList.appendChild(reminderElement);
        });
    }
    
    saveReminderBtn.addEventListener('click', () => {
        const title = reminderTitle.value.trim();
        const datetime = reminderDateTime.value;
        
        if(title && datetime) {
            reminders.push({ title, datetime });
            localStorage.setItem('reminders', JSON.stringify(reminders));
            updateRemindersList();
            reminderTitle.value = '';
            reminderDateTime.value = '';
        }
    });
    
    updateRemindersList();
}

// Patient list functionality
function initializePatientList() {
    const patientCards = document.querySelectorAll('.patient-card');
    const patientDetails = document.querySelector('.patient-details');
    
    patientCards.forEach(card => {
        card.addEventListener('click', () => {
            const patientId = card.getAttribute('data-id');
            const patient = patients.find(p => p.id === parseInt(patientId));
            if (patient) {
                showPatientDetails(patient);
            }
        });
    });
}

function showPatientDetails(patient) {
    const patientDetails = document.querySelector('.patient-details');
    patientDetails.classList.remove('hidden');
    
    // Update form fields with patient data
    document.querySelector('input[placeholder="Patient Name"]').value = patient.name;
    // You would typically populate other fields here
}

// Profile Picture Upload
profileUpload.addEventListener('click', () => {
    profileInput.click();
});

profileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            profileImg.src = e.target.result;
            console.log('Profile picture updated');
        };
        reader.readAsDataURL(file);
    }
});

// X-Ray Upload
xrayUpload.addEventListener('click', () => {
    xrayInput.click();
});

xrayInput.addEventListener('change', (e) => {
    const files = Array.from(e.target.files);
    files.forEach(file => {
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                addXrayToGallery(e.target.result);
            };
            reader.readAsDataURL(file);
        }
    });
});

function addXrayToGallery(imgSrc) {
    const xrayImg = document.createElement('div');
    xrayImg.style.backgroundImage = `url(${imgSrc})`;
    xrayImg.style.backgroundSize = 'cover';
    xrayImg.style.backgroundPosition = 'center';
    xrayImg.className = 'upload-box';
    
    xrayUpload.insertBefore(xrayImg, xrayUpload.firstChild);
}

// Add Treatment Entry
addTreatmentBtn.addEventListener('click', () => {
    const treatmentSection = document.querySelector('.treatment-section');
    const newEntry = document.createElement('div');
    newEntry.className = 'treatment-entry';
    newEntry.innerHTML = `
        <input type="date" class="treatment-date">
        <textarea placeholder="Treatment Details" class="treatment-details"></textarea>
    `;
    
    treatmentSection.insertBefore(newEntry, addTreatmentBtn);
});

// Auto-save functionality for patient details
const detailInputs = document.querySelectorAll('.detail-input');
detailInputs.forEach(input => {
    input.addEventListener('change', () => {
        console.log(`Saving ${input.placeholder}: ${input.value}`);
    });
});
