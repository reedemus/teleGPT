var fileList = {
    source: "",
    target: ""
 };

function loadSourceImagePreview(inputId) {
    var input = document.getElementById(inputId);
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('preview' + inputId.charAt(inputId.length - 1)).setAttribute('src', e.target.result);
        }
        reader.readAsDataURL(input.files[0]);
        fileList["source"] = input.files[0];
        print(fileList["source"]);
    }
}

function loadTargetImagePreview(inputId) {
    var input = document.getElementById(inputId);
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('preview' + inputId.charAt(inputId.length - 1)).setAttribute('src', e.target.result);
        }
        reader.readAsDataURL(input.files[0]);
        fileList["target"] = input.files[0];
        print(fileList["target"]);
    }
}

function returnFilePath(){
    window.Telegram.WebApp.sendData(JSON.stringify(fileList));
}