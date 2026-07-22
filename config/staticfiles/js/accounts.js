function togglePasswordVisibility() {
  const passwordInput = document.getElementById('password');
  const eyeIcon = document.getElementById('eye-icon');
  const eyeCloseIcon = document.getElementById('eye-close-icon');
  
  if (eyeIcon && eyeCloseIcon) {
    eyeIcon.classList.toggle('hidden');
    eyeCloseIcon.classList.toggle('hidden');
  }
  
  if (!passwordInput) return;

  passwordInput.type =
    passwordInput.type === 'password' ? 'text' : 'password';
}
