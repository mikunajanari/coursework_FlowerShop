document.addEventListener("DOMContentLoaded", function () {
  // === Додавання клієнта ===
  const requiredIds = [
    "client-surname", "client-firstname", "client-middlename",
    "client-phone", "client-email", "client-city", "client-street",
    "client-house", "client-flat", "client-password"
  ];

  function validateClientForm() {
    const allFilled = requiredIds.every(id => {
      const el = document.getElementById(id);
      return el && el.value.trim();
    });
    document.getElementById("add-client-btn").disabled = !allFilled;
  }

  requiredIds.forEach(id => {
    document.getElementById(id).addEventListener("input", validateClientForm);
    document.getElementById(id).addEventListener("change", validateClientForm);
  });
  validateClientForm();

  document.getElementById("add-client-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const body = {
      surname: document.getElementById("client-surname").value.trim(),
      first_name: document.getElementById("client-firstname").value.trim(),
      middle_name: document.getElementById("client-middlename").value.trim(),
      phone: document.getElementById("client-phone").value.trim(),
      email: document.getElementById("client-email").value.trim(),
      city: document.getElementById("client-city").value.trim(),
      street: document.getElementById("client-street").value.trim(),
      house: document.getElementById("client-house").value.trim(),
      flat: document.getElementById("client-flat").value.trim(),
      db_password: document.getElementById("client-password").value.trim()
    };

    const res = await fetch("/api/clients", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    let data;
    try {
      data = await res.json();
    } catch {
      data = {};
    }

    if (res.ok && data.id) {
      alert(`Клієнта створено! ID: ${data.id}`);
      e.target.reset();
      validateClientForm();
      // Оновити allClients для автодоповнення
      fetchClients();
    } else {
      alert(`❌ ${data.error || "Помилка створення клієнта"}`);
    }
  });

  // === Глобальні масиви для клієнтів і квітів ===
  let allClients = [];
  let allFlowers = [];

  // === Підвантаження клієнтів ===
  function fetchClients() {
    fetch("/api/clients/list")
      .then(res => res.json())
      .then(data => {
        allClients = data;
        // Для замовлення
        const orderClientList = document.getElementById("order-client-list");
        if (orderClientList) {
          orderClientList.innerHTML = "";
          data.forEach(c => {
            const opt = document.createElement("option");
            opt.value = `${c.surname} ${c.first_name} ${c.middle_name} (${c.email})`;
            opt.dataset.id = c.id;
            orderClientList.appendChild(opt);
          });
        }
        // Для відстеження
        const trackClientList = document.getElementById("track-client-list");
        if (trackClientList) {
          trackClientList.innerHTML = "";
          data.forEach(c => {
            const opt = document.createElement("option");
            opt.value = `${c.surname} ${c.first_name} ${c.middle_name} (${c.email})`;
            opt.dataset.id = c.id;
            trackClientList.appendChild(opt);
          });
        }
      });
  }
  fetchClients();

  // === Підвантаження квітів ===
  fetch("/api/flowers/list")
    .then(res => res.json())
    .then(data => {
      allFlowers = data;

      // Для автодоповнення (замовлення)
      const orderFlowerList = document.getElementById("order-flower-list");
      if (orderFlowerList) {
        orderFlowerList.innerHTML = "";
        data.forEach(f => {
          const opt = document.createElement("option");
          opt.value = `${f.genus} ${f.species}`;
          opt.dataset.id = f.id;
          orderFlowerList.appendChild(opt);
        });
      }

      // Для перевірки наявності (datalist)
      const flowerSelectList = document.getElementById("flower-select-list");
      if (flowerSelectList) {
        flowerSelectList.innerHTML = "";
        data.forEach(f => {
          const opt = document.createElement("option");
          opt.value = `${f.genus} ${f.species}`;
          opt.dataset.id = f.id;
          flowerSelectList.appendChild(opt);
        });
      }

      // Для select (якщо залишили для сумісності)
      const select = document.getElementById("flower-select");
      if (select) {
        select.innerHTML = '<option value="" disabled selected hidden>Оберіть квітку</option>';
        data.forEach(f => {
          const opt = document.createElement("option");
          opt.value = f.id;
          opt.textContent = `${f.genus} ${f.species}`;
          select.appendChild(opt);
        });
      }
    });

  // === Функції для пошуку id по введеному значенню ===
  function getClientIdByInput() {
    const input = document.getElementById("order-client-input").value.trim().toLowerCase();
    const found = allClients.find(c =>
      (`${c.surname} ${c.first_name} ${c.middle_name} (${c.email})`).toLowerCase() === input
    );
    return found ? found.id : "";
  }

  function getTrackClientIdByInput() {
    const input = document.getElementById("track-client-input").value.trim().toLowerCase();
    const found = allClients.find(c =>
      (`${c.surname} ${c.first_name} ${c.middle_name} (${c.email})`).toLowerCase() === input
    );
    return found ? found.id : "";
  }

  function getFlowerIdByInput() {
    const input = document.getElementById("order-flower-input").value.trim().toLowerCase();
    const found = allFlowers.find(f =>
      (`${f.genus} ${f.species}`).toLowerCase() === input
    );
    return found ? found.id : "";
  }

  function getStockFlowerIdByInput() {
    const input = document.getElementById("flower-select-input").value.trim().toLowerCase();
    const found = allFlowers.find(f =>
      (`${f.genus} ${f.species}`).toLowerCase() === input
    );
    return found ? found.id : "";
  }

  // === Створення замовлення ===
  let orderItems = [];
  function renderOrderItems() {
    const tbody = document.querySelector("#order-items-table tbody");
    tbody.innerHTML = "";
    orderItems.forEach((item, idx) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${item.flower_name}</td>
        <td>${item.amount}</td>
        <td><button type="button" class="btn btn-danger btn-sm" data-idx="${idx}">✖</button></td>
      `;
      tbody.appendChild(tr);
    });
    // Видалення позиції
    tbody.querySelectorAll("button").forEach(btn => {
      btn.onclick = () => {
        orderItems.splice(btn.dataset.idx, 1);
        renderOrderItems();
        validateOrderForm();
      };
    });
    validateOrderForm();
  }

  function validateOrderForm() {
    const clientId = getClientIdByInput();
    const date = document.getElementById("order-date").value;
    const method = document.getElementById("order-method").value.trim();
    const allItemsValid = orderItems.length > 0 && orderItems.every(item => !!item.flower_id);
    document.getElementById("create-order-btn").disabled = !(clientId && date && method && allItemsValid);
  }

  ["order-client-input", "order-date", "order-method"].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("input", validateOrderForm);
      el.addEventListener("change", validateOrderForm);
    }
  });

  document.getElementById("add-item-btn").onclick = function () {
    const flowerId = getFlowerIdByInput();
    const flowerName = document.getElementById("order-flower-input").value;
    const qty = parseInt(document.getElementById("order-qty").value, 10);
    if (!flowerId || !qty || qty <= 0) {
      alert("Оберіть квітку та введіть кількість!");
      return;
    }
    orderItems.push({ flower_id: flowerId, flower_name: flowerName, amount: qty });
    renderOrderItems();
    document.getElementById("order-qty").value = "";
  };

  document.getElementById("order-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const clientId = getClientIdByInput();
    if (!clientId) {
      alert("Оберіть клієнта зі списку!");
      return;
    }
    if (orderItems.length === 0) {
      alert("Додайте хоча б одну позицію!");
      return;
    }
    const body = {
      customer_id: clientId,
      delivery_date: document.getElementById("order-date").value,
      delivery_method: document.getElementById("order-method").value.trim(),
      items: orderItems.map(i => ({
        flower_id: i.flower_id,
        amount: i.amount
      }))
    };
    const res = await fetch("/api/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    let data;
    try { data = await res.json(); } catch { data = {}; }
    if (res.ok && data.order_id) {
      alert(`Замовлення №${data.order_id} створено!`);
      orderItems = [];
      renderOrderItems();
      e.target.reset();
      validateOrderForm();
    } else {
      alert(`❌ ${data.error || "Помилка створення замовлення"}`);
    }
  });

  // === Мінімальна дата доставки ===
  const today = new Date().toISOString().split('T')[0];
  document.getElementById("order-date").setAttribute("min", today);

  // === Перевірка наявності квітки ===
  document.getElementById("check-stock-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const speciesId = getStockFlowerIdByInput();
    if (!speciesId) {
      document.getElementById("stock-result").textContent = "Оберіть квітку зі списку!";
      return;
    }
    const res = await fetch(`/api/flowers/check-stock?species_id=${speciesId}`);
    const data = await res.json();
    if (res.ok) {
      document.getElementById("stock-result").innerHTML =
        `<b>${data.genus} ${data.species}</b>: доступно <b>${data.available_quantity}</b> шт.`;
    } else {
      document.getElementById("stock-result").textContent = data.error || "Помилка";
    }
  });

  // === Відстеження замовлення (М4) ===
  // Підвантажити замовлення клієнта при виборі
  document.getElementById("track-client-input").addEventListener("change", function () {
    const clientId = getTrackClientIdByInput();
    const select = document.getElementById("track-order-select");
    select.innerHTML = '<option value="" disabled selected hidden>Оберіть замовлення</option>';
    select.disabled = true;
    if (!clientId) return;
    fetch(`/api/orders/list?client_id=${clientId}`)
      .then(res => res.json())
      .then(data => {
        if (data.length === 0) {
          select.innerHTML = '<option value="" disabled selected>Немає замовлень</option>';
        } else {
          data.forEach(o => {
            const opt = document.createElement("option");
            opt.value = o.order_id;
            opt.textContent = `№${o.order_id} — ${o.delivery_date} (${o.status})`;
            select.appendChild(opt);
          });
          select.disabled = false;
        }
      });
  });

  // Обробка перевірки статусу замовлення
  document.getElementById("track-order-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const orderId = document.getElementById("track-order-select").value;
    if (!orderId) {
      document.getElementById("track-result").textContent = "Оберіть замовлення!";
      return;
    }
    const res = await fetch(`/api/orders/track?order_id=${encodeURIComponent(orderId)}`);
    const data = await res.json();
    if (res.ok) {
      document.getElementById("track-result").innerHTML =
        `<b>Замовлення №${data.order_id}</b>: статус — <b>${data.status}</b>`;
    } else {
      document.getElementById("track-result").textContent = data.error || "Помилка";
    }
  });
});