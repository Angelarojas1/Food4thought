   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *        This dofile merges recipe, region, country dataset      	  *
   *
   * Input: https://github.com/rubenmilla/Crop_Origins_Phylo?tab=readme-ov-file
   * ******************************************************************** *
	clear 
	
   *- Import dataset
	import delimited using "${rawdata}\Crop_Origins_Phylo-master\Crop_Origins_Phylo_v_live\crop_origins_v_live\crop_origins_live_db.csv", clear
	
	*- Explore duplicates in dataset
	duplicates report common_name_crop
	
	duplicates tag common_name_crop, gen(dup_tag)
	tab dup_tag
	
	tab common_name_crop if dup_tag > 0
	
	*br if dup_tag == 1
	
	*- Drop observations without information
	
	drop if common_name_crop == "na"
	drop if mode_ecoreg_code == "NA"
	
	*- Keep variables of interest
	
	rename (common_name_crop mode_ecoreg_name mode_ecoreg_centroid_lat mode_ecoreg_centroid_lon  mode_ecoreg_code) ///
	(ingredient ecoreg_name lat lon eco_code)
	replace ingredient = lower(ingredient)
	replace ingredient = subinstr(ingredient, "_", " ", .)
	keep ingredient ecoreg_name lat lon eco_code biogeografic_realm sd_longitude sd_latitude
	order ingredient ingredient ecoreg_name lat lon 
	
	* Rename ingredients so they match suitability dataset
	gsort ingredient
	replace ingredient = "alfalfa" if ingredient == "alfalfa for fodder"
	replace ingredient = "almonds" if ingredient == "almond" | ingredient == "country almond"
	replace ingredient = "anise" if ingredient == "anise seeds" | ingredient == "star anise"
	replace ingredient = "annatto" if ingredient == "annato"
	replace ingredient = "apples" if ingredient == "apple" | ingredient == "asiatic apple" | ingredient == "cainito star apple" | ingredient == "chinese apple" | ingredient == "malay apple" | ingredient == "velvet apple" | ingredient == "wax apple" | ingredient == "wood apple" | ingredient == "african star apple"
	replace ingredient = "apricots" if ingredient == "apricot" | ingredient == "apricot plum" | ingredient == "japanese apricot"
	replace ingredient = "artichokes" if ingredient == "jerusalem artichoke" | ingredient == "chinese artichoke"
	replace ingredient = "avocados" if ingredient == "avocado"
	replace ingredient = "banana" if ingredient == "enset abyssinian banana"	
	replace ingredient = "beans" if ingredient == "african locust bean"	| ingredient == "bean dry edible" | ingredient == "bitter bean"| ingredient == "butter bean lima bean" | ingredient == "hyacinth bean" | ingredient == "ice cream bean" | ingredient == "jack bean" | ingredient == "mat bean" | ingredient == "mung bean" | ingredient == "narbon bean" | ingredient == "oblique seed jackbean" | ingredient == "ricebean" | ingredient == "runner bean" | ingredient == "sword bean" | ingredient == "tepary bean" | ingredient == "tonka beans" | ingredient == "year long bean" | ingredient == "adzuki bean"
	replace ingredient = "blueberries" if ingredient == "blueberry"
	replace ingredient = "cabbages" if ingredient == "ethiopian cabbage" | ingredient == "cabbage"
	replace ingredient = "cardamom" if ingredient == "cambodian cardamom"	
	replace ingredient = "carrots" if ingredient == "carrot"
	replace ingredient = "cherries" if ingredient == "cereza" | ingredient == "cherry plum" | ingredient == "ground cherry" | ingredient == "ground cherry husk tomato" | ingredient == "nanking cherry" | ingredient == "sour cherry" | ingredient == "sweet cherry" | ingredient == "acerola cherry" | ingredient == "cambridge cherry" 
	replace ingredient = "chickpeas" if ingredient == "chickpea gram pea"
	replace ingredient = "chillies&peppers" if ingredient == "chilly"
	replace ingredient = "cinnamon" if ingredient == "saigon cinnamon" | ingredient == "chinese cinnamon" | ingredient == "cinnamomum tamala"
	replace ingredient = "clover" if ingredient == "alsike clover" | ingredient == "barrelclover" | ingredient == "crimson clover italian clover" | ingredient == "egyptian clover berseem clover" | ingredient == "hungarian clover" | ingredient =="kenya clover" | ingredient == "kura clover" | ingredient == "red clover" | ingredient == "reversed clover" | ingredient == "strawberry clover" | ingredient == "subterranean clover" | ingredient == "white clover"
	replace ingredient = "cloves" if ingredient == "clove"
	replace ingredient = "cocoa beans" if ingredient == "cocoa cacao" | ingredient == "cacao de monte"
	replace ingredient = "coffee" if ingredient == "eugenioides coffee" | ingredient == "liberian coffee" | ingredient == "robusta coffee"
	replace ingredient = "coriander" if ingredient == "vietnamese coriander"
	replace ingredient = "cottonseed oil" if inlist(ingredient, "seed cotton", "short staple cotton")
	replace ingredient = "cowpeas" if ingredient == "cowpea"
	replace ingredient = "cranberries" if ingredient == "cranberry" | ingredient == "small cranberry" 
	replace ingredient = "cucumbers" if ingredient == "cucumber" | ingredient == "cucumber tree" | ingredient == "horned cucumber"
	replace ingredient = "curry" if ingredient == "curry tree"
	replace ingredient = "dates" if ingredient == "date plum" | ingredient == "desert date" | ingredient == "wild date plum" | ingredient == "cape verde island date palm" 
	replace ingredient = "dry pea" if ingredient == "pea"
	replace ingredient = "eggplants" if ingredient == "eggplant" | ingredient == "gboma eggplant" | ingredient == "scarlet eggplant" 
	replace ingredient = "faba beans" if ingredient == "broad bean"
	replace ingredient = "figs" if ingredient == "fig" | ingredient == "roxburgh fig" | ingredient == "sicomore fig"
	replace ingredient = "garlic" if ingredient == "garlic chives"
	replace ingredient = "ginger" if ingredient == "japanese ginger" | ingredient == "java ginger" | ingredient == "torch ginger" 
	replace ingredient = "gram" if ingredient == "chickpea gram pea" | ingredient == "black gram" | ingredient == "horse gram"
	replace ingredient = "grapes" if ingredient == "grape" | ingredient == "amur river grape" | ingredient == "burmese grape" 
	replace ingredient = "groundnut" if ingredient == "ground nut" | ingredient == "earth pea bambara groundnut" 
	replace ingredient = "hazelnuts" if ingredient == "hazelnut" | ingredient == "japanese hazel" | ingredient == "chinese hazel"
	replace ingredient = "hops" if ingredient == "hop"
	replace ingredient = "jamaican_sorrel" if ingredient == "sorrel" | ingredient == "buckler leaved sorrel"
	replace ingredient = "jatropha" if ingredient == "jatrofa"
	replace ingredient = "kiwi" if ingredient == "variegated leaf hardy kiwi"
	replace ingredient = "kokum" if ingredient == "mangosteen" | ingredient == "yellow mangosteen" | ingredient == "button mangosteen"
	replace ingredient = "leeks" if ingredient == "leek"
	replace ingredient = "lemon_balm" if ingredient == "wild mint"
	replace ingredient = "lemons_limes" if ingredient == "lemon"
	replace ingredient = "lentils" if ingredient == "lentil" | ingredient == "black lentil" 
	replace ingredient = "lettuce" if ingredient == "indian lettuce" | ingredient == "african lettuce"
	replace ingredient = "mangoes" if ingredient == "mango" | ingredient == "wild mango" | ingredient == "horse mango"
	replace ingredient = "mate" if ingredient == "yerba mate"
	replace ingredient = "melons" if ingredient == "melon and cantaloupe" | ingredient == "bitter melon"
	replace ingredient = "millets" if ingredient == "millet pearl"
	replace ingredient = "millets" if ingredient == "millet" | ingredient == "white millet siberian millet" | ingredient == "japanese millet" | ingredient == "kodo millet" | ingredient == "millet finger" | ingredient == "millet italian" | ingredient == "millet pearl" 
	replace ingredient = "mint" if ingredient == "minth" | ingredient == "round leaved mint"
	replace ingredient = "mustard seed" if ingredient == "mustard" | ingredient == "musttard"
	replace ingredient = "oats" if ingredient == "sideoats grama" | ingredient == "abyssinian oat" | ingredient == "false oat grass"
	replace ingredient = "olives" if ingredient == "indian olive" | ingredient == "olive"
	replace ingredient = "onions" if ingredient == "onion" | ingredient == "welsh onion" | ingredient == "wild onion"
	replace ingredient = "oranges" if ingredient == "orange" 
	replace ingredient = "palm oil" if ingredient == "oil palm" 
	replace ingredient = "pandan_leaf" if ingredient == "pandan"
	replace ingredient = "papayas" if ingredient == "papaya pawpaw" | ingredient == "mountain papaya"
	replace ingredient = "parsley" if ingredient == "parsely"
	replace ingredient = "peaches_nectarines" if ingredient == "peach" | ingredient == "peach of gansu" | ingredient == "peach palm" | ingredient == "peach plum" | ingredient == "smoothpit peach"
	replace ingredient = "pears" if ingredient == "pear" | ingredient == "prickly pear" | ingredient == "red flower prickly pear" | ingredient == "sand pear" | ingredient == "arborescent pricklypear" | ingredient == "chinese white pear" 
	replace ingredient = "peas" if ingredient == "grass pea common chickling"	
	replace ingredient = "pepper" if ingredient == "long pepper" | ingredient == "melegueta pepper" |ingredient == "pepper elder" | ingredient == "shichuan pepper" | ingredient == "tree pepper" | ingredient == "water pepper" | ingredient == "ashanti pepper" | ingredient == "balinese long pepper" | ingredient == "bonnet pepper" 
	replace ingredient = "peppercorn" if ingredient == "black pepper"
	replace ingredient = "pigeonpeas" if ingredient == "pigeon pea"
	replace ingredient = "pineapples" if ingredient == "pineapple"
	replace ingredient = "plums" if ingredient == "plum and prune" | ingredient == "wild goose plum" | ingredient == "american plum" | ingredient == "black plum" | ingredient == "canadian plum" | ingredient == "chickasaw plum" | ingredient == "cocoplum" | ingredient == "japanese plum" | ingredient == "malabar plum" | ingredient == "natal plum"
	replace ingredient = "pumpkins" if ingredient == "pumpkin giant pumpkin"
	replace ingredient = "potatoes" if ingredient == "air potato" | ingredient == "kaffir potato" | ingredient == "potato" 
	replace ingredient = "rape&mustard seed" if ingredient == "rapeseed"
	replace ingredient = "reed canary grass" if ingredient == "common reed" | ingredient == "reedmace"
	replace ingredient = "rice" if ingredient == "wild rice american" | ingredient == "wild rice" | ingredient == "rice african"
	replace ingredient = "wetland rice" if ingredient == "jungle rice"
	replace ingredient = "rye" if ingredient == "rye brome" | ingredient == "ryegrass" | ingredient == "canadian wild rye"
	replace ingredient = "seasame" if ingredient == "false sesame" | ingredient == "sesame" | ingredient == "sesame grass" | ingredient == "sesame of the gazelle"
	replace ingredient = "spinach" if ingredient == "ceylan spinach" | ingredient == "ceylon spinach" | ingredient == "kangkong water spinach" | ingredient == "new zealand spinach"
	replace ingredient = "strawberries" if ingredient == "strawberry" | ingredient == "green strawberry" | ingredient == "hautbois strawberry" | ingredient == "scarlet strawberry" | ingredient == "strawberry raspberry" | ingredient == "beach strawberry"
	replace ingredient = "sugar beet" if ingredient == "beet chard"
	replace ingredient = "sweet potatoes" if ingredient == "potato sweet"
	replace ingredient = "taro" if ingredient == "chinese taro" | ingredient == "giant taro"
	replace ingredient = "thyme_bayleaf" if ingredient == "common thyme" | ingredient == "caraway thyme"
	replace ingredient = "tomatoes" if ingredient == "husk tomato tomatillo" | ingredient == "tomato" | ingredient == "tree tomato" | ingredient == "childrens tomatoes" 
	replace ingredient = "watermelons" if ingredient == "watermelon"
	replace ingredient = "wheat" if ingredient == "bread wheat" | ingredient == "durum wheat" | ingredient == "einkorn wheat" | ingredient == "emmer wheat" | ingredient == "persian wheat" | ingredient == "shot wheat"
	replace ingredient = "yams" if ingredient == "white yam"	| ingredient == "ube yam" | ingredient == "yam sp1" | ingredient == "yam sp2" | ingredient == "african bitter yam" | ingredient == "elephant yam" | ingredient == "fanleaf yam" | ingredient == "fiveleaf yam" | ingredient == "indian yam" | ingredient == "japanese yam" | ingredient == "lesser yam" | ingredient == "mountain yam" | ingredient == "pacific yam"
	
	*- Get native countries using lat and lon information
	
	net get geo2xy, from("http://fmwww.bc.edu/repec/bocode/g")
	
