   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *        This dofile merges recipe, region, country dataset      	  *
   *
   * Input: https://github.com/rubenmilla/Crop_Origins_Phylo?tab=readme-ov-file
   * ******************************************************************** *
	clear 
	
	preserve
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
	keep ingredient 
	gsort ingredient
	
	* Rename ingredients so they match suitability dataset
	replace ingredient = "alfalfa" if ingredient == "alfalfa for fodder"
	replace ingredient = "almonds" if ingredient == "almond"
	replace ingredient = "anise_seed" if ingredient == "anise seeds"
	replace ingredient = "annatto" if ingredient == "annato"
	replace ingredient = "apples" if ingredient == "apple"
	replace ingredient = "apricots" if ingredient == "apricot"
	replace ingredient = "artichokes" if ingredient == "jerusalem artichoke" | ingredient == "chinese artichoke"
	replace ingredient = "avocados" if ingredient == "avocado"
	replace ingredient = "blueberries" if ingredient == "blueberry"
	replace ingredient = "cherries" if ingredient == "cereza"
	replace ingredient = "chickpea" if ingredient == "chickpea gram pea"
	replace ingredient = "blueberries" if ingredient == "blueberry"
	replace ingredient = "chillies_peppers" if ingredient == "chilly"
	replace ingredient = "blueberries" if ingredient == "blueberry"
	replace ingredient = "clover" if ingredient == "crimson clover italian clover" | ingredient == "egyptian clover berseem clover" | ingredient == "hungarian clover" | ingredient =="kenya clover" | ingredient == "kura clover" | ingredient == "red clover" | ingredient == "reversed clover" | ingredient == "strawberry clover" | ingredient == "subterranean clover" | ingredient == "white clover"
	replace ingredient = "cloves" if ingredient == "clove"
	replace ingredient = "cocoa" if ingredient == "cocoa cacao"
	replace ingredient = "cotton" if inlist(ingredient, "seed cotton", "short staple cotton")
	replace ingredient = "cranberries" if ingredient == "cranberry"
	replace ingredient = "cucumbers" if ingredient == "cucumber"
	replace ingredient = "curry" if ingredient == "curry tree"
	replace ingredient = "dry pea" if ingredient == "pea"
	replace ingredient = "dryland rice" if ingredient == "rice african"
	replace ingredient = "eggplants" if ingredient == "eggplant"
	replace ingredient = "figs" if ingredient == "fig"
	replace ingredient = "foxtail millet" if ingredient == "millet"
	replace ingredient = "gram" if ingredient == "chickpea gram pea"
	replace ingredient = "grapes" if ingredient == "grape"
	replace ingredient = "groundnut" if ingredient == "ground nut"
	replace ingredient = "hazelnuts" if ingredient == "hazelnut"
	replace ingredient = "hops" if ingredient == "hop"
	replace ingredient = "jamaican_sorrel" if ingredient == "sorrel"
	replace ingredient = "jatropha" if ingredient == "jatrofa"
	replace ingredient = "kiwi" if ingredient == "kwini"
	replace ingredient = "leeks" if ingredient == "leek"
	replace ingredient = "lemons_limes" if ingredient == "lemon"
	replace ingredient = "lentiles" if ingredient == "lentil"
	replace ingredient = "mangoes" if ingredient == "mango"
	replace ingredient = "mate" if ingredient == "yerba mate"
	replace ingredient = "melons" if ingredient == "melon and cantaloupe"
	replace ingredient = "mint" if ingredient == "minth"
	replace ingredient = "mustard_seed" if ingredient == "mustard"
	replace ingredient = "nutmeg_mace" if ingredient == "nutmeg and mace"
	replace ingredient = "oat" if ingredient == "oats"
	replace ingredient = "oranges" if ingredient == "orange"
	replace ingredient = "pandan_leaf" if ingredient == "pandan"
	replace ingredient = "papayas" if ingredient == "papaya pawpaw"
	replace ingredient = "parsley" if ingredient == "parsely"
	replace ingredient = "peaches_nectarines" if ingredient == "peach"
	replace ingredient = "pearl millet" if ingredient == "millet pearl"
	replace ingredient = "pears" if ingredient == "pear"
	replace ingredient = "phaseolus bean" if ingredient == "adzuki bean"
	replace ingredient = "pigeonpea" if ingredient == "pigeon pea"
	replace ingredient = "pineapples" if ingredient == "pineapple"
	replace ingredient = "plums" if ingredient == "plum and prune"
	replace ingredient = "pumpkins" if ingredient == "pumpkin giant pumpkin"
	replace ingredient = "rape_mustard_seed" if ingredient == "rapeseed"
	replace ingredient = "reed canary grass" if ingredient == "common reed"
	replace ingredient = "strawberries" if ingredient == "strawberry"
	replace ingredient = "sugarbeet" if ingredient == "beet chard"
	replace ingredient = "sweet potato" if ingredient == "potato sweet"
	replace ingredient = "thyme_bayleaf" if ingredient == "common thyme"
	replace ingredient = "watermelons" if ingredient == "watermelon"
	replace ingredient = "wetland rice" if ingredient == "rice"
	replace ingredient = "wheat" if ingredient == "bread wheat"
	replace ingredient = "white potato" if ingredient == "potato"
	replace ingredient = "yam" if ingredient == "white yam"	
	
	duplicates drop

	* Change ingredients names to be able to merge it with CIAT data
	
