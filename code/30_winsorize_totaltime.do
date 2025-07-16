* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: June 16, 2025 						   	   *
*				Winsorizing totaltime from recipe data
* **************************************************************************** *

	* ***************************************************** *
	*				Looking into recipes
	* ***************************************************** *	

	use "$recipes\recipe_all_countries.dta", replace
	encode country, gen(Country)
	*hist Country, addl lw(0)
	* Codes: Kosovo = 70; Armenia = 5; Belarus = 12
	gen outlier = 0
	replace outlier = 1 if Country == 70 | Country == 5 | Country == 12 | country == "Armenia" | country == "Jordan" | country == "Ethiopia"
	* Mean = 61.46, Median = 58
	gen out_country = country if Country == 70 | Country == 5 | Country == 12
	qui summ Country, d
	*catplot, over(out_country) blabel(bar, format(%02.0f)) yline(`r(p50)', lc(navy%70) lw(1) lpattern(dash)) title("Outliers - Median at 58")
	*graph export "$files\Outputs\No_of_recipes_outlier.png", replace
	
	* dealing with Kosovo outliers: totaltime 21605 27289001
	drop if country == "Kosovo" & totaltime == 21605
	drop if country == "Kosovo" & totaltime == 27289001
	
	* Min Max Mean by Country
	bys Country: egen min_totaltime = min(totaltime)
	bys Country: egen max_totaltime = max(totaltime)
	bys Country: egen mean_totaltime = mean(totaltime)
	bys Country: egen median_totaltime = median(totaltime)
	bys Country: egen mean_spices = mean(numberofspices)
	bys Country: egen median_spices = median(numberofspices)
	bys Country: egen median_ingredients = median(numberofingredients)
	bys Country: egen mean_ingredients = mean(numberofingredients)
	
	* winsorize
	winsor4 totaltime, method(winsor) outlier(tail) level(1) group(Country) newvar(TotalTime)
	winsor4 numberofspices, method(winsor) outlier(tail) level(1) group(Country) newvar(w_numberofspices)
	bys Country: egen w_mean_totaltime = mean(TotalTime)
	bys Country: egen w_mean_spices = mean(w_numberofspices)
	
	preserve
	keep w_mean_totaltime w_mean_spices Country country mean_ingredients median_spices median_ingredients median_totaltime
	duplicates drop 
	save "$recipes/complexity_recipe.dta", replace
	restore


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
		
	use "${versatility}/reg_variables.dta", replace
	
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
	
	* ***************************************************** *
	*				Mexico Vs Colombia
	* ***************************************************** *	
	if $run == 0 {
	
	keep if country == "Mexico" | country == "Colombia"
	twoway scatter FLFP importVersatility, mlabel(country) mlabs(tiny) ///
	ytitle("FLFP") xtitle("Imported Versatility")
	graph export "$figures\MC_FLFP_Imported.png", replace
	
	twoway scatter FLFP nativeVersatility, mlabel(country) mlabs(tiny) ///
	ytitle("FLFP") xtitle("Native Versatility")
	graph export "$figures\MC_FLFP_Native.png", replace
	
	}
	
	