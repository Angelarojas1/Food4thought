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
	replace ingredient = trim(ingredient)
	replace ingredient = "acerola"           if ingredient == "acerola cherry"
	replace ingredient = "apple"             if ingredient == "asiatic apple" | ingredient == "cainito star apple" | ingredient == "chinese apple" | ingredient == "malay apple" | ingredient == "velvet apple" | ingredient == "wax apple" | ingredient == "wood apple" | ingredient == "african star apple"
	replace ingredient = "apricot"           if ingredient == "apricot plum" | ingredient == "japanese apricot"
	replace ingredient = "banana"            if ingredient == "banana poka" | ingredient == "enset abyssinian banana"
	replace ingredient = "berry"             if ingredient == "aberia caffra" | ingredient == "barbados gooseberry" | ingredient == "bignay" | ingredient == "juneberry"
	replace ingredient = "black_mulberry"    if ingredient == "black mulberry"
	replace ingredient = "black_raspberry"   if ingredient == "black raspberry"
	replace ingredient = "blueberry"         if ingredient == "canada bluegrass"
	replace ingredient = "cherry"            if ingredient == "cereza" | ingredient == "cambridge cherry" | ingredient == "cherry plum" | ingredient == "sour cherry" | ingredient == "sweet cherry"
	replace ingredient = "chinese_bayberry"  if ingredient == "chinese bayberry"
	replace ingredient = "common_persimmon"  if ingredient == "american persimmon" | ingredient == "date plum"
	replace ingredient = "cranberry"         if ingredient == "small cranberry"
	replace ingredient = "cupuau"            if ingredient == "cupuassu"
	replace ingredient = "currant_black"     if ingredient == "black currant"
	replace ingredient = "currant_red"       if ingredient == "red currant" | ingredient == "rock red currant" | ingredient == "nordic currant"
	replace ingredient = "dates"             if ingredient == "cape verde island date palm" | ingredient == "desert date" 
	replace ingredient = "fig"               if ingredient == "roxburgh fig" | ingredient == "sicomore fig"
	replace ingredient = "gooseberry"        if ingredient == "otaheite gooseberry"
	replace ingredient = "grape"             if ingredient == "amur river grape" | ingredient == "muscadine" | ingredient == "burmese grape" 
	replace ingredient = "groundcherry"      if ingredient == "ground cherry husk tomato" | ingredient == "husk tomato tomatillo" | ingredient == "tomatillo" | ingredient == "ground cherry" 
	replace ingredient = "guava"             if ingredient == "brazilian guava" | ingredient == "cattley guava" | ingredient == "costa rican guava" | ingredient == "guavasteen"
	replace ingredient = "hogplum"           if ingredient == "ambarella" | ingredient == "jocote" | ingredient == "yellow mombin"
	replace ingredient = "jackfruit"         if ingredient == "chempedak" | ingredient == "monkey jack"
	replace ingredient = "japanese_persimmon" if ingredient == "japanese plum"
	replace ingredient = "kiwi"              if ingredient == "variegated leaf hardy kiwi"
	replace ingredient = "kumquat"           if ingredient == "ronda kumquat"
	replace ingredient = "malabar_plum"      if ingredient == "malabar plum"
	replace ingredient = "malayapple"        if ingredient == "malay apple"
	replace ingredient = "mammee_apple"      if ingredient == "mamey"
	replace ingredient = "mango"             if ingredient == "horse mango" | ingredient == "wild mango"
	replace ingredient = "purple_mangosteen" if ingredient == "mangosteen"
	replace ingredient = "melon"             if ingredient == "melon and cantaloupe"
	replace ingredient = "mulberry"          if ingredient == "mulberry for silkworms"
	replace ingredient = "nanking_cherry"    if ingredient == "nanking cherry"
	replace ingredient = "orange"            if ingredient == "clementine"
	replace ingredient = "bitter_orange"     if ingredient == "orange bitter"
	replace ingredient = "papaya"            if ingredient == "papaya pawpaw" | ingredient == "mountain papaya" | ingredient == "pawpaw"
	replace ingredient = "peach"             if ingredient == "peach of gansu" | ingredient == "smoothpit peach" | ingredient == "peach palm" 
	replace ingredient = "pear"              if ingredient == "chinese white pear" | ingredient == "sand pear"
	replace ingredient = "plum"              if ingredient == "plum and prune" | ingredient == "american plum" | ingredient == "canadian plum" | ingredient == "chickasaw plum" | ingredient == "wild goose plum" | ingredient == "natal plum" | ingredient == "black plum" | ingredient == "cocoplum"
	replace ingredient = "pummelo"           if ingredient == "pomelo"
	replace ingredient = "raspberry"         if ingredient == "strawberry raspberry"
	replace ingredient = "roseapple"         if ingredient == "wax apple" | ingredient == "jambos"
	replace ingredient = "saskatoon_berry"   if ingredient == "saskatoon"
	replace ingredient = "soursop"           if ingredient == "guanábana" | ingredient == "mountain soursop"
	replace ingredient = "starfruit"         if ingredient == "star fruit"
	replace ingredient = "strawberry"        if ingredient == "beach strawberry" | ingredient == "green strawberry" | ingredient == "hautbois strawberry" | ingredient == "scarlet strawberry"
	replace ingredient = "tomato"            if ingredient == "childrens tomatoes" | ingredient == "tree tomato"
	replace ingredient = "woodapple"         if ingredient == "wood apple"

	replace ingredient = "artichoke"         if ingredient == "jerusalem artichoke" | ingredient == "chinese artichoke"
	replace ingredient = "bamboo_shoots"     if ingredient == "common bamboo" | ingredient == "dragon bamboo" | ingredient == "giant thorny bamboo" | ingredient == "odashimae bamboo" | ingredient == "taiwan giant bamboo"
	replace ingredient = "bittergourd"       if ingredient == "bitter melon" | ingredient == "bottle gourd"
	replace ingredient = "cabbage"           if ingredient == "chou blanc" | ingredient == "ethiopian cabbage"
	replace ingredient = "pepper"          if ingredient == "bonnet pepper"
	replace ingredient = "chard"             if ingredient == "beet chard"
	replace ingredient = "beetroot"        if ingredient == "sugar beet"
	replace ingredient = "chillies_peppers"             if ingredient == "chilly"
	replace ingredient = "taro"         if ingredient == "chinese taro" | ingredient == "giant taro"
	replace ingredient = "corn"    if ingredient == "maize" | ingredient == "annual teosinte" | ingredient == "corn salad"
	replace ingredient = "drumstick"         if ingredient == "drumstick tree"
	replace ingredient = "eggplant"          if ingredient == "gboma eggplant" | ingredient == "scarlet eggplant"
	replace ingredient = "beans_redkidneybeans" if ingredient == "broad bean"
	replace ingredient = "garlic"            if ingredient == "rocambole" | ingredient == "wild onion"
	replace ingredient = "garland_chrysanthemum" if ingredient == "garland chrysanthemum"
	replace ingredient = "gourd"             if ingredient == "calabash tree"
	replace ingredient = "jerusalem_artichoke" if ingredient == "jerusalem artichoke"
	replace ingredient = "jicama"            if ingredient == "jícama" | ingredient == "ahipa"
	replace ingredient = "lambsquarters"     if ingredient == "fat hen"
	replace ingredient = "lettuce"           if ingredient == "african lettuce" | ingredient == "indian lettuce"
	replace ingredient = "lotus"             if ingredient == "sacred water lotus"
	replace ingredient = "malabar_spinach"   if ingredient == "ceylon spinach" | ingredient == "ceylan spinach"
	replace ingredient = "mustard_seed"           if ingredient == "musttard" | ingredient == "white musttard"
	replace ingredient = "new_zealand_spinach" if ingredient == "new zealand spinach"
	replace ingredient = "spinach" if ingredient == "kangkong water spinach" 
	replace ingredient = "nopal"             if ingredient == "nopal cascaron" | ingredient == "cochineal nopal cactus" | ingredient == "spiny nopal" | ingredient == "arborescent pricklypear" | ingredient == "prickly pear" | ingredient == "red flower prickly pear"
	replace ingredient = "okra"              if ingredient == "bush okra"
	replace ingredient = "olive"             if ingredient == "indian olive" | ingredient == "fragrant olive"
	replace ingredient = "peas"              if ingredient == "pea"
	replace ingredient = "pepper"            if ingredient == "black pepper" | ingredient == "ashanti pepper" | ingredient == "long pepper" | ingredient == "balinese long pepper" | ingredient == "melegueta pepper" | ingredient == "shichuan pepper" | ingredient == "tree pepper"
	replace ingredient = "potato"            if ingredient == "papa amarilla" | ingredient == "papa criolla" | ingredient == "papa rucki"
	replace ingredient = "pumpkin"           if ingredient == "pumpkin giant pumpkin" | ingredient == "japanese pie pumpkin"
	replace ingredient = "rocket_salad"      if ingredient == "rocket"
	replace ingredient = "squash"            if ingredient == "summer squash"
	replace ingredient = "sweetpotato"       if ingredient == "potato sweet"
	replace ingredient = "watercress"        if ingredient == "land cress"
	replace ingredient = "welsh_onion"       if ingredient == "welsh onion"
	replace ingredient = "onion" 			if ingredient == "wild onion"
	replace ingredient = "groundnut" if ingredient == "ground nut" | ingredient == "earth pea bambara groundnut" 
	replace ingredient = "yam"               if ingredient == "yam sp1" | ingredient == "yam sp2" | ingredient == "african bitter yam" | ingredient == "fanleaf yam" | ingredient == "fiveleaf yam" | ingredient == "indian yam" |ingredient == "japanese yam" | ingredient == "lesser yam" | ingredient == "pacific yam" | ingredient == "white yam"
	replace ingredient = "mountain_yam"      if ingredient == "mountain yam"
	replace ingredient = "clover" if ingredient == "alsike clover" | ingredient == "barrelclover" | ingredient == "crimson clover italian clover" | ingredient == "egyptian clover berseem clover" | ingredient == "hungarian clover" | ingredient =="kenya clover" | ingredient == "kura clover" | ingredient == "red clover" | ingredient == "reversed clover" | ingredient == "strawberry clover" | ingredient == "subterranean clover" | ingredient == "white clover"
	replace ingredient = "cowpeas" if ingredient == "cowpea"
	replace ingredient = "peas" if ingredient == "grass pea common chickling"	
	replace ingredient = "beans"             if ingredient == "bean dry edible" | ingredient == "bitter bean" | ingredient == "broad bean" | ingredient == "butter bean lima bean" | ingredient == "bush vetch" | ingredient == "chaucha" | ingredient == "earthnut pea" | ingredient == "guar" | ingredient == "hairy vetch fodder vetch winter vetch" | ingredient == "horse gram" | ingredient == "hungarian vetch" | ingredient == "hyacinth bean" | ingredient == "jack bean" | ingredient == "longbeak rattlebox" | ingredient == "louisiana vetch" | ingredient == "mat bean" | ingredient == "narbon bean" | ingredient == "oblique seed jackbean" | ingredient == "pale pea" | ingredient == "purple vetch reddish tufted vetch" | ingredient == "red vetchling" | ingredient == "runner bean" | ingredient == "single flowered vetch" | ingredient == "smooth vetch" | ingredient == "sword bean" | ingredient == "tepary bean" | ingredient == "tufted vetch" | ingredient == "two leaved vetch" | ingredient == "vetch for grain" | ingredient == "vicia chica" | ingredient == "year long bean" | ingredient == "african locust bean"	| ingredient == "ice cream bean" |ingredient == "mung bean" | ingredient == "ricebean" | ingredient == "tonka beans" | ingredient == "adzuki bean"
	
	replace ingredient = "chickpea"          if ingredient == "chickpea gram pea"
	replace ingredient = "grass_pea"         if ingredient == "flat pea"
	replace ingredient = "lentils"           if ingredient == "lentil" | ingredient == "black lentil"
	replace ingredient = "lupine"            if ingredient == "blue lupin" | ingredient == "hairy blue lupin" | ingredient == "pearl lupin" | ingredient == "sundial lupine" | ingredient == "yellow lupin"
	replace ingredient = "white_lupine"      if ingredient == "white lupin"
	replace ingredient = "mung_bean"         if ingredient == "mung bean"
	replace ingredient = "peanut"            if ingredient == "creeping forage peanut" | ingredient == "ground nut" | ingredient == "hog peanut" | ingredient == "sacha peanut"
	replace ingredient = "pigeonpea"         if ingredient == "pigeon pea"

	replace ingredient = "flaxseed"          if ingredient == "flax"
	replace ingredient = "wheat"        if ingredient == "bread wheat" 
	replace ingredient = "hard_wheat"        if ingredient == "durum wheat" | ingredient == "einkorn wheat" | ingredient == "emmer wheat" | ingredient == "persian wheat" | ingredient == "shot wheat"
	replace ingredient = "millet"            if ingredient == "millet finger" | ingredient == "millet italian" |ingredient == "millet pearl" | ingredient == "japanese millet" | ingredient == "kodo millet" | ingredient == "white millet siberian millet" | ingredient == "black fonio"| ingredient == "fonio"
	replace ingredient = "oats"              if ingredient == "abyssinian oat"| ingredient == "false oat grass" | ingredient == "sideoats grama"
	replace ingredient = "quinoa"            if ingredient == "cañihua"
	replace ingredient = "rice"              if ingredient == "jungle rice"
	replace ingredient = "red_rice"          if ingredient == "rice african"
	replace ingredient = "sorghum"           if ingredient == "columbus grass"
	replace ingredient = "wheat"             if ingredient == "intermediate wheatgrass"
	replace ingredient = "wild_rice"         if ingredient == "wild rice" | ingredient == "wild rice american"

	replace ingredient = "almond"            if ingredient == "almonds"|ingredient == "country almond"
	replace ingredient = "annatto" if ingredient == "annato"
	replace ingredient = "brazilnut"         if ingredient == "brazil nut"
	replace ingredient = "cashew_nut"        if ingredient == "cashew nuts"
	replace ingredient = "chestnut"          if ingredient == "american sweet chestnut"|ingredient == "chinese chestnut"
	replace ingredient = "chestnut"          if ingredient == "japanese chestnut"| ingredient == "tahitian chestnut"
	replace ingredient = "filbert"           if ingredient == "siberian filbert"
	replace ingredient = "hazelnut" if ingredient == "japanese hazel" | ingredient == "chinese hazel"
	replace ingredient = "nuts"              if ingredient == "canarium nut"| ingredient == "cutnut"| ingredient == "paradise nut"| ingredient == "pekea nut"|ingredient == "pig nut"| ingredient == "pignut"| ingredient == "wild karuka"
	replace ingredient = "pili_nut"          if ingredient == "pili nut"
	replace ingredient = "sesame"            if ingredient == "benniseed" | ingredient == "black beniseed" | ingredient == "sesame grass" | ingredient == "sesame of the gazelle"
	replace ingredient = "walnut"            if ingredient == "black walnut"| ingredient == "hinds black walnut"| ingredient == "japanese walnut"
		
	replace ingredient = "alfalfa"             if ingredient == "alfalfa for fodder"
	replace ingredient = "anise"             if ingredient == "anise seeds"
	replace ingredient = "anise"   if ingredient == "star anise"
	replace ingredient = "cucumber"   if ingredient == "pepino"
	replace ingredient = "thyme"           if ingredient == "caraway seeds"|ingredient == "caraway thyme"
	replace ingredient = "cardamom"          if ingredient == "cambodian cardamom" | ingredient == "round cardamom " | ingredient == "round chinese cardamom"
	replace ingredient = "potato"           if ingredient == "air potato" | ingredient == "kaffir potato" 
	replace ingredient = "rhubarb"           if ingredient == "alpine dock"
	replace ingredient = "colocasia"           if ingredient == "amankani"
