var pagePath = window.location.pathname;

var cartItemsQuantityElement = document.getElementById(`cart-total`)
var itemQuantity = getItemAmountFromCookies()

// Assign item quantity update functionality to every `update-cart` button
var updateBtns = document.getElementsByClassName('update-cart')
for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', async function() {
        var productId = this.dataset.product
        var action = this.dataset.action

        // console.log("USER:", user);

        await updateProductQuantity(productId, action)

        updateNavbarItemsCounter(itemQuantity)
        if (pagePath == "/cart/") {
            updateCartTotals()
        }
    })

}

/**
 * Update product quantity.
 * @param {Number} productId    The ID of the product which quanitity is changed
 * @param {String} action       The action performed on this ordered item's quantity.
 *                              Can have these values: "add", "remove_one" 
 */
async function updateProductQuantity(productId, action) {
    // if (user == "AnonymousUser") {
    //     // If the user is unathenticated, edit cookies
    //     addCartCookieItem(productId, action)
    // } else {
    //     // If the user is athenticated, edit the order via back end
    //     await updateUserOrder(productId, action)
    // }
    await updateUserOrder(productId, action)
}

/**
 * Fetch a request to edit the quantity of an item with the `productId` ID.
 * 
 * @param {String} deviceId     The ID of the customer's device. Used for
 *                              unathenticated users
 * @param {Number} productId    The ID of the product which quanitity is changed
 * @param {String} action       The action performed on this ordered item's quantity.
 *                              Can have these values: "add", "remove_one" 
 */
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
            /*
            Back-end response is a dictionary containing the edited item's new
            quantity and the total amount of ordered items.
            */
            var dataParsed = JSON.parse(data)
            itemQuantity = dataParsed['total_items']

            if (pagePath == "/cart/") {
                updateCartProduct(productId, dataParsed['ordered_item_quantity'])
            }
        })
}

/**
 * Update product quantity inside of the `cart` cookie.
 * @param {Number} productId    The ID of the product which quanitity is changed
 * @param {String} action       The action performed on this ordered item's quantity.
 *                              Can have these values: "add", "remove_one" 
 */
function addCartCookieItem(productId, action) {
    // Update the quantity code-wise
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

    // Remove the item cookie if its quantity is 0 or less
    //if (cart[productId]['quantity'] <= 0) {
    //    console.log('Remove item #', productId)
    //    delete cart['productId']
    //}

    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"

    // Update quantity labels
    if (pagePath == "/cart/") {
        updateCartProduct(productId, cart[productId]['quantity'])
    }
}

/**
 * Update the ordered item's HTML representation on the `cart` page
 * @param {Number} productId        The ID of the product which quanitity is changed
 * @param {Number} productQuantity  The new quantity of the ordered item
 */
function updateCartProduct(productId, productQuantity) {
    var productQuantityElement = document.getElementById(`item${productId}-quantity`)
    productQuantityElement.innerHTML = productQuantity

    if (productQuantity <= 0) {
        document.getElementById(`item${productId}-div`).remove()
    }
}

/**
 * Update the total amount of ordered items
 * @param {Number} new_total 
 */
function updateNavbarItemsCounter(new_total) {
    cartItemsQuantityElement.innerHTML = new_total
}

/**
 * Retrieve the total amount of ordered items 
 * @returns {Number}        The amount of ordered items
 */
function getItemAmountFromCookies() {
    // var amount = 0
    // for (const item_id in cart) {
    //     amount += parseInt(cart[item_id]['quantity'])
    // }
    // return amount
    return 0
}

/**
 * Update cart totals: total item count, order price
 */
function updateCartTotals() {
    var orderPrice = 0.0
    itemQuantity = 0

    /*
    Go over every item in the cart and add its quantity and price to the total
    amount variables
    */
    var cartRows = document.getElementsByClassName("cart-row actual")
    for (let cartRow of cartRows) {
        var itemId = cartRow.dataset.itemproductid

        var itemPrice = parseInt(parseFloat(document.getElementById(`item${itemId}-price`).innerHTML * 100))
            // Multiply the float value by 100 to avoid losing precision

        var quantity = parseInt(document.getElementById(`item${itemId}-quantity`).innerHTML)

        // Calculate the total price for this item
        var itemPriceTotal = itemPrice * quantity / 100 // Divide by 100 to return to the float format

        orderPrice += itemPriceTotal
        itemQuantity += quantity
        document.getElementById(`item${itemId}-price-total`).innerHTML = itemPriceTotal.toFixed(2)
    }

    // Update the counters
    document.getElementById("items-total").innerHTML = itemQuantity
    document.getElementById("cart-price").innerHTML = orderPrice.toFixed(2)
}