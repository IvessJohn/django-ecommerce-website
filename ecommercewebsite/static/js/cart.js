var pagePath = window.location.pathname;

var updateBtns = document.getElementsByClassName('update-cart')

var cartItemsQuantityElement = document.getElementById(`cart-total`)
var itemQuantity = getItemAmountFromCookies()
console.log(itemQuantity)

for (i = 0; i < updateBtns.length; i++) {
	updateBtns[i].addEventListener('click', function () {
		var productId = this.dataset.product
		var action = this.dataset.action
		//console.log('productId:', productId, 'Action:', action)

		console.log("USER:", user)
		if (user == "AnonymousUser") {
			addCartCookieItem(productId, action)
		} else {
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
			console.log("updateUserOrder first then")
			return response.json()
		})
		.then((data) => {
			var data_parsed = JSON.parse(data)
			updateCartItemsCounter(data_parsed['total_items'])

			if (pagePath == "/cart/") {
				var productQuantityElement = document.getElementById(`item${productId}-quantity`)
				productQuantityElement.innerHTML = data_parsed['ordered_item_quantity']

				if (data_parsed['ordered_item_quantity'] <= 0) {
					document.getElementById(`item${productId}-div`).remove()
					console.log(`remove item ${productId}`)
				}
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

	document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"

	// Update quantity labels
	updateCartItemsCounter(itemQuantity)
	if (pagePath == "/cart/") {
		var productQuantityElement = document.getElementById(`item${productId}-quantity`)
		productQuantityElement.innerHTML = cart[productId]['quantity']

		if (cart[productId]['quantity'] <= 0) {
			document.getElementById(`item${productId}-div`).remove()
			console.log(`remove item ${productId}`)
		}
	}

	// Remove the item cookie if its quantity is 0 or less
	if (cart[productId]['quantity'] <= 0) {
		console.log('Remove item #', productId)
		delete cart[productId]
	}
}

function updateCartItemsCounter(new_total) {
	console.log("updateCartItemsCounter(" + new_total + ")")
	cartItemsQuantityElement.innerHTML = new_total
}

function getItemAmountFromCookies() {
	var amount = 0
	for (const item_id in cart) {
		amount += parseInt(cart[item_id]['quantity'])
	}
	return amount
}