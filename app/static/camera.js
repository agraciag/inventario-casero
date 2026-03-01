// Camera capture and preview functionality
(function() {
  const photoInput = document.getElementById('photo-input');
  const cameraBtn = document.getElementById('camera-btn');
  const uploadBtn = document.getElementById('upload-btn');
  const preview = document.getElementById('photo-preview');
  const previewImg = document.getElementById('preview-img');
  const removeBtn = document.getElementById('remove-photo');

  if (!photoInput) return;

  // Camera button - use capture attribute for mobile
  if (cameraBtn) {
    cameraBtn.addEventListener('click', function() {
      photoInput.setAttribute('capture', 'environment');
      photoInput.click();
    });
  }

  // Upload button - file picker without capture
  if (uploadBtn) {
    uploadBtn.addEventListener('click', function() {
      photoInput.removeAttribute('capture');
      photoInput.click();
    });
  }

  // Preview selected photo
  photoInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(ev) {
      previewImg.src = ev.target.result;
      preview.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
  });

  // Remove photo
  if (removeBtn) {
    removeBtn.addEventListener('click', function() {
      photoInput.value = '';
      preview.classList.add('hidden');
      previewImg.src = '';
    });
  }
})();
