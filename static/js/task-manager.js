$(document).ready(function () {
    $('#id_assigners').select2({
        placeholder: 'Select assignees...',
        allowClear: true,
        width: '100%'
    });

    // Deadline validation
    const deadlineInput = document.getElementById('id_deadline');
    if (deadlineInput) {
        const now = new Date();
        const minDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
            .toISOString()
            .slice(0, 16);
        deadlineInput.min = minDateTime;

        deadlineInput.addEventListener('change', function() {
            const selectedDate = new Date(this.value);
            if (selectedDate < now) {
                this.setCustomValidity('Please select a future date and time.');
            } else {
                this.setCustomValidity('');
            }
        });
    }
});


(function () {
    'use strict'
    var forms = document.querySelectorAll('.needs-validation')
    Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault()
                    event.stopPropagation()
                }
                form.classList.add('was-validated')
            }, false)
        })
})()