// 	replace ingredients = "almonds" if ingredients == "almond"
// 	replace ingredients = "anise" if ingredients == "anise seeds"
// 	replace ingredients = "apples" if ingredients == "apple"
// 	replace ingredients = "apricots" if ingredients == "apricot"
// 	replace ingredients = "avocados" if ingredients == "avocado"
// 	replace ingredients = "bananas" if ingredients == "banana"
// 	replace ingredients = "blueberries" if ingredients == "blueberry"
// 	replace ingredients = "cabbages" if ingredients == "cabbage"
// 	replace ingredients = "carrots" if ingredients == "carrot"
// 	replace ingredients = "chickpeas" if ingredients == "chickpea gram pea"
// 	replace ingredients = "chicory roots" if ingredients == "chicory"
// 	replace ingredients = "chillies&peppers" if ingredients == "chilly"
// 	replace ingredients = "cocoa beans" if ingredients == "cocoa cacao"
// 	replace ingredients = "coconuts" if ingredients == "coconut"
// 	replace ingredients = "cowpeas" if ingredients == "cowpea"
	
	gen Milla = 1
	
	tempfile origin
	save `origin'
	
	restore
	
// 	preserve
//		
// 	*- CIAT dataset
// 	import excel "${rawdata}/CIAT/ingredients_category.xlsx", sheet("Sheet1") firstrow case(lower) clear
//	
// 	gen CIAT = 1
// 	keep ingredients
//	
// 	tempfile CIAT
// 	save `CIAT'
//	
// 	restore
//	
// 	*- Merge to compare ingredients in data
// 	merge m:1 ingredients using `CIAT'
	
	*- FAO suitability dataset
	use "${fao_suit}/suitability_FAO.dta", clear
	
	keep ingredient
	duplicates drop
	replace ingredient = lower(ingredient)
	
	preserve
	use "${precodedata}/suitability/crop_suitability.dta", clear
	drop al_mn pt_mn ph_mn cl_md
	keep if _n == 1
	
	xpose, varname clear
	keep _varname 
	drop if _n == 1
	
	replace _varname = subinstr(_varname, "ap_", "", .)
	rename _varname ingredient
	
	tempfile crop
	save `crop'
	restore
	
	preserve
	use "${precodedata}/suitability/spices_suitability.dta", clear
	drop al_mn pt_mn ph_mn cl_md
	keep if _n == 1
	
	xpose, varname clear
	keep _varname 
	drop if _n == 1
	
	replace _varname = subinstr(_varname, "ap_", "", .)
	rename _varname ingredient
	
	tempfile spices
	save `spices'
	restore
	
	append using `crop'
	append using `spices'

	duplicates drop
	
	
	* Merge suitability information with Millan data
	
	merge 1:m  ingredient using `origin'
	
	gsort ingredient