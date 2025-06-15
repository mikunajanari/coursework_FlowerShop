async function fetchOrders() {
  const res = await fetch("/api/courier/orders");
  const data = await res.json();

  const todayBody = document.getElementById("today-orders-body");
  todayBody.innerHTML = "";
  data.today.forEach(order => {
    todayBody.innerHTML += `
      <tr>
        <td>${order.id}</td>
        <td>${order.name}</td>
        <td>${order.phone}</td>
        <td>${order.address}</td>
        <td>
          <button class="btn btn-primary btn-sm accept-order" data-id="${order.id}">Прийняти</button>
        </td>
      </tr>`;
  });

  const inProgressBody = document.getElementById("in-progress-body");
  inProgressBody.innerHTML = "";
  data.inProgress.forEach(order => {
    inProgressBody.innerHTML += `
      <tr>
        <td>${order.id}</td>
        <td>${order.name}</td>
        <td>${order.phone}</td>
        <td>${order.address}</td>
        <td>
          <button class="btn btn-success btn-sm finish-order" data-id="${order.id}">Доставлено</button>
        </td>
      </tr>`;
  });
}

document.addEventListener("click", async (e) => {
  if (e.target.classList.contains("accept-order")) {
    const id = e.target.getAttribute("data-id");
    await fetch(`/api/courier/accept/${id}`, { method: "POST" });
    fetchOrders();
  }

  if (e.target.classList.contains("finish-order")) {
    const id = e.target.getAttribute("data-id");
    await fetch(`/api/courier/complete/${id}`, { method: "POST" });
    fetchOrders();
  }
});

fetchOrders();