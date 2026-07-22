const form = document.getElementById('search-form');

if (form) {

    const statusInput = document.getElementById('status-input');

    const filters = document.querySelectorAll('.filter-card');

    filters.forEach(filter => {

        filter.addEventListener('click', () => {

            statusInput.value = filter.dataset.status;

            form.submit();

        });

    });

}