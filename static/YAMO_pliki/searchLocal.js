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
    if(where=="/songs"){
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

function returnAlbArt(){
     table = document.getElementById("rows");
        tr = table.getElementsByTagName("a");
        for (i = 0; i < tr.length; i++) {
            ida=tr[i].id;
            if(document.getElementById("dd"+ida).style.display=='none'){
                    document.getElementById("dd"+ida).style.display='block';
            } 
        }
}
function checkBlock(){
    var input, filter, table, tr, td, i;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("rows");
    tr = table.getElementsByTagName("a");
    for (i = 0; i < tr.length; i++) {
        count=0
        if (tr[i].innerHTML.toUpperCase().indexOf(filter) > -1) {
            //console.log(tr[i].innerHTML.toUpperCase());
            ida=tr[i].id;
            if(document.getElementById("dd"+ida).style.display!='block'){
                        document.getElementById("dd"+ida).style.display='block';
            } 
        }else {
            ida=tr[i].id;
            if(document.getElementById("dd"+ida).style.display!='none'){
                        document.getElementById("dd"+ida).style.display='none';
            }
        }
    }
}

function ArtAlb(){
    where=window.location.pathname;
    var lists=['list','box'];
    var ids=['0','1','2'];
    if(where=='/albums'){
        if(filter!=''){
            for(i=0;i<lists.length;i++){
                for(j=0;j<ids.length;j++){
                    if(document.getElementById(lists[i]+ids[j]).style.display=='block'){
                        document.getElementById(lists[i]+ids[j]).style.display='none';
                        starts=lists[i]+ids[j];
                        document.getElementById('searching').style.display='block';
                        idd=ids[j];
                        sort=lists[i];
                        document.getElementById(ids[j]).classList.remove("active");
                        document.getElementById(lists[i]).classList.remove("active");
                    }
                }
            }
        checkBlock();
        }else{
            document.getElementById('searching').style.display='none';  
            document.getElementById(starts).style.display='block';
            document.getElementById(idd).classList.add("active");
            document.getElementById(sort).classList.add("active");
        }
    }else if(where=='/artists'){
         if(filter!=''){
            for(i=0;i<lists.length;i++){
                if(document.getElementById(lists[i]+'0').style.display=='block'){
                        document.getElementById(lists[i]+'0').style.display='none';
                        starts2=lists[i]+'0';
                        document.getElementById('searching').style.display='block';
                        sort2=lists[i];
                        document.getElementById(lists[i]).classList.remove("active");
                }
            }
            checkBlock();
        }else{
            document.getElementById('searching').style.display='none';  
            document.getElementById(starts2).style.display='block';
            document.getElementById(sort2).classList.add("active");
        }
    }
}

function searchLocal(){
    where=window.location.pathname;
    var lists=['list','box'];
    var ids=['0','1','2'];
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    if(where=='/albums' || where=='/artists'){
         ArtAlb();        
    }else if(where=='/songs'){
        searchTable();
    }
}

function searchTable(){
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
