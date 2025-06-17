document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const response = await fetch("/token", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    });

    const result = document.getElementById("message");

    if (response.ok) {
        const data = await response.json();
        localStorage.setItem("token", data.access_token);

        // Redirigir dependiendo del host
        const hostname = window.location.hostname;
        if (hostname.includes("holamundo")) {
            window.location.href = "/static/welcome.html?tipo=hola";
        } else if (hostname.includes("adiosmundo")) {
            window.location.href = "/static/welcome.html?tipo=adios";
        } else {
            result.innerText = "No se pudo determinar la aplicación.";
        }
    } else {
        result.innerText = "Credenciales inválidas. Inténtalo de nuevo.";
    }
});
