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

function loadGenera() {
    fetch('/api/admin/get_genera/')
        .then(r => r.json())
        .then(data => {
            const select = document.getElementById('species_genus_name');
            select.innerHTML = '<option value="">Оберіть рід...</option>';
            data.genera.forEach(function(genus) {
                const option = document.createElement('option');
                option.value = genus;
                option.textContent = genus;
                select.appendChild(option);
            });
        });
}
document.addEventListener('DOMContentLoaded', loadGenera);

// А1: Додати рід
function addGenus(event) {
    const input = document.getElementById('genus_name');
    const button = event.target;
    fetch('/api/admin/add_genus/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')},
        body: JSON.stringify({genus_name: input.value})
    })
    .then(r => r.json())
    .then(data => {
        alert(data.message);
        input.value = ""; // очищаємо поле
        button.blur();    // знімаємо фокус з кнопки
    });
}

// А2: Додати вид
function addSpecies(event) {
    const name = document.getElementById('species_name');
    const genus = document.getElementById('species_genus_name');
    const instructions = document.getElementById('species_instructions');
    const period = document.getElementById('species_storage_period');
    const photo = document.getElementById('species_photo_link');
    fetch('/api/admin/add_species_sql/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')},
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
        alert(data.message);
        name.value = "";
        genus.value = "";
        instructions.value = "";
        period.value = "";
        photo.value = "";
        event.target.blur();
    });
}

// А3: Додати добриво
function addFertilizer(event) {
    const input = document.getElementById('fertilizer_name');
    fetch('/api/admin/add_fertilizer/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')},
        body: JSON.stringify({fertilizer_name: input.value})
    })
    .then(r => r.json())
    .then(data => {
        alert(data.message);
        input.value = "";
        event.target.blur();
    });
}

// А4: Зв’язати рід з добривом
function linkGenusFertilizer(event) {
    const genus = document.getElementById('link_genus_id');
    const fertilizer = document.getElementById('link_fertilizer_id');
    fetch('/api/admin/link_genus_fertilizer_sql/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')},
        body: JSON.stringify({
            genus_id: genus.value,
            fertilizer_id: fertilizer.value
        })
    })
    .then(r => r.json())
    .then(data => {
        alert(data.message);
        genus.value = "";
        fertilizer.value = "";
        event.target.blur();
    });
}

// А5: Додати постачальника
function addSupplier(event) {
    const name = document.getElementById('supplier_name');
    const address = document.getElementById('supplier_address');
    const phone = document.getElementById('supplier_phone');
    fetch('/api/admin/add_supplier/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')},
        body: JSON.stringify({
            supplier_name: name.value,
            address: address.value,
            phone: phone.value
        })
    })
    .then(r => r.json())
    .then(data => {
        alert(data.message);
        name.value = "";
        address.value = "";
        phone.value = "";
        event.target.blur();
    });
}

// А6: Додати кур’єра
function addCourier(event) {
    const first = document.getElementById('courier_first_name');
    const surname = document.getElementById('courier_surname');
    const middle = document.getElementById('courier_middle_name');
    const phone = document.getElementById('courier_phone');
    const email = document.getElementById('courier_email');
    const password = document.getElementById('courier_password');
    fetch('/api/admin/add_courier_sql/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')},
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
        alert(data.message);
        first.value = "";
        surname.value = "";
        middle.value = "";
        phone.value = "";
        email.value = "";
        password.value = "";
        event.target.blur();
    });
}