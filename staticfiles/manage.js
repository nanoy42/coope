total = 0
products = []
menus = []
paymentMethod = null
balance = 0
username = ""
id = 0

function get_product(barcode){
	res = $.get("getProduct/" + barcode, function(data){
		add_product(data.pk, data.barcode, data.name, data.amount);
	});
}

function get_menu(barcode){
	res = $.get("getMenu/" + barcode, function(data){
		add_menu(data.pk, data.barcode, data.name, data.amount);
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

function add_menu(pk, barcode, name, amount){
	exist = false;
	index = -1;
	for(k=0; k < menus.length; k++){
		if(menus[k].pk == pk){
			exist = true;
			index = k;
		}
	}
	if(exist){
		menus[index].quantity += 1;
	}else{
		menus.push({"pk": pk, "barcode": barcode, "name": name, "amount": amount, "quantity":1});
	}
	generate_html();
}

function generate_html(){
	html =""
	for(k=0;k<products.length;k++){
		product = products[k]
		html += '<tr><td>' + product.barcode + '</td><td>' + product.name + '</td><td>' + String(product.amount) + '</td><td><input type="number" data-target="' + String(k) + '" onChange="updateInput(this)" value="' + String(product.quantity) + '"/></td><td>' + String(Number((product.quantity * product.amount).toFixed(2))) + '</td></tr>';
	}
	for(k=0; k<menus.length;k++){
		menu = menus[k]
		html += '<tr><td>' + menu.barcode + '</td><td>' + menu.name + '</td><td>' + String(menu.amount) + '</td><td><input type="number" data-target="' + String(k) + '" onChange="updateMenuInput(this)" value="' + String(menu.quantity) + '"/></td><td>' + String(Number((menu.quantity * menu.amount).toFixed(2))) + '</td></tr>';
	}
	$("#items").html(html)
	updateTotal();
}

function updateTotal(){
	total = 0
	for(k=0;k<products.length;k++){
		total += products[k].quantity * products[k].amount;
	}
	for(k=0; k<menus.length;k++){
		total += menus[k].quantity * menus[k].amount;
	}
	$("#totalAmount").text(String(Number(total.toFixed(2))) + "€")
	totalAfter = balance - total
	$("#totalAfter").text(String(Number(totalAfter.toFixed(2))) + "€")
}

function updateInput(a){
	quantity = parseInt(a.value)
	k = parseInt(a.getAttribute("data-target"))
	products[k].quantity = quantity
	generate_html()
}

function updateMenuInput(a){
	quantity = parseInt(a.value);
	k = parseInt(a.getAttribute("data-target"));
	menus[k].quantity = quantity;
	generate_html();
}

$(document).ready(function(){
	$(".product").click(function(){
		product = get_product($(this).attr('target'));
	});
	$(".menu").click(function(){
		menu = get_menu($(this).attr('target'));
	})
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
		$.post("order", {"user":id, "paymentMethod": $(this).attr('data-payment'), "order_length": products.length + menus.length, "order": JSON.stringify(products), "amount": total, "menus": JSON.stringify(menus)}, function(data){
			alert(data);
			location.reload();
		}).fail(function(data){
			alert("Impossible d'effectuer la transaction. Veuillez contacter le trésorier ou le président");
			location.reload();
		});
	});
});
