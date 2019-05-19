function switching(id1,id2){
    if(document.getElementById('searching').style.display=='block'){
        document.getElementById('searching').style.display='none';
        document.getElementById("local").style.width = "0px";
        document.getElementById("local2").style.width = "20px";
        input = document.getElementById("myInput");
        input.value="";
        returnAlbArt();
    }
    var ids=['0','1','2'];
    var td = document.getElementById(id1);
    if(!td.classList.contains('active')){
        td.classList.add("active");
        document.getElementById(id2).classList.remove("active");
        for (i = 0; i < ids.length; i++) { 
            if(document.getElementById(ids[i]).classList.contains('active')){
                document.getElementById(ids[i]).classList.remove("active");
                if(document.getElementById(id2+ids[i]).style.display=='block'){
                        document.getElementById(id2+ids[i]).style.display='none';
                }
            }
        }
        document.getElementById("0").classList.add("active");
        document.getElementById(id1+"0").style.display='block';
    }
}

function change(check,id){
     var ids=['0','1','2'];
     for (i = 0; i < ids.length; i++) { 
            if(document.getElementById(ids[i]).classList.contains('active')){
                document.getElementById(ids[i]).classList.remove("active");
                if(document.getElementById(id+ids[i]).style.display=='block'){
                        document.getElementById(id+ids[i]).style.display='none';
                }
            }
        }
    document.getElementById(check).classList.add("active");
    document.getElementById(id+check).style.display='block';
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
function sortAlb(spanId){
    var box=document.getElementById('box');
    var list=document.getElementById('list');
    if(box.classList.contains('active') && document.getElementById('box'+spanId)!='block'){
        change(spanId,'box');
    }else if(list.classList.contains('active') && document.getElementById('box'+spanId)!='block'){
        change(spanId,'list');
    }
}

function switching2(id1,id2){
    var td = document.getElementById(id1);
    if(!td.classList.contains('active')){
        td.classList.add("active");
        document.getElementById(id2).classList.remove("active");
        document.getElementById(id2+"0").style.display='none';
        document.getElementById(id1+"0").style.display='block';
    }
}

