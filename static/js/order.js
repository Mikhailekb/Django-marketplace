const inputs = [
  {inputID: 'name', displayID: 'full_name_value'},
  {inputID: 'phone', displayID: 'phone_value'},
  {inputID: 'email', displayID: 'email_value'},
  {inputID: 'city', displayID: 'city_value'},
  {inputID: 'address', displayID: 'address_value'}
];

function setInputEvent(input, display) {
  const inputEl = document.getElementById(input);
  const displayEl = document.getElementById(display);

  displayEl.textContent = inputEl.value;

  inputEl.addEventListener('input', () => {
    displayEl.textContent = inputEl.value;
  });
}

inputs.forEach(input => setInputEvent(input.inputID, input.displayID));


const deliveryRadios = document.querySelectorAll('input[name="delivery_category"]');
const deliveryDisplay = document.getElementById('delivery_value');

const payRadios = document.querySelectorAll('input[name="payment_category"]');
const payDisplay = document.getElementById('pay_value');

function updateDisplay(radios, display) {
  radios.forEach(function (radio) {
    if (radio.checked) {
      const selectedToggleText = radio.parentElement.querySelector('.toggle-text');
      display.textContent = selectedToggleText.textContent;
    }
  });
}

updateDisplay(deliveryRadios, deliveryDisplay);
updateDisplay(payRadios, payDisplay);

deliveryRadios.forEach(function (radio) {
  radio.addEventListener('change', function () {
    updateDisplay(deliveryRadios, deliveryDisplay);
  });
});

payRadios.forEach(function (radio) {
  radio.addEventListener('change', function () {
    updateDisplay(payRadios, payDisplay);
  });
});