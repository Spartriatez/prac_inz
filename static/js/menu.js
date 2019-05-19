function openImport(){
    document.getElementById("import").style.display="block";
}

function closeImport(){
    document.getElementById("import").style.display="none";
}

function sshValue(){

}

document.addEventListener("hashchange", function(){
    var url_string=window.location.href;
    var url = new URL(url_string);
    var c = url.searchParams.get("directory_path");
    console.log(c);
});

function example() {
    window.location.reload();
    var url_string=window.location.href;
    var url = new URL(url_string);
    var c = url.searchParams.get("directory_path");
    console.log(c);
    document.getElementById("dirPath").value="dsadasdada";
}
if (window.performance) {
  var url_string=window.location.href;
  var url = new URL(url_string);
  var c = url.searchParams.get("directory_path");
  console.log(c);
}



