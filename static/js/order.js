const ID_INPUTS_AND_DISPLAY = [
  {inputID: 'name', displayID: 'full_name_value'},
  {inputID: 'phone', displayID: 'phone_value'},
  {inputID: 'email', displayID: 'email_value'},
  {inputID: 'city', displayID: 'city_value'},
  {inputID: 'address', displayID: 'address_value'}
];

function displayEnteredInfo(input, display) {
  const inputEl = document.getElementById(input);
  const displayEl = document.getElementById(display);
  displayEl.textContent = inputEl.value;

  inputEl.addEventListener('input', () => {
    displayEl.textContent = inputEl.value;
  });
}

ID_INPUTS_AND_DISPLAY.forEach(input => displayEnteredInfo(input.inputID, input.displayID));


const DELIVERY_RADIOS = document.querySelectorAll('input[name="delivery_category"]');
const DELIVERY_DISPLAY = document.getElementById('delivery_value');

const PAY_RADIOS = document.querySelectorAll('input[name="payment_category"]');
const PAY_DISPLAY = document.getElementById('pay_value');

const LANGUAGE_CODE = JSON.parse(document.getElementById('language-code').textContent);
const IS_FREE_DELIVERY = JSON.parse(document.getElementById('is_free_delivery').textContent);
const totalPriceStr = document.getElementById('total-price').textContent;


updateDisplay(DELIVERY_RADIOS, DELIVERY_DISPLAY);
updateDisplay(PAY_RADIOS, PAY_DISPLAY);
updateDeliveryInfo();


PAY_RADIOS.forEach(function (radio) {
  radio.addEventListener('change', function () {
    updateDisplay(PAY_RADIOS, PAY_DISPLAY);
  });
});

DELIVERY_RADIOS.forEach(function (radio) {
  radio.addEventListener('change', function () {
    updateDisplay(DELIVERY_RADIOS, DELIVERY_DISPLAY);
    updateDeliveryInfo();
  });
});

function updateDisplay(radios, display) {
  radios.forEach(function (radio) {
    if (radio.checked) {
      const selectedToggleText = radio.parentElement.querySelector('.toggle-text');
      display.textContent = selectedToggleText.textContent;
    }
  });
}

function additionValute(str1, str2) {
  const regex = /[^\d.,-]/g;
  const numStr1 = str1.replace(regex, "");
  const numStr2 = str2.replace(regex, "");
  const decimalSeparator = numStr1.indexOf(",") !== -1 ? "," : ".";
  const num1 = parseFloat(numStr1.replace(",", ".").replace(decimalSeparator, "."));
  const num2 = parseFloat(numStr2.replace(",", ".").replace(decimalSeparator, "."));
  const sum = num1 + num2;
  const formattedSum = sum.toLocaleString(LANGUAGE_CODE, {minimumFractionDigits: 2, maximumFractionDigits: 2});
  return str1.includes("$") ? "$" + formattedSum : formattedSum + str1.slice(-1);
}

function updateDeliveryInfo() {
  let deliveryCategory = document.querySelector('input[name="delivery_category"]:checked').value;
  let xhr = new XMLHttpRequest();
  xhr.open('GET', '/order/delivery_info/' + deliveryCategory, true);
  xhr.onreadystatechange = function () {
    if (this.readyState === 4 && this.status === 200) {
      let data = JSON.parse(this.responseText);

      if (!IS_FREE_DELIVERY || data.codename !== 'regular-delivery') {
        document.querySelector('.Cart-delivery').style.display = ''
        document.querySelector('.Delivery-title').textContent = data.title;

        let DeliveryPriceStr = document.querySelector('.Delivery-price').textContent = data.price;
        document.getElementById('total-price').textContent = additionValute(DeliveryPriceStr, totalPriceStr)

      } else {
        document.querySelector('.Cart-delivery').style.display = 'none';
        document.getElementById('total-price').textContent = totalPriceStr;
      }
    }
  };
  xhr.send();
}