replace ingredient = "arrowhead"           if ingredient == "arrow head"
	replace ingredient = "laurel"           if ingredient == "bay laurel"
	replace ingredient = "cinnamon"           if ingredient == "canela de ceilan"
	replace ingredient = "cinnamon" if ingredient == "saigon cinnamon" | ingredient == "chinese cinnamon" | ingredient == "cinnamomum tamala"
	replace ingredient = "rape_mustard_seed"         if ingredient == "rape&mustard seed" | ingredient == "rapeseed"
	replace ingredient = "ryeflour"            if ingredient == "rye" | ingredient == "rye brome" | ingredient == "ryegrass" | ingredient == "canadian wild rye"
	replace ingredient = "medlar"            if ingredient == "azarole"
	replace ingredient = "nigella"            if ingredient == "blackseed"
	replace ingredient = "garciniaindica"            if ingredient == "bor thekera" | ingredient == "charichuelo"
	replace ingredient = "sorrel"            if ingredient == "buckler leaved sorrel"
	replace ingredient = "avocado"            if ingredient == "butterfruit"
	replace ingredient = "taro"            if ingredient == "calalou"
	replace ingredient = "sapodilla"            if ingredient == "canistel"
	replace ingredient = "walnut"            if ingredient == "chinese hickory"
	replace ingredient = "cucurbita"            if ingredient == "cidra chilacayote"
	replace ingredient = "citrus"            if ingredient == "citron"
	replace ingredient = "french_plantain"            if ingredient == "common plantain"
	replace ingredient = "thyme"            if ingredient == "common thyme" | strpos(ingredient, "oregano") > 0
	replace ingredient = "garden_cress"            if ingredient == "cress"
	replace ingredient = "cherimoya"            if ingredient == "custard apple"
	replace ingredient = "gooseberry"            if ingredient == "emblic"
	replace ingredient = "breadfruit"            if ingredient == "fruit salad plant"
	replace ingredient = "sweet_grass"            if ingredient == "gan cao"
	replace ingredient = "buffalo_currant"            if ingredient == "golden currant"
	replace ingredient = "groundcherry"            if ingredient == "ground cherry"
	replace ingredient = "hops"            if ingredient == "hop"
	replace ingredient = "persimmon"  if ingredient == "wild date plum"
	replace ingredient = "waterchestnut"  if ingredient == "water chestnut"
	replace ingredient = "horned_melon"  if ingredient == "horned cucumber"
	replace ingredient = "cucumber" if ingredient == "cucumber tree" 
	replace ingredient = "parsley"  if ingredient == "parsely"
	replace ingredient = "lime"  if ingredient == "kaffir lime"
	replace ingredient = "passionfruit"  if ingredient == "passion fruit"
	replace ingredient = "oil_palm"  if ingredient == "oil palm"
	replace ingredient = "sago_palm"  if ingredient == "sago palm"
	replace ingredient = "yam"  if ingredient == "konjac"
	replace ingredient = "safflower"  if ingredient == "safflower seed"
	replace ingredient = "curryleaf"  if ingredient == "curry tree"
	replace ingredient = "cocoa" if ingredient == "cocoa cacao" | ingredient == "cacao de monte"
	replace ingredient = "coffee" if ingredient == "eugenioides coffee" | ingredient == "liberian coffee" | ingredient == "robusta coffee"
	replace ingredient = "coriander" if ingredient == "vietnamese coriander"
	replace ingredient = "cottonseed" if inlist(ingredient, "seed cotton", "short staple cotton")
	replace ingredient = "garlic" if ingredient == "garlic chives"
	replace ingredient = "chive" if ingredient == "chinese chives" | ingredient == "chives" | ingredient == "long stamen chive"
	replace ingredient = "ginger" if ingredient == "japanese ginger" | ingredient == "java ginger" | ingredient == "torch ginger" | ingredient == "greater galangal" | ingredient == "lesser galangal" | ingredient == "kencur"
	replace ingredient = "gram" if ingredient == "chickpea gram pea" | ingredient == "black gram" | ingredient == "horse gram"
	replace ingredient = "mint" if ingredient == "wild mint"
	replace ingredient = "mint" if ingredient == "minth" | ingredient == "round leaved mint"
	replace ingredient = "mate" if ingredient == "yerba mate"
	
	* Include generic names for unspecified ingredients
	replace ingredient = "crab"            if strpos(ingredient, "crab") > 0 
	replace ingredient = "arrowroot"       if strpos(ingredient, "arrowroot") > 0 
	replace ingredient = "valerian"        if strpos(ingredient, "valerian") > 0 
	replace ingredient = "yam"             if strpos(ingredient, "yam") > 0 
	replace ingredient = "passionfruit"    if strpos(ingredient, "granadilla") > 0 | strpos(ingredient, "passionfruit") > 0
	replace ingredient = "amaranth"            if strpos(ingredient, "amaranth") > 0
	replace ingredient = "liquorice"       if strpos(ingredient, "liquorice") > 0
	
	*- Get native countries using lat and lon information
	
	net get geo2xy, from("http://fmwww.bc.edu/repec/bocode/g")
	
	replace lon = "" if lon == "NA"	
	replace lat = "" if lat == "NA"
	
	destring lat lon, replace dpcomma
	
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
	bys country (iso3): replace iso3 = iso3[_N]
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
	drop keep
	isid country
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
	sort country
	bys country (continent): replace continent = continent[_N] 
	bys country (region): replace region = region[_N] 
	bysort country ingredient: gen keep = (_n == _N)
	drop if keep == 0 
	drop keep
	tempfile ing_country
	save `ing_country'
		
	*- For countries without native ingredients use region
	import excel "${rawdata}\Crop_Origins_Phylo-master\ecoregion_country.xlsx", sheet("Sheet1") firstrow clear
	
	keep ECO_NAME eco_code iso3 name continent region
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
	
	drop _merge
	
	*- Merge ingredient and region	
	joinby eco_code using `ing_eco'
	
	keep country ingredient iso3 continent region
	
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
	
	*- Create dataset that combines Milla native ingredients and CIAT
	use "${versatility}/cuisine_ciat.dta", clear
	
	gen CIAT = 1
	keep country ingredient adm0 CIAT region_nice continent_name
	rename (region_nice continent_name) (region continent)
	
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
	
	save "${versatility}/Milla_CIAT_ing.dta", replace
	
	
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
	
	*- Clean ingredient variable
	replace ingredient = trim(ingredient)
	duplicates drop
	
	replace ingredient = "nigella"            if ingredient == "nigella seed"
	replace ingredient = "pepper"            if ingredient == "black pepper"
	replace ingredient = "chinese keys"            if ingredient == "fingerroot"
	replace ingredient = "laurel"            if ingredient == "bay leaf"
	replace ingredient = "caper"            if ingredient == "capers"
	replace ingredient = "chive"            if ingredient == "chives"
	replace ingredient = "curryleaf"            if ingredient == "curry"
	replace ingredient = "lime"  			if ingredient == "kaffir lime"
	replace ingredient = "nutmeg and mace"  			if ingredient == "nutmeg, mace"
	replace ingredient = "capsicum" if ingredient == "capsicums"
	duplicates drop
	
	*-- Merge with crop origin data
	merge 1:m ingredient using "${versatility}/Milla_CIAT_ing.dta"
	
	gen spice = (_merge == 3)
	
	drop if _merge == 1 
	drop _merge
	
	*-- Drop fruits. 
	// [AR 20260909: I looked for them on internet to make sure they were fruits]
	tab ingredient
	drop if ingredient == "abiú"
	drop if ingredient == "acai"
	drop if ingredient == "acerola"
	drop if ingredient == "ackee"
	drop if ingredient == "apple"
	drop if ingredient == "apricot"
	drop if ingredient == "babaco"
	drop if ingredient == "banana"
	drop if ingredient == "baobab"
	drop if ingredient == "berry"
	drop if ingredient == "biriba"
	drop if ingredient == "bitter_orange"
	drop if ingredient == "black_mulberry"
	drop if ingredient == "black_raspberry"
	drop if ingredient == "blackberry"
	drop if ingredient == "blueberry"
	drop if ingredient == "breadfruit"
	drop if ingredient == "calamansi"
	drop if ingredient == "cherimoya"
	drop if ingredient == "cherry"
	drop if ingredient == "chocolate pudding fruit"
	drop if ingredient == "citrus"
	drop if ingredient == "cloudberry"
	drop if ingredient == "coconut"
	drop if ingredient == "cranberry"
	drop if ingredient == "currant_black"
	drop if ingredient == "currant_red"
	drop if ingredient == "dates"
	drop if ingredient == "dogberry"
	drop if ingredient == "dragonfruit"
	drop if ingredient == "durian"
	drop if ingredient == "elderberry"
	drop if ingredient == "fig"
	drop if ingredient == "french_plantain"
	drop if ingredient == "gandaria"
	drop if ingredient == "garden huckleberry"
	drop if ingredient == "goldenberry"
	drop if ingredient == "gooseberry"
	drop if ingredient == "grape"
	drop if ingredient == "grapefruit"
	drop if ingredient == "green sapote"
	drop if ingredient == "groundcherry"
	drop if ingredient == "guabiroba"
	drop if ingredient == "guama"
	drop if ingredient == "guava"
	drop if ingredient == "guayabillo"
	drop if ingredient == "hogplum"
	drop if ingredient == "horned_melon"
	drop if ingredient == "ilama"
	drop if ingredient == "jackfruit"
	drop if ingredient == "japanese_persimmon"
	drop if ingredient == "japanese wineberry"
	drop if ingredient == "jujube"
	drop if ingredient == "kerson fruit"
	drop if ingredient == "kiwi"
	drop if ingredient == "kumquat"
	drop if ingredient == "kwini"
	drop if ingredient == "litchi"
	drop if ingredient == "longan"
	drop if ingredient == "loquat"
	drop if ingredient == "lucma"
	drop if ingredient == "lucumo"
	drop if ingredient == "malabar_plum"
	drop if ingredient == "mammee_apple"
	drop if ingredient == "mamoncillo"
	drop if ingredient == "mango"
	drop if ingredient == "marula"
	drop if ingredient == "medlar"
	drop if ingredient == "melon"
	drop if ingredient == "menteng"
	drop if ingredient == "monkey fruit"
	drop if ingredient == "mora de castilla"
	drop if ingredient == "mulberry"
	drop if ingredient == "mundu"
	drop if ingredient == "nanking_cherry"
	drop if ingredient == "naranjilla"
	drop if ingredient == "olive"
	drop if ingredient == "orange"
	drop if ingredient == "pacay"
	drop if ingredient == "papaya"
	drop if ingredient == "passionfruit"
	drop if ingredient == "peach"
	drop if ingredient == "peach plum"
	drop if ingredient == "peanut butter fruit"
	drop if ingredient == "pear"
	drop if ingredient == "persimmon"
	drop if ingredient == "phalsa"
	drop if ingredient == "pineapple"
	drop if ingredient == "pitaya agria"
	drop if ingredient == "pitomba"
	drop if ingredient == "piñuela"
	drop if ingredient == "plum"
	drop if ingredient == "pomegranate"
	drop if ingredient == "pummelo"
	drop if ingredient == "purple_mangosteen"
	drop if ingredient == "quince"
	drop if ingredient == "rambai"
	drop if ingredient == "rambutan"
	drop if ingredient == "raspberry"
	drop if ingredient == "roseapple"
	drop if ingredient == "salak"
	drop if ingredient == "sanduri"
	drop if ingredient == "santol"
	drop if ingredient == "sapodilla"
	drop if ingredient == "saskatoon_berry"
	drop if ingredient == "soursop"
	drop if ingredient == "south american sapote"
	drop if ingredient == "starfruit"
	drop if ingredient == "strawberry"
	drop if ingredient == "sugar apple"
	drop if ingredient == "tamarillo"
	drop if ingredient == "tamarind"
	drop if ingredient == "uvalha"
	drop if ingredient == "wampee"
	drop if ingredient == "wani"
	drop if ingredient == "water lemon"
	drop if ingredient == "watermelon"
	drop if ingredient == "white sapote"
	drop if ingredient == "yellow mangosteen"
	drop if ingredient == "yvapuru"
	
	save "${versatility}/Milla_CIAT_ing_origin.dta", replace

