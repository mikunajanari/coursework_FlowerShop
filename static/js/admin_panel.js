function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showMessage(id, msg, isError = true) {
    const el = document.getElementById(id);
    el.textContent = msg;
    el.className = isError ? "text-danger mb-2" : "text-success mb-2";
}

function loadGenera() {
    fetch('/api/admin/get_genera/')
        .then(r => r.json())
        .then(data => {
            const select = document.getElementById('species_genus_name');
            select.innerHTML = '<option value="">Оберіть рід...</option>';
            data.genera.forEach(function (genus) {
                const option = document.createElement('option');
                option.value = genus;
                option.textContent = genus;
                select.appendChild(option);
            });
        });
}
document.addEventListener('DOMContentLoaded', loadGenera);

// А1: Додати рід
document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('genus_name');
    const btn = document.getElementById('genus_btn');
    input.addEventListener('input', function () {
        btn.disabled = !input.value.trim();
    });
});

function addGenus(event) {
    const input = document.getElementById('genus_name');
    fetch('/api/admin/add_genus/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({ genus_name: input.value })
    })
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                alert(data.message);
                input.value = "";
                event.target.blur();
                document.getElementById('genus_btn').disabled = true;
            }
        })
        .catch(() => {
            alert("Сталася помилка на сервері!");
        });
}


// А2: Додати вид
document.addEventListener('DOMContentLoaded', function () {
    ['species_name', 'species_genus_name', 'species_instructions', 'species_storage_period', 'species_photo_link'].forEach(id => {
        document.getElementById(id).addEventListener('input', validateSpeciesFields);
        document.getElementById(id).addEventListener('change', validateSpeciesFields);
    });
    validateSpeciesFields();
});
function validateSpeciesFields() {
    const name = document.getElementById('species_name').value.trim();
    const genus = document.getElementById('species_genus_name').value.trim();
    const instructions = document.getElementById('species_instructions').value.trim();
    const period = document.getElementById('species_storage_period').value.trim();
    const photo = document.getElementById('species_photo_link').value.trim();
    document.getElementById('species_btn').disabled = !(name && genus && instructions && period && photo && parseInt(period) >= 1);
}
function addSpecies(event) {
    const name = document.getElementById('species_name');
    const genus = document.getElementById('species_genus_name');
    const instructions = document.getElementById('species_instructions');
    const period = document.getElementById('species_storage_period');
    const photo = document.getElementById('species_photo_link');
    fetch('/api/admin/add_species_sql/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({
            species_name: name.value,
            genus_name: genus.value,
            instructions: instructions.value,
            storage_period: period.value,
            photo_link: photo.value
        })
    })
        .then(r => r.json())
        .then(data => {
            alert(data.error || data.message);
            if (!data.error) {
                name.value = "";
                genus.value = "";
                instructions.value = "";
                period.value = "";
                photo.value = "";
                event.target.blur();
                validateSpeciesFields();
            }
        })
        .catch(() => alert("Сталася помилка на сервері!"));
}


// А3: Додати добриво
document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('fertilizer_name');
    const btn = document.getElementById('fertilizer_btn');
    input.addEventListener('input', function () {
        btn.disabled = !input.value.trim();
    });
});
function addFertilizer(event) {
    const input = document.getElementById('fertilizer_name');
    fetch('/api/admin/add_fertilizer/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({ fertilizer_name: input.value })
    })
        .then(r => r.json())
        .then(data => {
            alert(data.error || data.message);
            if (!data.error) {
                input.value = "";
                event.target.blur();
                document.getElementById('fertilizer_btn').disabled = true;
            }
        })
        .catch(() => alert("Сталася помилка на сервері!"));
}


// А4: Зв’язати рід з добривом
function loadGenusAndFertilizers() {
    // Роди
    fetch('/api/admin/get_genera/')
        .then(r => r.json())
        .then(data => {
            const select = document.getElementById('link_genus_id');
            select.innerHTML = '<option value="">Оберіть рід...</option>';
            data.genera.forEach(function (genus) {
                const option = document.createElement('option');
                option.value = genus;
                option.textContent = genus;
                select.appendChild(option);
            });
        });

    // Добрива
    fetch('/api/admin/get_fertilizers/')
        .then(r => r.json())
        .then(data => {
            const select = document.getElementById('link_fertilizer_id');
            select.innerHTML = '<option value="">Оберіть добриво...</option>';
            data.fertilizers.forEach(function (fertilizer) {
                const option = document.createElement('option');
                option.value = fertilizer;
                option.textContent = fertilizer;
                select.appendChild(option);
            });
        });
}
document.addEventListener('DOMContentLoaded', loadGenusAndFertilizers);

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('link_genus_id').addEventListener('change', validateLinkFields);
    document.getElementById('link_fertilizer_id').addEventListener('change', validateLinkFields);
    validateLinkFields();
});
function validateLinkFields() {
    const genus = document.getElementById('link_genus_id').value;
    const fertilizer = document.getElementById('link_fertilizer_id').value;
    document.getElementById('link_btn').disabled = !(genus && fertilizer);
}
function linkGenusFertilizer(event) {
    const genusName = document.getElementById('link_genus_id').value;
    const fertilizerName = document.getElementById('link_fertilizer_id').value;
    fetch('/api/admin/link_genus_fertilizer_sql/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({
            genus_name: genusName,
            fertilizer_name: fertilizerName
        })
    })
        .then(r => r.json())
        .then(data => {
            alert(data.error || data.message);
            if (!data.error) {
                document.getElementById('link_genus_id').value = "";
                document.getElementById('link_fertilizer_id').value = "";
                event.target.blur();
                validateLinkFields();
            }
        })
        .catch(() => alert("Сталася помилка на сервері!"));
}


