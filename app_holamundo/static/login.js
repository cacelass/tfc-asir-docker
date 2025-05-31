document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault();  // Evita el envío tradicional del form
    const usuario = document.getElementById("usuario").value;
    const clave = document.getElementById("clave").value;
    const errorElem = document.getElementById("error");
    errorElem.textContent = "";

    fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ usuario: usuario, clave: clave })
    })
    .then(response => {
        if (response.ok) {
            // Autenticación correcta: redirigir a welcome.html
            window.location.href = "welcome.html";
        } else if (response.status === 401) {
            return response.json().then(data => { throw new Error(data.detail || "Credenciales incorrectas"); });
        } else {
            throw new Error("Error en la autenticación");
        }
    })
    .catch(error => {
        // Mostrar mensaje de error
        errorElem.textContent = error.message;
    });
});
