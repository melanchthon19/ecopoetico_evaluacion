let formSubmitted = false;  // Track if the form has been submitted

// Attach the beforeunload event to always show the warning unless form is submitted
window.addEventListener('beforeunload', function (e) {
    console.log("User is trying to leave the page.");  // Debug log for page unload
    if (!formSubmitted) {
        console.log("Warning: form not submitted yet.");  // Log when the form has not been submitted
        e.preventDefault();
        e.returnValue = '';  // Show the warning dialog
    } else {
        console.log("No warning: form was submitted.");  // Log when the form was submitted
    }
});

// Select all links that should trigger a warning (Instrucciones and Cerrar Sesión)
const warningLinks = document.querySelectorAll('.warning-link');

// Attach the click event listener to each link to display the warning
warningLinks.forEach(function (link) {
    link.addEventListener('click', function (event) {
        console.log("User clicked a warning link:", event.target.href);  // Log the link click
        const confirmation = confirm("Tienes anotaciones sin enviar. ¿Estás seguro de que quieres abandonar esta página?");
        
        if (!confirmation) {
            console.log("User canceled navigation.");  // Log when the user cancels the navigation
            event.preventDefault();  // Stop the navigation
        } else {
            console.log("User confirmed navigation.");  // Log when the user confirms the navigation
        }
    });
});

// Attach the submit event to the form
document.querySelector('form').addEventListener('submit', function (event) {
    console.log("Form submission initiated.");  // Log when form submission starts
    //var isValid = validateForm();
    const isValid = false;
    if (isValid) {
        console.log("Form validation passed. Proceeding with submission.");  // Log if the form is valid
        formSubmitted = true;  // Mark form as submitted to stop warnings on page unload
    } else {
        console.log("Form validation failed. Stopping submission.");  // Log if the form is invalid
        event.preventDefault();
        //alert("Por favor, selecciona una calificación para todos los poemas antes de enviar.");
    }
});

