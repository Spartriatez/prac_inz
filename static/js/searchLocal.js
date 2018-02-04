function openNavSL() {
    document.getElementById("local").style.width = "200px";
    document.getElementById("local2").style.width = "0px";
}
var sort;
var idd;
var starts;
var starts2;
var sort2;
function closeNavSL() {
    where=window.location.pathname;
    document.getElementById("local").style.width = "0px";
    document.getElementById("local2").style.width = "20px";
    input = document.getElementById("myInput");
    input.value="";
}
    /*if(where=="/songs"){
        table = document.getElementById("myTable");
        tr = table.getElementsByTagName("tr");
            for (i = 1; i < tr.length; i++) {
                if(tr[i].style.display == "none"){
                    tr[i].style.display="";
                }
            }
    }else if(where=="/albums"){
        returnAlbArt();
        document.getElementById('searching').style.display='none';
        document.getElementById(idd).classList.add("active");
        document.getElementById(sort).classList.add("active");
        document.getElementById(starts).style.display='block';
    }else if(where=="/artists"){
        returnAlbArt();
        document.getElementById('searching').style.display='none';
        document.getElementById(sort2).classList.add("active");
        document.getElementById(starts2).style.display='block';
    }
}
*/
function searchLocal(){
    where=window.location.pathname;
    var lists=['list','box'];
    var ids=['0','1','2'];
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    if(where=='/albums'){
        console.log(where);        
    }
}

/*function searchTable(){
    var input, filter, table, tr, td, i;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("myTable");
    tr = table.getElementsByTagName("tr");
    for (i = 1; i < tr.length; i++) {
        tds = tr[i].getElementsByTagName("td");
        count=0
        for(j=0; j<tds.length;j++){
            td = tr[i].getElementsByTagName("td")[j];
            if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
                count++;
            }
        }       
        if(count>0){
            tr[i].style.display = "";
        } else {
            tr[i].style.display = "none";
        }
    }
}
*/
