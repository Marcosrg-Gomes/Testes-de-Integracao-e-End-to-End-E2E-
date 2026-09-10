// Validação simples no lado do cliente do formulário de cadastro.
// A validação definitiva sempre acontece no servidor (app.py).
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const senha = document.getElementById("senha");
    const confirmarSenha = document.getElementById("confirmar_senha");

    if (form && senha && confirmarSenha) {
        form.addEventListener("submit", function (event) {
            if (senha.value !== confirmarSenha.value) {
                event.preventDefault();
                alert("As senhas não coincidem.");
            }
        });
    }
});
