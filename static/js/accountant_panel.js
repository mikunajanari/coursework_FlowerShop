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
});