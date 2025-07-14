* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: June 24, 2025 						   	   *
*				Cooktime calculations for India
* **************************************************************************** *
	
	

	clear all
	set more off
	global run = 1

	* ***************************************************** *

	tempfile time
	save `time', emptyok
	
	if $run == 1 {
	import delim using "$precodedata\recipes\final\India.csv", clear

	encode recipecategory, gen(r_category)
	gen category = .
	* Breakfast - Indian Breakfast North Indian Breakfast South Indian Breakfast World Breakfast

	* Lunch - Lunch Brunch 

	* Appetizer - Side Dish Appetizer 

	* Dessert - Dessert

	ren totaltime total_time

	gen new_category = .
	replace new_category = 1 if recipecategory == "Indian Breakfast" | recipecategory == "North Indian Breakfast" | recipecategory == "South Indian Breakfast" | recipecategory == "World Breakfast" | recipecategory == "Brunch"
	replace new_category = 2 if r_category == 6 // Lunch
	replace new_category = 3 if r_category == 4 // Dinner
	replace new_category = 4 if recipecategory == "Appetizer" | recipecategory == "Main Course" | recipecategory == "Dessert" | recipecategory == "Side Dish" | recipecategory == "One Pot Dish" | recipecategory == ""
	replace new_category = 5 if recipecategory == "Snack"


	gen meal = (new_category != 5)

	bys meal: egen mean_time = mean(total_time)

	bys meal: egen median_time = median(total_time)

	egen time = mean(total_time)
	
	gen m_time = 3*total_time if meal == 1
	replace m_time = 2*total_time if mean != 1
	
	bys meal: egen mean_a_time = mean(m_time)

	bys meal: egen median_a_time = median(m_time)
	
	
	*========================================================
	*					New calculation
	*--------------------------------------------------------
	
	* Main Course
	gen main_course = 0
	replace main_course = 1 if new_category < 4 | recipecategory == "Main Course" | recipecategory == "One Pot Dish"
	
	bys main_course: egen time_mains_mean = mean(total_time)
	bys main_course: egen time_mains_median = median(total_time)
	
	* Subcategories
	gen subcategories = 0
	replace subcategories = 1 if new_category < 4 | recipecategory == "Main Course" | recipecategory == "One Pot Dish"
	replace subcategories = 2 if recipecategory == "Appetizer"
	replace subcategories = 3 if recipecategory == "Dessert"
	replace subcategories = 4 if recipecategory == "Side Dish"
	replace subcategories = 5 if recipecategory == "Snack"
	
	bys subcategories: egen time_subcategories_mean = mean(total_time)
	bys subcategories: egen time_subcategories_median = median(total_time)
	
	gen country = "India"
	keep country time_mains_mean time_mains_median time_subcategories_mean time_subcategories_median main_course category subcategories
	
	*collapse (first)country (mean)time_mains_mean (median)time_mains_median (mean)time_subcategories_mean (median)time_subcategories_median
	
	append using `time', force
	
	save `time', replace
	
	}
	
	*========================================================
	*					Australia
	*========================================================
	
	import delim using "$precodedata\recipes\final/Australia.csv", clear varn(1)
	split category, parse (",")
	drop category category2 category3 category4 category5
	ren category1 category
	
	* Main Course
	gen main_course = 0
	replace main_course = 1 if category == "dinner" | category == "breakfast" | category == "lunch" | category == "brunch" | category == "main"
	
	bys main_course: egen time_mains_mean = mean(totaltime)
	bys main_course: egen time_mains_median = median(totaltime)
	
	bys category: egen time_subcategories_mean = mean(totaltime)
	bys category: egen time_subcategories_median = median(totaltime)
	
	gen country = "Australia"
	
	*collapse (first)country (mean)time_mains_mean (median)time_mains_median (mean)time_subcategories_mean (median)time_subcategories_median
	keep category country main_course time_mains_mean time_mains_median time_subcategories_mean time_subcategories_median
	
	append using `time', force
	
	save `time', replace
	
	*========================================================
	*					New Zealand
	*========================================================
	
	import delimited using "$recipes\New_Zealand_categories_cleaned.csv", clear varn(1)
	ren category Category
	ren item category
	tempfile nz_cl
	save `nz_cl'
	
	import delim using "$precodedata\recipes\final/New Zealand.csv", clear varn(1)
	
	merge m:1 category using "`nz_cl'"
	
	drop category
	ren Category category
	
	gen main_course = 0
	replace main_course = 1 if category == "Main"
	
	bys main_course: egen time_mains_mean = mean(totaltime)
	bys main_course: egen time_mains_median = median(totaltime)
	
	bys category: egen time_subcategories_mean = mean(totaltime)
	bys category: egen time_subcategories_median = median(totaltime)
	
	gen country = "New Zealand"
	
	*collapse (first)country (mean)time_mains_mean (median)time_mains_median (mean)time_subcategories_mean (median)time_subcategories_median
	keep category country main_course time_mains_mean time_mains_median time_subcategories_mean time_subcategories_median
		
	append using `time', force
	
	save `time', replace
	
	
	*********************************************************
	* Merging cooktime
	*********************************************************
	
	use "$recipes\recipe_all_countries.dta", replace
	
	preserve
	keep if country == "South Africa"
	
	split category, parse(",")
	
	drop category category2 category3 category4 category5
	ren category1 category
	
	* Main Course
	gen main_course = 0
	replace main_course = 1 if category == "dinner" | category == "breakfast" | category == "lunch" | category == "brunch" | category == "main"
	
	bys main_course: egen time_mains_mean = mean(totaltime)
	bys main_course: egen time_mains_median = median(totaltime)
	
	bys category: egen time_subcategories_mean = mean(totaltime)
	bys category: egen time_subcategories_median = median(totaltime)
	
	*collapse (first)country (mean)time_mains_mean (median)time_mains_median (mean)time_subcategories_mean (median)time_subcategories_median
	keep category country main_course time_mains_mean time_mains_median time_subcategories_mean time_subcategories_median
	
	append using `time', force
	
	save `time', replace
	restore
	
	preserve 
	import delim using "$recipes/UK_category_translated.csv", clear varn(1)
	
	tempfile uk
	save `uk'
	restore
	
	preserve
	keep if country == "United Kingdom"
	
	gen item = category
	drop category
	
	/*
	keep category
	duplicates drop
	
	export delim using "$recipes/UK_category.csv", replace
	*/
	
	merge m:1 item using `uk'
	
	gen main_course = 0
	replace main_course = 1 if category == "Main" | category == "Main/Side"
	
	bys main_course: egen time_mains_mean = mean(totaltime)
	bys main_course: egen time_mains_median = median(totaltime)
	
	bys category: egen time_subcategories_mean = mean(totaltime)
	bys category: egen time_subcategories_median = median(totaltime)
	
	*collapse (first)country (mean)time_mains_mean (median)time_mains_median (mean)time_subcategories_mean (median)time_subcategories_median
	keep category country main_course time_mains_mean time_mains_median time_subcategories_mean time_subcategories_median
	
	append using `time', force
	
	save `time', replace
	restore
	
	preserve
	keep if country == "Mexico"
	
	gen main_course = 0
	replace main_course = 1 if category == "Main Dish" | category == "Soup"
	
	bys main_course: egen time_mains_mean = mean(totaltime)
	bys main_course: egen time_mains_median = median(totaltime)
	
	bys category: egen time_subcategories_mean = mean(totaltime)
	bys category: egen time_subcategories_median = median(totaltime)
	
	*collapse (first)country (mean)time_mains_mean (median)time_mains_median (mean)time_subcategories_mean (median)time_subcategories_median
	keep category country main_course time_mains_mean time_mains_median time_subcategories_mean time_subcategories_median
	
	append using `time', force
	
	save `time', replace
	restore
	
	preserve 
	import delim using "$recipes/Russia_category_translated.csv", clear varn(1)
	
	tempfile rus
	save `rus'
	restore
	
	preserve
	keep if country == "Russia"
	
	gen item = category
	drop category
	
	/*
	keep item
	duplicates drop
	
	export delim using "$recipes/Russia_category.csv", replace
	*/
	
	merge m:1 item using `rus'
	
	gen main_course = 0
	replace main_course = 1 if category == "Main" | category == "Main/Side"
	
	bys main_course: egen time_mains_mean = mean(totaltime)
	bys main_course: egen time_mains_median = median(totaltime)
	
	bys category: egen time_subcategories_mean = mean(totaltime)
	bys category: egen time_subcategories_median = median(totaltime)
	
	*collapse (first)country (mean)time_mains_mean (median)time_mains_median (mean)time_subcategories_mean (median)time_subcategories_median
	keep category country main_course time_mains_mean time_mains_median time_subcategories_mean time_subcategories_median
	
	append using `time', force
	
	save `time', replace
	restore
	
	
	keep if country == "Lithuania"
	
	gen item = category
	drop category
	
	/*
	keep item
	duplicates drop
	
	export delim using "$recipes/Russia_category.csv", replace
	*/
	
	merge m:1 item using `rus'
	
	gen main_course = 0
	replace main_course = 1 if category == "Main" | category == "Main/Side"
	
	bys main_course: egen time_mains_mean = mean(totaltime)
	bys main_course: egen time_mains_median = median(totaltime)
	
	bys category: egen time_subcategories_mean = mean(totaltime)
	bys category: egen time_subcategories_median = median(totaltime)
	
	*collapse (first)country (mean)time_mains_mean (median)time_mains_median (mean)time_subcategories_mean (median)time_subcategories_median
	keep category country main_course time_mains_mean time_mains_median time_subcategories_mean time_subcategories_median
	
	append using `time', force
	
	save `time', replace
	x
	
	
	bys country: egen mean_totaltime = mean(totaltime)
	bys country: egen median_totaltime = median(totaltime)
	
	duplicates drop country, force
	
	
	merge m:1 country using `time'
	keep if _merge == 3
	drop _merge
	merge 1:1 country using "$outputs/first_stage_dataset.dta"
	keep if _merge == 3
	keep country mean_totaltime median_totaltime time_mains_median time_subcategories_mean time_subcategories_median adm0 time_mains_mean

	merge 1:1 adm0 using "$versatility/all_versatility.dta"
	keep if _merge == 3
	*First Stage
	reghdfe time_mains_mean suit_versatility