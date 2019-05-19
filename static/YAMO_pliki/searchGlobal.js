function searchGlobal(){
    lists=['list','box'];
    ids=['0','1','2'];
    input = document.getElementById("myInput2");
    filter = input.value.toUpperCase();
    where=window.location.pathname;
    if(filter!=''){
        document.getElementById("sidSearch").style.width = "400px";
        document.getElementById("sid2").style.display = "none";
        document.getElementById("local2").style.display = "none";
        document.getElementById("searchMenu").style.display = "block";
        if(where=="/albums" || where=="/artists"){
            document.getElementById("boxed").style.display = "none";
            if(where=="/albums"){
                 document.getElementById("menu1").style.display = "none";
            }else{
                document.getElementById("menu2").style.display = "none";
            }
        }else if(where='/songs'){
             document.getElementById("menu3").style.display = "none";
        }
        
    }else{
        document.getElementById("sidSearch").style.width = "0px";
        document.getElementById("sid2").style.display = "block";
        document.getElementById("local2").style.display = "block";
        document.getElementById("searchMenu").style.display = "none";
         if(where=="/albums" || where=="/artists"){
            document.getElementById("boxed").style.display = "block";
             if(where=="/albums"){
                 document.getElementById("menu1").style.display = "block";
            }else{
                document.getElementById("menu2").style.display = "block";
            }
        }else if(where='/songs'){
             document.getElementById("menu3").style.display = "block";
        }
    }
}
