document.addEventListener("DOMContentLoaded", () => {
    let speciesData = [];
    let genusData = [];
    let genusFertilizerMap = {};

    // Завантаження видів і родів
    fetch('/api/species')
        .then(res => res.json())
        .then(data => {
            speciesData = data;
            // Збираємо унікальні роди
            const genusMap = {};
            data.forEach(({ genus_id, genus }) => {
                genusMap[genus_id] = genus;
            });
            genusData = Object.entries(genusMap).map(([id, name]) => ({ id, name }));

            // Заповнюємо select родів
            const genusSelect = document.getElementById("genus-select");
            genusSelect.innerHTML = '<option value="" disabled selected hidden>Оберіть рід...</option>';
            genusData.forEach(g => {
                const opt = document.createElement("option");
                opt.value = g.id;
                opt.textContent = g.name;
                genusSelect.appendChild(opt);
            });

            // При зміні роду — оновлюємо види
            genusSelect.addEventListener("change", () => {
                const genusId = genusSelect.value;
                const speciesSelect = document.getElementById("species-select");
                speciesSelect.innerHTML = '<option value="" disabled selected hidden>Оберіть вид...</option>';
                if (!genusId) {
                    speciesSelect.disabled = true;
                    return;
                }
                const filteredSpecies = speciesData.filter(s => s.genus_id == genusId);
                filteredSpecies.forEach(s => {
                    const opt = document.createElement("option");
                    opt.value = s.id;
                    opt.textContent = s.name;
                    speciesSelect.appendChild(opt);
                });
                speciesSelect.disabled = false;
            });
        });

    // Завантаження добрив по роду
    fetch('/api/fertilizer/grouped')
        .then(res => res.json())
        .then(data => {
            genusFertilizerMap = data;
        });

    // При виборі роду — оновлюємо види та добрива
    document.getElementById("genus-select").addEventListener("change", function () {
        const genusId = this.value;

        // Оновлюємо види
        const speciesSelect = document.getElementById("species-select");
        speciesSelect.innerHTML = '<option value="" disabled selected hidden>Оберіть вид...</option>';
        if (genusId) {
            const filteredSpecies = speciesData.filter(s => s.genus_id == genusId);
            filteredSpecies.forEach(s => {
                const opt = document.createElement("option");
                opt.value = s.id;
                opt.textContent = s.name;
                speciesSelect.appendChild(opt);
            });
            speciesSelect.disabled = false;
        } else {
            speciesSelect.disabled = true;
        }

        // Оновлюємо добрива
        const fertSelect = document.getElementById("fertilizer-select");
        fertSelect.innerHTML = '<option value="" disabled selected hidden>Оберіть добриво...</option>';
        if (genusId && genusFertilizerMap[genusId]) {
            genusFertilizerMap[genusId].forEach(f => {
                const opt = document.createElement("option");
                opt.value = f.id;
                opt.textContent = f.name;
                fertSelect.appendChild(opt);
            });
            fertSelect.disabled = false;
        } else {
            fertSelect.disabled = true;
        }
    });


    // Відправка форми посадки
    document.getElementById("planting-form").addEventListener("submit", e => {
        e.preventDefault();
        const genusId = document.getElementById("genus-select").value;
        const speciesId = document.getElementById("species-select").value;
        const species = speciesData.find(s => String(s.id) === String(speciesId) && String(s.genus_id) === String(genusId));
        const payload = {
            species_id: species.id,
            quantity: parseInt(document.getElementById("planting-count").value), // кількість квіток
            genus_fertilizer_id: parseInt(document.getElementById("fertilizer-select").value),
            fertilizer_amount: parseInt(document.getElementById("fertilizer-amount").value) // кількість добрива
        };
        fetch('/api/plants/plant-with-fertilizer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(async res => {
                let data;
                try {
                    data = await res.json();
                } catch {
                    data = {};
                }
                if (res.ok && data.status === 'ok') {
                    alert("Посадка з добривом успішна");
                    // Очищення форми
                    document.getElementById("genus-select").value = "";
                    document.getElementById("species-select").innerHTML = '<option value="" disabled selected hidden>Оберіть вид...</option>';
                    document.getElementById("species-select").disabled = true;
                    document.getElementById("fertilizer-select").innerHTML = '<option value="" disabled selected hidden>Оберіть добриво...</option>';
                    document.getElementById("fertilizer-select").disabled = true;
                    document.getElementById("planting-count").value = "";
                    document.getElementById("fertilizer-amount").value = "";
                } else {
                    alert("Помилка: " + (data.error || data.status || res.statusText || "Невідома помилка"));
                }
            })
            .catch(() => alert("❌ Помилка при з'єднанні з сервером!"));
    });

    // Відмітка готовності
    fetch("/api/plants/unready")
        .then(res => res.json())
        .then(plants => {
            const tbody = document.getElementById("ready-plants-table");
            plants.forEach(p => {
                const row = document.createElement("tr");
                row.innerHTML = `
          <td>${p.genus}</td>
          <td>${p.species}</td>
          <td>${p.amount}</td>
          <td>${p.planting_day}</td>
          <td>
            <button class="btn btn-sm btn-outline-success" data-id="${p.id}">✅ Готово</button>
          </td>`;
                tbody.appendChild(row);
            });
            tbody.querySelectorAll("button").forEach(btn => {
                btn.addEventListener("click", () => {
                    const plantedId = btn.dataset.id;
                    fetch("/api/plants/mark-ready", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ planted_id: plantedId })
                    }).then(res => {
                        if (res.ok) {
                            btn.textContent = "✅ Відмічено";
                            btn.disabled = true;
                        } else {
                            res.text().then(text => alert("❌ Помилка: " + text));
                        }
                    });
                });
            });
        });

    // Списання рослин
    fetch("/api/plants/available_for_writeoff")
        .then(res => res.json())
        .then(plants => {
            const tbody = document.getElementById("remove-plants-table");
            plants.forEach(p => {
                const row = document.createElement("tr");
                row.innerHTML = `
          <td>${p.genus}</td>
          <td>${p.species}</td>
          <td>${p.amount}</td>
          <td>${p.planting_day}</td>
          <td>
            <input type="number" min="1" max="${p.amount}" placeholder="Кількість" class="form-control form-control-sm mb-1 writeoff-count">
            <button class="btn btn-sm btn-outline-danger" data-id="${p.id}">🗑️ Списати</button>
          </td>`;
                tbody.appendChild(row);
            });
            tbody.querySelectorAll("button").forEach(btn => {
                btn.addEventListener("click", () => {
                    const plantedId = btn.dataset.id;
                    const input = btn.parentElement.querySelector(".writeoff-count");
                    const count = parseInt(input.value);
                    if (!count || count <= 0) return alert("Вкажіть кількість для списання");
                    fetch("/api/plants/writeoff", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ planted_id: plantedId, quantity: count })
                    }).then(res => {
                        if (res.ok) {
                            btn.textContent = "✅ Списано";
                            btn.disabled = true;
                            input.disabled = true;
                        } else {
                            res.text().then(text => alert("❌ Помилка: " + text));
                        }
                    });
                });
            });
        });
});