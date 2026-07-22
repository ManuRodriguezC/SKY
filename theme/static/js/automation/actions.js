function openConfirmationModal(config) {
    document.getElementById('modal-title').textContent =
        config.title || 'Confirmar acción';

    document.getElementById('modal-message').textContent =
        config.message || '';

    document.getElementById('modal-submit-button').textContent =
        config.buttonText || 'Confirmar';

    document.getElementById('confirmation-form').action =
        config.url;

    document.getElementById('confirmation-modal').showModal();
}
