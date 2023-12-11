*================================================
* Raw correlations of FLFP and cuisine complexity
*================================================

* import data
use "${codedata}/recipes/recipe_FLFP2019.dta", clear

** scatter plot
foreach var of varlist mTime{
	egen clock1 = mlabvpos(FLFP `var')
	twoway (scatter FLFP `var',mlabel(country) mlabvpos(clock1)  mlabsize(small) xtitle("Avge Recipe Prep Time"))(lfit FLFP `var')
	graph export "${outputs}/Figures/RecipeFLFPTime.png", replace
	
}

foreach var of varlist mIng{
	egen clock2 = mlabvpos(FLFP `var')
	twoway (scatter FLFP `var',mlabel(country) mlabvpos(clock2)  mlabsize(small) xtitle("Number of Ingredients"))(lfit FLFP `var')
	graph export "${outputs}/Figures/RecipeFLFPIng.png", replace
	
}

foreach var of varlist mSpice{
	egen clock3 = mlabvpos(FLFP `var')
	twoway (scatter FLFP `var',mlabel(country) mlabvpos(clock3)  mlabsize(small) xtitle("Number of Spices"))(lfit FLFP `var')
	graph export "${outputs}/Figures/RecipeFLFPSpi.png", replace
	
}

** regressions
foreach var of varlist mTime mIng mSpice{
	
	reg FLFP `var'
}
