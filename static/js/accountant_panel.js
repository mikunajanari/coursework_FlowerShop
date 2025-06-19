document.addEventListener("DOMContentLoaded", function () {
  // Підвантажити добрива
  fetch("/api/fertilizers")
    .then(res => res.json())
    .then(data => {
      const select = document.getElementById("order_fertilizer_id");
      select.innerHTML = '<option value="" disabled selected hidden>Оберіть добриво...</option>';
      data.forEach(f => {
        const opt = document.createElement("option");
        opt.value = f.id;
        opt.textContent = f.name;
        select.appendChild(opt);
      });
    });

  // Підвантажити постачальників
  fetch("/api/suppliers")
    .then(res => res.json())
    .then(data => {
      const select = document.getElementById("order_supplier_id");
      select.innerHTML = '<option value="" disabled selected hidden>Оберіть постачальника...</option>';
      data.forEach(s => {
        const opt = document.createElement("option");
        opt.value = s.id;
        opt.textContent = s.name;
        select.appendChild(opt);
      });
    });

  // Валідація для кнопки "Замовити"
  function validateOrderFields() {
    const fertilizer = document.getElementById("order_fertilizer_id").value;
    const supplier = document.getElementById("order_supplier_id").value;
    const amount = document.getElementById("order_amount").value;
    const price = document.getElementById("order_price").value;
    document.getElementById("order_btn").disabled = !(fertilizer && supplier && amount && price);
  }

  // Додаємо обробники для всіх полів
  ["order_fertilizer_id", "order_supplier_id", "order_amount", "order_price"].forEach(id => {
    document.getElementById(id).addEventListener("input", validateOrderFields);
    document.getElementById(id).addEventListener("change", validateOrderFields);
  });

  // Початкова перевірка
  validateOrderFields();

  // Обробка замовлення добрив
  document.getElementById("order_btn").addEventListener("click", function (event) {
    event.preventDefault();
    const fertilizer_id = document.getElementById("order_fertilizer_id").value;
    const supplier_id = document.getElementById("order_supplier_id").value;
    const amount = document.getElementById("order_amount").value;
    const price = document.getElementById("order_price").value;

    fetch("/api/fertilizers/order", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fertilizer_id, supplier_id, amount, price })
    })
      .then(res => res.json())
      .then(result => {
        alert("Замовлення успішно створено!");
        document.getElementById("order_fertilizer_id").value = "";
        document.getElementById("order_supplier_id").value = "";
        document.getElementById("order_amount").value = "";
        document.getElementById("order_price").value = "";
        validateOrderFields();
      })
      .catch(err => {
        alert("Помилка при замовленні!");
      });
  });

  // Підвантажити готові квіти для встановлення ціни
  fetch("/api/flowers/ready")
    .then(res => res.json())
    .then(data => {
      const tbody = document.querySelector("#set-price-table tbody");
      tbody.innerHTML = "";
      if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Немає готових квітів</td></tr>';
        return;
      }
      data.forEach(flower => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${flower.genus}</td>
          <td>${flower.species}</td>
          <td>${flower.planting_day}</td>
          <td>
            <input type="number" min="0.01" step="0.01" class="form-control form-control-sm price-input" placeholder="Ціна">
          </td>
          <td>
            <button class="btn btn-primary btn-sm set-price-btn">💾 Зберегти</button>
          </td>
        `;
        tr.querySelector(".set-price-btn").dataset.id = flower.id;
        tbody.appendChild(tr);
      });

      // Додаємо обробник для кожної кнопки
      tbody.querySelectorAll(".set-price-btn").forEach(btn => {
        btn.addEventListener("click", function () {
          const productId = btn.dataset.id;
          const priceInput = btn.closest("tr").querySelector(".price-input");
          const price = priceInput.value;
          if (!price || Number(price) <= 0) {
            alert("Введіть коректну ціну!");
            return;
          }
          fetch("/api/flowers/set-price", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ flowerId: productId, price })
          })
            .then(async res => {
              let data;
              try {
                data = await res.json();
              } catch {
                data = {};
              }
              if (res.ok && data.status === 'ok') {
                alert("Ціну встановлено успішно!");
              } else {
                alert("Помилка: " + (data.error || data.status || res.statusText || "Невідома помилка"));
              }
            })
            .catch(() => alert("❌ Помилка при з'єднанні з сервером!"));
        });
      });
    });
});