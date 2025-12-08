   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   * This dofile checks recipe information to be sure it makes sense i.e. recipes with more number of ingredients takes longer to cook
   *																	  *
   * - Inputs: "${recipes}/recipe_all_countries.dta"		      		  *
   * - Output:   										          		  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Angela Rojas
   ** EDITTED BY:       
   ** Last date modified: April 19, 2024

	* Remove duplicates
	duplicates drop nameoftherecipe country, force // Drop 12,529 observations
	
	* Drop recipes without a name
	drop if nameoftherecipe == "" // 5 recipes
	
	* Fix variable of number of ingredients 
	destring numberofingredients_raw, replace
	replace numberofingredients = numberofingredients_raw if numberofingredients == 0 
	replace numberofingredients = numberofingredients_raw if numberofingredients == 1 & inlist(country, "Chile", "Libya", "Peru")
	
	* Count ingredients for each recipe
	local len = length(",")
	gen n_ing = (length(listofingredients) - length(subinstr(listofingredients, ",", "", .))) / `len' 
	replace numberofingredients = n_ing + 1 if numberofingredients == 1 & inlist(country, "Jordan", "Latvia")
	drop n_ing
	drop if numberofingredients >= 47 & country == "Iraq" // The precode is counting wrong the ingredients, I drop 13 observations
	
	* Fix time variable  using prep time and cook time
	gen prep = preptime
	replace prep = "" if strpos(preptime,"P")>0 | strpos(preptime,"m")>0 | ///
	strpos(preptime,"M")>0 | strpos(preptime,"h")>0 | strpos(preptime,"R")>0
	destring prep , replace

	gen cook = cooktime
	replace cook = "" if strpos(cooktime,"P")>0 | strpos(cooktime,"m")>0 | ///
	strpos(cooktime,"M")>0 | strpos(cooktime,"h")>0 | strpos(cooktime,"R")>0 | ///
	strpos(cooktime,"H")>0 | strpos(cooktime,"~")>0
	destring cook , replace

	replace totaltime = prep + cook if totaltime == 0 | totaltime == .

	* Organize time variable
	replace totaltime = 4320 if cooktime == "~ 3-4 days"
	replace totaltime = 1440 if cooktime == "~ 1 day"
	replace totaltime = 255 if strpos(cooktime,"4 hrs 15")>0
	replace totaltime = 210 if strpos(cooktime,"3 1/2 h")>0 | strpos(cooktime,"3 hrs 30")>0
	replace totaltime = 180 if cooktime == "~ 3hrs"
	replace totaltime = 150 if cooktime == "PT2H30M" | strpos(cooktime,"2 hrs 30")>0 | strpos(cooktime,"2 hours 30")>0
	replace totaltime = 150 if strpos(cooktime,"2 hrs 15")>0
	replace totaltime = 120 if cooktime == "~ 2 hours" | cooktime == "~ 2hrs" | cooktime == "2 hours"
	replace totaltime = 105 if strpos(cooktime,"1 hr 45")>0
	replace totaltime = 100 if strpos(cooktime,"1 hr 40")>0
	replace totaltime = 90 if cooktime == "PT1H30M" | strpos(cooktime,"1 hr 30")>0
	replace totaltime = 80 if cooktime == "PT1H20M" | cooktime == "~ 1 hour 20 minutes"
	replace totaltime = 75 if strpos(cooktime,"1 hr 15")>0
	replace totaltime = 70 if strpos(cooktime,"1 hr 10")>0
	replace totaltime = 60 if cooktime == "~ 1 hour" | cooktime == "~ 1 hr" | cooktime == "1 hour"
	replace totaltime = 50 if preptime == "PT50M" & cooktime == "" 
	replace totaltime = 40 if preptime == "PT15M" & cooktime == "PT25M"
	replace totaltime = 40 if preptime == "PT60M" & cooktime == ""
	replace totaltime = 40 if preptime == "PT40M" & cooktime == "" 
	replace totaltime = 30 if preptime == "PT15M" & cooktime == "PT15M"
	replace totaltime = 30 if preptime == "PT30M" & cooktime == "" 
	replace totaltime = 20 if preptime == "PT20M" & cooktime == "" 
	replace totaltime = 10 if preptime == "PT10M" & cooktime == "" 
	
	* Drop recipes with zeros in number of ingredients
	drop if numberofingredients==0 // 546 observations deleted
	
	* Drop countries with more than 65% of its recipes without ingredient or time information.
	sort country
	bysort nameoftherecipe country: gen numrecipe = _n
	
	bysort country: egen welose1 = count(nameoftherecipe) if totaltime == 0 | totaltime ==.
	bysort country: egen welose2 = count(nameoftherecipe) if numberofingredients == 0
	bysort country: egen totalrecipe = total(numrecipe)
	egen welose = rowtotal(welose1 welose2)
	gen percent = (welose/totalrecipe)*100
	
	levelsof country if percent >= 65 & percent != ., local(country)
	foreach c of local country {
		drop if country == "`c'"
	}
	
	drop welose* percent totalrecipe
	
	* Drop recipes with zeros in time and number of ingredients
	drop if totaltime==0 | missing(totaltime) // 70 observations deleted
	
	* Argentina
	replace totaltime = 30 if nameoftherecipe == "Acelgas horneadas"
	replace totaltime = 45 if nameoftherecipe == "Aderezo de pollo"
	replace totaltime = 75 if nameoftherecipe == "Ají de gallina"
	replace totaltime = 60 if nameoftherecipe == "Arroz con leche y canela"
	replace totaltime = 80 if nameoftherecipe == "Alfajores de maicena"
	replace totaltime = 45 if nameoftherecipe == "Arroz con hongos en caldo"
	replace totaltime = 40 if nameoftherecipe == "Asado a la parrilla"
	replace totaltime = 30 if nameoftherecipe == "Arroz con calamares a la gran argentina"
	replace totaltime = 45 if nameoftherecipe == "Berenjenas rellenas"
	replace totaltime = 20 if nameoftherecipe == "Chimichurri"
	replace totaltime = 90 if nameoftherecipe == "Canelones de espinaca y ricotta"
	replace totaltime = 45 if nameoftherecipe == "Carne al horno con papas"
	replace totaltime = 50 if nameoftherecipe == "Cazuela argentina"
	replace totaltime = 60 if nameoftherecipe == "Empanadas cordobesas"
	replace totaltime = 60 if nameoftherecipe == "Empanadas salteñas"
	replace totaltime = 60 if nameoftherecipe == "Empanadas árabes"
	replace totaltime = 90 if nameoftherecipe == "Pastel de choclo y queso"
	replace totaltime = 75 if nameoftherecipe == "Canelones de verdura"
	replace totaltime = 80 if nameoftherecipe == "Canelones de espinaca y ricotta"

	
	* dealing with Kosovo outliers: totaltime 21605 27289001
	drop if country == "Kosovo" & totaltime == 21605
	drop if country == "Kosovo" & totaltime == 27289001
	
	* Check Mexico, Brazil and Bangladesh that are the ones with higher 	
	gsort country -totaltime
	replace totaltime = 120 if nameoftherecipe == "Kol de pavo de monte" & country == "Mexico"
	replace totaltime = 60 if nameoftherecipe == "Dulce de calabaza" & country == "Mexico"
	replace totaltime = 60 if nameoftherecipe == "Lengua en pebre" & country == "Mexico"
	replace totaltime = 120 if nameoftherecipe == "Pozole de trigo" & country == "Mexico"
	replace totaltime = 120 if nameoftherecipe == "Pan de cazón mexicano" & country == "Mexico"
	replace totaltime = 70 if nameoftherecipe == "Poc chuc" & country == "Mexico"
	replace totaltime = 140 if nameoftherecipe == "Caldo de gallina" & country == "Mexico"
	replace totaltime = 60 if nameoftherecipe == "Ceviche de atún" & country == "Mexico"
	replace totaltime = 50 if nameoftherecipe == "Cebadina" & country == "Mexico"
	replace totaltime = 120 if nameoftherecipe == "Jabalí alcaparrado" & country == "Mexico"
	replace totaltime = 80 if nameoftherecipe == "Conejo relleno al horno" & country == "Mexico"
	replace totaltime = 80 if nameoftherecipe == "Conejo relleno al horno" & country == "Mexico"
	replace totaltime = 120 if nameoftherecipe == "Chorizo de Campeche" & country == "Mexico"
	replace totaltime = 120 if nameoftherecipe == "Burritos de chile con carne" & country == "Mexico"
	replace totaltime = 40 if nameoftherecipe == "Ceviche de sierra" & country == "Mexico"
	replace totaltime = 90 if nameoftherecipe == "Alberjones con nopalitos" & country == "Mexico"
	replace totaltime = 35 if nameoftherecipe == "Arroz con leche" & country == "Mexico"
	replace totaltime = 20 if nameoftherecipe == "Atole de cajeta" & country == "Mexico"
	replace totaltime = 60 if nameoftherecipe == "Berenjenas capeadas" & country == "Mexico"
	replace totaltime = 50 if nameoftherecipe == "Budín" & country == "Mexico"
	replace totaltime = 60 if nameoftherecipe == "Caldillo en chile verde" & country == "Mexico"
	replace totaltime = 40 if nameoftherecipe == "Caldo de queso" & country == "Mexico"
	replace totaltime = 30 if nameoftherecipe == "Caldo de langostinos" & country == "Mexico"
	replace totaltime = 50 if nameoftherecipe == "Caldo tlalpeño" & country == "Mexico"
	replace totaltime = 30 if nameoftherecipe == "Camarones al mojo de ajo" & country == "Mexico"
	replace totaltime = 30 if nameoftherecipe == "Camarones en aguachile rojo" & country == "Mexico"
	replace totaltime = 60 if nameoftherecipe == "Cazuela" & country == "Mexico"
	replace totaltime = 20 if nameoftherecipe == "Cazón frito" & country == "Mexico"
	replace totaltime = 60 if nameoftherecipe == "Chilaquiles de rancho" & country == "Mexico"
	replace totaltime = 50 if nameoftherecipe == "Chul de frijol verde" & country == "Mexico"
	replace totaltime = 30 if nameoftherecipe == "Жент" & country == "Kazakhstan"
	replace totaltime = 30 if nameoftherecipe == "Валгаская булка" & country == "Estonia"
	replace totaltime = 100 if nameoftherecipe == "Мульгикапсад" & country == "Estonia"
	replace totaltime = 30 if nameoftherecipe == "How To Make "Trahana" (Crushed Wheat Soup)" & country == "Cyprus"
	replace totaltime = 240 if nameoftherecipe == "Orange Easter Bread (Tsoureki)" & country == "Cyprus"
	replace totaltime = 45 if nameoftherecipe == "Olive Bread (Eliopita)" & country == "Cyprus"
	replace totaltime = 180 if nameoftherecipe == "Savoury Meat Doughnuts (Koupes)" & country == "Cyprus"
