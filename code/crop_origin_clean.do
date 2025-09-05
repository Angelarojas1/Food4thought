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
	
	drop if common_name_crop == "na"
	
	*br if dup_tag == 1
	
	rename common_name_crop ingredient
	replace ingredient = lower(ingredient)
	replace ingredient = subinstr(ingredient, "_", " ", .)
	keep ingredient mode_ecoreg_name mode_ecoreg_centroid_lon mode_ecoreg_centroid_lat mode_ecoreg_code biogeografic_realm sd_longitude sd_latitude
	
	** Get native countries using lat and lon information
	
	*net get geo2xy, from("http://fmwww.bc.edu/repec/bocode/g")
	
	replace mode_ecoreg_centroid_lon = "" if mode_ecoreg_centroid_lon == "NA"	
	replace mode_ecoreg_centroid_lat = "" if mode_ecoreg_centroid_lat == "NA"
	
	drop if mode_ecoreg_code == "NA"
	
	destring mode_ecoreg_centroid_lat mode_ecoreg_centroid_lon, replace dpcomma
	
	geoinpoly mode_ecoreg_centroid_lat mode_ecoreg_centroid_lon using "geo2xy_world_coor.dta"
	
	merge m:1 _ID using "geo2xy_world_data.dta", ///
    keep(master match) keepusing(geounit) nogen

	gsort ingredient
	
	* Fill empty geounits using coordinates and search them in google
	
	*br if geounit == ""
	replace geounit = "Japan" if mode_ecoreg_centroid_lat == 34.361 & mode_ecoreg_centroid_lon == 134.6892
	replace geounit = "France" if mode_ecoreg_centroid_lat == 42.6939 & mode_ecoreg_centroid_lon == 3.4335
	replace geounit = "Australia" if mode_ecoreg_centroid_lat == -19.2227 & mode_ecoreg_centroid_lon == 147.1827
	replace geounit = "Brazil" if mode_ecoreg_centroid_lat == -24.6212 & mode_ecoreg_centroid_lon == -46.8115
	replace geounit = "Honduras" if mode_ecoreg_centroid_lat == 13.2743 & mode_ecoreg_centroid_lon == -87.489
	replace geounit = "United States of America" if mode_ecoreg_centroid_lat == 28.9732 & mode_ecoreg_centroid_lon == -94.6914
	replace geounit = "Greece" if mode_ecoreg_centroid_lat == 38.757 & mode_ecoreg_centroid_lon == 24.783
	replace geounit = "United Kingdom" if mode_ecoreg_centroid_lat == 53.6337 & mode_ecoreg_centroid_lon == -4.1459
	replace geounit = "Vanuatu" if mode_ecoreg_centroid_lat == -15.9008 & mode_ecoreg_centroid_lon == 167.6143
	replace geounit = "Costa Rica" if mode_ecoreg_centroid_lat == 10.2027 & mode_ecoreg_centroid_lon == -82.4885
	replace geounit = "Cabo Verde" if mode_ecoreg_centroid_lat == 15.8858 & mode_ecoreg_centroid_lon == -23.9164
	replace geounit = "United States of America" if mode_ecoreg_centroid_lat == 14.5189 & mode_ecoreg_centroid_lon == 145.1588
	replace geounit = "Indonesia" if mode_ecoreg_centroid_lat == -2.1611 & mode_ecoreg_centroid_lon == 121.7733
	replace geounit = "Japan" if mode_ecoreg_centroid_lat == 38.4691 & mode_ecoreg_centroid_lon == 139.3263
	replace geounit = "United States of America" if mode_ecoreg_centroid_lat == 20.3482 & mode_ecoreg_centroid_lon == -156.4066
	replace geounit = "Germany" if mode_ecoreg_centroid_lat == 54.5537 & mode_ecoreg_centroid_lon == 13.5193
	replace geounit = "Papua New Guinea" if mode_ecoreg_centroid_lat == 6.6523 & mode_ecoreg_centroid_lon == 157.877
	replace geounit = "Croatia" if mode_ecoreg_centroid_lat == 42.3298 & mode_ecoreg_centroid_lon == 18.0836

	* Rename ingredients so they match suitability dataset
	replace ingredient = "alfalfa" if ingredient == "alfalfa for fodder"
	replace ingredient = "almonds" if ingredient == "almond" | ingredient == "country almond"
	replace ingredient = "anise_seed" if ingredient == "anise seeds" | ingredient == "star anise"
	replace ingredient = "annatto" if ingredient == "annato"
	replace ingredient = "apples" if ingredient == "apple" | ingredient == "asiatic apple" | ingredient == "cainito star apple" | ingredient == "chinese apple" | ingredient == "malay apple" | ingredient == "velvet apple" | ingredient == "wax apple" | ingredient == "wood apple" | ingredient == "african star apple"
	replace ingredient = "apricots" if ingredient == "apricot" | ingredient == "apricot plum" | ingredient == "japanese apricot"
	replace ingredient = "artichokes" if ingredient == "jerusalem artichoke" | ingredient == "chinese artichoke"
	replace ingredient = "avocados" if ingredient == "avocado"
	replace ingredient = "banana" if ingredient == "enset abyssinian banana"	
	replace ingredient = "beans" if ingredient == "african locust bean"	| ingredient == "bean dry edible" | ingredient == "bitter bean"| ingredient == "butter bean lima bean" | ingredient == "hyacinth bean" | ingredient == "ice cream bean" | ingredient == "jack bean" | ingredient == "mat bean" | ingredient == "mung bean" | ingredient == "narbon bean" | ingredient == "oblique seed jackbean" | ingredient == "ricebean" | ingredient == "runner bean" | ingredient == "sword bean" | ingredient == "tepary bean" | ingredient == "tonka beans" | ingredient == "year long bean"
	replace ingredient = "blueberries" if ingredient == "blueberry"
	replace ingredient = "cabbage" if ingredient == "ethiopian cabbage"	
	replace ingredient = "cardamom" if ingredient == "cambodian cardamom"	
	replace ingredient = "cherries" if ingredient == "cereza" | ingredient == "cherry plum" | ingredient == "ground cherry" | ingredient == "ground cherry husk tomato" | ingredient == "nanking cherry" | ingredient == "sour cherry" | ingredient == "sweet cherry" | ingredient == "acerola cherry" | ingredient == "cambridge cherry" 
	replace ingredient = "chickpea" if ingredient == "chickpea gram pea"
	replace ingredient = "chillies_peppers" if ingredient == "chilly"
	replace ingredient = "cinnamon" if ingredient == "saigon cinnamon" | ingredient == "chinese cinnamon" | ingredient == "cinnamomum tamala"
	replace ingredient = "clover" if ingredient == "alsike clover" | ingredient == "barrelclover" | ingredient == "crimson clover italian clover" | ingredient == "egyptian clover berseem clover" | ingredient == "hungarian clover" | ingredient =="kenya clover" | ingredient == "kura clover" | ingredient == "red clover" | ingredient == "reversed clover" | ingredient == "strawberry clover" | ingredient == "subterranean clover" | ingredient == "white clover"
	replace ingredient = "cloves" if ingredient == "clove"
	replace ingredient = "cocoa" if ingredient == "cocoa cacao" | ingredient == "cacao de monte"
	replace ingredient = "coffee" if ingredient == "eugenioides coffee" | ingredient == "liberian coffee" | ingredient == "robusta coffee"
	replace ingredient = "coriander" if ingredient == "vietnamese coriander"
	replace ingredient = "cotton" if inlist(ingredient, "seed cotton", "short staple cotton")
	replace ingredient = "cowpeas" if ingredient == "cowpea"
	replace ingredient = "cranberries" if ingredient == "cranberry" | ingredient == "small cranberry" 
	replace ingredient = "cucumbers" if ingredient == "cucumber" | ingredient == "cucumber tree" | ingredient == "horned cucumber"
	replace ingredient = "curry" if ingredient == "curry tree"
	replace ingredient = "dates" if ingredient == "date plum" | ingredient == "desert date" | ingredient == "wild date plum" | ingredient == "cape verde island date palm" 
	replace ingredient = "dry pea" if ingredient == "pea"
	replace ingredient = "eggplants" if ingredient == "eggplant" | ingredient == "gboma eggplant" | ingredient == "scarlet eggplant" 
	replace ingredient = "faba beans" if ingredient == "broad bean"
	replace ingredient = "figs" if ingredient == "fig" | ingredient == "roxburgh fig" | ingredient == "sicomore fig"
	replace ingredient = "foxtail millet" if ingredient == "millet" | ingredient == "white millet siberian millet" | ingredient == "japanese millet" | ingredient == "kodo millet" | ingredient == "millet finger" | ingredient == "millet italian" | ingredient == "millet pearl" 
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
	replace ingredient = "lentiles" if ingredient == "lentil" | ingredient == "black lentil" 
	replace ingredient = "lettuce" if ingredient == "indian lettuce" | ingredient == "african lettuce"
	replace ingredient = "mangoes" if ingredient == "mango" | ingredient == "wild mango" | ingredient == "horse mango"
	replace ingredient = "mate" if ingredient == "yerba mate"
	replace ingredient = "melons" if ingredient == "melon and cantaloupe" | ingredient == "bitter melon"
	replace ingredient = "mint" if ingredient == "minth" | ingredient == "round leaved mint"
	replace ingredient = "mustard_seed" if ingredient == "mustard" | ingredient == "musttard"
	replace ingredient = "nutmeg_mace" if ingredient == "nutmeg and mace"
	replace ingredient = "oat" if ingredient == "oats" | ingredient == "sideoats grama" | ingredient == "abyssinian oat" | ingredient == "false oat grass"
	replace ingredient = "olives" if ingredient == "indian olive" | ingredient == "olive"
	replace ingredient = "onions" if ingredient == "onion" | ingredient == "welsh onion" | ingredient == "wild onion"
	replace ingredient = "palm oil" if ingredient == "oil palm" 
	replace ingredient = "pandan_leaf" if ingredient == "pandan"
	replace ingredient = "papayas" if ingredient == "papaya pawpaw" | ingredient == "mountain papaya"
	replace ingredient = "parsley" if ingredient == "parsely"
	replace ingredient = "peaches_nectarines" if ingredient == "peach" | ingredient == "peach of gansu" | ingredient == "peach palm" | ingredient == "peach plum" | ingredient == "smoothpit peach"
	replace ingredient = "pearl millet" if ingredient == "millet pearl"
	replace ingredient = "pears" if ingredient == "pear" | ingredient == "prickly pear" | ingredient == "red flower prickly pear" | ingredient == "sand pear" | ingredient == "arborescent pricklypear" | ingredient == "chinese white pear" 
	replace ingredient = "peas" if ingredient == "grass pea common chickling"	
	replace ingredient = "pepper" if ingredient == "long pepper" | ingredient == "melegueta pepper" |ingredient == "pepper elder" | ingredient == "shichuan pepper" | ingredient == "tree pepper" | ingredient == "water pepper" | ingredient == "ashanti pepper" | ingredient == "balinese long pepper" | ingredient == "bonnet pepper" 
	replace ingredient = "peppercorn" if ingredient == "black pepper"
	replace ingredient = "phaseolus bean" if ingredient == "adzuki bean"
	replace ingredient = "pigeonpea" if ingredient == "pigeon pea"
	replace ingredient = "pineapples" if ingredient == "pineapple"
	replace ingredient = "plums" if ingredient == "plum and prune" | ingredient == "wild goose plum" | ingredient == "american plum" | ingredient == "black plum" | ingredient == "canadian plum" | ingredient == "chickasaw plum" | ingredient == "cocoplum" | ingredient == "japanese plum" | ingredient == "malabar plum" | ingredient == "natal plum"
	replace ingredient = "pumpkins" if ingredient == "pumpkin giant pumpkin"
	replace ingredient = "potatoes" if ingredient == "air potato" | ingredient == "kaffir potato" | ingredient == "potato" 
	replace ingredient = "rape_mustard_seed" if ingredient == "rapeseed"
	replace ingredient = "reed canary grass" if ingredient == "common reed" | ingredient == "reedmace"
	replace ingredient = "rice" if ingredient == "wild rice american" | ingredient == "wild rice" | ingredient == "jungle rice"
	replace ingredient = "rye" if ingredient == "rye brome" | ingredient == "ryegrass" | ingredient == "canadian wild rye"
	replace ingredient = "seasame" if ingredient == "false sesame" | ingredient == "sesame" | ingredient == "sesame grass" | ingredient == "sesame of the gazelle"
	replace ingredient = "spinach" if ingredient == "ceylan spinach" | ingredient == "ceylon spinach" | ingredient == "kangkong water spinach" | ingredient == "new zealand spinach"
	replace ingredient = "strawberries" if ingredient == "strawberry" | ingredient == "green strawberry" | ingredient == "hautbois strawberry" | ingredient == "scarlet strawberry" | ingredient == "strawberry raspberry" | ingredient == "beach strawberry"
	replace ingredient = "sugarbeet" if ingredient == "beet chard"
	replace ingredient = "sweet potato" if ingredient == "potato sweet"
	replace ingredient = "taro" if ingredient == "chinese taro" | ingredient == "giant taro"
	replace ingredient = "thyme_bayleaf" if ingredient == "common thyme" | ingredient == "caraway thyme"
	replace ingredient = "tomatoes" if ingredient == "husk tomato tomatillo" | ingredient == "tomato" | ingredient == "tree tomato" | ingredient == "childrens tomatoes" 
	replace ingredient = "watermelons" if ingredient == "watermelon"
	replace ingredient = "wetland rice" if ingredient == "rice african"
	replace ingredient = "wheat" if ingredient == "bread wheat" | ingredient == "durum wheat" | ingredient == "einkorn wheat" | ingredient == "emmer wheat" | ingredient == "persian wheat" | ingredient == "shot wheat"
	replace ingredient = "yam" if ingredient == "white yam"	| ingredient == "ube yam" | ingredient == "yam sp1" | ingredient == "yam sp2" | ingredient == "african bitter yam" | ingredient == "elephant yam" | ingredient == "fanleaf yam" | ingredient == "fiveleaf yam" | ingredient == "indian yam" | ingredient == "japanese yam" | ingredient == "lesser yam" | ingredient == "mountain yam" | ingredient == "pacific yam"
	
	duplicates drop

