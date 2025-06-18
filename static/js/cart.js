// Utility function for consistent price formatting
function formatPrice(value) {
    // You can change 'UAH' to your preferred currency and locale
    return value.toLocaleString('uk-UA', { style: 'currency', currency: 'UAH' });
}

document.addEventListener('DOMContentLoaded', function() {
    // Get all remove buttons
    const removeButtons = document.querySelectorAll('.product-remove');

    removeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the product row
            const productRow = this.closest('tr');
            
            // Get the product name for identification
            const productName = productRow.querySelector('.product-info a').textContent;
            
            // Remove the product row with animation
            productRow.style.animation = 'fadeOut 0.5s';
            setTimeout(() => {
                productRow.remove();
                
                // Update cart counter in header if exists
                updateCartCounter();
                
                // Save cart state to localStorage
                saveCartState();
            }, 500);
        });
    });

    // Додавання одиночного продукту з кількістю
    const addBtn = document.getElementById('add-to-cart-btn');
    if (addBtn) {
        addBtn.addEventListener('click', function() {
            // Read product data from data attributes
            const btn = document.getElementById('add-to-cart-btn');
            const productId = btn.getAttribute('data-product-id');
            const productName = btn.getAttribute('data-product-name');
            const productPrice = btn.getAttribute('data-product-price');
            const productImage = btn.getAttribute('data-product-image');
            const quantity = parseInt(document.getElementById('product-quantity').value) || 1;

            addToCart({
                id: productId,
                name: productName,
                price: Number(productPrice),
                image: productImage,
                quantity: quantity
            });
        });
    }
});

// Додаємо товар у кошик
function addToCart(product) {
    let cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const idx = cart.findIndex(item => item.id == product.id);
    if (idx !== -1) {
        cart[idx].quantity += product.quantity;
    } else {
        cart.push(product);
    }
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCounter();
    renderCartTable();
    showNotification('Товар додано до кошика!');
}

function showNotification(message) {
    // Ваш кастомний код для спливаючого повідомлення
    // Наприклад:
    let notif = document.createElement('div');
    notif.className = 'cart-notification';
    notif.textContent = message;
    document.body.appendChild(notif);
    setTimeout(() => notif.remove(), 2000);
}

function updateCartCounter() {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const count = cart.reduce((sum, item) => sum + item.quantity, 0);
    const el = document.getElementById('cart-counter');
    if (el) el.textContent = count;
}

