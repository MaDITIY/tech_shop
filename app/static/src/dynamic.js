var input = document.querySelector("#product_count");

  input.oninput = function() {
    document.querySelector('.dynamic-price').innerHTML = 'Total: ' + input.value*document.querySelector('.dynamic-price-value > span').innerHTML + ' $';
    if(input.value*document.querySelector('.dynamic-price-value > span').innerHTML>document.querySelector('.dynamic-balance>span').innerHTML || input.value>1000)
        document.querySelector('.dynamic-price').classList.add('bad-total');
    else document.querySelector('.dynamic-price').classList.remove('bad-total');
};