// А5: Додати постачальника
document.addEventListener('DOMContentLoaded', function () {
    ['supplier_name', 'supplier_city', 'supplier_street', 'supplier_house', 'supplier_flat', 'supplier_phone'].forEach(id => {
        document.getElementById(id).addEventListener('input', validateSupplierFields);
    });
    validateSupplierFields();
});

function validateSupplierFields() {
    const ids = [
        'supplier_name',
        'supplier_city',
        'supplier_street',
        'supplier_house',
        'supplier_flat',
        'supplier_phone',
        'supplier_btn'
    ];
    // Перевіряємо, що всі елементи існують
    for (const id of ids) {
        if (!document.getElementById(id)) {
            // Якщо хоча б одного поля немає — виходимо з функції
            return;
        }
    }
    // Далі ваша логіка:
    const name = document.getElementById('supplier_name').value.trim();
    const city = document.getElementById('supplier_city').value.trim();
    const street = document.getElementById('supplier_street').value.trim();
    const house = document.getElementById('supplier_house').value.trim();
    const flat = document.getElementById('supplier_flat').value.trim();
    const phone = document.getElementById('supplier_phone').value.trim();
    const valid = name && city && street && house && flat && phone &&
        !isNaN(Number(house)) && Number(house) > 0 &&
        !isNaN(Number(flat)) && Number(flat) > 0;
    document.getElementById('supplier_btn').disabled = !valid;
}

function addSupplier(event) {
    const name = document.getElementById('supplier_name');
    const city = document.getElementById('supplier_city');
    const street = document.getElementById('supplier_street');
    const house = document.getElementById('supplier_house');
    const flat = document.getElementById('supplier_flat');
    const phone = document.getElementById('supplier_phone');
    fetch('/api/admin/add_supplier/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({
            supplier_name: name.value,
            city: city.value,
            street: street.value,
            house: house.value,
            flat: flat.value,
            phone: phone.value
        })
    })
    .then(r => r.json())
    .then(data => {
        alert(data.error || data.message);
        if (!data.error) {
            name.value = "";
            city.value = "";
            street.value = "";
            house.value = "";
            flat.value = "";
            phone.value = "";
            event.target.blur();
            validateSupplierFields();
        }
    })
    .catch(() => alert("Сталася помилка на сервері!"));
}


// А6: Додати кур’єра
document.addEventListener('DOMContentLoaded', function () {
    ['courier_first_name', 'courier_surname', 'courier_phone', 'courier_email', 'courier_password'].forEach(id => {
        document.getElementById(id).addEventListener('input', validateCourierFields);
    });
    validateCourierFields();
});
function validateCourierFields() {
    const first = document.getElementById('courier_first_name').value.trim();
    const surname = document.getElementById('courier_surname').value.trim();
    const phone = document.getElementById('courier_phone').value.trim();
    const email = document.getElementById('courier_email').value.trim();
    const password = document.getElementById('courier_password').value.trim();
    document.getElementById('courier_btn').disabled = !(first && surname && phone && email && password);
}
function addCourier(event) {
    const first = document.getElementById('courier_first_name');
    const surname = document.getElementById('courier_surname');
    const middle = document.getElementById('courier_middle_name');
    const phone = document.getElementById('courier_phone');
    const email = document.getElementById('courier_email');
    const password = document.getElementById('courier_password');
    fetch('/api/admin/add_courier_sql/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({
            first_name: first.value,
            surname: surname.value,
            middle_name: middle.value,
            phone: phone.value,
            email: email.value,
            password: password.value
        })
    })
        .then(r => r.json())
        .then(data => {
            alert(data.error || data.message);
            if (!data.error) {
                first.value = "";
                surname.value = "";
                middle.value = "";
                phone.value = "";
                email.value = "";
                password.value = "";
                event.target.blur();
                validateCourierFields();
            }
        })
        .catch(() => alert("Сталася помилка на сервері!"));
}