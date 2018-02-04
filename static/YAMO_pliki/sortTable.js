function sortTable(id,id2) {
  var table, rows, switching, i, x, y, shouldSwitch;
  table = document.getElementById("myTable");
  switching = true;
  /*Zrób pętle która będzie się wykonywać dopóki żadne przełożenie nie zostało zrobione */
  while (switching) {
    //zacznij poprzez powiedzenie że żadne przełożenie nie jest robione
    switching = false;
    rows = table.getElementsByTagName("TR");
    /*Przeiteruj przez każdy wiersz tabeli (oprócz pierwszej bo zawiera nagłówki tabeli) */
    for (i = 1; i < (rows.length - 1); i++) {
      //zacznij poprzez powiedzenie że nie powinno być żadnego przekładania
      shouldSwitch = false;
      /*Weź dwa elementy które chcesz porównać , jeden z akutalnego wierszu, drugi z kolejnego */
      var q=parseInt(id)
      x = rows[i].getElementsByTagName("TD")[q];
      y = rows[i + 1].getElementsByTagName("TD")[q];
      //sprawdź czy dwa wierze powinny zmienić miejsce
      if(id2=="1"){
        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
            //jeżeli tak, oznacz jako zamiane i wyjdź z pętli
            shouldSwitch= true;
            break;
        }
      }else if(id2=="2"){
            if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
            //jeżeli tak, oznacz jako zamiane i wyjdź z pętli
                shouldSwitch= true;
                break;
            }
      }
    }
    if (shouldSwitch) {
      /*Jeżeli zamiana została zaznaczona, zrób zamiane i oznacz że zamiana została zrobiona */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
    }
  }
}
