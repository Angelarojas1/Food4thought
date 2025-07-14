* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: June 16, 2025 						   	   *
*				First Stage Review
* **************************************************************************** *
	
	

	clear all
	set more off
	global run = 1

	* ***************************************************** *
	
	use "$outputs/first_stage_dataset.dta", replace
	
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
	eststo c1_`o': reghdfe `o' versatility i.continent
	eststo c1_`o': ivregress 2sls FLFP ( `o' = versatility)
	
	eststo c2_`o': reg `o'  suit_versatility
	eststo c2_`o': reghdfe `o'  suit_versatility i.continent
	eststo c2_`o': ivregress 2sls FLFP (`o' = suit_versatility)
	}

	esttab c1* c2* using "$tables/FirstStage_versatility.csv", replace star(* 0.1 ** 0.05 *** 0.01) r2 ar2 p label
	