/*	
	* Check Paraguay 
	replace totaltime = 90  if nameoftherecipe == "Mazamorra paraguaya"
	replace totaltime = 240 if nameoftherecipe == "Asado a la estaca"
	replace totaltime = 300 if nameoftherecipe == "Cabeza guateada"
	replace totaltime = 40  if nameoftherecipe == "Ensalada de porotos rojos"
	replace totaltime = 75  if nameoftherecipe == "Caldo de chipa de maíz"
	replace totaltime = 180 if nameoftherecipe == "Pato al horno"
	replace totaltime = 150 if nameoftherecipe == "Estofado trinchado"
	replace totaltime = 130 if nameoftherecipe == "Cazuela de ternera"
	replace totaltime = 20  if nameoftherecipe == "Crema de leche"
	replace totaltime = 90  if nameoftherecipe == "Chicharrón huití"
	replace totaltime = 60  if nameoftherecipe == "Caldo de pollo"
	replace totaltime = 50  if nameoftherecipe == "Caldo de mandi'i"
	replace totaltime = 90  if nameoftherecipe == "Tallarines con salsa de carne"
	replace totaltime = 30  if nameoftherecipe == "Choripan"
	replace totaltime = 100 if nameoftherecipe == "Caldo de gallina con maní"
	replace totaltime = 90  if nameoftherecipe == "Jukysy"
	replace totaltime = 150 if nameoftherecipe == "Dulce de leche con miel"
	replace totaltime = 90  if nameoftherecipe == "Ñoquis de papa con salsa boloñesa"
	replace totaltime = 180 if nameoftherecipe == "Ubre de vaca"
	replace totaltime = 90  if nameoftherecipe == "Chupín de pescado"
	replace totaltime = 90  if nameoftherecipe == "Caldo de arroz con carne"
	replace totaltime = 60  if nameoftherecipe == "El kivevé de calabaza"
	replace totaltime = 240 if nameoftherecipe == "Lechoncito asado"
	replace totaltime = 45  if nameoftherecipe == "Sopa de hojas de tayao"
	replace totaltime = 90  if nameoftherecipe == "Arroz con pollo"
	replace totaltime = 180 if nameoftherecipe == "Pan dulce"
	replace totaltime = 60  if nameoftherecipe == "Vorí blanco"
	replace totaltime = 150 if nameoftherecipe == "Pastel mandi'o"
	replace totaltime = 90  if nameoftherecipe == "Chinchulines tiernizados a la parrilla"
	replace totaltime = 60  if nameoftherecipe == "Pechugas de pollo"
	replace totaltime = 150 if nameoftherecipe == "Gallina asada"
	replace totaltime = 90  if nameoftherecipe == "Picadito de carne"
	replace totaltime = 180 if nameoftherecipe == "Arrollado de matambre"
	replace totaltime = 90  if nameoftherecipe == "Guiso de porotos"
	replace totaltime = 120 if nameoftherecipe == "Humita en olla"
	replace totaltime = 60  if nameoftherecipe == "Guiso de fideo"
	replace totaltime = 150 if nameoftherecipe == "Puchero paraguayo"
	replace totaltime = 90  if nameoftherecipe == "Batiburrillo"
	replace totaltime = 90  if nameoftherecipe == "Albóndigas de carne con arroz"
	replace totaltime = 90  if nameoftherecipe == "Budín de pan"
	replace totaltime = 180 if nameoftherecipe == "Torta de miel negra"
	replace totaltime = 60  if nameoftherecipe == "Arroz con leche"
	replace totaltime = 90  if nameoftherecipe == "Asado a la olla"
	replace totaltime = 150 if nameoftherecipe == "Estofado de cabra"
	replace totaltime = 90  if nameoftherecipe == "Chastaca"
	replace totaltime = 90  if nameoftherecipe == "Dulce de guayaba"
	replace totaltime = 60  if nameoftherecipe == "Sopa de zapallo cremosa"
	replace totaltime = 150 if nameoftherecipe == "Asado de carne de chancho"
	replace totaltime = 90  if nameoftherecipe == "Longanizas asadas"
	replace totaltime = 60  if nameoftherecipe == "Caldo de choclos"
	replace totaltime = 120 if nameoftherecipe == "Yopará"
	replace totaltime = 90  if nameoftherecipe == "Chorizo misionero"
	replace totaltime = 90  if nameoftherecipe == "Caldo de porotos con queso"
	replace totaltime = 60  if nameoftherecipe == "Filetes de salmón"
	replace totaltime = 90  if nameoftherecipe == "Vorí vorí de carne"
	replace totaltime = 15  if nameoftherecipe == "Sandwich de empanada"
	replace totaltime = 60  if nameoftherecipe == "Leche asada"
	replace totaltime = 90  if nameoftherecipe == "Bifes de hígado"
	replace totaltime = 60  if nameoftherecipe == "Caldo de surubí"
	replace totaltime = 150 if nameoftherecipe == "Carbonada"
	replace totaltime = 90  if nameoftherecipe == "Arroz con chorizos"
	replace totaltime = 120 if nameoftherecipe == "Butifarra"
replace totaltime = 150 if nameoftherecipe == "Bollos con crema"
replace totaltime = 90  if nameoftherecipe == "Estofado la novia"
replace totaltime = 60  if nameoftherecipe == "Lampreado de harina"
replace totaltime = 90  if nameoftherecipe == "Mousse de maracuyá"
replace totaltime = 60  if nameoftherecipe == "Puretón"
replace totaltime = 90  if nameoftherecipe == "Guiso de mondongo con arvejas"
replace totaltime = 90  if nameoftherecipe == "Guiso de lentejas y arroz"
replace totaltime = 60  if nameoftherecipe == "Vorí sati"
replace totaltime = 90  if nameoftherecipe == "Locro de pata"
replace totaltime = 60  if nameoftherecipe == "Pira caldo"
replace totaltime = 60  if nameoftherecipe == "Sopa de cebolla"
replace totaltime = 60  if nameoftherecipe == "Pollo saltado"
replace totaltime = 90  if nameoftherecipe == "Vorí vorí paraguayo"
replace totaltime = 90  if nameoftherecipe == "Costilla de cerdo frito"
replace totaltime = 90  if nameoftherecipe == "Chicharón trenzado"
replace totaltime = 240 if nameoftherecipe == "Asado"
replace totaltime = 60  if nameoftherecipe == "Soyo"
replace totaltime = 90  if nameoftherecipe == "Enrollado de cerdo"
replace totaltime = 60  if nameoftherecipe == "Chorizo parrillero picante"
replace totaltime = 90  if nameoftherecipe == "Chipa"
replace totaltime = 30  if nameoftherecipe == "Ensalada paraguaya de mandioca"
replace totaltime = 60  if nameoftherecipe == "Empanadas de mandioca"
replace totaltime = 90  if nameoftherecipe == "Mantecados"
replace totaltime = 60  if nameoftherecipe == "Empanadas de jamón y queso"
replace totaltime = 45  if nameoftherecipe == "Sopa de ajo"
replace totaltime = 90  if nameoftherecipe == "Vori vori karaí"
replace totaltime = 120 if nameoftherecipe == "Morcilla con arroz"
replace totaltime = 90  if nameoftherecipe == "Dulce de batata"
replace totaltime = 90  if nameoftherecipe == "Papas gratinadas"
replace totaltime = 60  if nameoftherecipe == "Sopa de verduras"
replace totaltime = 60  if nameoftherecipe == "Caldo de gallina"
replace totaltime = 45  if nameoftherecipe == "Sopa de tomates"
replace totaltime = 30  if nameoftherecipe == "Ensalada de arroz"
replace totaltime = 30  if nameoftherecipe == "Ensalada paraguaya"
replace totaltime = 30  if nameoftherecipe == "Sopa paraguaya"
replace totaltime = 30  if nameoftherecipe == "Ensalada de porotos"
replace totaltime = 90  if nameoftherecipe == "Piracaldo"
replace totaltime = 45  if nameoftherecipe == "Snack de pollo"
replace totaltime = 30  if nameoftherecipe == "Mandioca frita"
replace totaltime = 90  if nameoftherecipe == "Mbeju relleno de jamón y queso"
replace totaltime = 90  if nameoftherecipe == "Fugazza paraguaya"
replace totaltime = 30  if nameoftherecipe == "Ensalada mixta"
replace totaltime = 120 if nameoftherecipe == "Churros caseros"
replace totaltime = 30  if nameoftherecipe == "Ensalada fresca"
replace totaltime = 90  if nameoftherecipe == "Torta manduvi"
replace totaltime = 90  if nameoftherecipe == "Flandín"
replace totaltime = 120 if nameoftherecipe == "Chicharrón trenzado y enharinado"
replace totaltime = 30  if nameoftherecipe == "Tortilla paraguaya"
replace totaltime = 90  if nameoftherecipe == "Alfajores"
replace totaltime = 120 if nameoftherecipe == "Pizza con borde relleno"
replace totaltime = 45  if nameoftherecipe == "Mbeyu"
replace totaltime = 30  if nameoftherecipe == "Crema de leche y maizena"
replace totaltime = 120 if nameoftherecipe == "Payagua mascada"
replace totaltime = 45  if nameoftherecipe == "Ensalada rusa"
replace totaltime = 15  if nameoftherecipe == "Mate dulce"
replace totaltime = 15  if nameoftherecipe == "Chororqui"
replace totaltime = 30  if nameoftherecipe == "Ensalada de papa"
replace totaltime = 120 if nameoftherecipe == "Paguayá mascada"
replace totaltime = 90  if nameoftherecipe == "Berlinesas"
replace totaltime = 60  if nameoftherecipe == "Caldo de choclo"
replace totaltime = 30  if nameoftherecipe == "Cocido quemado"
replace totaltime = 90  if nameoftherecipe == "Dulce de piña"
replace totaltime = 120 if nameoftherecipe == "Torta de ricota"
replace totaltime = 30  if nameoftherecipe == "Tortilla de papas"
replace totaltime = 30  if nameoftherecipe == "Chipa so'o"
replace totaltime = 120 if nameoftherecipe == "Panettone"

	* Check Argentina
replace totaltime = 240 if nameoftherecipe == "Corderito patagónico a la parrilla"
replace totaltime = 240 if nameoftherecipe == "Cordero asado al estilo patagonico"
replace totaltime = 240 if nameoftherecipe == "Pierna de cordero patagónico con marmelada de cebollas"
replace totaltime = 240 if nameoftherecipe == "Costillar  de cordero a la salvia"

replace totaltime = 150 if inlist(nameoftherecipe,"Carbonada","Locro riojano","Locro de gallina","Puchero argentino","Sancocho argentino","Matambre")
replace totaltime = 120 if inlist(nameoftherecipe,"Pastafrola","Facturas","Medialunas","Pan casero argentino","Pizza a la piedra","Fugazza argentina","Pastel de choclo y queso","Pastel de papas","Arrollado de pollo")
replace totaltime = 120 if inlist(nameoftherecipe,"Arrollado de carne","Empanadas tucumanas","Empanadas salteñas","Empanadas cordobesas","Empanadas árabes","Empanadas mendocinas","Tarta balcarce","Tarta de brócoli")

replace totaltime = 90 if inlist(nameoftherecipe,"Budín de pan","Budín de remolacha","Alfajores de maicena","Alfajores argentinos")

replace totaltime = 45 if inlist(nameoftherecipe,"Gazpacho","Sopa de calabaza y zanahoria","Sopa hipertérmica de chorizo colorado")

replace totaltime = 60 if inlist(nameoftherecipe,"Bebida ruda y caña","Chicha de maíz argentina","Clericó argentino","Limoncello","Licor de dulce de leche argentino","Licor de calafate","Hesperidina","Vino artesanal patero")

replace totaltime = 180 if nameoftherecipe == "Payagua mascada"
replace totaltime = 120 if nameoftherecipe == "Sopa buenos aires"
replace totaltime = 120 if nameoftherecipe == "Guiso carrero"
replace totaltime = 120 if nameoftherecipe == "Asado criollo simple"
replace totaltime = 120 if nameoftherecipe == "Costeleta de vaca con salsa criolla y maíz fresco"
replace totaltime = 120 if nameoftherecipe == "Cordero con oporto"
replace totaltime = 90  if nameoftherecipe == "Bizcocho económico con yogurt"
replace totaltime = 90  if nameoftherecipe == "Pastel de manzana"
replace totaltime = 90  if nameoftherecipe == "Arrollado de carne a la cerveza"
replace totaltime = 90  if nameoftherecipe == "Pizza de mandioca"
replace totaltime = 90  if nameoftherecipe == "Sorrentinos caseros de ricota, jamón y mozzarella"
replace totaltime = 90  if nameoftherecipe == "Tarta de acelgas"
replace totaltime = 90  if nameoftherecipe == "Crema de calabaza"
replace totaltime = 90  if nameoftherecipe == "Sopa de pollo con fideos"
replace totaltime = 90  if nameoftherecipe == "Ñoquis de mandioca"
replace totaltime = 90  if nameoftherecipe == "Alfajor tradicional"
replace totaltime = 90  if nameoftherecipe == "Alfajor de turrón salteño"
replace totaltime = 90  if nameoftherecipe == "Varéniqui de mandioca"
replace totaltime = 90  if nameoftherecipe == "Postre rosario"
replace totaltime = 90  if nameoftherecipe == "Ceviche de camarón"
replace totaltime = 90  if nameoftherecipe == "Bondiola de cerdo al yatay"
replace totaltime = 90  if nameoftherecipe == "Kiveve"
replace totaltime = 90  if nameoftherecipe == "Conejo en escabeche"
replace totaltime = 90  if nameoftherecipe == "Alitas de pollo a la cai"

	* Check Bolivia
replace totaltime = 60 if inlist(nameoftherecipe, "Guarapo boliviano", "Aloja de cebada", "Api", "Chicha de uva", "Aloja de maní")
replace totaltime = 45 if nameoftherecipe == "Api morado"
replace totaltime = 45 if nameoftherecipe == "Hervido de Linaza Boliviano"
replace totaltime = 60 if nameoftherecipe == "Chicha Morada"
replace totaltime = 60 if nameoftherecipe == "Chicha de piña"
replace totaltime = 60 if nameoftherecipe == "Tojorí, receta paceña"
replace totaltime = 60 if nameoftherecipe == "Tejti o chicha de maní"
replace totaltime = 60 if nameoftherecipe == "Chicha de maní"
replace totaltime = 60 if inlist(nameoftherecipe, "Cookies de quinoa y chocolate", "Barritas de quinoa y chocolate", "Budin de Quinua", "Budin de Manzanas", "Budin de Platanos", "Budín de coco", "Pastel de quinoa y chocolate")
replace totaltime = 60 if inlist(nameoftherecipe, "Flan de quinoa", "Flan de leche", "Natilla con nueces", "Tablillas de Leche con Canela")
replace totaltime = 60 if inlist(nameoftherecipe, "Cupcakes de miel de caña", "Bollitos integrales", "Rosca de Reyes", "Rosca de navidad")
replace totaltime = 90 if nameoftherecipe == "Dulce de Membrillo"
replace totaltime = 90 if nameoftherecipe == "Mermelada de Manzanas"
replace totaltime = 90 if nameoftherecipe == "Dulce de cayote"
replace totaltime = 120 if inlist(nameoftherecipe, "Salteñas de Pollo", "Salteñas", "Salteña Potosina", "Salteñas bolivianas")
replace totaltime = 90  if inlist(nameoftherecipe, "Empanada chuquisaqueña", "Empanadas cruceñas", "Empanadas Tucumanas", "Empanadas fritas de pollo", "Empanada frita de pollo", "Empanada frita de queso")
replace totaltime = 90  if nameoftherecipe == "Pukacapas tradicionales"
replace totaltime = 90 if inlist(nameoftherecipe, "Sopa de maní boliviana", "Sopa de maní tarijeña")
replace totaltime = 90 if inlist(nameoftherecipe, "Sopa de quinua", "Sopa de quinoa y verduras", "Sopa de quinoa al maiz", "Sopa de quinua con carne")
replace totaltime = 60 if inlist(nameoftherecipe, "Sopa de tomates", "Sopa de palmito", "Sopa de albóndigas de maíz", "Sopa de papalisa", "Sopa de pirañas")
replace totaltime = 60 if inlist(nameoftherecipe, "Chairo Paceño", "Sopa de verduras en pan", "Sopa de quinua y verduras")
replace totaltime = 45 if nameoftherecipe == "Caldo de papas y huevos"
replace totaltime = 120 if inlist(nameoftherecipe, "Lechón al horno", "Pierna de Chancho al Horno", "Pato al Horno", "Asado de Cordero a la Olla", "Brazuelo de cordero tradicional")
replace totaltime = 30 if inlist(nameoftherecipe, "Soltero", "Solteron", "P'huti de chuño", "Chuño Phuti")
replace totaltime = 30 if inlist(nameoftherecipe, "Corazones blancos", "Caramelos de miel", "Frituras de quinua")
replace totaltime = 150 if nameoftherecipe == "Picana de navidad"
replace totaltime = 150 if nameoftherecipe == "Picana Chuquisaqueña"
replace totaltime = 150 if nameoftherecipe == "Mondongo chuquisaqueño tradicional"
replace totaltime = 150 if nameoftherecipe == "Tamales Tarijeños"
replace totaltime = 180 if nameoftherecipe == "Picana"
replace totaltime = 90 if nameoftherecipe == "Humintas al horno"
replace totaltime = 60 if nameoftherecipe == "Chorizos Chuquisaqueños"
replace totaltime = 40 if nameoftherecipe == "Sandwichs de chola"
replace totaltime = 75 if nameoftherecipe == "Queque marmoleado"
replace totaltime = 80 if nameoftherecipe == "Budin de Pan"
replace totaltime = 70 if nameoftherecipe == "Sopa de papapica"
replace totaltime = 90 if nameoftherecipe == "Surubí al horno"
replace totaltime = 70 if nameoftherecipe == "Llauchas"
replace totaltime = 120 if nameoftherecipe == "Mermelada de Frutillas"
replace totaltime = 180 if nameoftherecipe == "Mondongo chuquisaqueño"
replace totaltime = 45 if nameoftherecipe == "Ceviche de Pejerrey"
replace totaltime = 70 if nameoftherecipe == "Budín de cacao"
replace totaltime = 150 if nameoftherecipe == "Tamales Tupiceños"
replace totaltime = 80 if nameoftherecipe == "Rosquetas tarijeñas"
replace totaltime = 50 if nameoftherecipe == "Helado de canela, estilo criollo"
replace totaltime = 150 if nameoftherecipe == "Tamales"
replace totaltime = 45 if nameoftherecipe == "Cuñapes"
replace totaltime = 180 if nameoftherecipe == "Patasca portachueleña"
replace totaltime = 75 if nameoftherecipe == "Aji de Fideos"
replace totaltime = 90 if nameoftherecipe == "Sopa boliviana"
replace totaltime = 150 if nameoftherecipe == "Sopa de quinua en tres tiempos"
replace totaltime = 120 if nameoftherecipe == "Ch'ajchu potosino"
replace totaltime = 70 if nameoftherecipe == "El intendente"
replace totaltime = 120 if nameoftherecipe == "Sopa de maní"
replace totaltime = 90 if nameoftherecipe == "Pastelitos de yuca"
replace totaltime = 150 if nameoftherecipe == "Lasaña boliviana"
replace totaltime = 100 if nameoftherecipe == "Pastel de quinua con espinaca"
replace totaltime = 80 if nameoftherecipe == "Albóndigas de carne al horno"
replace totaltime = 70 if nameoftherecipe == "Pukacapas"
replace totaltime = 60 if nameoftherecipe == "Salpicon de Pollo"
replace totaltime = 80 if nameoftherecipe == "Empanadas tipo pucacapas"
replace totaltime = 90 if nameoftherecipe == "Sajta de pollo tradicional"
replace totaltime = 45 if nameoftherecipe == "Barras de cereal"
replace totaltime = 90 if nameoftherecipe == "Empanadas de carne picada"
replace totaltime = 60 if nameoftherecipe == "Somó"
replace totaltime = 120 if nameoftherecipe == "Sopa Chuquisaqueña"
replace totaltime = 90 if nameoftherecipe == "Buñuelos"
replace totaltime = 90 if nameoftherecipe == "Chairo de Tunta"
replace totaltime = 120 if nameoftherecipe == "Majao"
replace totaltime = 120 if nameoftherecipe == "Asadito camba"
replace totaltime = 45 if nameoftherecipe == "Bombones de corte"
replace totaltime = 70 if nameoftherecipe == "Empanadas de Hojaldre"
replace totaltime = 45 if nameoftherecipe == "Cocadas"
replace totaltime = 60 if nameoftherecipe == "Empanadas de Queso para Api"
replace totaltime = 120 if nameoftherecipe == "Silpancho Cochabambino"
replace totaltime = 60 if nameoftherecipe == "Chinchulines"
replace totaltime = 80 if nameoftherecipe == "Queque de almendras"
replace totaltime = 90 if nameoftherecipe == "Pan de cebolla y amapolas"
replace totaltime = 120 if nameoftherecipe == "Racacha con chuletas asadas de chancho"
replace totaltime = 90 if nameoftherecipe == "Sopa de leche con maní"
replace totaltime = 70 if nameoftherecipe == "Rollo de Queso"
replace totaltime = 75 if nameoftherecipe == "Bizcochuelo"
replace totaltime = 90 if nameoftherecipe == "Cucuruchos Rellenos"
replace totaltime = 70 if nameoftherecipe == "Fartonns de queso"
replace totaltime = 90 if nameoftherecipe == "Alfajores de arequipe y coco"
replace totaltime = 90 if nameoftherecipe == "Tantawawas"
replace totaltime = 120 if nameoftherecipe == "Majao de Pato"
replace totaltime = 20 if nameoftherecipe == "Copas de banano"
replace totaltime = 75 if nameoftherecipe == "Ají de fideo"
replace totaltime = 180 if nameoftherecipe == "Brazuelo de Cordero"
replace totaltime = 70 if nameoftherecipe == "Sopaipillas"
replace totaltime = 150 if nameoftherecipe == "Aji de Conejo"
replace totaltime = 180 if nameoftherecipe == "Enrollado de Chancho"
replace totaltime = 90 if nameoftherecipe == "Pan de maiz oriental"
replace totaltime = 150 if nameoftherecipe == "Chorizo chuquisaqueño, preparación completa"
replace totaltime = 80 if nameoftherecipe == "Sopa de hojas de trigo"
replace totaltime = 90 if nameoftherecipe == "Humintas de Quinua"
replace totaltime = 150 if nameoftherecipe == "Kalapurka"
replace totaltime = 80 if nameoftherecipe == "Trucha a la crema"
replace totaltime = 75 if nameoftherecipe == "Pastel de choclo"
replace totaltime = 180 if nameoftherecipe == "Puchero de Carnaval"
replace totaltime = 120 if nameoftherecipe == "Locro de semilla de maíz"
replace totaltime = 60 if nameoftherecipe == "Hojarascas"
replace totaltime = 80 if nameoftherecipe == "Aji de Platano"
replace totaltime = 60 if nameoftherecipe == "Causa"
replace totaltime = 120 if nameoftherecipe == "Plato Paceño"
replace totaltime = 90 if nameoftherecipe == "Pimientos rellenos con quinua"
replace totaltime = 75 if nameoftherecipe == "Jarwi uchu"
replace totaltime = 60 if nameoftherecipe == "Tomates Rellenos"
replace totaltime = 80 if nameoftherecipe == "Aji de Chuño"
replace totaltime = 45 if nameoftherecipe == "Pejerrey frito"
replace totaltime = 120 if nameoftherecipe == "Sopa de Invierno"
replace totaltime = 150 if nameoftherecipe == "Pique a lo macho"
replace totaltime = 75 if nameoftherecipe == "Jaka lawa"
replace totaltime = 100 if nameoftherecipe == "Pipián de pollo"
replace totaltime = 60 if nameoftherecipe == "Bocaditos de Choclo"
replace totaltime = 120 if nameoftherecipe == "Sajta de gallina"
replace totaltime = 150 if nameoftherecipe == "Sopa de verduras"
replace totaltime = 150 if nameoftherecipe == "Fritanga chuquisaqueña"
replace totaltime = 80 if nameoftherecipe == "Crema de Espinacas"
replace totaltime = 180 if nameoftherecipe == "K'arapecho"
replace totaltime = 80 if nameoftherecipe == "Masaco de plátano"
replace totaltime = 90 if nameoftherecipe == "Teqo"
replace totaltime = 75 if nameoftherecipe == "Suflé de quinoa"
replace totaltime = 70 if nameoftherecipe == "Pectu de Habas"
replace totaltime = 90 if nameoftherecipe == "Sopa de papa lisa"
replace totaltime = 45 if nameoftherecipe == "Bocaditos de queso"
replace totaltime = 80 if nameoftherecipe == "Locotos crocantes rellenos"
replace totaltime = 90 if nameoftherecipe == "Chaque de Quinua"
replace totaltime = 120 if nameoftherecipe == "Mermelada de Durazno"
replace totaltime = 70 if nameoftherecipe == "Anticucho"
replace totaltime = 180 if nameoftherecipe == "Fricasé de cerdo, estilo paceño"
replace totaltime = 100 if nameoftherecipe == "Rape con quinoa y algas"
replace totaltime = 150 if nameoftherecipe == "Pan integral de sésamo"
replace totaltime = 45 if nameoftherecipe == "Galletas sin sal"
replace totaltime = 70 if nameoftherecipe == "Mazamorra de quinua"
replace totaltime = 80 if nameoftherecipe == "Alfajor de maicena"
replace totaltime = 60 if nameoftherecipe == "Dulces de avena"
replace totaltime = 90 if nameoftherecipe == "Melcochas bolivianas"
replace totaltime = 180 if nameoftherecipe == "Thimpu"
replace totaltime = 150 if nameoftherecipe == "Chupe de camarones"
replace totaltime = 180 if nameoftherecipe == "Picana Cochabambina"
replace totaltime = 180 if nameoftherecipe == "Keperi boliviano"
replace totaltime = 70 if nameoftherecipe == "Budín de atún"
replace totaltime = 90 if nameoftherecipe == "Ajíes rellenos"
replace totaltime = 120 if nameoftherecipe == "Montañitas de yuca"
replace totaltime = 60 if nameoftherecipe == "Cauquitas como galletas"
replace totaltime = 150 if nameoftherecipe == "Chairo paceño tradicional"
replace totaltime = 80 if nameoftherecipe == "Salpicon de Carne"
replace totaltime = 120 if nameoftherecipe == "Ch'aqi de trigo"
replace totaltime = 90 if nameoftherecipe == "Escabeche de pescado"
replace totaltime = 180 if nameoftherecipe == "Brazuelo"
replace totaltime = 70 if nameoftherecipe == "Queso umacha"
replace totaltime = 120 if nameoftherecipe == "Moldeado de atún y berenjena"
replace totaltime = 60 if nameoftherecipe == "Pipocas de pollo"
replace totaltime = 120 if nameoftherecipe == "Aguadito de casa"
replace totaltime = 70 if nameoftherecipe == "Queque fácil"
replace totaltime = 80 if nameoftherecipe == "Arepitas andinas"
replace totaltime = 90 if nameoftherecipe == "Pastel de quinoa"
replace totaltime = 75 if nameoftherecipe == "Manjar Blanco"
replace totaltime = 70 if nameoftherecipe == "Tawa-Tawas"
replace totaltime = 120 if nameoftherecipe == "Pan Casero"
replace totaltime = 60 if nameoftherecipe == "Manzanas golosas"
replace totaltime = 90 if nameoftherecipe == "Budin de Naranja"
replace totaltime = 60 if nameoftherecipe == "Mocochinchi camba"
replace totaltime = 75 if nameoftherecipe == "Mazamorra de Quinua con Manzanas"
replace totaltime = 50 if nameoftherecipe == "Paletas coloridas"
replace totaltime = 180 if nameoftherecipe == "Keperi"
replace totaltime = 120 if nameoftherecipe == "Majadito de pollo"
replace totaltime = 150 if nameoftherecipe == "Canasta de pasta filo rellena de pollo en salsa de curry"
replace totaltime = 90 if nameoftherecipe == "Pastel de quinua"
replace totaltime = 90 if nameoftherecipe == "Pastel de choclo al ají"
replace totaltime = 90 if nameoftherecipe == "Pesque de Quinua"
replace totaltime = 70 if nameoftherecipe == "Chascas"
replace totaltime = 90 if nameoftherecipe == "Empanadas de quinua con albahaca"
replace totaltime = 75 if nameoftherecipe == "Pan o roscas de canela"
*/
sum totaltime if country == "Bolivia", de
	
// 	br if country == "Colombia"
//	
// 	keep if country == "Brazil" | country == "Chile" | country == "Colombia" | country == "Cuba" | ///
//          country == "Ecuador" | country == "Uruguay" | country == "Peru" | country == "Argentina" | ///
//          country == "Costa Rica" | country == "Guatemala" | country == "Honduras" | country == "Nicaragua" | ///
//          country == "Panama" | country == "Paraguay" | country == "El Salvador" | country == "Venezuela" | country == "Bolivia" 

/*
	preserve
	use "$versatility/first_stage_dataset_native_m_c.dta", clear
	keep country continent*
	duplicates drop
	tempfile adm0
	save `adm0'
	restore
	
	merge m:1 country using `adm0'
	tabstat totaltime if continent_name == "South America" | continent_name == "North America", by(country) stats(n mean median sd min max)
*/

	*br totaltime numberofingredients numberofspices country if inlist(country, "Cyprus", "Estonia", "Kazakhstan", "Malaysia", "Paraguay")

	** drop recipes that the total time are higher than 99%
	bys country: egen p99 = pctile(totaltime), p(99)
	drop if totaltime > p99
	note: `r(N_drop)' recipes are dropped because of higher than 99%.