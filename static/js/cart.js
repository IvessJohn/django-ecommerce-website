var pagePath = window.location.pathname;

var cartItemsQuantityElement = document.getElementById(`cart-total`)
var itemQuantity = 0

// Assign item quantity update functionality to every `update-cart` button
var updateBtns = document.getElementsByClassName('update-cart')
for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', async function() {
        var productId = this.dataset.product
        var action = this.dataset.action

        // console.log("USER:", user);

        await updateItemQuantity(productId, action)

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
async function updateItemQuantity(productId, action) {
    await fetchItemQuantityUpdate(productId, action)
}

/**
 * Fetch a request to edit the quantity of an item with the `productId` ID.
 * 
 * @param {Number} productId    The ID of the product which quanitity is changed
 * @param {String} action       The action performed on this ordered item's quantity.
 *                              Can have these values: "add", "remove_one" 
 */
async function fetchItemQuantityUpdate(productId, action) {
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
 * Update the ordered item's HTML representation on the `cart` page. \
 * INTENDED TO WORK ONLY ON THE `cart` PAGE.
 * 
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
 * Update the total amount of ordered items.
 * @param {Number} new_total 
 */
function updateNavbarItemsCounter(new_total) {
    cartItemsQuantityElement.innerHTML = new_total
}

/**
 * Update cart totals: total item count, order price.
 */
function updateCartTotals() {
    var orderPrice = 0.0
    itemQuantity = 0

    /*
    Iterate over every item in the cart and add its quantity and price to the
    total amount variables
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