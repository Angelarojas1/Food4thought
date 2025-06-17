* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: June 16, 2025 						   	   *
*				First Stage Review
* **************************************************************************** *
	
	use "$codedata/Outputs/first_stage_dataset.dta", replace
	
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
	
	if $run == 0{  // Old versions of calculation start here
	est clear
	foreach o of local outcome {
		*********************************************
		* Newest Cleanest Versatility
		*********************************************
	eststo c1_`o': reg `o' versatility
	eststo c2_`o': reghdfe `o' versatility i.continent
	testparm `o' versatility
	ivregress 2sls FLFP ( `o' = versatility)
	
	}
	
	
	esttab c1* c2* using "$tables/FirstStage_clean_versatility.csv", replace star(* 0.1 ** 0.05 *** 0.01) r2 ar2 p label
	
	
	
	
	
		est clear
	foreach o of local outcome {
		*********************************************
		* Native Versatility
		*********************************************
	eststo s1_`o': reg `o' nativeVersatility
	eststo s2_`o': reghdfe `o' nativeVersatility i.continent
	testparm `o' nativeVersatility
	ivregress 2sls FLFP ( `o' = nativeVersatility)
	
	}
	
	
	esttab s1* s2* using "$tables/FirstStage_nativeVersatility.csv", replace
	
	
	
	est clear
	foreach o of local outcome {
		*********************************************
		* Import Versatility
		*********************************************
	
	eststo s1_`o': reg `o' importVersatility
	eststo s2_`o': reghdfe `o' importVersatility i.continent
	testparm `o' importVersatility
	ivregress 2sls FLFP ( `o' = importVersatility)
	
	}
	
	
	esttab s1* s2* using "$tables/FirstStage_importVersatility.csv", replace
	
		est clear
	foreach o of local outcome {
		
		*********************************************
		* Composite Min Distance
		*********************************************
	eststo s1_`o': reg `o' Versatility_mindist
	eststo s2_`o': reghdfe `o' Versatility_mindist i.continent
	testparm `o' Versatility_mindist
	ivregress 2sls FLFP ( `o' = Versatility_mindist)
		*********************************************
		*********************************************
	}
	
	esttab s1* s2* using "$tables/FirstStage_versatility_mindist.csv", replace
	
		est clear
	foreach o of local outcome {
		
		*********************************************
		* Composite
		*********************************************
	eststo s1_`o': reg `o' Versatility
	eststo s2_`o': reghdfe `o' Versatility i.continent
	testparm `o' Versatility
	ivregress 2sls FLFP ( `o' = Versatility)
		*********************************************
		*********************************************
	}
	
	esttab s1* s2* using "$tables/FirstStage_versatility.csv", replace
	
		est clear
	foreach o of local outcome {
		
		*********************************************
		* Composite Weighted
		*********************************************
	eststo s1_`o': reg `o' Versatility_weighted
	eststo s2_`o': reghdfe `o' Versatility_weighted i.continent
	testparm `o' Versatility_weighted
	ivregress 2sls FLFP ( `o' = Versatility_weighted)
		*********************************************
		*********************************************
	}
	
	esttab s1* s2* using "$tables/FirstStage_versatility_weighted.csv", replace
	
	}
	