 **
	
	use "$codedata\iv_versatility\first_stage_native_m_c.dta", clear
	*-- Set controls

	global c6 "numrecipes"
	global c7 "numrecipes avg_suitability trade_distCapital_2000 al_mn"
	global c8 "numrecipes avg_suitability trade_distCapital_2000 al_mn GDP"
	global c9 "numrecipes avg_suitability trade_distCapital_2000 al_mn ph_mn  GDP"
	global c10 "numrecipes  avg_suitability trade_distCapital_2000 al_mn ph_mn rough landlocked  staple_suitability GDP"
	
	global c11 "numrecipes  avg_suitability trade_distCapital_2000 al_mn ph_mn rough landlocked  staple_suitability"
	
	
	 cd "$figures"
	 
	 


* ---- Scheme: clean navy/blue look ----
set scheme s2color   // base; overridden below via graphregion/colors

* Shared style macros
local bg        graphregion(color(white)) bgcolor(white)
local titlesize size(medlarge)
local notesize  size(small)
local export    as(pdf) replace   // PDF = crisp in Beamer



/* =========================================================
   SECTION 1: Spices & Temperature
   ========================================================= */

* ----------------------------------------------------------
* 1A. Weighted scatter + linear fit
* ----------------------------------------------------------
twoway ///
    (scatter median_spices temp ///
        [aw=population], ///
        mcolor("31 73 125") msize(small) msymbol(circle) ) ///
    (lfit median_spices temp  ///
        [aw=population], ///
        lcolor("192 0 0") lwidth(medthick) lpattern(solid)), ///
    `bg' ///
    xtitle("Average Temperature (°C)", `titlesize') ///
    ytitle("Median Number of Spices", `titlesize') ///
    title("Spice Use and Temperature", `titlesize' color("31 73 125")) ///
    legend(order(1 "Country " 2 "Linear fit") ///
           ring(0) position(1) cols(1) size(small) ///
           region(lcolor(none))) ///


graph export "scatter_spices_temp.pdf", `export'

/*
* ----------------------------------------------------------
* 1B. Binscatter — no FE
* ----------------------------------------------------------

binscatter median_spices temp, ///
    mcolor("31 73 125") lcolor("31 73 125") ///
    `bg' ///
    xtitle("Average Temperature (°C)", `titlesize') ///
    ytitle("Median Number of Spices", `titlesize') ///
    title("Spice Use and Temperature", `titlesize' color("31 73 125")) ///
    note("Note: Binscatter with 20 equal-sized bins.", `notesize' color(gray))

graph export "binscatter_spices_temp_noFE.pdf", `export'


* ----------------------------------------------------------
* 1C. Binscatter — absorb continent FE
* ----------------------------------------------------------


binscatter median_spices temp, absorb(continent) ///
    mcolor("31 73 125") lcolor("31 73 125") ///
    `bg' ///
    xtitle("Average Temperature (°C)", `titlesize') ///
    ytitle("Median Number of Spices (residualized)", `titlesize') ///
    title("Spice Use and Temperature", `titlesize' color("31 73 125")) ///
    note("Note: Binscatter conditional on continent fixed effects.", `notesize' color(gray))

graph export "binscatter_spices_temp_contFE.pdf", `export'


* ----------------------------------------------------------
* 1D. Regression table — all control sets (c7–c10)
* ----------------------------------------------------------
eststo clear

forvalue i = 7/10 {
    eststo m_spices_`i': reghdfe median_spices temp ${c`i'}, absorb(continent) vce(robust)
}

* Column labels matching your table style
local colnames `" "Baseline" "Add Suitability" "Add Climate & Geo" "Full Controls" "'

esttab m_spices_7 m_spices_8 m_spices_9 m_spices_10 ///
    using "reg_spices_temp.tex", replace ///
    booktabs b(3) se(3) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp) ///
    varlabels(temp "Average Temperature (°C)") ///
    mtitles("Baseline" "Add Suitability" "Add Climate \& Geo" "Full Controls") ///
    mgroups("Dependent variable: Median number of spices", ///
            pattern(1 0 0 0) ///
            prefix(\multicolumn{@span}{c}{) suffix(}) ///
            span erepeat(\cmidrule(lr){@span})) ///
    stats(N r2 ymean, ///
          labels("Observations" "\$R^2\$" "Mean dep. var.") ///
          fmt(%9.0fc %9.3f %9.3f)) ///
    scalars("ymean Mean dep. var.") ///
    addnotes("Robust standard errors in parentheses." ///
             "All specifications include continent fixed effects." ///
             "Controls: (1) Baseline; (2) + Mean Suitability;" ///
             "(3) + GDP, Trade Distance, Altitude, pH, Roughness, Landlocked;" ///
             "(4) + Individual \& household controls.") ///
    label nonumbers nonote substitute(\_ _) ///
fragment


/* =========================================================
   SECTION 2: Cooking Time & Temperature
   ========================================================= */

* ----------------------------------------------------------
* 2A. Weighted scatter + linear fit
* ----------------------------------------------------------
twoway ///
    (scatter w_mean_totaltime temp ///
        [aw=population], ///
        mcolor("31 73 125") msize(small) msymbol(circle) ) ///
    (lfit w_mean_totaltime temp ///
        [aw=population], ///
        lcolor("192 0 0") lwidth(medthick) lpattern(solid)), ///
    `bg' ///
    xtitle("Average Temperature (°C)", `titlesize') ///
    ytitle("Avg. Cooking Time (minutes)", `titlesize') ///
    title("Cooking Time and Temperature", `titlesize' color("31 73 125")) ///
    legend(order(1 "Country " 2 "Linear fit") ///
           ring(0) position(1) cols(1) size(small) ///
           region(lcolor(none))) ///
    note("Note: Population-weighted scatter.", `notesize' color(gray))

graph export "scatter_time_temp.pdf", `export'


* ----------------------------------------------------------
* 2B. Binscatter — no FE
* ----------------------------------------------------------
binscatter w_mean_totaltime temp, ///
    mcolor("31 73 125") lcolor("31 73 125") ///
    `bg' ///
    xtitle("Average Temperature (°C)", `titlesize') ///
    ytitle("Avg. Cooking Time (minutes)", `titlesize') ///
    title("Cooking Time and Temperature", `titlesize' color("31 73 125")) ///
    note("Note: Binscatter with 20 equal-sized bins.", `notesize' color(gray))

graph export "binscatter_time_temp_noFE.pdf", `export'


* ----------------------------------------------------------
* 2C. Binscatter — absorb continent FE
* ----------------------------------------------------------
binscatter w_mean_totaltime temp, absorb(continent) ///
    mcolor("31 73 125") lcolor("31 73 125") ///
    `bg' ///
    xtitle("Average Temperature (°C)", `titlesize') ///
    ytitle("Avg. Cooking Time (residualized)", `titlesize') ///
    title("Cooking Time and Temperature", `titlesize' color("31 73 125")) ///
    note("Note: Binscatter conditional on continent fixed effects.", `notesize' color(gray))

graph export "binscatter_time_temp_contFE.pdf", `export'


* ----------------------------------------------------------
* 2D. Regression table — all control sets (c7–c10)
* ----------------------------------------------------------
eststo clear

forvalue i = 7/10 {
    eststo m_time_`i': reghdfe w_mean_totaltime temp ${c`i'}, absorb(continent) vce(robust)
}

esttab m_time_7 m_time_8 m_time_9 m_time_10 ///
    using "reg_time_temp.tex", replace ///
    booktabs b(3) se(3) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp) ///
    varlabels(temp "Average Temperature (°C)") ///
    mtitles("Baseline" "Add Suitability" "Add Climate \& Geo" "Full Controls") ///
    mgroups("Dependent variable: Average cooking time (minutes)", ///
            pattern(1 0 0 0) ///
            prefix(\multicolumn{@span}{c}{) suffix(}) ///
            span erepeat(\cmidrule(lr){@span})) ///
    stats(N r2 ymean, ///
          labels("Observations" "\$R^2\$" "Mean dep. var.") ///
          fmt(%9.0fc %9.3f %9.3f)) ///
    addnotes("Robust standard errors in parentheses." ///
             "All specifications include continent fixed effects." ///
             "Controls: (1) Baseline; (2) + Mean Suitability;" ///
             "(3) + GDP, Trade Distance, Altitude, pH, Roughness, Landlocked;" ///
             "(4) + Individual \& household controls.") ///
    label nonumbers nonote substitute(\_ _) ///
    fragment
	
	

/* =========================================================
   SECTION 3: Food preservation & Temperature
   ========================================================= */

   */
   
* Merge recipe-level data to compute share of recipes with >1 day preparation time
 
preserve
use "$recipes\recipe_all_countries.dta", clear
keep country totaltime numberofspices
gen slow = (totaltime > 1440)
gen counter = 1
replace slow = . if totaltime == .
collapse (mean) slow totaltime numberofspices (sum) counter, by(country)
tempfile recipe_raw
save `recipe_raw'
restore

duplicates drop country, force
drop _merge
merge 1:1 country using `recipe_raw', keep(1 3)

* Replace to % units

replace slow = slow * 100

* 3A. Map of share preservation

*twoway scatter slow temp , mlabel(adm0)



* ----------------------------------------------------------
* 3A. Weighted scatter + linear fit
* ----------------------------------------------------------
twoway ///
    (scatter slow temp ///
        [aw=population], ///
        mcolor("31 73 125") msize(small) msymbol(circle) ) ///
    (lfit slow temp ///
        [aw=population], ///
        lcolor("192 0 0") lwidth(medthick) lpattern(solid)), ///
    `bg' ///
    xtitle("Average Temperature (°C)", `titlesize') ///
    ytitle("Share >1 day preparation time", `titlesize') ///
    title("Food Preservation and Temperature", `titlesize' color("31 73 125")) ///
    legend(order(1 "Country " 2 "Linear fit") ///
           ring(0) position(1) cols(1) size(small) ///
           region(lcolor(none))) ///
    note("Note: Population-weighted scatter.", `notesize' color(gray))


	
graph export "scatter_gr1d_temp.pdf", `export'


/*
* ----------------------------------------------------------
* 3B. Binscatter — no FE
* ----------------------------------------------------------
binscatter slow temp, ///
    mcolor("31 73 125") lcolor("31 73 125") ///
    `bg' ///
    xtitle("Average Temperature (°C)", `titlesize') ///
    ytitle("Avg. Cooking Time (minutes)", `titlesize') ///
    title("Cooking Time and Temperature", `titlesize' color("31 73 125")) ///
    note("Note: Binscatter with 20 equal-sized bins.", `notesize' color(gray))

graph export "binscatter_gr1d_temp_noFE.pdf", `export'



* ----------------------------------------------------------
* 3C. Binscatter — absorb continent FE
* ----------------------------------------------------------
binscatter slow temp, absorb(continent) ///
    mcolor("31 73 125") lcolor("31 73 125") ///
    `bg' ///
    xtitle("Average Temperature (°C)", `titlesize') ///
    ytitle("Avg. Cooking Time (residualized)", `titlesize') ///
    title("Cooking Time and Temperature", `titlesize' color("31 73 125")) ///
    note("Note: Binscatter conditional on continent fixed effects.", `notesize' color(gray))

graph export "binscatter_gr1d_temp_contFE.pdf", `export'



* ----------------------------------------------------------
* 3D. Regression table — all control sets (c7–c10)
* ----------------------------------------------------------
eststo clear

forvalue i = 7/10 {
    quietly sum slow if e(sample) 
    eststo m_time_`i': reghdfe slow temp ${c`i'}, absorb(continent) vce(robust)
    quietly sum slow if e(sample)
    estadd scalar ymean = r(mean)
}

esttab m_time_7 m_time_8 m_time_9 m_time_10 ///
    using "reg_gr1d_temp.tex", replace ///
    booktabs b(3) se(3) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp) ///
    varlabels(temp "Average Temperature (°C)") ///
    mtitles("Baseline" "Add Suitability" "Add Climate \& Geo" "Full Controls") ///
    mgroups("Dependent variable: Share $>$ 1 day preparation time", ///
            pattern(1 0 0 0) ///
            prefix(\multicolumn{@span}{c}{) suffix(}) ///
            span erepeat(\cmidrule(lr){@span})) ///
    stats(N r2 ymean, ///
          labels("Observations" "\$R^2\$" "Mean dep. var.") ///
          fmt(%9.0fc %9.3f %9.3f)) ///
    addnotes("Robust standard errors in parentheses." ///
             "All specifications include continent fixed effects." ///
             "Controls: (1) Baseline; (2) + Mean Suitability;" ///
             "(3) + GDP, Trade Distance, Altitude, pH, Roughness, Landlocked;" ///
             "(4) + Individual \& household controls.") ///
    label nonumbers nonote substitute(\_ _) ///
    fragment
	
	

/* =========================================================
   SECTION 4: Food preservation & Patience
   ========================================================= */

* Load and merge GPS data
preserve
use "C:\Users\stevebc\Dropbox\food4thought\analysis23\data\raw\GPS\country.dta", clear
rename isocode adm0
tempfile adm0_gps
save `adm0_gps'
restore

cap drop _merge
merge 1:1 adm0 using `adm0_gps'
drop _merge

* Standardize variable before regression
foreach var in totaltime slow patience risktaking posrecip negrecip altruism trust {
    egen `var'_std = std(`var')
}

label variable slow_std "\% $>$ 1 day prep. time"
label variable totaltime_std "Avg. cooking time"

reg patience totaltime, robust
local r2: display %4.3f e(r2)
	 
* Table: patience ~ totaltime_std
local x "totaltime_std"
eststo clear
eststo col1: reg patience_std `x', robust
eststo col2: reg risktaking_std `x', robust
eststo col3: reg posrecip_std `x', robust
eststo col4: reg negrecip_std `x', robust
eststo col5: reg altruism_std `x', robust
eststo col6: reg trust_std `x', robust

foreach est in col1 col2 col3 col4 col5 col6 {
    quietly sum `x' if e(sample)
    estadd scalar ymean = r(mean), replace: `est'
}

esttab col1 col2 col3 col4 col5 col6 ///
    using "${tables}/reg_patience_totalTime.tex", replace ///
    booktabs b(3) se(3) star(* 0.10 ** 0.05 *** 0.01) ///
    drop(_cons) ///
    mtitles("Patience" "Risk taking" "Pos. reciprocity" "Neg. reciprocity" "Altruism" "Trust") ///
    stats(N r2, ///
          labels("Observations" "\$R^2\$") ///
          fmt(%9.0fc %9.3f)) ///
    label nonumbers nonote substitute(\_ _) ///
    fragment


* Panel A: Unconditional
local x "slow_std"
eststo clear
eststo col1: reg patience_std `x', robust
eststo col2: reg risktaking_std `x', robust
eststo col3: reg posrecip_std `x', robust
eststo col4: reg negrecip_std `x', robust
eststo col5: reg altruism_std `x', robust
eststo col6: reg trust_std `x', robust
foreach est in col1 col2 col3 col4 col5 col6 {
    quietly sum `x' if e(sample)
    estadd scalar ymean = r(mean), replace: `est'
}
esttab col1 col2 col3 col4 col5 col6 ///
    using "${tables}/reg_patience_gt1dayTime_wContr.tex", replace ///
    booktabs b(3) se(3) star(* 0.10 ** 0.05 *** 0.01) ///
    drop(_cons) ///
    mgroups("Patience" "Risk taking" "Pos. reciprocity" "Neg. reciprocity" "Altruism" "Trust", ///
            pattern(1 1 1 1 1 1) prefix(\multicolumn{1}{c}{) suffix(})) ///
    posthead("\midrule" "& \multicolumn{6}{c}{\textit{Panel A: Unconditional}} \\" ///
             "\cmidrule{2-7}" "\addlinespace") ///
    stats(N r2, labels("Observations" "\$R^2\$") fmt(%9.0fc %9.3f)) ///
    nomtitles nonumbers nonote substitute(\_ _) ///
    varlabels(slow_std "\% \$>\$ 1 day prep. time") ///
    fragment
	
local x "totaltime_std"

* Panel B: Continent FE
eststo clear
eststo col1: reghdfe patience_std `x' $c11, absorb(continent) vce(robust)
eststo col2: reghdfe risktaking_std `x' $c11, absorb(continent) vce(robust)
eststo col3: reghdfe posrecip_std `x' $c11, absorb(continent) vce(robust)
eststo col4: reghdfe negrecip_std `x' $c11, absorb(continent) vce(robust)
eststo col5: reghdfe altruism_std `x' $c11, absorb(continent) vce(robust)
eststo col6: reghdfe trust_std `x' $c11, absorb(continent) vce(robust)
foreach est in col1 col2 col3 col4 col5 col6 {
    quietly sum `x' if e(sample)
    estadd scalar ymean = r(mean), replace: `est'
}
esttab col1 col2 col3 col4 col5 col6 ///
    using "${tables}/reg_patience_gt1dayTime_wContr.tex", append ///
    booktabs b(3) se(3) star(* 0.10 ** 0.05 *** 0.01) ///
    drop(_cons) ///
    posthead("& \multicolumn{6}{c}{\textit{Panel B: Continent FE}} \\" ///
             "\cmidrule{2-7}" "\addlinespace") ///
    stats(N r2, labels("Observations" "\$R^2\$") fmt(%9.0fc %9.3f)) ///
    nomtitles nonumbers nonote substitute(\_ _) ///
    varlabels(slow_std "\% \$>\$ 1 day prep. time") ///
    fragment
	
	

* Table: patience ~ slow_std
local x "slow_std"
eststo clear
eststo col1: reg patience_std `x', robust
eststo col2: reg risktaking_std `x', robust
eststo col3: reg posrecip_std `x', robust
eststo col4: reg negrecip_std `x', robust
eststo col5: reg altruism_std `x', robust
eststo col6: reg trust_std `x', robust

foreach est in col1 col2 col3 col4 col5 col6 {
    quietly sum `x' if e(sample)
    estadd scalar ymean = r(mean), replace: `est'
}

esttab col1 col2 col3 col4 col5 col6 ///
    using "${tables}/reg_patience_gt1dayTime.tex", replace ///
    booktabs b(3) se(3) star(* 0.10 ** 0.05 *** 0.01) ///
    drop(_cons) ///
    mtitles("Patience" "Risk taking" "Pos. reciprocity" "Neg. reciprocity" "Altruism" "Trust") ///
    stats(N r2, ///
          labels("Observations" "\$R^2\$") ///
          fmt(%9.0fc %9.3f)) ///
    label nonumbers nonote substitute(\_ _) ///
    fragment
	
	

* ----------------------------------------------------------
* 4B. Weighted scatter + linear fit
* ----------------------------------------------------------
twoway ///
    (scatter patience slow ///
        [aw=population], ///
        mcolor("31 73 125") msize(small) msymbol(circle) ) ///
    (lfit patience slow ///
        [aw=population], ///
        lcolor("192 0 0") lwidth(medthick) lpattern(solid)), ///
    `bg' ///
    xtitle("Share >1 day preparation time", `titlesize') ///
    ytitle("Patience", `titlesize') ///
    title("Food Preservation and Patience", `titlesize' color("31 73 125")) ///
    legend(order(1 "Country " 2 "Linear fit") ///
           ring(0) position(1) cols(1) size(small) ///
           region(lcolor(none))) ///
    note("Note: Population-weighted scatter.", `notesize' color(gray))


	
graph export "scatter_patience_gr1d.pdf", replace



* ----------------------------------------------------------
* 3B. Binscatter — no FE
* ----------------------------------------------------------
binscatter patience slow, ///
    mcolor("31 73 125") lcolor("31 73 125") ///
    `bg' ///
    xtitle("Share >1 day preparation time", `titlesize') ///
    ytitle("Patience", `titlesize') ///
    title("Food Preservation and Patience", `titlesize' color("31 73 125")) ///
    note("Note: Binscatter with 20 equal-sized bins.", `notesize' color(gray))

graph export "scatter_patience_gr1d_noFE.pdf", replace


* ----------------------------------------------------------
* 3C. Binscatter — absorb continent FE
* ----------------------------------------------------------
binscatter patience slow, absorb(continent) ///
    mcolor("31 73 125") lcolor("31 73 125") ///
    `bg' ///
    xtitle("Share >1 day preparation time", `titlesize') ///
    ytitle("Patience", `titlesize') ///
    title("Food Preservation and Patience", `titlesize' color("31 73 125")) ///
    note("Note: Binscatter conditional on continent fixed effects.", `notesize' color(gray))

graph export "scatter_patience_gr1d_contFE.pdf", replace
	
	

* ----------------------------------------------------------
* 4. Spices and Altruism
* ----------------------------------------------------------
	
* Merge in spice use
merge 1:1 country using "$codedata\recipes\ingredients\stata_merge\country_category_shares.dta"
drop _merge

binscatter altruism spice, absorb(continent) ///
    mcolor("31 73 125") lcolor("31 73 125") ///
    `bg' ///
    xtitle("Share ingredients that are spices", `titlesize') ///
    ytitle("Altruism", `titlesize') ///
    title("Spice Use and Altruism", `titlesize' color("31 73 125")) ///
    note("Note: Binscatter conditional on continent fixed effects.", `notesize' color(gray))

graph export "scatter_altruism_gr1d_contFE.pdf", replace
	


* Panel A: Unconditional
local x "spice"
eststo clear
eststo col1: reg patience_std `x', robust
eststo col2: reg risktaking_std `x', robust
eststo col3: reg posrecip_std `x', robust
eststo col4: reg negrecip_std `x', robust
eststo col5: reg altruism_std `x', robust
eststo col6: reg trust_std `x', robust
foreach est in col1 col2 col3 col4 col5 col6 {
    quietly sum `x' if e(sample)
    estadd scalar ymean = r(mean), replace: `est'
}
esttab col1 col2 col3 col4 col5 col6 ///
    using "${tables}/reg_altruism_spices.tex", replace ///
    booktabs b(3) se(3) star(* 0.10 ** 0.05 *** 0.01) ///
    drop(_cons) ///
    mgroups("Patience" "Risk taking" "Pos. reciprocity" "Neg. reciprocity" "Altruism" "Trust", ///
            pattern(1 1 1 1 1 1) prefix(\multicolumn{1}{c}{) suffix(})) ///
    posthead("\midrule" "& \multicolumn{6}{c}{\textit{Panel A: Unconditional}} \\" ///
             "\cmidrule{2-7}" "\addlinespace") ///
    stats(N r2, labels("Observations" "\$R^2\$") fmt(%9.0fc %9.3f)) ///
    nomtitles nonumbers nonote substitute(\_ _) ///
    varlabels(slow_std "\% \$>\$ 1 day prep. time") ///
    fragment
	
local x "spice"

* Panel B: Continent FE
eststo clear
eststo col1: reghdfe patience_std `x' , absorb(continent) vce(robust)
eststo col2: reghdfe risktaking_std `x' , absorb(continent) vce(robust)
eststo col3: reghdfe posrecip_std `x' , absorb(continent) vce(robust)
eststo col4: reghdfe negrecip_std `x' , absorb(continent) vce(robust)
eststo col5: reghdfe altruism_std `x' , absorb(continent) vce(robust)
eststo col6: reghdfe trust_std `x' , absorb(continent) vce(robust)
foreach est in col1 col2 col3 col4 col5 col6 {
    quietly sum `x' if e(sample)
    estadd scalar ymean = r(mean), replace: `est'
}
esttab col1 col2 col3 col4 col5 col6 ///
    using "${tables}/reg_altruism_spices.tex", append ///
    booktabs b(3) se(3) star(* 0.10 ** 0.05 *** 0.01) ///
    drop(_cons) ///
    posthead("& \multicolumn{6}{c}{\textit{Panel B: Continent FE}} \\" ///
             "\cmidrule{2-7}" "\addlinespace") ///
    stats(N r2, labels("Observations" "\$R^2\$") fmt(%9.0fc %9.3f)) ///
    nomtitles nonumbers nonote substitute(\_ _) ///
    varlabels(slow_std "\% \$>\$ 1 day prep. time") ///
    fragment