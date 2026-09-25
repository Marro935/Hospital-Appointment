/**
 * Hospital Management System (HMS) - Client JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // ---------------------------------------------------------
    // Mobile Sidebar Toggle
    // ---------------------------------------------------------
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const sidebar = document.querySelector('.sidebar');
    if (sidebarToggleBtn && sidebar) {
        sidebarToggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('show');
        });
    }

    // ---------------------------------------------------------
    // Auto-dismiss Alerts after 5 seconds
    // ---------------------------------------------------------
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });
});

/**
 * Quick Autofill Helper for Demo Login Credentials
 */
function fillLogin(role) {
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');

    if (!usernameInput || !passwordInput) return;

    switch (role) {
        case 'admin':
            usernameInput.value = 'admin';
            passwordInput.value = 'admin123';
            break;
        case 'doctor':
            usernameInput.value = 'dr_sarah';
            passwordInput.value = 'doctor123';
            break;
        case 'receptionist':
            usernameInput.value = 'receptionist1';
            passwordInput.value = 'rec123';
            break;
        case 'patient':
            usernameInput.value = 'patient_john';
            passwordInput.value = 'patient123';
            break;
    }

    // Add subtle visual feedback
    usernameInput.classList.add('is-valid');
    passwordInput.classList.add('is-valid');
    setTimeout(() => {
        usernameInput.classList.remove('is-valid');
        passwordInput.classList.remove('is-valid');
    }, 1500);
}

/**
 * Update Appointment Status via AJAX
 */
async function updateAppointmentStatus(appointmentId, status) {
    if (!confirm(`Are you sure you want to mark this appointment as '${status}'?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/appointments/${appointmentId}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status })
        });

        const data = await response.json();
        if (response.ok) {
            window.location.reload();
        } else {
            alert(data.error || 'Failed to update appointment status.');
        }
    } catch (err) {
        console.error('Error updating status:', err);
        alert('Server connection error. Please try again.');
    }
}

/**
 * Delete Item (Patient / Appointment / User) with confirmation
 */
async function deleteItem(endpoint, id, itemLabel) {
    if (!confirm(`Are you sure you want to permanently delete this ${itemLabel}?`)) {
        return;
    }

    try {
        const response = await fetch(`${endpoint}/${id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();
        if (response.ok) {
            window.location.reload();
        } else {
            alert(data.error || 'Failed to delete record.');
        }
    } catch (err) {
        console.error('Delete error:', err);
        alert('Network error while attempting deletion.');
    }
}

/**
 * Open Consultation & Prescription Modal for Doctors
 */
function openPrescriptionModal(patientId, patientName, appointmentId = null) {
    const modalEl = document.getElementById('addRecordModal');
    if (!modalEl) return;

    const patientSelect = document.getElementById('recordPatientSelect');
    if (patientSelect) {
        patientSelect.value = patientId;
    }

    const modal = new bootstrap.Modal(modalEl);
    modal.show();
}
