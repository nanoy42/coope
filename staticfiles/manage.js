total = 0
products = []
menus = []
cotisations = []
reloads = []
paymentMethod = null
balance = 0
username = ""
id_user = 0
listPintes = []
nbPintes = 0;
use_pinte_monitoring = false;

function get_config(){
	res = $.get("../preferences/getConfig", function(data){
		use_pinte_monitoring = data.use_pinte_monitoring;
	});
}

function get_product(id){
	res = $.get("getProduct/" + id, function(data){
		nbPintes += data.nb_pintes;
		add_product(data.pk, data.name, data.amount, data.needQuantityButton);
	});
}

function get_menu(id){
	res = $.get("getMenu/" + id, function(data){
		nbPintes += data.nb_pintes;
		add_menu(data.pk, data.name, data.amount, data.needQuantityButton);
	});
}

function get_cotisation(id){
	res = $.get("../preferences/getCotisation/" + id, function(data){
		add_cotisation(data.pk, data.duration, data.amount);
	});
}

function add_product(pk, name, amount, needQuantityButton){
	exist = false
	index = -1;
	for(k=0;k < products.length; k++){
		if(products[k].pk == pk){
			exist = true
			index = k
		}
	}
	if(needQuantityButton){
		quantity = parseInt(window.prompt("Quantité ?",""));
	}else{
		quantity = 1;
	}
	if(quantity == null || !Number.isInteger(quantity)){
		quantity = 1;
	}
	if(exist){
		products[index].quantity += quantity;
	}else{
		products.push({"pk": pk, "name": name, "amount": amount, "quantity": quantity});
	}
	generate_html()
}

function add_menu(pk, name, amount){
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
		menus.push({"pk": pk, "name": name, "amount": amount, "quantity":1});
	}
	generate_html();
}

function add_cotisation(pk, duration, amount){
	exist = false;
	index = -1;
	for(k=0; k < cotisations.length; k++){
		if(cotisations[k].pk == pk){
			exist = true;
			index = k;
		}
	}
	if(exist){
		cotisations[index].quantity += 1;
	}else{
		cotisations.push({"pk": pk, "duration": duration, "amount": amount, "quantity":1});
	}
	generate_html();
}

function add_reload(value, payment_method, payment_method_name){
	exist = false;
	index = -1;
	for(k=0; k < reloads.length; k++){
		if(reloads[k].value == value && reloads[k].payment_method == payment_method){
			exist = true;
			index = k;
		}
	}
	if(exist){
		reloads[index].quantity += 1;
	}else{
		reloads.push({"value": value, "quantity": 1, "payment_method": payment_method, "payment_method_name": payment_method_name});
	}
	generate_html();
}