**********************************************************************************	
/*
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
	
*********************************************************************************
	
	* Add spice from closest country making sure the spice is in the compound data
// 	use "${versatility}/Milla_CIAT_ing_origin.dta", clear
//	
// 	merge m:1 ingredient using "$precodedata\flavor_profile\CIAT\ing_list.dta", gen(flavordb)	
//	
// 	*- Keep countries and their native spices
// 	preserve
// 	keep if spice == 1 & flavordb == 3
// 	rename adm0 nativeadm0
// 	drop region continent
// 	tempfile spice
// 	save `spice'
// 	restore
//	
// 	*- Keep names of countries that have native spices
// 	preserve
// 	keep if spice == 1 & flavordb == 3
// 	rename adm0 nativeadm0
// 	keep nativeadm0
// 	duplicates drop
// 	tempfile info
// 	save `info'
// 	restore
//	
// 	*- Identify countries without native spices
// 	bys adm0: egen spices2 = sum(spice) if spice == 1 & flavordb == 3
// 	replace spices2 = 0 if missing(spices2)
// 	collapse (mean) spices2 , by(country adm0)
// 	keep if spices2 == 0
// 	drop spices2
//	
// 	*- Keep names of the countries without native spices
// 	preserve 
// 	keep adm0
// 	rename adm0 nativeadm0
// 	duplicates drop
// 	tempfile no_spice
// 	save `no_spice'
// 	restore
//	
// 	*- Merge with others countries and the distance
// 	merge 1:m adm0 using "${versatility}/distance_capital.dta", keep(3) nogen
//	
// 	*- Merge with countries without native spices so these are not being considered
// 	merge m:1 nativeadm0 using `no_spice', keep(1) nogen
//	
// 	*- Merge with countries that do have native spices
// 	merge m:1 nativeadm0 using `info', keep(3) nogen
//	
// 	*- Keep only closest country
//     sort adm0 distance 
// 	bys adm0 (distance): keep if _n == 1
//	
// 	*- Add the native spices of the closest country
// 	joinby nativeadm0 using `spice'
//	
// 	keep ingredient country adm0 CIAT numNative spice 
//	
// 	tempfile added_spice
// 	save `added_spice'
//	
// 	use "${versatility}/Milla_CIAT_ing_origin.dta", clear
//	
// 	append using `added_spice'
//	
// 	sort adm0 continent region
// 	by adm0: replace continent = continent[_n+1] if missing(continent) 
// 	by adm0: replace continent = continent[_N] if missing(continent)
// 	by adm0: replace region = region[_n+1] if missing(region) 
// 	by adm0: replace region = region[_N] if missing(region)
//	
// // keep if ///
// // inlist(country, "Albania", "Argentina", "Burundi", "Chile", "Colombia", "Cuba") | ///
// // inlist(country, "Dominican Republic", "Ecuador", "Guatemala", "Honduras", "Haiti", "Jamaica") | ///
// // inlist(country, "Kenya", "South Korea", "Kuwait", "Sri Lanka", "Morocco", "Montenegro") | ///
// // inlist(country, "Panama", "Peru", "North Korea", "Portugal", "Paraguay", "Singapore") | ///
// // inlist(country, "Uruguay")
//	
// 	save "${versatility}/Milla_CIAT_ing_origin_flavor.dta", replace
//
