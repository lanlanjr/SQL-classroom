// Function to show a confirmation dialog using SweetAlert2
function showConfirmDialog(options) {
    return Swal.fire({
        title: options.title || 'Confirm Action',
        text: options.text || 'Are you sure you want to proceed?',
        icon: options.icon || 'warning',
        showCancelButton: true,
        confirmButtonColor: options.confirmButtonColor || '#3085d6',
        cancelButtonColor: options.cancelButtonColor || '#dc3545',
        confirmButtonText: options.confirmButtonText || 'Yes',
        cancelButtonText: options.cancelButtonText || 'No'
    });
}

// Function to handle submit answer confirmation
function confirmSubmitAnswer() {
    return showConfirmDialog({
        title: 'Submit Answer',
        text: 'Are you sure you want to submit this answer? This will be recorded as your submission.',
        icon: 'question',
        confirmButtonColor: '#28a745',
        confirmButtonText: 'Yes, submit my answer',
        cancelButtonText: 'No, keep editing'
    });
}

// Function to handle reset terminal confirmation
function confirmResetTerminal() {
    return showConfirmDialog({
        title: 'Reset Terminal',
        text: 'Are you sure you want to reset the terminal? Your query will be cleared.',
        icon: 'warning',
        confirmButtonText: 'Yes, clear it',
        cancelButtonText: 'No, keep my query'
    });
}

// Function to show correct answer alert
function showCorrectAnswerAlert(message) {
    return Swal.fire({
        title: 'Correct!',
        text: message || 'Your answer is correct! Great job!',
        icon: 'success',
        confirmButtonColor: '#28a745',
        confirmButtonText: 'Continue',
        allowOutsideClick: false,
        showConfirmButton: true
    });
}

// Function to show wrong answer alert
function showWrongAnswerAlert(message) {
    return Swal.fire({
        title: 'Incorrect',
        text: message || 'Your answer is incorrect. Please try again.',
        icon: 'error',
        confirmButtonColor: '#dc3545',
        confirmButtonText: 'Try Again',
        allowOutsideClick: false,
        showConfirmButton: true
    });
} 