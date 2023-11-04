function loadImagePreview(inputId) {
    var input = document.getElementById(inputId);
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('preview' + inputId.charAt(inputId.length - 1)).setAttribute('src', e.target.result);
        }
        reader.readAsDataURL(input.files[0]);
    }
}
