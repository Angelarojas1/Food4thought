* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: June 16, 2025 						   	   *
*				Winsorizing totaltime from recipe data
* **************************************************************************** *

	* Plots
	if $run == 0 {
	preserve
	duplicates drop Country w_mean_totaltime mean_ingredients, force
	*drop if Country == 70
	twoway scatter w_mean_totaltime mean_ingredients if outlier == 0, mlabel(country) mlabs(tiny) mlw(none) || ///
			scatter w_mean_totaltime mean_ingredients if outlier == 1, mlabel(country) mlabs(tiny) mfc(dkgreen) mlw(none)  legend(label(2 "Outliers")) ///
	title("Mean Ingredients by Winsorized Mean Time") ytitle("Winsorized Average Time") ///
	xtitle("Average Number of Ingredients")
	graph export "$figures/WinTime_Ingredients.png", replace
	
	destring numberofingredients_raw, replace
	replace numberofingredients = numberofingredients_raw if country == "Armenia"
	drop mean_ingredients
	bys Country: egen mean_ingredients = mean(numberofingredients)
	twoway scatter w_mean_totaltime mean_ingredients if outlier == 0, mlw(none) || ///
			scatter w_mean_totaltime mean_ingredients if outlier == 1, mlabel(country) mlabs(tiny) mfc(dkgreen) mlw(none)  legend(label(2 "Outliers")) ///
	title("Mean Ingredients by Winsorized Mean Time") ytitle("Winsorized Average Time") ///
	xtitle("Average Number of Ingredients - Armenia Raw")
	graph export "$figures/WinTime_Ingredients_ARRaw.png", replace
	
	twoway scatter w_mean_totaltime w_mean_spices if outlier == 0, mlabel(country) mlabs(tiny) mlw(none) || ///
		scatter w_mean_totaltime w_mean_spices if outlier == 1, mlabel(country) mlabs(tiny) mfc(dkgreen) mlw(none)  legend(label(2 "Outliers")) ///
	ytitle("Average Time") xtitle("Average Number of spices - Armenia Raw") title("Winzorised Mean Time by Winsorized Mean Spices")
	graph export "$figures\WinTime_NOS_ARRaw.png", replace
	restore
	}
	
	
	* ***************************************************** *
	*				Cooktime outliers
	* ***************************************************** *
	
	
	if $run == {
		
	use "${versatility}/reg_variables.dta", replace // [AR 20250903: this dataset contains a measure of the variables that we don't use anymore]
	
	preserve 
	keep if nativeVersatility == 0
	export delim country using "$tables/no_native.csv", replace
	restore
	
	preserve 
	keep if importVersatility == 0
	export delim country using "$tables/no_import.csv", replace
	restore
	
	preserve 
	keep if nativeVersatility == 0 & importVersatility == 0
	export delim country using "$tables/no_versatility.csv", replace
	restore
	
	twoway scatter time_mean nativeVersatility if nativeVersatility != 0, mlabel(country) mlabs(tiny) mlw(none) legend(label(1 "Non-Zero")) || ///
		scatter time_mean nativeVersatility if nativeVersatility == 0, mlabel(country) mlabs(tiny) mfc(dkgreen) mlw(none) legend(label(2 "Zero Native")) || ///
		scatter time_mean nativeVersatility if nativeVersatility == 0 & importVersatility == 0,  mlabel(country) mlabs(tiny) mfc(blue) mlw(none)  legend(label(3 "Zero Native & Import")) ///
	ytitle("Average Time") xtitle("Native Versatility") title("Native Versatility by Mean Time")
	graph export "$figures\Time_NoNative.png", replace
	
	if $run == 0 {
	twoway scatter time_mean ingredients_mean, mlabel(country) mlabs(tiny) || ///
		scatter time_mean spices_mean, mlabel(country) mlabs(tiny)
	ytitle("Average Time") xtitle("Average Number of ingredients")
	graph export "$figures\Time_NOI.png", replace
	
	twoway scatter time_mean spices_mean, mlabel(country) mlabs(tiny) ///
	ytitle("Average Time") xtitle("Average Number of spices")
	graph export "$figures\Time_NOS.png", replace
	
	twoway scatter time_mean importVersatility, mlabel(country) mlabs(tiny) ///
	ytitle("Average Time") xtitle("Imported Versatility")
	graph export "$figures\Time_Imported.png", replace
	
	twoway scatter time_mean nativeVersatility, mlabel(country) mlabs(tiny) ///
	ytitle("Average Time") xtitle("Native Versatility")
	graph export "$figures\Time_Native.png", replace
	}
	}
	
	