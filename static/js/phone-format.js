document.addEventListener('DOMContentLoaded', () => {
    const phoneInputs = document.querySelectorAll('input[name="phone_number"]');

    phoneInputs.forEach((input) => {
        input.addEventListener('input', () => {
            input.value = formatRussianPhone(input.value);
        });

        if (input.value) {
            input.value = formatRussianPhone(input.value);
        }
    });
});


function formatRussianPhone(value) {
    let digits = value.replace(/\D/g, '');

    if (!digits) {
        return '';
    }

    if (digits.startsWith('8')) {
        digits = '7' + digits.slice(1);
    }

    if (!digits.startsWith('7')) {
        digits = '7' + digits;
    }

    digits = digits.slice(0, 11);

    const country = digits.slice(0, 1);
    const operator = digits.slice(1, 4);
    const firstPart = digits.slice(4, 7);
    const secondPart = digits.slice(7, 9);
    const thirdPart = digits.slice(9, 11);

    let result = `+${country}`;

    if (operator) {
        result += ` (${operator}`;
    }

    if (operator.length === 3) {
        result += ')';
    }

    if (firstPart) {
        result += ` ${firstPart}`;
    }

    if (secondPart) {
        result += `-${secondPart}`;
    }

    if (thirdPart) {
        result += `-${thirdPart}`;
    }

    return result;
}
