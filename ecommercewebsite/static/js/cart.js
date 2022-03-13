var pagePath = window.location.pathname;

var updateBtns = document.getElementsByClassName('update-cart')

// Get the amount of ordered items
var cartItemsQuantityElement = document.getElementById(`cart-total`)
var itemQuantity = parseInt(cartItemsQuantityElement.innerHTML)

for (i = 0; i < updateBtns.length; i++) {
	updateBtns[i].addEventListener('click', function () {
		var productId = this.dataset.product
		var action = this.dataset.action
		console.log('productId:', productId, 'Action:', action)

		console.log("USER:", user)
		if (user == "AnonymousUser") {
			addCartCookieItem(productId, action)
		} else {
			//console.log("User is authenticated (" + user + ") - sending data...")
			updateUserOrder(productId, action)
		}
	})

}


function updateUserOrder(productId, action) {
	console.log("User is authenticated - sending data...")

	var url = "/update_item/"

	fetch(url, {
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
	.then((data) => function () {
		location.reload()
	})
}


function addCartCookieItem(productId, action) {
	console.log('addCartCookieItem()')

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

			if (cart[productId]['quantity'] <= 0) {
				console.log('Remove item #', productId)
				delete cart[productId]
				location.reload()
			}
		}
		itemQuantity -= 1
	}

	document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"

	// Update quantity labels
	cartItemsQuantityElement.innerHTML = itemQuantity
	if (pagePath == "/cart/") {
		var productQuantityElement = document.getElementById(`item${productId}-quantity`)
		productQuantityElement.innerHTML = cart[productId]['quantity']
	}
}