function generate_html(){
	html = "";
	for(k=0;k<cotisations.length;k++){
		cotisation = cotisations[k];
		html += '<tr><td></td><td>Cotisation ' + String(cotisation.duration) + ' jours</td><td>' + String(cotisation.amount) + ' €</td><td><input type="number" data-target="' + String(k) + '" onChange="updateCotisationInput(this)" value="' + String(cotisation.quantity) + '"/></td><td>' + String(Number((cotisation.quantity * cotisation.amount).toFixed(2))) + ' €</td></tr>';
	}
	for(k=0;k<reloads.length;k++){
		reload = reloads[k];
		html += '<tr><td>Rechargement ' + String(reload.payment_method_name) + " " + String(reload.value) + ' €</td><td>-' + String(reload.value) + ' €</td><td><input type="number" data-target="' + String(k) + '" onChange="updateReloadInput(this)" value="' + String(reload.quantity) + '"/></td><td>-' + String(Number((reload.quantity * reload.value).toFixed(2))) + ' €</td></tr>';
	}
	for(k=0;k<products.length;k++){
		product = products[k]
		html += '<tr><td>' + product.name + '</td><td>' + String(product.amount) + ' €</td><td><input type="number" data-target="' + String(k) + '" onChange="updateInput(this)" value="' + String(product.quantity) + '"/></td><td>' + String(Number((product.quantity * product.amount).toFixed(2))) + ' €</td></tr>';
	}
	for(k=0; k<menus.length;k++){
		menu = menus[k]
		html += '<tr><td>' + menu.name + '</td><td>' + String(menu.amount) + ' €</td><td><input type="number" data-target="' + String(k) + '" onChange="updateMenuInput(this)" value="' + String(menu.quantity) + '"/></td><td>' + String(Number((menu.quantity * menu.amount).toFixed(2))) + ' €</td></tr>';
	}
	$("#items").html(html);
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
	for(k=0; k<cotisations.length;k++){
		total += cotisations[k].quantity * cotisations[k].amount;
	}
	for(k=0; k<reloads.length;k++){
		total -= reloads[k].quantity * reloads[k].value;
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

function updateCotisationInput(a){
	quantity = parseInt(a.value);
	k = parseInt(a.getAttribute("data-target"));
	cotisations[k].quantity = quantity;
	generate_html();
}

function updateReloadInput(a){
	quantity = parseInt(a.value);
	k = parseInt(a.getAttribute("data-target"));
	reloads[k].quantity = quantity;
	generate_html();
}

$(document).ready(function(){
	$(".cotisation-hidden").hide();
	get_config();

	$(".product").click(function(){
		product = get_product($(this).attr('target'));
	});

	$(".menu").click(function(){
		menu = get_menu($(this).attr('target'));
	});

	$(".cotisation").click(function(){
		cotisation = get_cotisation($(this).attr('target'));
	});

	$(".reload").click(function(){
		add_reload(parseInt($(this).attr('target')), parseInt($(this).attr('data-payment')), $(this).attr('data-payment-name'));
	})

	$("#id_client").on('change', function(){
		id_user = $("#id_client").val();
		$.get("/users/getUser/" + id_user, function(data){
		balance = data.balance;
		username = data.username;
		is_adherent = data.is_adherent;
		$("#balance").html(balance + "€");
		if(!is_adherent){
			$(".cotisation-hidden").show();
		}
		updateTotal();
	}).fail(function(){
		alert("Une erreur inconnue est survenue");
		window.location.reload()
	});
	});

	$("#id_product").on('change', function(){
		product = get_product(parseInt($("#id_product").val()));		
	});

	$(".pay_button").click(function(){
		if(use_pinte_monitoring){
			message = "Il reste " + nbPintes.toString() + " pintes à renseigner. Numéro de la pinte ?"
			while(nbPintes > 0){
				id_pinte = window.prompt(message,"");
				if(id_pinte == null){
					return; 
				}else{
					id_pinte = parseInt(id_pinte);
					if(!Number.isInteger(id_pinte) || id_pinte < 0){
						message = "Numéro incorrect. Il reste " + nbPintes.toString() + " pintes à renseigner. Numéro de la pinte ?";
					}else{
						listPintes.push(id_pinte)
						nbPintes -= 1;
						message = "Il reste " + nbPintes.toString() + " pintes à renseigner. Numéro de la pinte ?"
					}
				}
			}
		}
		$.post("order", {"user":id_user, "paymentMethod": $(this).attr('data-payment'), "order_length": products.length + menus.length + cotisations.length + reloads.length, "order": JSON.stringify(products), "amount": total, "menus": JSON.stringify(menus), "listPintes": JSON.stringify(listPintes), "cotisations": JSON.stringify(cotisations), "reloads": JSON.stringify(reloads)}, function(data){
			if(data == "fame"){
				document.location.href="../wall-of-fame/"+id_user; 
			}else{
				alert(data);
				location.reload();
			}
		}).fail(function(data){
			alert("Impossible d'effectuer la transaction. Veuillez contacter le trésorier ou le président");
			console.log(data);
			location.reload();
		});
	});
});
