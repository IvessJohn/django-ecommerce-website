var requiresShipping = '{{requires_shipping}}'
var total = '{{order.get_final_price}}'
var appliedCouponCode = '{{order.applied_coupon.code}}'

var form = document.getElementById('form')
var couponForm = document.getElementById('coupon-form')
var couponEditButton = document.getElementById('coupon-edit-button')

//
if (user != "AnonymousUser") {
    document.getElementById("user-info").innerHTML = ''
}
if (requiresShipping == "False") {
    document.getElementById("shipping-info").innerHTML = ''
}
if (user != "AnonymousUser" && requiresShipping == 'False') {
    // Hide the info form altogether
    document.getElementById("form-wrapper").classList.add("hidden")
        // Show the payment button
    document.getElementById("payment-info").classList.remove("hidden")
}

if (appliedCouponCode != "") {
    couponInputField = document.getElementById("coupon-field")
    couponSubmitButton = document.getElementById("coupon-submit-button")

    couponInputField.value = appliedCouponCode
    lockCouponEntering()
}

//csrftoken = form.getElementsByTagName("input")[0]
//console.log(csrfToken)

form.addEventListener('submit', function(e) {
    //console.log("Form submitted...")
    e.preventDefault()
    document.getElementById("form-button").classList.add("hidden")
    document.getElementById("payment-info").classList.remove("hidden")
})
couponForm.addEventListener('submit', function(e) {
    //console.log("Coupon submitted...")
    e.preventDefault()
    lockCouponEntering()
    submitCoupon()
})
couponEditButton.addEventListener('click', function(e) {
    e.preventDefault()
    unlockCouponEntering()
})

// #region FOR: Updating visual (HTML) elements

function lockCouponEntering() {
    document.getElementById("coupon-submit-button").classList.add("hidden")
    document.getElementById("coupon-field").setAttribute("readonly", true)
    couponEditButton.classList.remove("hidden")
}

function unlockCouponEntering() {
    document.getElementById("coupon-submit-button").classList.remove("hidden")
    document.getElementById("coupon-field").removeAttribute("readonly")
    couponEditButton.classList.add("hidden")
}

function updatePrices(finalPrice, discountValue) {


}

// #endregion

// #region FOR: Submitting data
function submitFormData() {
    console.log("Payment button clicked")

    var userFormData = {
        'name': null,
        'email': null,
        'total': total,
    }
    var shippingInfo = {
        'address': null,
        'city': null,
        'state': null,
        'country': null,
        'zipcode': null,
    }

    if (user == "AnonymousUser") {
        userFormData.name = form.name.value
        userFormData.email = form.email.value
    }
    if (requiresShipping == "True") {
        shippingInfo.address = form.address.value
        shippingInfo.city = form.city.value
        shippingInfo.state = form.state.value
        shippingInfo.country = form.country.value
        shippingInfo.zipcode = form.zipcode.value
    }

    total = document.getElementById('order-final-price').innerHTML
    console.log(total)

    var url = '/process_order/'
    fetch(url, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                'userFormData': userFormData,
                'shippingInfo': shippingInfo
            })
        })
        .then((response) => response.json())
        .then((data) => {
            console.log("Success:", data)
            alert("Transaction complete.")

            cart = {}
            document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"

            window.location.href = "{% url 'store' %}"
        })
}

/**
 * Submit the applied coupon to the back end
 */
function submitCoupon() {
    console.log('submitCoupon()')

    var coupon = couponForm.code.value

    if (coupon != "") {
        var url = '/apply_coupon/'
        fetch(url, {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({
                    'price': total,
                    'couponCode': coupon
                })
            })
            .then((response) => response.json())
            .then((data) => {
                location.reload()
            })
    }
}

// #endregion