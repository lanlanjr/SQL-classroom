// Main JavaScript for SQL Classroom

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize all popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-hide alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert) {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
    
    // Add multiselect functionality to select elements with the 'multiselect' class
    const multiSelects = document.querySelectorAll('select.multiselect');
    multiSelects.forEach(function(select) {
        // If we had a multiselect library, we'd initialize it here
        select.setAttribute('multiple', 'multiple');
    });
    
    // Add confirmation to delete buttons and other confirmation actions
    const confirmButtons = document.querySelectorAll('.btn-delete, [data-confirm]');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const message = button.getAttribute('data-confirm') || 'Are you sure you want to delete this item? This action cannot be undone.';
            const title = button.getAttribute('data-confirm-title') || 'Confirm Action';
            const confirmText = button.getAttribute('data-confirm-button') || 'Yes, proceed';
            const cancelText = button.getAttribute('data-cancel-button') || 'Cancel';
            const icon = button.getAttribute('data-icon') || 'warning';
            
            try {
                const result = await Swal.fire({
                    title: title,
                    text: message,
                    icon: icon,
                    showCancelButton: true,
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#d33',
                    confirmButtonText: confirmText,
                    cancelButtonText: cancelText
                });
                
                if (result.isConfirmed) {
                    // If this is a link, navigate to the href
                    if (button.tagName === 'A' && button.href) {
                        window.location.href = button.href;
                    }
                    // If this is a form submit button, submit the form
                    else if (button.type === 'submit') {
                        button.form.submit();
                    }
                    // If this is a button with form attribute, submit that form
                    else if (button.getAttribute('form')) {
                        document.getElementById(button.getAttribute('form')).submit();
                    }
                    // For custom handling, dispatch a custom event
                    else {
                        button.dispatchEvent(new CustomEvent('confirm'));
                    }
                }
            } catch (error) {
                console.error('SweetAlert2 error:', error);
            }
        });
    });
    
    // Global function for showing confirmation dialogs
    window.showConfirmation = async function(options = {}) {
        const defaultOptions = {
            title: 'Confirm Action',
            text: 'Are you sure you want to proceed?',
            icon: 'warning',
            confirmButtonText: 'Yes, proceed',
            cancelButtonText: 'Cancel',
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            showCancelButton: true
        };
        
        const swalOptions = { ...defaultOptions, ...options };
        return Swal.fire(swalOptions);
    };
    
    // Global function for showing success messages
    window.showSuccess = function(message, timer = 2000) {
        return Swal.fire({
            icon: 'success',
            title: 'Success',
            text: message,
            timer: timer,
            showConfirmButton: false
        });
    };
    
    // Global function for showing error messages
    window.showError = function(message) {
        return Swal.fire({
            icon: 'error',
            title: 'Error',
            text: message
        });
    };
    
    // Handle form submissions with the 'needs-validation' class
    const forms = document.querySelectorAll('form.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Set date inputs to today's date
    const dateInputs = document.querySelectorAll('input[type="date"].set-today');
    if (dateInputs.length > 0) {
        const today = new Date().toISOString().split('T')[0];
        dateInputs.forEach(function(input) {
            input.value = today;
        });
    }

    // Function to handle logout and prevent back navigation
    function handleLogout() {
        // Clear browser history
        window.history.pushState(null, '', window.location.href);
        window.onpopstate = function () {
            window.history.pushState(null, '', window.location.href);
        };
        
        // Redirect to logout URL using the dynamic URL
        window.location.href = URLS.logout;
        
        // Prevent default link behavior
        return false;
    }

    // Find all logout links and attach the handler
    const logoutLinks = document.querySelectorAll(`a[href="${URLS.logout}"]`);
    logoutLinks.forEach(link => {
        link.onclick = handleLogout;
    });
}); 