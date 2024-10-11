function validateForm() {
    var isValid = true;
    var selects = document.querySelectorAll('select'); // Get all select dropdowns
    for (var i = 0; i < selects.length; i++) {
        if (selects[i].value === "") {  // Check if any dropdown is unselected
            isValid = false;
            break;
        }
    }

    if (!isValid) {
        alert("Por favor, selecciona una calificación para todos los poemas antes de enviar.");
    }

    return isValid; // Prevent form submission if not valid
}
