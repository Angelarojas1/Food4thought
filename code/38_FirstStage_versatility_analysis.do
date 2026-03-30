* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: June 16, 2025 						   	   *
*				Modified by:  Angela Rojas
*				First Stage Review
* **************************************************************************** *
	
	use "$versatility/first_stage_dataset.dta", replace
	
	**********************************************************
	*			First Stage
	**********************************************************
	
	local outcome median_spices median_totaltime median_ingredients w_mean_totaltime
	
	est clear
	foreach o of local outcome {
		*********************************************
		* All Versatility
		*********************************************
	eststo c1_`o': reg `o' versatility
	estadd local fe No
	eststo c1_`o'_fe: reghdfe `o' versatility i.continent
	estadd local fe Yes
	eststo c1_`o'_iv: ivregress 2sls FLFP ( `o' = versatility)
	estadd local fe No
	
	eststo c2_`o': reg `o'  suit_versatility
	estadd local fe No
	eststo c2_`o'_fe: reghdfe `o'  suit_versatility i.continent
	estadd local fe Yes
	eststo c2_`o'_iv: ivregress 2sls FLFP (`o' = suit_versatility)
	estadd local fe No
	}
	
	* Export regressions results
	esttab c1_median_spices c1_median_spices_fe c1_median_spices_iv c2_median_spices c2_median_spices_fe c2_median_spices_iv ///
	using "$tables/reg_median_spices.tex", replace ///
	nocons keep(versatility suit_versatility median_spices) ///
	star(* 0.1 ** 0.05 *** 0.01) p label ///
	stats(fe N, labels("Continent FE" "Observations")) ///
	mti("1st Stage" "1st Stage" "FLFP" "1st Stage" "1st Stage" "FLFP")
	
	esttab c1_median_totaltime c1_median_totaltime_fe c1_median_totaltime_iv c2_median_totaltime c2_median_totaltime_fe c2_median_totaltime_iv ///
	using "$tables/reg_median_totaltime.tex", replace ///
	nocons keep(versatility suit_versatility median_totaltime) ///
	star(* 0.1 ** 0.05 *** 0.01) p label ///
	stats(fe N, labels("Continent FE" "Observations")) ///
	mti("1st Stage" "1st Stage" "FLFP" "1st Stage" "1st Stage" "FLFP")
	
	esttab c1_median_ingredients c1_median_ingredients_fe c1_median_ingredients_iv c2_median_ingredients c2_median_ingredients_fe c2_median_ingredients_iv ///
	using "$tables/reg_median_ingredients.tex", replace ///
	nocons keep(versatility suit_versatility median_ingredients) ///
	star(* 0.1 ** 0.05 *** 0.01) p label ///
	stats(fe N, labels("Continent FE" "Observations")) ///
	mti("1st Stage" "1st Stage" "FLFP" "1st Stage" "1st Stage" "FLFP")
	
	esttab c1_w_mean_totaltime c1_w_mean_totaltime_fe c1_w_mean_totaltime_iv c2_median_totaltime c2_w_mean_totaltime_fe c2_w_mean_totaltime_iv ///
	using "$tables/reg_w_mean_totaltime.tex", replace ///
	nocons keep(versatility suit_versatility w_mean_totaltime) ///
	star(* 0.1 ** 0.05 *** 0.01) p label ///
	stats(fe N, labels("Continent FE" "Observations")) ///
	mti("1st Stage" "1st Stage" "FLFP" "1st Stage" "1st Stage" "FLFP")
	

	