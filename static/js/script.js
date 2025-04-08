// static/js/script.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Initialize session booking calendar if present
    const calendarDays = document.querySelectorAll('.calendar-day');
    if (calendarDays.length > 0) {
        calendarDays.forEach(day => {
            day.addEventListener('click', function() {
                // Clear previous selection
                document.querySelectorAll('.calendar-day.selected').forEach(selected => {
                    selected.classList.remove('selected');
                });
                
                // Set new selection
                this.classList.add('selected');
                
                // Update hidden form field with selected date
                document.getElementById('selected_date').value = this.dataset.date;
                
                // Load available time slots for this date
                loadTimeSlots(this.dataset.date);
            });
        });
    }
    
    // Time slot selection
    const timeSlotContainer = document.getElementById('time-slots-container');
    if (timeSlotContainer) {
        timeSlotContainer.addEventListener('click', function(e) {
            if (e.target.classList.contains('time-slot-btn') && !e.target.classList.contains('booked')) {
                // Clear previous selection
                document.querySelectorAll('.time-slot-btn.selected').forEach(selected => {
                    selected.classList.remove('selected');
                });
                
                // Set new selection
                e.target.classList.add('selected');
                
                // Update hidden form field with selected time slot
                document.getElementById('selected_time_slot').value = e.target.dataset.slot;
                
                // Enable submit button
                document.getElementById('book-session-btn').disabled = false;
            }
        });
    }
    
    // Function to load available time slots via AJAX
    function loadTimeSlots(date) {
        // Show loading indicator
        const timeSlotContainer = document.getElementById('time-slots-container');
        if (!timeSlotContainer) return;
        
        timeSlotContainer.innerHTML = '<p class="text-center">Loading available time slots...</p>';
        
        // Make AJAX request to get available time slots
        fetch(`/session/available-slots/?date=${date}`)
            .then(response => response.json())
            .then(data => {
                if (data.slots && data.slots.length > 0) {
                    let html = '<div class="row">';
                    data.slots.forEach(slot => {
                        const btnClass = slot.is_available ? 'btn-outline-primary' : 'booked btn-outline-danger';
                        html += `
                            <div class="col-md-4 col-6">
                                <button type="button" 
                                        class="btn time-slot-btn ${btnClass}" 
                                        data-slot="${slot.slot_id}"
                                        ${!slot.is_available ? 'disabled' : ''}>
                                    ${slot.start_time} - ${slot.end_time}
                                </button>
                            </div>
                        `;
                    });
                    html += '</div>';
                    timeSlotContainer.innerHTML = html;
                } else {
                    timeSlotContainer.innerHTML = '<p class="text-center text-muted">No time slots available for this date.</p>';
                }
            })
            .catch(error => {
                console.error('Error loading time slots:', error);
                timeSlotContainer.innerHTML = '<p class="text-center text-danger">Error loading time slots. Please try again.</p>';
            });
    }
    
    // Payment form validation
    const paymentForm = document.getElementById('payment-form');
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Simple form validation
            const cardNumber = document.getElementById('card_number').value;
            const cardExpiry = document.getElementById('card_expiry').value;
            const cardCvv = document.getElementById('card_cvv').value;
            
            let isValid = true;
            let errorMessage = '';
            
            if (!/^\d{16}$/.test(cardNumber.replace(/\s/g, ''))) {
                isValid = false;
                errorMessage = 'Please enter a valid 16-digit card number.';
            } else if (!/^\d{2}\/\d{2}$/.test(cardExpiry)) {
                isValid = false;
                errorMessage = 'Please enter a valid expiry date (MM/YY).';
            } else if (!/^\d{3,4}$/.test(cardCvv)) {
                isValid = false;
                errorMessage = 'Please enter a valid CVV code.';
            }
            
            if (isValid) {
                // Show processing message
                document.getElementById('payment-status').innerHTML = '<div class="alert alert-info">Processing payment...</div>';
                
                // Simulate payment processing
                setTimeout(function() {
                    document.getElementById('payment-status').innerHTML = '<div class="alert alert-success">Payment successful! Redirecting...</div>';
                    
                    // Submit the form after delay
                    setTimeout(function() {
                        paymentForm.submit();
                    }, 1500);
                    
                }, 2000);
            } else {
                document.getElementById('payment-status').innerHTML = `<div class="alert alert-danger">${errorMessage}</div>`;
            }
        });
    }
});