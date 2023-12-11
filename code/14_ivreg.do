****************************************
* 1st stage regression data
****************************************


use "${codedata}/recipes/recipe_FLFP2019.dta", clear
rename three_letter_country_code adm0

** merge with geographical data
merge 1:1 adm0 using "${codedata}/iv_versatility/geographical.dta"
assert _merge != 2
keep if _merge == 3
count
assert `r(N)' == 135
drop _merge

** merge with numNative
preserve
use "${codedata}/iv_versatility/recipe_flfp_ciat.dta", clear
unique adm0
assert `r(sum)' == 135
keep adm0 numNative
duplicates drop
tempfile numNative
save `numNative', replace
restore

merge 1:1 adm0 using `numNative'
assert _merge == 3
drop _merge

unique adm0
assert `r(sum)' == 135

** merge with native versatility
merge 1:1 adm0 using "${codedata}/iv_versatility/nativebycountry_p60_g3simple.dta"
assert _merge != 2
assert missing(nativeVersatility) if _merge == 1
drop _merge

*** set missing native versatility as 0
replace nativeVersatility = 0 if missing(nativeVersatility)
assert !missing(nativeVersatility)

** merge with imported versatility
merge 1:1 adm0 using "${codedata}/iv_versatility/importbycountry_p60.dta"
assert _merge !=2
assert missing(importVersatility) if _merge == 1
drop _merge

*** set missing import versatility as 0
replace importVersatility = 0 if missing(importVersatility)
assert !missing(importVersatility)

** create factor 
encode continent_name, gen(continentFactor)
gen logmtime = log(mTime)
egen std_native = std(nativeVersatility)
egen std_import = std(importVersatility)

label var std_native "std of native versatility"
label var nativeVersatility "native versatility"
label var std_import "std of import versatility"
label var importVersatility "import versatility"
label var mIng "average number of ingredients"
label var mSpice "average number of spices"

foreach var of varlist logmtime mIng mSpice{
	
	* 1st stage
	reghdfe `var' std_native std_import numNative al_mn [aweight=num_recipes] , absorb(continentFactor)  
	eststo reg1
	sum `var' if e(sample)
	local mean = r(mean)
	estadd scalar mean = `mean'
	estadd local continent "\multicolumn{1}{c}{Yes}"
	estadd local geographical "\multicolumn{1}{c}{Yes}"
	
	* iv
	ivreg2 FLFP numNative al_mn i.continentFactor (`var' = std_native std_import)[aweight=num_recipes]
	eststo reg2
	sum FLFP if e(sample)
	local mean = r(mean)
	estadd scalar mean = `mean'
	estadd local continent "\multicolumn{1}{c}{Yes}"
	estadd local geographical "\multicolumn{1}{c}{Yes}"
	
	* ors form
	reghdfe FLFP `var' numNative al_mn [aweight=num_recipes], absorb(continentFactor)  
	eststo reg3
	sum FLFP if e(sample)
	local mean = r(mean)
	estadd scalar mean = `mean'
	estadd local continent "\multicolumn{1}{c}{Yes}"
	estadd local geographical "\multicolumn{1}{c}{Yes}"
	
	*reduced form
	reghdfe FLFP std_native std_import numNative al_mn[aweight=num_recipes], absorb(continentFactor) 
	eststo reg4
	sum FLFP if e(sample)
	local mean = r(mean)
	estadd scalar mean = `mean'
	estadd local continent "\multicolumn{1}{c}{Yes}"
	estadd local geographical "\multicolumn{1}{c}{Yes}"
	
	esttab reg1 reg2 reg3 reg4 using "${outputs}/Tables/ivreg_best1st_`var'.tex", ///
se r2 star(* 0.1 ** 0.05 *** .01) keep(std_native std_import `var')label ///
mtitles("First stage" "IV" "OLS" "Reduced form")  ///
s( r2  mean N continent geographical, ///
labels( "\midrule R-squared" "Control Mean" "Number of obs.") fmt( %9.3f %9.3f %9.0g))  style(tex)  ///
nobaselevels  prehead("\begin{tabular}{l*{5}{c}} \hline\hline") ///
fragment postfoot("\hline" "\end{tabular}")replace
	
}

