use "$versatility\first_stage_native_m_c_series.dta", clear


foreach var in rel_EU_HICP  GDP exchange_rate LFP_female  rel_US_PPI CPI {
	gen l`var'=log(`var')
}

keep if fem_lfp==1
keep if year<2020
xtset Country year
 
egen gregion=group(region)

tsline  rel_EU_HICP   if country=="Colombia"

	 cd "$tables"

*--- Regressions 
eststo clear
	eststo: reghdfe LFP_female  rel_EU_HICP  CPI GDP exchange_rate, absorb(country year)
	qui sum `e(depvar)' if e(sample)
	estadd scalar Mean = r(mean)
	
	eststo: reghdfe LFP_female  rel_EU_HICP  CPI GDP exchange_rate, absorb(country year##gregion)
	qui sum `e(depvar)' if e(sample)
	estadd scalar Mean = r(mean)

	 estout using reg_app.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep( rel_EU_HICP ) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 , labels("Mean dep. var." "Observations" "R-squared" ) fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
	
*--- Regressions 
eststo clear
	eststo: reghdfe LFP_female  rel_EU_HICP c.rel_EU_HICP#c.z_pca_recipe  CPI GDP exchange_rate, absorb(country year)
	qui sum `e(depvar)' if e(sample)
	estadd scalar Mean = r(mean)

	eststo: reghdfe LFP_female  rel_EU_HICP  c.rel_EU_HICP#c.z_pca_recipe  CPI GDP exchange_rate, absorb(country year##gregion)
	qui sum `e(depvar)' if e(sample)
	estadd scalar Mean = r(mean)

	
	estout using reg_app_pca.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(rel_EU_HICP c.rel_EU_HICP#c.z_pca_recipe) ///
		varlabels("c.rel_EU_HICP#c.z_pca_recipe" "Relative HICP: Household Appliances x Cuisine complexity") ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 , labels("Mean dep. var." "Observations" "R-squared" ) fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace

*--- Regressions 
eststo clear
	eststo: reghdfe LFP_female  rel_US_PPI   CPI GDP exchange_rate, absorb(country year)
	qui sum `e(depvar)' if e(sample)
	estadd scalar Mean = r(mean)

	eststo: reghdfe LFP_female  rel_US_PPI   CPI GDP exchange_rate, absorb(country year##gregion)
	qui sum `e(depvar)' if e(sample)
	estadd scalar Mean = r(mean)

	
	estout using reg_ppi.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(rel_US_PPI) ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 , labels("Mean dep. var." "Observations" "R-squared" ) fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace

*--- Regressions 
eststo clear
	eststo: reghdfe LFP_female  rel_US_PPI  c.rel_US_PPI#c.z_pca_recipe  CPI GDP exchange_rate, absorb(country year)
	qui sum `e(depvar)' if e(sample)
	estadd scalar Mean = r(mean)

	eststo: reghdfe LFP_female  rel_US_PPI   c.rel_US_PPI#c.z_pca_recipe CPI GDP exchange_rate, absorb(country year##gregion)
	qui sum `e(depvar)' if e(sample)
	estadd scalar Mean = r(mean)


	estout using reg_ppi_pca.tex, ///
		style(tex) ///
		cells(b(star f(3)) se(par f(3))) ///
		starlevels(* 0.10 ** 0.05 *** 0.01) ///
		keep(rel_US_PPI  c.rel_US_PPI#c.z_pca_recipe) ///
		varlabels("c.rel_US_PPI#c.z_pca_recipe" "Relative PPI by Industry: Household Appliance Manufacturing x Cuisine complexity") ///
		label ml(none) collabels(none) ///
		stats(Mean N r2 , labels("Mean dep. var." "Observations" "R-squared" ) fmt(%9.3f %9.1gc %4.3f)) ///
		postfoot("\hline") ///
    replace
 