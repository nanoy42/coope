total = 0
products = []
paymentMethod = null
balance = 0
username = ""
id = 0

function get_product(barcode){
	res = $.get("getProduct/" + barcode, function(data){
		add_product(data.pk, data.barcode, data.name, data.amount);
	});
}

function add_product(pk, barcode, name, amount){
	exist = false
	index = -1
	for(k=0;k < products.length; k++){
		if(products[k].pk == pk){
			exist = true
			index = k
		}
	}
	if(exist){
		products[index].quantity += 1;
	}else{
		products.push({"pk": pk, "barcode": barcode, "name": name, "amount": amount, "quantity": 1});
	}
	generate_html()
}

function generate_html(){
	html =""
	for(k=0;k<products.length;k++){
		product = products[k]
		html += "<tr><td>" + product.barcode + "</td><td>" + product.name + "</td><td>" + String(product.amount) + "</td><td>" + String(product.quantity) + "</td><td>" + String(product.quantity * product.amount) + "</td></tr>"
	}
	$("#items").html(html)
	updateTotal()
}

function updateTotal(){
	total = 0
	for(k=0;k<products.length;k++){
		total += products[k].quantity * products[k].amount
	}
	$("#totalAmount").text(String(total) + "€")
	totalAfter = balance - total
	$("#totalAfter").text(totalAfter + "€")
}

$(document).ready(function(){
	$(".product").click(function(){
		product = get_product($(this).attr('target'));
	});
	$("#id_client").on('change', function(){
		id = $("#id_client").val();
		$.get("/users/getUser/" + id, function(data){
		balance = data.balance;
		username = data.username;
		$("#balance").html(balance + "€");
		updateTotal();
	}).fail(function(){
		alert("Une erreur inconnue est survenue");
		window.location.reload()
	});
	});
	$(".pay_button").click(function(){
		alert('Tentative de paiment avec le moyen ' + $(this).attr('data-payment'));
		console.log(products)
		$.post("order", {"user":id, "paymentMethod": $(this).attr('data-payment'), "order_length": products.length, "order": JSON.stringify(products), "amount": total}, function(data){
			alert(data);
			location.reload();
		}).fail(function(data){
			alert("Impossible d'effectuer la transaction");
			location.reload();
		});
	});
});
