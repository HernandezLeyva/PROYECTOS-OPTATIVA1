// FriendlyEats - JavaScript del formulario y de las acciones de detalle.

function showMessage(text, ok) {
    const message = document.getElementById("message");
    if (!message) return;
    message.textContent = text;
    message.className = "message " + (ok ? "message-ok" : "message-error");
}

// Convierte la respuesta de error de FastAPI (string o lista de errores 422) en texto.
function errorText(error) {
    const detail = error && error.detail;
    if (Array.isArray(detail)) {
        return detail
            .map((e) => `${(e.loc || []).slice(1).join(".")}: ${e.msg}`)
            .join(" | ");
    }
    return detail || "Ocurrió un error al guardar.";
}

// ---------- Crear / editar ----------
const form = document.getElementById("restaurant-form");

if (form) {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const isEdit = form.dataset.mode === "edit";
        const id = form.dataset.id;

        const data = Object.fromEntries(new FormData(form));
        data.price = Number(data.price);
        data.photoUrl = (data.photoUrl || "").trim() || null;

        const url = isEdit ? `/api/v1/restaurants/${id}` : "/api/v1/restaurants";
        const submit = form.querySelector("button[type=submit]");
        submit.disabled = true;

        try {
            const response = await fetch(url, {
                method: isEdit ? "PATCH" : "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });

            if (response.ok) {
                const saved = await response.json();
                showMessage(
                    isEdit ? "Restaurante actualizado correctamente" : "Restaurante creado correctamente",
                    true
                );
                const flag = isEdit ? "updated" : "created";
                setTimeout(() => {
                    window.location.href = `/restaurants/${saved.id}?msg=${flag}`;
                }, 800);
            } else {
                showMessage(errorText(await response.json().catch(() => ({}))), false);
                submit.disabled = false;
            }
        } catch (err) {
            showMessage("No se pudo conectar con el servidor.", false);
            submit.disabled = false;
        }
    });
}

// ---------- Eliminar ----------
const deleteBtn = document.getElementById("delete-btn");

if (deleteBtn) {
    deleteBtn.addEventListener("click", async () => {
        const name = deleteBtn.dataset.name;
        if (!window.confirm(`¿Eliminar "${name}"? Esta acción no se puede deshacer.`)) return;

        deleteBtn.disabled = true;
        try {
            const response = await fetch(`/api/v1/restaurants/${deleteBtn.dataset.id}`, {
                method: "DELETE",
            });
            if (response.status === 204) {
                window.location.href = "/?msg=deleted";
            } else {
                showMessage(errorText(await response.json().catch(() => ({}))), false);
                deleteBtn.disabled = false;
            }
        } catch (err) {
            showMessage("No se pudo conectar con el servidor.", false);
            deleteBtn.disabled = false;
        }
    });
}
