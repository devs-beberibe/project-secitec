var elements = document
.querySelectorAll('[id^="id_data"]')
.forEach((e) => {
    let dataFormat = FormataStringData(e.value)
    
    e.type = 'date'
    e.value = dataFormat
})

let messagem = document.querySelector('#messages')
let btn = document.querySelector('#button-messagens')
btn.addEventListener('click', function () {
    messagem.parentElement.removeChild(messagem)
})