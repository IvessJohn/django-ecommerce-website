var pagePath = window.location.pathname;

var updateBtns = document.getElementsByClassName('update-cart')

var cartItemsQuantityElement = document.getElementById(`cart-total`)
var itemQuantity = getItemAmountFromCookies()

for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', async function() {
        var productId = this.dataset.product
        var action = this.dataset.action

        console.log("USER:", user);

        await updateProductQuantity(productId, action)

        updateNavbarItemsCounter(itemQuantity)
        if (pagePath == "/cart/") {
            updateCartTotals()
        }
    })

}

async function updateProductQuantity(productId, action) {
    if (user == "AnonymousUser") {
        addCartCookieItem(productId, action)
    } else {
        await updateUserOrder(productId, action)
    }
}

async function updateUserOrder(productId, action) {
    //console.log("User is authenticated - sending data...")

    var url = "/update_item/"

    await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({ 'productId': productId, 'action': action })
        })
        .then((response) => {
            return response.json()
        })
        .then((data) => {
            var dataParsed = JSON.parse(data)
            itemQuantity = dataParsed['total_items']

            if (pagePath == "/cart/") {
                updateCartProduct(productId, dataParsed['ordered_item_quantity'])
            }
        })
}

function addCartCookieItem(productId, action) {
    if (action == 'add') {
        if (cart[productId] == undefined) {
            cart[productId] = { 'quantity': 1 }
        } else {
            cart[productId]['quantity'] += 1
        }
        itemQuantity += 1
    } else if (action == 'remove_one') {
        if (cart[productId]) {
            cart[productId]['quantity'] -= 1
        }
        itemQuantity -= 1
    }


    // Update labels
    if (pagePath == "/cart/") {
        updateCartProduct(productId, cart[productId]['quantity'])
    }

    // Remove the item cookie if its quantity is 0 or less
    //if (cart[productId]['quantity'] <= 0) {
    //    console.log('Remove item #', productId)
    //    delete cart['productId']
    //}

    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
}

function updateCartProduct(productId, productQuantity) {
    var productQuantityElement = document.getElementById(`item${productId}-quantity`)
    productQuantityElement.innerHTML = productQuantity

    if (productQuantity <= 0) {
        document.getElementById(`item${productId}-div`).remove()
    }
}

function updateNavbarItemsCounter(new_total) {
    cartItemsQuantityElement.innerHTML = new_total
}


function getItemAmountFromCookies() {
    var amount = 0
    for (const item_id in cart) {
        amount += parseInt(cart[item_id]['quantity'])
    }
    return amount
}

function updateCartTotals() {
    var orderPrice = 0.0
    itemQuantity = 0
    var cartRows = document.getElementsByClassName("cart-row actual")
    for (let cartRow of cartRows) {
        var itemId = cartRow.dataset.itemproductid

        var itemPrice = parseInt(parseFloat(document.getElementById(`item${itemId}-price`).innerHTML * 100))
        var quantity = parseInt(document.getElementById(`item${itemId}-quantity`).innerHTML)
        var itemPriceTotal = itemPrice * quantity / 100

        orderPrice += itemPriceTotal
        itemQuantity += quantity
        document.getElementById(`item${itemId}-price-total`).innerHTML = itemPriceTotal.toFixed(2)
    }
    document.getElementById("items-total").innerHTML = itemQuantity
    document.getElementById("cart-price").innerHTML = orderPrice.toFixed(2)
}