// 	replace lon = "" if lon == "NA"	
// 	replace lat = "" if lat == "NA"
//	
// 	destring lat lon, replace dpcomma
	
	geoinpoly lat lon using "geo2xy_world_coor.dta"
	
	merge m:1 _ID using "geo2xy_world_data.dta", ///
    keep(master match) keepusing(geounit iso_a3 continent region_un) nogen
	
	*- Fill empty geounits using coordinates and search them in google
	
	*br if geounit == ""
	replace geounit = "Japan" if lat == 34.361 & lon == 134.6892
	replace geounit = "France" if lat == 42.6939 & lon == 3.4335
	replace geounit = "Australia" if lat == -19.2227 & lon == 147.1827
	replace geounit = "Brazil" if lat == -24.6212 & lon == -46.8115
	replace geounit = "Honduras" if lat == 13.2743 & lon == -87.489
	replace geounit = "United States" if lat == 28.9732 & lon == -94.6914
	replace geounit = "Greece" if lat == 38.757 & lon == 24.783
	replace geounit = "United Kingdom" if lat == 53.6337 & lon == -4.1459
	replace geounit = "Vanuatu" if lat == -15.9008 & lon == 167.6143
	replace geounit = "Costa Rica" if lat == 10.2027 & lon == -82.4885
	replace geounit = "Cabo Verde" if lat == 15.8858 & lon == -23.9164
	replace geounit = "United States" if lat == 14.5189 & lon == 145.1588
	replace geounit = "Indonesia" if lat == -2.1611 & lon == 121.7733
	replace geounit = "Japan" if lat == 38.4691 & lon == 139.3263
	replace geounit = "United States" if lat == 20.3482 & lon == -156.4066
	replace geounit = "Germany" if lat == 54.5537 & lon == 13.5193
	replace geounit = "Papua New Guinea" if lat == 6.6523 & lon == 157.877
	replace geounit = "Croatia" if lat == 42.3298 & lon == 18.0836
	
	replace geounit = "United States" if geounit == "United States of America"
	replace geounit = "Cote D'Ivoire" if geounit == "Ivory Coast"
	replace geounit = "Democratic Republic of the Congo" if geounit == "Republic of Congo"
	replace geounit = "United Republic of Tanzania" if geounit == "Tanzania"
	
	rename (geounit iso_a3 region_un) (country iso3 region)
	
	*- Organize ISO code
	bys country: replace iso3 = iso3[_N]
	tab country if iso3 == ""
	
	replace iso3 = "CPV" if country == "Cabo Verde"
	replace iso3 = "HRV" if country == "Croatia"
	replace iso3 = "GRC" if country == "Greece"
	replace iso3 = "HND" if country == "Honduras"
	replace iso3 = "JPN" if country == "Japan"
	replace iso3 = "GBR" if country == "United Kingdom"
	replace iso3 = "VUT" if country == "Vanuatu"
	replace iso3 = "COD" if country == "Democratic Republic of the Congo"
	
	*- Countries in new dataset
	preserve 
	keep country continent region
	duplicates drop
	bysort country: gen keep = (_n == _N)
	drop if keep == 0 
	tempfile country
	save `country'
	restore
	
	*- Ingredients by region
	preserve
	keep ingredient eco_code
	duplicates drop
	
	tempfile ing_eco
	save `ing_eco' 
	restore
	
	keep ingredient country iso3 continent region
	tempfile ing_country
	save `ing_country'
		
	*- For countries without native ingredients use region
	import excel "${rawdata}\Crop_Origins_Phylo-master\ecoregion_country.xlsx", sheet("Sheet1") firstrow clear
	
	keep ECO_NAME G200_REGIO eco_code iso3 name continent region
	duplicates drop 
	rename name country
	
	replace country = "Bosnia And Herzegovina" if country == "Bosnia & Herzegovina"
	replace country = "Democratic Republic of the Congo" if country == "Congo"
	replace iso3 = "COD"					   if country == "Democratic Republic of the Congo"
	replace country = "Cabo Verde" 			   if country == "Cape Verde"
    replace country = "Cote D'Ivoire"		   if country == "Côte d'Ivoire"
	replace country = "Iran" 				   if country == "Iran (Islamic Republic of)"
	replace country = "Laos" 				   if country == "Lao People's Democratic Republic"
    replace country = "Libya" 				   if country == "Libyan Arab Jamahiriya"
	replace country = "Moldova" 			   if country == "Moldova, Republic of"
	replace country = "North Korea" 		   if country == "Democratic People's Republic of Korea"
    replace country = "Russia" 				   if country == "Russian Federation"
	replace country = "South Korea" 		   if country == "Republic of Korea"
	replace country = "Syria" 				   if country == "Syrian Arab Republic"
    replace country = "United Kingdom" 		   if country == "U.K. of Great Britain and Northern Ireland"
    replace country = "United States" 		   if country == "United States of America"
	replace country = "Palestine" 		   	   if iso3 == "PSE"
	
	*- Merge with recipe data to identify countries in both databases
	preserve
	use "${recipes}/recipe_all_countries.dta", clear
	keep country
	duplicates drop
	
	tempfile countries_recipes
	save `countries_recipes'
	restore
	
	merge m:1 country using `countries_recipes' // Kosovo is not in Milla data
	
	*gen recipe = 1 if _merge == 3 | _merge == 2
	drop _merge
	
	*- Merge ingredient and region	
	joinby eco_code using `ing_eco'
	
	*unique country if _merge == 3
	keep eco_code country ingredient iso3 continent region
	
	*- Get native ingredients for countries that didn't have this information 	
	merge m:1 country using `country'
	*keep if _merge == 1 // we keep countries without native ingredients to assign 
						// ingredients based on the eco region
						
	keep country ingredient iso3 continent region
	duplicates drop
	drop if ingredient == ""
	
	append using `ing_country'
	
	rename iso3 adm0
	duplicates drop

	*- Create variables of interest	
	tempfile working
	save `working', replace
	
{	
// 	*- generate controls: number of ingredients
// 	duplicates drop
// 	gen one = 1
// 	collapse (sum)numNative = one, by(country)
//	
// 	** merge back 
// 	merge 1:m country using `working'
//	
// 	duplicates drop adm0 ingredient, force
// 	drop if adm0 == "" | adm0 == " "
//	
// 	drop _merge 
//	
// 	*- save dataset with native ingredients according to Milla data
// 	save "${versatility}/Milla_ing_origin.dta", replace
}	
	*- Create dataset that combines Milla native ingredients and CIAT
	use "${versatility}/cuisine_ciat.dta", clear
	
	gen CIAT = 1
	keep country ingredient adm0 CIAT region_nice continent_name
	rename (region_nice continent_name) (region continent)
	
	*- Clean ingredient variable
	replace ingredient = "jicama" if ingredient == "jícama"
	replace ingredient = "pig nut" if ingredient == "pignut"
	replace ingredient = "pistachio" if ingredient == "pistachios"
	replace ingredient = "walnut" if ingredient == "walnuts"
	
	append using `working', gen(source)
	
	bys country (adm0): replace adm0 = adm0[_N] 
	bys adm0 (region): replace region = region[_N] 
	bys adm0 (continent): replace continent = continent[_N] 

	* If we have duplicates, keep the one from Milla
	bysort adm0 country ingredient (source): gen keep = (_n == _N)
	drop if keep == 0 
	
	* Drop countries that are not in recipe data
	drop if adm0 == " "
	drop source keep 
	
	replace CIAT = 0 if missing(CIAT)

	gen one = 1
	bys country : egen numNative = total(one)
	drop one
	
	duplicates drop
	
	
	*-- Organize continent variable
	tab continent
	tab country if continent == "Americas"
	replace continent = "Central America" if continent == "Americas"
	
	tab country if continent == "Central America"
	replace continent = "Central America" if inlist(country, ///
    "Costa Rica", "Honduras","Panama", "Dominican Republic", "Puerto Rico")
	
	tab country if continent == "South America"
	replace continent = "South America" if inlist(country, ///
    "Guyana", "Paraguay","Venezuela", "French Guiana")

	tab country if continent == "North America"
	
	save "${versatility}/Milla_CIAT_ing_origin.dta", replace
	
	
	*---- Merge with spice indicator ----*
	import excel "${rawdata}\roster_spices\roster_spices_edited.xlsx", sheet("Spices") firstrow clear
	
	* Organize spice variable
	drop if missing(Spice)
	keep Spice
	gsort Spice
	
	replace Spice = lower(Spice)
	
	tempfile spice
	save `spice'
	
	*- Import other dataset
	import excel "${rawdata}\roster_spices\spices.xlsx", sheet("spices") firstrow clear
	
	rename SpiceName Spice
	replace Spice = lower(Spice)
	duplicates drop
	
	append using `spice'
	
	duplicates drop
	rename Spice ingredient
	
	*-- Merge with crop origin data
	merge 1:m ingredient using "${versatility}/Milla_CIAT_ing_origin.dta"
	
	gen spice = (_merge == 3)
	
	drop if _merge == 1 
	drop _merge
	
	save "${versatility}/Milla_CIAT_ing_origin.dta", replace

	
	* For countries without native spices add spices of closest country
	use "${versatility}/Milla_CIAT_ing_origin.dta", clear
	
	*- Keep countries and their native spices
	preserve
	keep if spice == 1
	rename adm0 nativeadm0
	drop region continent
	tempfile spice
	save `spice'
	restore
	
	*- Keep names of countries that have native spices
	preserve
	keep if spice == 1
	rename adm0 nativeadm0
	keep nativeadm0
	duplicates drop
	tempfile info
	save `info'
	restore
	
	*- Identify countries without native spices
	collapse (mean) spice , by(country adm0)
	keep if spice == 0
	drop spice
	
	*- Keep names of the countries without native spices
	preserve 
	keep adm0
	rename adm0 nativeadm0
	duplicates drop
	tempfile no_spice
	save `no_spice'
	restore
	
	*- Merge with others countries and the distance
	merge 1:m adm0 using "${versatility}/distance_capital.dta", keep(3) nogen
	
	*- Merge with countries without native spices so these are not being considered
	merge m:1 nativeadm0 using `no_spice', keep(1) nogen
	
	*- Merge with countries that do have native spices
	merge m:1 nativeadm0 using `info', keep(3) nogen
	
	*- Keep only closest country
    sort adm0 distance 
	bys adm0 (distance): keep if _n == 1
	
	*- Add the native spices of the closest country
	joinby nativeadm0 using `spice'
	
	keep ingredient country adm0 CIAT numNative spice 
	
	tempfile added_spice
	save `added_spice'
	
	use "${versatility}/Milla_CIAT_ing_origin.dta", clear
	
	append using `added_spice'
	
	sort adm0 continent region
	by adm0: replace continent = continent[_n+1] if missing(continent) 
	by adm0: replace continent = continent[_N] if missing(continent)
	by adm0: replace region = region[_n+1] if missing(region) 
	by adm0: replace region = region[_N] if missing(region)
	
	save "${versatility}/Milla_CIAT_ing_origin_add.dta", replace
	

	