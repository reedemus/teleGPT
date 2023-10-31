class PhotoSubmission {
    constructor() {
        const inputs = document.querySelectorAll('.js-photo_submit-input');

        for (var i = 0; i < inputs.length; i++) {
            inputs[i].addEventListener('change', this.uploadImage);
        }
    }

    uploadImage(e) {
        const fileInput = e.target;
        const uploadBtn = fileInput.parentNode;
        const deleteBtn = uploadBtn.childNodes[7];

        const reader = new FileReader();

        reader.onload = function(e) {
            uploadBtn.setAttribute('style', `background-image: url('${e.target.result}');`);
            uploadBtn.classList.add('photo_submit--image');
            fileInput.setAttribute('disabled', 'disabled');
        };

        reader.readAsDataURL(e.target.files[0]);

        deleteBtn.addEventListener('click', () => {
            uploadBtn.removeAttribute('style');
            uploadBtn.classList.remove('photo_submit--image');
            
            setTimeout(() => {
                fileInput.removeAttribute('disabled', 'disabled');
            }, 200);
        });
    }
};

new PhotoSubmission;