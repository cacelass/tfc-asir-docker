let usuario = "";
let intervaloTiempo = null;

const loginTitle = document.getElementById('login-title');
const loginForm = document.getElementById('login-form');
const holaSection = document.getElementById('hola-section');
const adiosSection = document.getElementById('adios-section');

// Mostrar login y título
function mostrarLogin() {
    if (intervaloTiempo) {
        clearInterval(intervaloTiempo);
        intervaloTiempo = null;
    }
    loginForm.reset();
    loginTitle.style.display = 'block';
    loginForm.style.display = 'block';
    holaSection.style.display = 'none';
    adiosSection.style.display = 'none';
    usuario = "";
}

// Ocultar login y título
function ocultarLogin() {
    loginTitle.style.display = 'none';
    loginForm.style.display = 'none';
}

// Mostrar la pantalla principal (hola)
function mostrarHola() {
    holaSection.style.display = 'block';
    adiosSection.style.display = 'none';

    // Primero pintamos todos los datos y metemos un span con id="valor-tiempo"
    fetch('/holamundo', {
        headers: {
            'autenticado': 'si',
            'usuario': usuario
        }
    })
    .then(res => res.json())
    .then(data => {
        let meteoHtml = "";
        if (data.meteo && Object.keys(data.meteo).length > 0) {
            meteoHtml = `
                <ul>
                    <li><b>Temperatura:</b> ${data.meteo.temperatura} ºC</li>
                    <li><b>Sensación térmica:</b> ${data.meteo.sensacion_termica} ºC</li>
                    <li><b>Estado cielo:</b> ${data.meteo.estado_cielo}</li>
                    <li><b>Tendencia temperatura:</b> ${data.meteo.tendencia_temperatura}</li>
                    <li><b>Viento:</b> ${data.meteo.viento}</li>
                    <li><b>Fecha:</b> ${data.meteo.fecha}</li>
                    <li><b>Concello:</b> ${data.meteo.concello}</li>
                    <li><b>Provincia:</b> ${data.meteo.provincia}</li>
                </ul>
            `;
        } else {
            meteoHtml = `<p><i>No hay datos meteorológicos disponibles.</i></p>`;
        }
        holaSection.innerHTML = `
            <h2>${data.bienvenida}</h2>
            <p>Bienvenido, ${data.usuario}!</p>
            <p><b>Provincia:</b> ${data.provincia}</p>
            <p><b>Concello:</b> ${data.concello ? data.concello : ''}</p>
            <img src="${data.foto_perfil}" alt="Foto de perfil" style="width:100px;height:100px;border-radius:50%;object-fit:cover;margin-bottom:1rem;">
            <p><b>Edad:</b> ${data.edad}</p>
            <p><b>Tiempo actual:</b> <span id="valor-tiempo">${data.tiempo}</span></p>
            <div>${meteoHtml}</div>
            <button id="ir-adios">Ir a Adiós mundo</button>
        `;
        document.getElementById('ir-adios').onclick = mostrarAdios;

        // Iniciamos el refresco automático del tiempo
        if (intervaloTiempo) clearInterval(intervaloTiempo);
        intervaloTiempo = setInterval(actualizarSoloTiempo, 10000);
    })
    .catch(err => {
        holaSection.innerHTML = `<p>Error obteniendo los datos: ${err}</p>`;
    });
}

// Solo actualiza el campo de tiempo (no repinta toda la página)
function actualizarSoloTiempo() {
    fetch('/holamundo', {
        headers: {
            'autenticado': 'si',
            'usuario': usuario
        }
    })
    .then(res => res.json())
    .then(data => {
        const tiempoElem = document.getElementById('valor-tiempo');
        if (tiempoElem) {
            tiempoElem.textContent = data.tiempo;
        }
        // Si quieres actualizar algún otro campo puntual, puedes añadirlo aquí
    })
    .catch(err => {
        const tiempoElem = document.getElementById('valor-tiempo');
        if (tiempoElem) {
            tiempoElem.textContent = 'Error';
        }
    });
}

function mostrarAdios() {
    holaSection.style.display = 'none';
    adiosSection.style.display = 'block';
    if (intervaloTiempo) {
        clearInterval(intervaloTiempo);
        intervaloTiempo = null;
    }
    fetch('/adiosmundo', { headers: { 'autenticado': 'si' } })
        .then(res => res.json())
        .then(adiosData => {
            adiosSection.innerHTML = `
                <h2>¿Seguro que quiere salir, <span id="nombre-usuario"></span>?</h2>
                <button id="logout-btn">Desloguearse</button>
            `;
            document.getElementById('nombre-usuario').textContent = usuario;
            document.getElementById('logout-btn').onclick = mostrarLogin;
        });
}

loginForm.addEventListener('submit', function(e) {
    e.preventDefault();
    usuario = document.getElementById('username').value;
    const pass = document.getElementById('password').value;
    fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: usuario, password: pass })
    })
    .then(res => res.json())
    .then(data => {
        if (data.autenticado === 'si') {
            ocultarLogin();
            mostrarHola();
        } else {
            alert('Usuario o contraseña incorrectos');
        }
    });
});

// Por si recargas y hay que mostrar login por defecto
mostrarLogin();