// Рендеримо кошик на сторінці cart.html
function renderCartTable() {
    const tbody = document.getElementById('cart-table-body');
    if (!tbody) return;
    tbody.innerHTML = '';
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    if (cart.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Кошик порожній</td></tr>';
        return;
    }
    cart.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><img src="${item.image}" width="60"></td>
            <td>${item.name}</td>
            <td>${formatPrice(item.price)}</td>
            <td>${item.quantity}</td>
            <td><a href="#" class="remove-from-cart" data-id="${item.id}">Видалити</a></td>
        `;
        tbody.appendChild(tr);
    });
}

// Видалення товару з кошика
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('remove-from-cart')) {
        e.preventDefault();
        const id = e.target.dataset.id;
        let cart = JSON.parse(localStorage.getItem('cart') || '[]');
        cart = cart.filter(item => item.id != id);
        localStorage.setItem('cart', JSON.stringify(cart));
        renderCartTable();
        updateCartCounter();
    }
});

// Save cart state to localStorage
function saveCartState() {
    // Save the full cart structure from localStorage (if exists), else from DOM
    let cart = JSON.parse(localStorage.getItem('cart') || '[]');
    if (cart.length === 0) {
        // Fallback: try to reconstruct from DOM if needed
        cart = [];
        document.querySelectorAll('.product-list tbody tr').forEach(row => {
            const name = row.querySelector('.product-info a')?.textContent || '';
            const priceText = row.querySelector('td:nth-child(2)')?.textContent || '';
            const price = parseFloat(priceText.replace(/[^0-9.-]+/g, ""));
            const image = row.querySelector('.product-info img')?.src || '';
            // Try to get product id from a data attribute if present
            const id = row.querySelector('.remove-from-cart')?.getAttribute('data-id') ||
                       row.querySelector('.product-remove')?.getAttribute('data-id') ||
                       '';
            // Quantity is not shown in this table, default to 1
            cart.push({ id, name, price, image, quantity: 1 });
        });
    }
    localStorage.setItem('cart', JSON.stringify(cart));
}

class Cart {
    constructor() {
        this.items = [];
        this.loadCart();
        this.initEventListeners();
    }

    loadCart() {
        const savedCart = localStorage.getItem('cart');
        if (savedCart) {
            this.items = JSON.parse(savedCart);
        }
        this.updateAllCartUI();
    }

    saveCart() {
        localStorage.setItem('cart', JSON.stringify(this.items));
    }

    removeItem(itemName) {
        // Find the item in main cart table first
        const cartTable = document.querySelector('.product-list table tbody');
        if (cartTable) {
            const row = cartTable.querySelector(`tr:has([data-name="${itemName}"])`);
            if (row) {
                // Add animation class
                row.classList.add('removing');
                
                // Wait for animation to complete before removing
                setTimeout(() => {
                    this.items = this.items.filter(item => item.name !== itemName);
                    this.saveCart();
                    this.updateAllCartUI();
                }, 500); // Match animation duration
                return;
            }
        }

        // If no animation possible, remove immediately
        this.items = this.items.filter(item => item.name !== itemName);
        this.saveCart();
        this.updateAllCartUI();
    }

    addItem(name, price, image, quantity = 1) {
        // Remove currency symbol and convert to number
        price = parseFloat(price.replace(/[^0-9.-]+/g, ""));
        
        const existingItem = this.items.find(item => item.name === name);
        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            this.items.push({
                name: name,
                price: price,
                image: image,
                quantity: quantity
            });
        }
        this.saveCart();
        this.updateAllCartUI();
        this.showNotification('Товар додано до кошика!');
    }

    updateCheckoutSummary() {
        const checkoutBlock = document.querySelector('.product-checkout-details .block');
        if (!checkoutBlock) return;

        const productCardsContainer = checkoutBlock.querySelector('.product-cards');
        if (!productCardsContainer) return;

        productCardsContainer.innerHTML = this.items.map(item => `
            <div class="media product-card">
                <a class="pull-left" href="product-single.html">
                    <img class="media-object" src="${item.image}" alt="${item.name}" />
                </a>
                <div class="media-body">
                    <h4 class="media-heading">
                        <a href="product-single.html">${item.name}</a>
                    </h4>
                    <p class="price">${item.quantity} x ${formatPrice(item.price)}</p>
                    <p class="item-total">${formatPrice(item.quantity * item.price)}</p>
                    <span class="remove" data-name="${item.name}">Прибрати</span>
                </div>
            </div>
        `).join('');

        // Update total
        const total = this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const summaryTotal = checkoutBlock.querySelector('.summary-total');
        if (summaryTotal) {
            summaryTotal.innerHTML = `
                <span>Всього</span>
                <span>${formatPrice(total)}</span>
            `;
        }
    }

    updateAllCartUI() {
        this.updateMiniCart();
        this.updateMainCart();
        this.updateCheckoutSummary(); // Add this line
    }

    updateMiniCart() {
        const cartDropdown = document.querySelector('.cart-dropdown');
        if (!cartDropdown) return;

        // Update cart items in dropdown
        const mediaArea = cartDropdown.querySelector('.media-area');
        if (mediaArea) {
            mediaArea.innerHTML = this.items.length === 0 ? 
                '<p class="text-center">Кошик порожній</p>' : 
                this.items.map(item => `
                    <div class="media">
                        <a class="pull-left" href="#!">
                            <img class="media-object" src="${item.image}" alt="${item.name}" />
                        </a>
                        <div class="media-body">
                            <h4 class="media-heading"><a href="#!">${item.name}</a></h4>
                            <div class="cart-price">
                                <span>${item.quantity} x</span>
                                <span>${formatPrice(item.price)}</span>
                            </div>
                        </div>
                        <a href="#!" class="remove" data-name="${item.name}">
                            <i class="tf-ion-close"></i>
                        </a>
                    </div>
                `).join('');
        }

        // Update total price
        const total = this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const totalElement = cartDropdown.querySelector('.total-price');
        if (totalElement) {
            totalElement.textContent = formatPrice(total);
        }

        // Update cart count badge
        const cartCount = this.items.reduce((sum, item) => sum + item.quantity, 0);
        const cartCountElement = document.querySelector('.cart-nav .cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = cartCount.toString();
            cartCountElement.style.display = cartCount > 0 ? 'inline-block' : 'none';
        }
    }

    updateMainCart() {
        const mainCartTable = document.querySelector('.product-list table tbody');
        if (!mainCartTable) return;

        mainCartTable.innerHTML = this.items.map(item => `
            <tr>
                <td>
                    <div class="product-info">
                        <img width="80" src="${item.image}" alt="${item.name}" />
                        <a href="#!">${item.name}</a>
                    </div>
                </td>
                <td>${formatPrice(item.price * item.quantity)}</td>
                <td>
                    <a class="product-remove" href="#!" data-name="${item.name}">
                        <i class="tf-ion-close"></i>
                    </a>
                </td>
            </tr>
        `).join('');
    }

    initEventListeners() {
        document.addEventListener('click', (e) => {
            const addButton = e.target.closest('.add-to-cart');
            if (addButton) {
                e.preventDefault();
                
                // Get closest product container
                const productContainer = addButton.closest('.product-item') || 
                                      addButton.closest('.single-product-details');
                
                if (productContainer) {
                    const name = productContainer.querySelector('.product-title')?.textContent || 
                               productContainer.querySelector('h2')?.textContent;
                    const price = productContainer.querySelector('.product-price')?.textContent || 
                                productContainer.querySelector('.price')?.textContent;
                    const image = productContainer.closest('section').querySelector('img')?.src || 
                                document.querySelector('.single-product-slider img')?.src;
                    const quantity = parseInt(document.getElementById('product-quantity')?.value || 1);

                    if (name && price && image) {
                        this.addItem(name, price, image, quantity);
                    }
                }
            }

            // Handle remove button clicks
            if (e.target.closest('.product-remove') || e.target.closest('.remove')) {
                e.preventDefault();
                const button = e.target.closest('.product-remove') || e.target.closest('.remove');
                const itemName = button.dataset.name;
                if (itemName) {
                    this.removeItem(itemName);
                }
            }

            // Handle remove from checkout summary
            if (e.target.classList.contains('remove')) {
                e.preventDefault();
                const itemName = e.target.dataset.name;
                if (itemName) {
                    this.removeItem(itemName);
                    this.showNotification('Товар видалено з кошика');
                }
            }
        });
    }

    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'cart-notification';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 2000);
    }
}

// Initialize cart when document loads
document.addEventListener('DOMContentLoaded', function() {
    window.cart = new Cart();
    updateCartCounter();
    renderCartTable();
});