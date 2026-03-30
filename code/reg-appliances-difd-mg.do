global projectfolder "C:\Users\mgafargo\Dropbox\food4thought\analysis23"
global versatility "$projectfolder\data\coded\iv_versatility"
	global outputs				"$projectfolder/outputs"
	global tables				"$outputs/Tables"
	global figures				"$outputs/Figures"
	
use "$versatility\first_stage_native_m_c_series.dta", clear
bys country year: egen aux=mean(LFP_male)
replace LFP_male=aux if LFP_male==. 
drop if LFP_female==. 

gen period5 = floor(year/5)*5

collapse (mean) median_totaltime median_spices median_ingredients mean_ingredients w_mean_totaltime w_mean_spices numrecipes z_pca_recipe pca_recipe LFP fem_lfp LFP_female LFP_male GDP population CPI exchange_rate US_PPI US_PPI_disc EU_HICP_m EU_HICP rel_US_PPI rel_US_PPI_disc rel_EU_HICP rel_EU_HICP_m numNative numNativeCIAT numSpice avg_suitability lat lon native_versatility native_versatility2 suit_versatility native_spice_vers native_spice_vers2 suit_spice_vers vers* trad*, by(country Country period5 continent region)

xtset Country period

gen gap= LFP_male-LFP_female

foreach var in LFP_male  z_pca_recipe rel_EU_HICP  GDP exchange_rate LFP_female  rel_US_PPI CPI {
	gen l`var'=log(`var')
}

sort Country period
foreach var in LFP_male  z_pca_recipe rel_EU_HICP  GDP exchange_rate LFP_female  rel_US_PPI CPI {
	 gen dl`var'=l`var'-l`var'[_n-1] if Country==Country[_n-1]
	 gen dl`var'1=dl`var'[_n-1] if Country==Country[_n-1]
}
 
 
*keep if period<2020

gen sample=1 if median_totaltime<80 & median_ingredients>5.5
keep if sample==1

egen vers_distCapital_2000_std=std(vers_distCapital_2000 )	
foreach var in  vers_distCapital_2000_std  {
	gen l`var'=log(`var')
}

 
egen gregion=group(region)
egen grcontinent=group(continent)

sum period
local m=r(min)
gen t=period-`m'


line US_PPI period if country=="Colombia", sort
line rel_US_PPI period if country=="Colombia", sort
line dlrel_US_PPI period  if country=="Colombia", sort
twoway (line dlLFP_female period  if country=="Colombia", sort) (line dlrel_US_PPI period  if country=="Colombia", sort) 

line CPI year if country=="Colombia", sort
line rel_US_PPI year if country=="Chile", sort
line dlrel_US_PPI year if country=="Chile", sort
twoway (line dlLFP_female period  if country=="Chile", sort) (line dlrel_US_PPI period  if country=="Chile", sort) 

line rel_US_PPI year if country!="Belarus"  & country!="Brazil", sort by(country)

binscatter dlrel_US_PPI year  


	 cd "$tables/"

	 foreach var in   z_pca_recipe {
	 gen comple_price=z_pca_recipe *rel_EU_HICP
	 gen iv_price=vers_distCapital_2000_std   *rel_EU_HICP
	 }
	 
* Labels
lab var rel_EU_HICP  "Home appliance relative price index"
lab var comple_price "Home appliance relative price index $\times$ Cuisine complexity"
lab var z_pca_recipe "Cuisine complexity"


reghdfe lLFP_female lrel_EU_HICP c.lvers_distCapital_2000_std  lCPI lGDP lexchange_rate [aw=population], absorb(country period) vce(cluster country) 	

reghdfe lLFP_male lrel_EU_HICP c.lvers_distCapital_2000_std  lCPI lGDP lexchange_rate [aw=population], absorb(country period) vce(cluster country) 	
				  
reghdfe lLFP_female c.lrel_EU_HICP##c.lvers_distCapital_2000_std  lCPI lGDP lexchange_rate [aw=population], absorb(country period##gregion) vce(cluster country) 				  

reghdfe lLFP_male c.lrel_EU_HICP##c.lvers_distCapital_2000_std  lCPI lGDP lexchange_rate [w=population], absorb(country year##gregion) vce(cluster country) 	



ivreghdfe LFP_male rel_EU_HICP (comple_price = iv_price) ///
                  CPI GDP exchange_rate   , absorb(country year) first ///
				   vce(cluster country)  
				   
ivreghdfe LFP_female rel_EU_HICP (comple_price = iv_price) ///
                  CPI GDP exchange_rate [w=population] , absorb(country year#gregion) first ///
				   vce(cluster country)  
				   
				  
				  qui sum z_pca_recipe if e(sample)
			local mz = r(mean)
			lincom _b[rel_EU_HICP] + `mz' * _b[comple_price]
 
