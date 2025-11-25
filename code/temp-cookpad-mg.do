	
	global cookpad  "C:\Users\mgafargo\Dropbox\food4thought\analysis23\data\coded\cookpad"
	
	use "$cookpad/cookpad_adm0.dta", replace
	
	*-- Rename variables
	ren (emp_ftemp emp_ftemp_pop emp_lfpr emp_work_hours) (ft p2p lfpr hours)
	
	gen log_gdp = ln(GDP)
	drop GDP
	rename log_gdp GDP 
	
	*--- Merge database to distance measures
	merge m:1 adm0 using "$versatility/native_versatility_m_c_dist_all.dta", keep(3)
		
		foreach var of varlist trade* vers* {
    local label : subinstr local var "_" " " , all
    label variable `var' "`label'"
	}
	
	*-- Create Principal Component Index 
	*- Standarized
	foreach v of varlist w_mean_spices median_totaltime median_ingredients {
		sum `v'
		gen z_`v' = (`v' - r(mean)) / r(sd)
	}

	* PCA con las variables estandarizadas
	pca z_w_mean_spices z_median_totaltime z_median_ingredients

	predict pca_index if e(sample), score
	
	label var pca_index "PCA Index"
	
	global c1 "numrecipes"
	global c2 "numrecipes avg_suitability al_mn"
	global c3 "numrecipes avg_suitability al_mn GDP"
	global c4 "numrecipes avg_suitability al_mn precip ph_mn abslat lon GDP"
	global c5 "numrecipes avg_suitability al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability GDP"
	
	global c6 "numrecipes"
	global c7 "numrecipes avg_suitability trade_distCapital_2000 al_mn"
	global c8 "numrecipes avg_suitability trade_distCapital_2000 al_mn GDP"
	global c9 "numrecipes avg_suitability trade_distCapital_2000 al_mn precip ph_mn abslat lon GDP"
	global c10 "numrecipes  avg_suitability trade_distCapital_2000 al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability GDP"
	
	global c11 "numrecipes"
	global c12 "numrecipes avg_suitability trade_distCapital_3000 al_mn"
	global c13 "numrecipes avg_suitability trade_distCapital_3000 al_mn GDP"
	global c14 "numrecipes avg_suitability trade_distCapital_3000 al_mn precip ph_mn abslat lon GDP"
	global c15"numrecipes  avg_suitability trade_distCapital_3000 al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability GDP"

	encode region, gen(region_cat)
	
	*------------------------------------------*
	**#  		        OLS                    *
	*------------------------------------------*
	
	*-------- FLFP --------*
	
	reghdfe lfpr  w_mean_spices ${c`i'} if fem_lfp==1, absorb(region_cat cl_md) vce(robust)
	
	