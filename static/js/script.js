/* 
    Pega todos os elementos que são para datas, mas que estão do tipo texto 
    e acerta eles 
*/
var elements = document
.querySelectorAll('[id^="id_data"]')
.forEach((e) => {
    let dataFormat = FormataStringData(e.value)
    
    e.type = 'date'
    e.value = dataFormat
})

function FormataStringData(data) {
    var dia  = data.split("/")[0];
    var mes  = data.split("/")[1];
    var ano  = data.split("/")[2];
  
    return ano + '-' + ("0"+mes).slice(-2) + '-' + ("0"+dia).slice(-2);
    // Utilizo o .slice(-2) para garantir o formato com 2 digitos.
}


function removeMessage() {
    /*
     * Função para remoção da mensagem
     */
    let mensagem = document.querySelector("#messages")
    mensagem.remove()
}


function inputUppercase() {
    /*
     * Esse pequeno trecho de código coloca todos os valores 
     * de input uppercase.
     */
    document.querySelectorAll("input[type='text']").forEach((e) => {
        e.addEventListener('input', function(){
            this.value=this.value.toUpperCase(); 
        })
    })
    document.querySelectorAll("textarea").forEach((e) => {
        e.addEventListener('input', function(){
            this.value=this.value.toUpperCase(); 
        })
    })
}

document.querySelectorAll("input[type=text]").forEach((e) => {
    e.classList.add("w-100");
})

document.querySelectorAll("select").forEach((e) => {
    e.classList.add("w-100");
})

document.querySelectorAll("textarea").forEach((e) => {
    e.classList.add("w-100");
})

var placeholder = [
    ["#id_numero_tombo", "Ex: 0000-0000"],
    ["#id_deixado", "Ex: Nome"],
    ["#id_responsavel_pc", "Ex: Nome"],
    ["#id_descricao_problema", "Ex: Não liga"],
    ["#id_buscado_por", "Ex: Nome"],
    ["#id_laudo", "Ex: 000"],
].forEach((e) => {
    document.querySelector(e[0]).placeholder = e[1];
})