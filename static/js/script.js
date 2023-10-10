let messagem = document.querySelector('#messages')
let btn = document.querySelector('#button-messagens')
btn.addEventListener('click', function () {
    messagem.parentElement.removeChild(messagem)
})