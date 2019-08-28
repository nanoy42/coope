$(document).ready(function(){
    $(".update-stock").click(function(){
        var pk = $(this).attr('data-pk');
        var current_value = $(this).attr('data-stock');
        var ok = false;
        while(!ok){
            var new_stock = prompt("Nouveau stock ? (entier attendu)", current_value);
            ok = new_stock == null || !(isNaN(parseInt(new_stock)));
        }
        if(new_stock != null){
            $.get("/gestion/updateStock/" + pk, {"stock": new_stock}, function(data){
                $("#stock-"+pk).html(new_stock);
            });
        }
    });
});