function loadHTML(elementId, fileName) {
    fetch(fileName)
        .then(response => response.text())
        .then(data => {
            document.getElementById(elementId).innerHTML = data;
        });
}

document.addEventListener('DOMContentLoaded', function() {
    loadHTML('header', 'header.html');
    loadHTML('sidebar', 'sidebar.html');
    loadHTML('toggle', 'toggle.html');
    loadHTML('footer', 'footer.html');
    
    setTimeout(() => {
        const toggleThemeButton = document.getElementById('toggle-theme');
        toggleThemeButton.addEventListener('click', function() {
            document.body.classList.toggle('bg-dark');
            document.body.classList.toggle('bg-light');
            document.body.classList.toggle('text-white');
            document.body.classList.toggle('text-dark');
        });

        document.querySelectorAll('form').forEach(form => {
            form.querySelectorAll('input, textarea, select').forEach(input => {
                input.setAttribute('required', true);
            });
        });
    }, 100);
});
