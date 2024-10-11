let formSubmitted = false;

// Attach beforeunload event to window
window.addEventListener('beforeunload', function (e) {
    if (!formSubmitted) {
        // Show a warning if the form is not submitted
        e.preventDefault();
        e.returnValue = ''; // Required for most browsers
    }
});

// Mark form as submitted when it is actually submitted
document.querySelector('form').addEventListener('submit', function () {
    formSubmitted = true;
});
