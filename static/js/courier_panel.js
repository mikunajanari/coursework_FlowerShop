document.addEventListener("DOMContentLoaded", function () {
  // Підвантажити замовлення для доставки сьогодні
  fetch("/api/courier/orders-for-delivery")
    .then(res => res.json())
    .then(data => {
      const tbody = document.getElementById("today-orders-body");
      tbody.innerHTML = "";
      if (!data.length) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Немає замовлень на сьогодні</td></tr>';
        return;
      }
      data.forEach(order => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${order.order_id}</td>
          <td>${order.surname} ${order.firstname} ${order.middlename}</td>
          <td>${order.phone}</td>
          <td>${order.city}, ${order.street} ${order.house}, кв. ${order.flat}</td>
          <td>
            <button class="btn btn-success btn-sm btn-assign-order" data-order="${order.order_id}">Прийняти</button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    });

  // Обробник для кнопки "Взяти"
  document.getElementById("today-orders-body").addEventListener("click", async function(e) {
    if (e.target.matches(".btn-assign-order")) {
      const orderId = e.target.dataset.order;
      if (!orderId) return;
      const res = await fetch("/api/courier/assign-order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order_id: orderId })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        alert("Замовлення взято в роботу!");
        location.reload();
      } else {
        alert(data.error || "Помилка");
      }
    }
  });

  // Підвантажити замовлення, взяті цим кур'єром
  fetch("/api/courier/taken-orders")
    .then(res => res.json())
    .then(data => {
      const tbody = document.getElementById("taken-orders-body");
      tbody.innerHTML = "";
      if (!data.length) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Немає взятих вами замовлень</td></tr>';
        return;
      }
      data.forEach(order => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${order.order_id}</td>
          <td>${order.surname} ${order.firstname} ${order.middlename}</td>
          <td>${order.phone}</td>
          <td>${order.city}, ${order.street} ${order.house}, кв. ${order.flat}</td>
          <td>
            <button class="btn btn-primary btn-sm btn-update-status" data-order="${order.order_id}">Доставлено</button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    });

  // Обробник для кнопки "Доставлено"
  document.getElementById("taken-orders-body").addEventListener("click", async function(e) {
    if (e.target.matches(".btn-update-status")) {
      const orderId = e.target.dataset.order;
      if (!orderId) return;
      // Тут зробіть fetch на ваш API для оновлення статусу
      const res = await fetch("/api/courier/update-status", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order_id: orderId, status: "доставлено" })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        alert("Статус оновлено!");
        location.reload();
      } else {
        alert(data.error || "Помилка");
      }
    }
  });
});