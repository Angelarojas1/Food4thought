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
	eststo c1_`o'_fe: reghdfe `o' versatility i.continent
	eststo c1_`o'_iv: ivregress 2sls FLFP ( `o' = versatility)
	
	eststo c2_`o': reg `o'  suit_versatility
	eststo c2_`o'_fe: reghdfe `o'  suit_versatility i.continent
	eststo c2_`o'_iv: ivregress 2sls FLFP (`o' = suit_versatility)
	}
	
	
	* Export regressions results
	esttab c1_median_spices c1_median_spices_fe c1_median_spices_iv c2_median_spices c2_median_spices_fe c2_median_spices_iv ///
	using "$tables/reg_median_spices.tex", replace ///
	star(* 0.1 ** 0.05 *** 0.01) p label
	
	esttab c1* c2* using "$tables/FirstStage_versatility.csv", replace star(* 0.1 ** 0.05 *** 0.01) r2 ar2 p label

	