ivreghdfe LFP_female rel_EU_HICP (comple_price = iv_price) ///
                  CPI GDP exchange_rate [w=population], absorb(country year##grcontinent) first
				  qui sum z_pca_recipe if e(sample)
			local mz = r(mean)	
		lincom _b[rel_EU_HICP] + `mz' * _b[comple_price]



reghdfe gap rel_EU_HICP CPI GDP exchange_rate [aw=population], absorb(country period##gregion)  vce(cluster country) 
reghdfe gap rel_EU_HICP CPI GDP exchange_rate , absorb(country period##gregion)  vce(cluster country) 	
reghdfe gap rel_EU_HICP CPI GDP exchange_rate , absorb(country period)  vce(cluster country) 	
reghdfe gap c.rel_EU_HICP##c.z_pca_recipe  CPI GDP exchange_rate , absorb(country period)  vce(cluster country) 	
reghdfe gap c.rel_EU_HICP##c.z_pca_recipe  CPI GDP exchange_rate , absorb(country period)  vce(cluster country) 	
reghdfe gap c.rel_EU_HICP##c.lvers_distCapital_2000_std  CPI GDP exchange_rate , absorb(country period)  vce(cluster country) 	



reghdfe lLFP_female lrel_EU_HICP lCPI lGDP lexchange_rate [aw=population], absorb(country period##gregion)  vce(cluster country) 	
reghdfe lLFP_female lrel_EU_HICP lCPI lGDP lexchange_rate , absorb(country period##gregion)  vce(cluster country) 	
reghdfe lLFP_female c.lrel_EU_HICP##c.z_pca_recipe lCPI lGDP lexchange_rate , absorb(country period##gregion)  vce(cluster country)
reghdfe lLFP_female c.lrel_EU_HICP##c.z_pca_recipe lCPI lGDP lexchange_rate [aw=population] , absorb(country period##gregion)  vce(cluster country)
			  
			  

reghdfe dlLFP_female dlrel_EU_HICP dlCPI dlGDP dlexchange_rate [aw=population], absorb(country period)  vce(cluster country) 	
			  
reghdfe dlLFP_female dlrel_EU_HICP dlCPI dlGDP dlexchange_rate  , absorb(country period)  vce(cluster country) 	

			  
reghdfe dlLFP_male dlrel_EU_HICP1 dlCPI dlGDP dlexchange_rate  , absorb(country period)  vce(cluster country) 	

reghdfe dlLFP_female (c.dlrel_EU_HICP1##c.z_pca_recipe) dlCPI dlGDP dlexchange_rate [aw=population] , absorb(country period##gregion)  vce(cluster country)
reghdfe dlLFP_female (c.dlrel_EU_HICP1##c.z_pca_recipe) dlCPI dlGDP dlexchange_rate  , absorb(country period##gregion)  vce(cluster country)





				  
*--- Regressions
eststo clear

* (1) OLS (no interaction)
reghdfe LFP_female rel_EU_HICP CPI GDP exchange_rate, absorb(country year)  vce(cluster country) 
qui sum `e(depvar)' if e(sample)
estadd scalar Mean   = r(mean)
estadd scalar ME_rel  = .
eststo m1

* (2) OLS + interaction
reghdfe LFP_female rel_EU_HICP comple_price CPI GDP exchange_rate, absorb(country year) vce(cluster country) 
qui sum `e(depvar)' if e(sample)
estadd scalar Mean   = r(mean)
 

qui sum z_pca_recipe if e(sample)
local mz = r(mean)
lincom _b[rel_EU_HICP] + `mz' * _b[comple_price]
estadd scalar ME_rel = r(estimate)
eststo m2

* (3) IV (interaction is comple_price)
ivreghdfe LFP_female rel_EU_HICP (comple_price = iv_price) ///
                  CPI GDP exchange_rate , absorb(country year) first vce(cluster country) 
qui sum `e(depvar)' if e(sample)
estadd scalar Mean = r(mean)

 
* marginal effect for IV column too (since it has the interaction)
qui sum z_pca_recipe if e(sample)
local mz = r(mean)
 lincom _b[rel_EU_HICP] + `mz' * _b[comple_price]
estadd scalar ME_rel = r(estimate)
eststo m3

*--- Table
esttab using reg_app.tex, ///
    style(tex) fragment booktabs ///
    b(a2) se(a2) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    label keep(rel_EU_HICP comple_price) order(rel_EU_HICP comple_price) ///
    stats(N Mean widstat ME_rel, ///
          labels("Observations" "Mean dep. var." "First-stage F-statistic" ///
                 "Marginal effect of price index at mean complexity")) ///
   posthead("")  prehead(" ")  prefoot("   ") postfoot("\hline") nogaps nomtitle nonotes replace nonumber

	 
	/// male
	
	
eststo clear
* (1) OLS (no interaction)
reghdfe LFP_male rel_EU_HICP CPI GDP exchange_rate, absorb(country year) vce(cluster country) 
qui sum `e(depvar)' if e(sample)
estadd scalar Mean   = r(mean)
estadd scalar ME_rel  = .
eststo m1
* (2) OLS + interaction
reghdfe LFP_male rel_EU_HICP comple_price CPI GDP exchange_rate, absorb(country year) vce(cluster country) 
qui sum `e(depvar)' if e(sample)
estadd scalar Mean   = r(mean)


qui sum z_pca_recipe if e(sample)
local mz = r(mean)
lincom _b[rel_EU_HICP] + `mz' * _b[comple_price]
estadd scalar ME_rel = r(estimate)
eststo m2

* (3) IV (interaction is comple_price)
ivreghdfe LFP_male rel_EU_HICP (comple_price = iv_price) ///
                  CPI GDP exchange_rate, absorb(country year) first vce(cluster country) 
qui sum `e(depvar)' if e(sample)
estadd scalar Mean = r(mean)


* marginal effect for IV column too (since it has the interaction)
qui sum z_pca_recipe if e(sample)
local mz = r(mean)
 lincom _b[rel_EU_HICP] + `mz' * _b[comple_price]
estadd scalar ME_rel = r(estimate)
eststo m3

esttab m* using reg_app-b.tex, ///
    style(tex) fragment booktabs ///
    b(a2) se(a2) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    label keep(rel_EU_HICP comple_price) order(rel_EU_HICP comple_price) ///
    stats(N Mean widstat ME_rel, ///
          labels("Observations" "Mean dep. var." "First-stage F-statistic" ///
                 "Marginal effect of price index at mean complexity")) ///
     prehead("") posthead("   ") prefoot("   ") postfoot("\hline")  nogaps nomtitle nonotes replace nonumber


	
	 
	 
	 
 	 
	 
	 
	 
	 
	 
	 
	 
	 
	 
	 
	 
	 
	 ///
	 lab var rel_EU_HICP "Home appliance relative price index"
	 lab var comple_price  "Home appliance relative price index $\times$ Cuisine complexity "
  
	 
*--- Regressions 
eststo clear

* (1) OLS
eststo: reghdfe LFP_female rel_EU_HICP CPI GDP exchange_rate, absorb(country year)
qui sum `e(depvar)' if e(sample)
estadd scalar Mean = r(mean)
estadd scalar Ffirst = .
estadd local IV "No"

* (2) OLS + comple_price
eststo: reghdfe LFP_female rel_EU_HICP comple_price CPI GDP exchange_rate, absorb(country year)
qui sum `e(depvar)' if e(sample)
estadd scalar Mean = r(mean)
estadd scalar Ffirst = .
estadd local IV "No"

qui: reghdfe LFP_female c.rel_EU_HICP##c.z_pca_recipe ///
         CPI GDP exchange_rate, absorb(country year)
	margins, dydx(rel_EU_HICP) atmeans	 

* (3) IV
eststo: ivreghdfe LFP_female rel_EU_HICP (comple_price = iv_price) CPI GDP exchange_rate, absorb(country year) first
qui sum `e(depvar)' if e(sample)
estadd scalar Mean = r(mean)
*estadd scalar Ffirst = e(rkf)
 estadd scalar Ffirst =e(widstat)

esttab using reg_app.tex, ///
    style(tex) fragment ///
    b(a2) se(a2) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    label keep(rel_EU_HICP comple_price) order(rel_EU_HICP comple_price) ///
    stats(N Mean widstat, ///
          labels("Observations" "Mean dep. var." "First stage F-statistic" )) ///
          nogaps nomtitle nonotes postfoot("\hline") prefoot("") replace

	
	
	 
	
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
 