// static/js/script.js

// Espera a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function () {

    console.log("ChatDash Vapi script.js cargado.");

    // Activar tooltips de Bootstrap (si los usas)
    // Asegúrate de que los elementos con tooltips tengan el atributo data-toggle="tooltip"
    // Ejemplo: <button data-toggle="tooltip" title="Este es un tooltip">Botón</button>
    // $('[data-toggle="tooltip"]').tooltip(); // Si usas jQuery y Bootstrap's JS

    // Ejemplo de auto-refresco de la página (puedes descomentar y ajustar el tiempo)
    // const autoRefreshInterval = 60000; // 60 segundos
    // const currentPath = window.location.pathname;

    // if (currentPath === '/' || currentPath.includes('/dashboard') || currentPath.includes('/calls')) {
    //     console.log(`Auto-refresco activado para ${currentPath} cada ${autoRefreshInterval / 1000} segundos.`);
    //     setTimeout(() => {
    //         window.location.reload();
    //     }, autoRefreshInterval);
    // }


    // Ejemplo de cómo podrías implementar una función para obtener datos vía API
    // y actualizar una sección del DOM sin recargar toda la página.
    // Esto es más avanzado y requiere que tu backend (app.py) tenga endpoints API.

    /*
    async function updateDashboardData() {
        console.log("Intentando actualizar datos del dashboard vía API...");
        try {
            // Asume que tienes un endpoint en Flask en '/api/dashboard-data'
            const response = await fetch('/api/dashboard-data'); // Cambia esto a tu endpoint real
            if (!response.ok) {
                console.error(`Error HTTP al obtener datos: ${response.status}`);
                return;
            }
            const data = await response.json();

            // Aquí actualizarías el DOM con los 'data' recibidos.
            // Por ejemplo, si 'data.agents' es una lista de agentes:
            // const agentsTableBody = document.querySelector('#agents-table-body-id'); // Necesitarías un ID en tu tbody
            // if (agentsTableBody) {
            //     agentsTableBody.innerHTML = ''; // Limpiar la tabla actual
            //     data.agents.forEach(agent => {
            //         const row = agentsTableBody.insertRow();
            //         row.insertCell().textContent = agent.id;
            //         row.insertCell().textContent = agent.name;
            //         // ... más celdas
            //     });
            // }
            
            // Actualizar el timestamp de "Última Actualización"
            const lastUpdatedElement = document.querySelector('#dashboard-last-updated'); // Necesitarías un ID
            if(lastUpdatedElement) {
                lastUpdatedElement.textContent = 'Última Actualización: ' + new Date().toLocaleString();
            }

            console.log("Datos del dashboard actualizados vía API.");

        } catch (error) {
            console.error("Error al actualizar datos del dashboard vía API:", error);
        }
    }

    // Si quieres actualizar periódicamente:
    // const ajaxRefreshInterval = 30000; // 30 segundos
    // if (currentPath === '/' || currentPath.includes('/dashboard')) {
    //     setInterval(updateDashboardData, ajaxRefreshInterval);
    //     // updateDashboardData(); // Llamada inicial opcional
    // }
    */

});

// Puedes añadir más funciones aquí a medida que tu aplicación crezca.
// Por ejemplo, funciones para manejar clics en botones específicos,
// enviar datos a tu backend, etc.
