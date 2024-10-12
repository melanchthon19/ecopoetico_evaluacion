function validateForm() {
    var isValid = true;  // Assume form is valid initially
    var selects = document.querySelectorAll('select'); // Get all select dropdowns

    // Loop through all select elements to check if any are unselected
    for (var i = 0; i < selects.length; i++) {
        if (selects[i].value === "") {  // If any dropdown is unselected, form is invalid
            isValid = false;
            break;  // Stop checking if we find an invalid field
        }
    }

    // Show alert if form is invalid
    if (!isValid) {
        alert("Por favor, selecciona una calificación para todos los poemas antes de enviar.");
    }

    // Return the validity state
    return isValid;
}

