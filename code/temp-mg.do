   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *              This dofile runs reduced form estimation	        	  *
   *																	  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Margarita Gafaro
   ** Created: 			20250915
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Oct 7, 2023

// reduced form estimation 
// m gafaro 
// 09152025

*glo dir "C:\Users\mgafargo\Dropbox\food4thought\analysis23\"
 
*----------------------------------*
*       	  Graphs 			   *
*----------------------------------*

use "$codedata\iv_versatility\first_stage_dataset_native_m_c.dta", clear
 
 sum native_versatility native_versatility2 suit_versatility
 
 scatter native_versatility native_versatility2
 scatter   native_versatility2 suit_versatility

histogram native_versatility2

histogram suit_versatility

lab var median_spices "Median spices"
lab var median_totaltime "Median cooking time" 
rename native_versatility versatility

 cd "$dir\outputs\Figures"
 
 //1. Figures to motivate the analysis 
  twoway ///
    (scatter FLFP median_totaltime if continent_code==1, mlabel(adm0) msymbol(none) mlabcolor(red) mlabposition(0) mlabsize(small)) ///
    (scatter FLFP median_totaltime if continent_code==2, mlabel(adm0) msymbol(none) mlabcolor(blue) mlabposition(0) mlabsize(small)) ///
    (scatter FLFP median_totaltime if continent_code==3, mlabel(adm0) msymbol(none) mlabcolor(green) mlabposition(0) mlabsize(small)) ///
    (scatter FLFP median_totaltime if continent_code==4, mlabel(adm0) msymbol(none) mlabcolor(orange) mlabposition(0) mlabsize(small)) ///
    (scatter  FLFP median_totaltime if continent_code==5, mlabel(adm0) msymbol(none) mlabcolor(purple) mlabposition(0) mlabsize(small)) ///
    (scatter FLFP median_totaltime if continent_code==6, mlabel(adm0) msymbol(none) mlabcolor(brown) mlabposition(0) mlabsize(small)), legend(off)
graph export  "raw_time.png", replace 

 twoway ///
    (scatter FLFP median_spices if continent_code==1, mlabel(adm0) msymbol(none) mlabcolor(red) mlabposition(0) mlabsize(small)) ///
    (scatter FLFP  median_spices if continent_code==2, mlabel(adm0) msymbol(none) mlabcolor(blue) mlabposition(0) mlabsize(small)) ///
    (scatter FLFP median_spices  if continent_code==3, mlabel(adm0) msymbol(none) mlabcolor(green) mlabposition(0) mlabsize(small)) ///
    (scatter FLFP median_spices if continent_code==4, mlabel(adm0) msymbol(none) mlabcolor(orange) mlabposition(0) mlabsize(small)) ///
    (scatter  FLFP median_spices if continent_code==5, mlabel(adm0) msymbol(none) mlabcolor(purple) mlabposition(0) mlabsize(small)) ///
    (scatter FLFP median_spices if continent_code==6, mlabel(adm0) msymbol(none) mlabcolor(brown) mlabposition(0) mlabsize(small)), legend(off) 
graph export  "raw_spices.png", replace 

 twoway ///
    (scatter FLFP w_mean_spices if continent_code==1, mlabel(adm0) msymbol(none) mlabcolor(red) mlabposition(0) mlabsize(small)) ///
    (scatter FLFP  w_mean_spices if continent_code==2, mlabel(adm0) msymbol(none) mlabcolor(blue) mlabposition(0) mlabsize(small)) ///
    (scatter FLFP w_mean_spices  if continent_code==3, mlabel(adm0) msymbol(none) mlabcolor(green) mlabposition(0) mlabsize(small)) ///
    (scatter FLFP w_mean_spices if continent_code==4, mlabel(adm0) msymbol(none) mlabcolor(orange) mlabposition(0) mlabsize(small)) ///
    (scatter  FLFP w_mean_spices if continent_code==5, mlabel(adm0) msymbol(none) mlabcolor(purple) mlabposition(0) mlabsize(small)) ///
    (scatter FLFP w_mean_spices if continent_code==6, mlabel(adm0) msymbol(none) mlabcolor(brown) mlabposition(0) mlabsize(small)), legend(off)  
graph export  "raw_mspices.png", replace 	
  
  binscatter FLFP median_totaltime,  savegraph("scat_time.png") replace xtitle("Median cooking time") 
 binscatter FLFP median_spices,   savegraph("scat_spices.png" )  replace xtitle("Median  spices") 
 
  binscatter FLFP w_mean_spices,   savegraph("scat_mean_spices.png" )  replace xtitle("Mean  spices") 
 
 
twoway ///
    (scatter median_totaltime median_spices if continent_code==1, mlabel(adm0) msymbol(none) mlabcolor(red) mlabposition(0) mlabsize(small)) ///
    (scatter median_totaltime median_spices if continent_code==2, mlabel(adm0) msymbol(none) mlabcolor(blue) mlabposition(0) mlabsize(small)) ///
    (scatter median_totaltime median_spices if continent_code==3, mlabel(adm0) msymbol(none) mlabcolor(green) mlabposition(0) mlabsize(small)) ///
    (scatter median_totaltime median_spices if continent_code==4, mlabel(adm0) msymbol(none) mlabcolor(orange) mlabposition(0) mlabsize(small)) ///
    (scatter median_totaltime median_spices if continent_code==5, mlabel(adm0) msymbol(none) mlabcolor(purple) mlabposition(0) mlabsize(small)) ///
    (scatter median_totaltime median_spices if continent_code==6, mlabel(adm0) msymbol(none) mlabcolor(brown) mlabposition(0) mlabsize(small)), legend(off)
graph export  "time_spices.png", replace 
	
	
twoway ///
    (scatter median_totaltime w_mean_spices if continent_code==1, mlabel(adm0) msymbol(none) mlabcolor(red) mlabposition(0) mlabsize(small)) ///
    (scatter median_totaltime w_mean_spices if continent_code==2, mlabel(adm0) msymbol(none) mlabcolor(blue) mlabposition(0) mlabsize(small)) ///
    (scatter median_totaltime w_mean_spices if continent_code==3, mlabel(adm0) msymbol(none) mlabcolor(green) mlabposition(0) mlabsize(small)) ///
    (scatter median_totaltime w_mean_spices if continent_code==4, mlabel(adm0) msymbol(none) mlabcolor(orange) mlabposition(0) mlabsize(small)) ///
    (scatter median_totaltime w_mean_spices if continent_code==5, mlabel(adm0) msymbol(none) mlabcolor(purple) mlabposition(0) mlabsize(small)) ///
    (scatter median_totaltime w_mean_spices if continent_code==6, mlabel(adm0) msymbol(none) mlabcolor(brown) mlabposition(0) mlabsize(small)), legend(off)
		graph export  "time_mspices.png", replace 
		
 
*----------------------------------*
*       	 Regressions		   *
*----------------------------------*
 
global c1 "numrecipes"
global c2 "numrecipes avg_suitability  al_mn"
global c3 "numrecipes avg_suitability  al_mn precip ph_mn abslat lon "
global c4 "numrecipes  avg_suitability  al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability "

*reghdfe FLFP median_spices numrecipes avg_suitability  al_mn  pt_mn ph_mn lat lon, absorb(continent cl_md)
reghdfe FLFP median_spices $c4, absorb(continent cl_md)
cap drop s
gen s=1 if  e(sample)
global s1 " if s==1"
global s2 "if median_totaltime<90 &  s==1"  
global s3 "if  cookpad==1 &  s==1"  



 //reduced form 
 cd "$dir\outputs\Tables"
forvalue j=1/3 { 
eststo clear
forvalue i=1/4{ 
eststo: reghdfe FLFP median_totaltime ${c`i'} ${s`j'}, absorb(continent)
 }
forvalue i=1/4{ 
eststo: reghdfe FLFP median_spices ${c`i'}  ${s`j'}, absorb(continent)
 }
 forvalue i=1/4{ 
eststo: reghdfe FLFP w_mean_spices ${c`i'}  ${s`j'}, absorb(continent)
 }
estout using reg-ols-s`j'.tex, style(tex) cells(b(star f(3)) se(par f(3))) starlevels(* 0.10 ** 0.05 *** 0.01)  order(median_totaltime median_spices w_mean_spices) drop(_cons) label  ml(none) collabels(none) stats(j N r2  , labels(" " "Observations" "R-squared"   ) fmt(%9.1gc %9.1gc %4.3f %9.2fc)) replace

} 



// first stage 
forvalue j=1/3 { 
eststo clear
forvalue i=1/4{ 
eststo: reghdfe   median_totaltime native_versatility2 ${c`i'}  ${s`j'}, absorb(continent)
}
 
forvalue i=1/4{ 
eststo: reghdfe   median_totaltime suit_versatility ${c`i'}  ${s`j'}, absorb(continent)
}
 
 forvalue i=1/4{ 
eststo: reghdfe   median_totaltime  versatility ${c`i'} ${s`j'}, absorb(continent)
}
 
estout using reg-fs-time-s`j'.tex, style(tex) cells(b(star f(3)) se(par f(3))) starlevels(* 0.10 ** 0.05 *** 0.01)   order( native_versatility2 suit_versatility  versatility)  drop(_cons) label  ml(none) collabels(none) stats(j N r2  , labels(" " "Observations" "R-squared"   ) fmt(%9.1gc %9.1gc %4.3f %9.2fc)) replace
} 

forvalue j=1/3 { 
eststo clear
forvalue i=1/4{ 
eststo: reghdfe   median_spices native_versatility2 ${c`i'}  ${s`j'}, absorb(continent)
}
 
forvalue i=1/4{ 
eststo: reghdfe   median_spices suit_versatility ${c`i'}  ${s`j'}, absorb(continent)
}
 
 forvalue i=1/4{ 
eststo: reghdfe   median_spices  versatility ${c`i'} ${s`j'}, absorb(continent)
}
 
  
estout using reg-fs-spices-s`j'.tex, style(tex) cells(b(star f(3)) se(par f(3))) starlevels(* 0.10 ** 0.05 *** 0.01)  order( native_versatility2 suit_versatility  versatility)  drop(_cons) label  ml(none) collabels(none) stats(j N r2  , labels(" " "Observations" "R-squared"   ) fmt(%9.1gc %9.1gc %4.3f %9.2fc)) replace
} 

forvalue j=1/3 { 
eststo clear
forvalue i=1/4{ 
eststo: reghdfe    w_mean_spices native_versatility2 ${c`i'}  ${s`j'}, absorb(continent)
}
 
forvalue i=1/4{ 
eststo: reghdfe    w_mean_spices suit_versatility ${c`i'}  ${s`j'}, absorb(continent)
}
 
 forvalue i=1/4{ 
eststo: reghdfe   w_mean_spices  versatility ${c`i'} ${s`j'}, absorb(continent)
}
 
  
estout using reg-fs-wspices-s`j'.tex, style(tex) cells(b(star f(3)) se(par f(3))) starlevels(* 0.10 ** 0.05 *** 0.01)  order( native_versatility2 suit_versatility  versatility)  drop(_cons) label  ml(none) collabels(none) stats(j N r2  , labels(" " "Observations" "R-squared"   ) fmt(%9.1gc %9.1gc %4.3f %9.2fc)) replace
} 



foreach j in 1 2 3 4 6  {
tab continent_code if continent_code==`j'
 reg    median_totaltime versatility $c3   if continent_code==`j'   
}


 reg    median_totaltime  versatility $c4   if  (country!="Bolivia" & country!="Paraguay")
 
 
 {
****************************************************
/*






reghdfe  median_totaltime native_versatility2  , absorb(continent)
reghdfe median_totaltime native_versatility2 numrecipes avg_suitability  al_mn , absorb(continent cl_md)
reghdfe median_totaltime native_versatility2 numrecipes avg_suitability  al_mn pt_mn ph_mn lat lon, absorb(continent cl_md)

reghdfe  median_spices native_versatility2  , absorb(continent)
reghdfe median_spices native_versatility2 numrecipes avg_suitability  al_mn , absorb(continent cl_md)
reghdfe median_spices native_versatility2 numrecipes avg_suitability  al_mn pt_mn ph_mn lat lon, absorb(continent cl_md)





// FLFP - time 
// whole sample
histogram median_totaltime
scatter FLFP median_totaltime  
binscatter FLFP median_totaltime  
binscatter FLFP median_totaltime, absorb(continent)


//cookpad sample 
scatter FLFP median_totaltime if cookpad==1
binscatter FLFP median_totaltime if cookpad==1 
binscatter FLFP median_totaltime if   cookpad==1, absorb(continent)

reghdfe FLFP median_totaltime , absorb(continent)
reghdfe FLFP median_totaltime if median_totaltime<90, absorb(continent)
reghdfe FLFP median_totaltime if median_totaltime<90 & cookpad==1, absorb(continent)

// spices 
scatter FLFP median_spices  
binscatter FLFP median_spices  
binscatter FLFP median_spices if cookpad==1 
binscatter FLFP median_spices if   cookpad==1, absorb(continent)


 
reghdfe FLFP median_spices numrecipes , absorb(continent)
reghdfe FLFP median_spices   if   cookpad==1, absorb(continent)



// First stage 
// native 
histogram native_versatility2
scatter  median_totaltime native_versatility2
binscatter   median_totaltime native_versatility2
binscatter   median_totaltime native_versatility2 if median_totaltime<90
binscatter  median_totaltime native_versatility2 if median_totaltime<90, absorb(continent)
 


reghdfe  median_totaltime native_versatility2  , absorb(continent)

// suit 
histogram suit_versatility
scatter  median_totaltime suit_versatility
binscatter   median_totaltime suit_versatility
binscatter   median_totaltime suit_versatility if median_totaltime<90
binscatter  median_totaltime suit_versatility if median_totaltime<90, absorb(continent)

reghdfe  median_totaltime suit_versatility    , absorb(continent)
reghdfe  median_totaltime suit_versatility if median_totaltime<90  , absorb(continent)


// first stage by continent
egen c=group(continent)

forvalue j=1/6{
tab continent if c==`j'
reg   median_totaltime suit_versatility  if c==`j' & median_totaltime<90, robust 
reg   median_totaltime native_versatility  if c==`j' & median_totaltime<90, robust 

}
// europa y sur america positivo
reghdfe   median_totaltime suit_versatility  if c!=3 & c!=6, absorb(continent)
reghdfe   median_totaltime suit_versatility  if c!=3 & c!=6 & median_totaltime<90, absorb(continent)
reghdfe   median_totaltime suit_versatility   if c!=3 & c!=6 & median_totaltime<90, absorb(continent)
reghdfe   median_totaltime native_versatility   if c!=3 & c!=6 & median_totaltime<90, absorb(continent)
reghdfe   median_totaltime native_versatility   if  c!=6 & median_totaltime<90, absorb(continent) // sur america es el problemático 
reghdfe   median_totaltime native_versatility   if    median_totaltime<90, absorb(continent)

scatter  median_totaltime suit_versatility  if c==3 
scatter  median_totaltime native_versatility  if c==3 
scatter  median_totaltime suit_versatility  if c==6 
scatter  median_totaltime native_versatility  if c==6  & median_totaltime<90 
scatter  median_totaltime native_versatility  if c==1  & median_totaltime<90 


tab Country if  median_totaltime>=90
// revisar Cyprus, Estonia, Kazakhastan, Malaysia, Paraguay 
// agregar número de recetas por país en la base de datos 
// completar variables con missing ie continent, continent_code
// agregar subregion: ie. europa del este, europa occidental 
// revisar suit_native: ordenes de magnitud menor que native  es posible que se estén promediando ceros 
// incluir en base de datos latitud y longitud del centroide de cada país
// agregar número de ingredientes nativos por país  
*/
 }
*------------------------------------------*
**# 		Regressions - LFP Gap	 	   *
* Continent FE
*------------------------------------------*

use "$codedata\iv_versatility\first_stage_dataset_native_m_c.dta", clear
 
global c1 "numrecipes"
global c2 "numrecipes avg_suitability  al_mn"
global c3 "numrecipes avg_suitability  al_mn precip ph_mn abslat lon "
global c4 "numrecipes  avg_suitability  al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability"

*reghdfe FLFP median_spices numrecipes avg_suitability  al_mn  pt_mn ph_mn lat lon, absorb(continent cl_md)
reghdfe LFP median_spices $c4, absorb(continent cl_md)
cap drop s
gen s=1 if  e(sample) 
global s1 "if s==1" // indicator of countries with all information
global s2 "if median_totaltime<90 &  s==1"  // Cleaned time
global s3 "if  cookpad==1 &  s==1"  // Cookpad


*-------- OLS --------*

 cd "$tables"
forvalue j=1/3 { 
eststo clear
forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.median_totaltime ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
 }
forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.median_spices ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
 }
 forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.w_mean_spices ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
 }
 forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.median_ingredients ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
 }
estout using reg-ols-s`j'-gap.tex, style(tex) cells(b(star f(3)) se(par f(3))) starlevels(* 0.10 ** 0.05 *** 0.01)  order(1.fem_lfp#c.median_totaltime median_totaltime 1.fem_lfp#c.median_spices median_spices 1.fem_lfp#c.w_mean_spices w_mean_spices 1.fem_lfp#c.median_ingredients median_ingredients) drop(_cons 0.fem_lfp 0.fem_lfp#c.median_totaltime 0.fem_lfp#c.median_spices 0.fem_lfp#c.w_mean_spices 0.fem_lfp#c.median_ingredients) label  ml(none) collabels(none) stats(j N r2  , labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f %9.2fc)) replace

} 

*-------- Reduced Form --------*

forvalue j=1/3 { 
eststo clear
forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.native_versatility ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
 }
forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.native_versatility2 ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
 }
 forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.suit_versatility ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
 }
estout using reg-rf-s`j'-gap.tex, style(tex) cells(b(star f(3)) se(par f(3))) starlevels(* 0.10 ** 0.05 *** 0.01)  order(1.fem_lfp#c.native_versatility native_versatility 1.fem_lfp#c.native_versatility2 native_versatility2 1.fem_lfp#c.suit_versatility suit_versatility) drop(_cons 0.fem_lfp 0.fem_lfp#c.native_versatility 0.fem_lfp#c.native_versatility2 0.fem_lfp#c.suit_versatility) label ml(none) collabels(none) stats(j N r2  , labels(" " "Observations" "R-squared"   ) fmt(%9.1gc %9.1gc %4.3f %9.2fc)) replace

} 

* Spices
forvalue j=1/3 { 
eststo clear
forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.native_spice_vers ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
 }
forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.native_spice_vers2 ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
 }
 forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.suit_spice_vers ${c`i'}  ${s`j'}, absorb(continent) vce(robust)
 }
estout using reg-rfsp-s`j'-gap.tex, style(tex) cells(b(star f(3)) se(par f(3))) starlevels(* 0.10 ** 0.05 *** 0.01)  order(1.fem_lfp#c.native_spice_vers native_spice_vers 1.fem_lfp#c.native_spice_vers2 native_spice_vers2 1.fem_lfp#c.suit_spice_vers suit_spice_vers) drop(_cons 0.fem_lfp 1.fem_lfp 0.fem_lfp#c.native_spice_vers 0.fem_lfp#c.native_spice_vers2 0.fem_lfp#c.suit_spice_vers) label ml(none) collabels(none) stats(j N r2  , labels(" " "Observations" "R-squared"   ) fmt(%9.1gc %9.1gc %4.3f %9.2fc)) replace
} 

*------------------------------------------*
**# 		Regressions - LFP Gap	 	   *
* Region FE
*------------------------------------------*

use "$codedata\iv_versatility\first_stage_dataset_native_m_c.dta", clear
 
global c1 "numrecipes"
global c2 "numrecipes avg_suitability  al_mn"
global c3 "numrecipes avg_suitability  al_mn precip ph_mn abslat lon "
global c4 "numrecipes  avg_suitability  al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability"
reghdfe LFP median_spices $c4, absorb(region cl_md)
cap drop s
gen s=1 if  e(sample) 
global s1 "if s==1" // indicator of countries with all information


*-------- OLS --------*
 cd "$tables"
eststo clear
forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.median_totaltime ${c`i'}  ${s1}, absorb(region) vce(robust)
 }
forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.median_spices ${c`i'}  ${s1}, absorb(region) vce(robust)
 }
 forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.w_mean_spices ${c`i'}  ${s1}, absorb(region) vce(robust)
 }
 forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.median_ingredients ${c`i'}  ${s1}, absorb(region) vce(robust)
 }
estout using reg-ols-s1-gap-region.tex, style(tex) cells(b(star f(3)) se(par f(3))) starlevels(* 0.10 ** 0.05 *** 0.01)  order(1.fem_lfp#c.median_totaltime median_totaltime 1.fem_lfp#c.median_spices median_spices 1.fem_lfp#c.w_mean_spices w_mean_spices 1.fem_lfp#c.median_ingredients median_ingredients) drop(_cons 0.fem_lfp 0.fem_lfp#c.median_totaltime 0.fem_lfp#c.median_spices 0.fem_lfp#c.w_mean_spices 0.fem_lfp#c.median_ingredients) label  ml(none) collabels(none) stats(j N r2  , labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f %9.2fc)) replace


*-------- Reduced Form --------*

eststo clear
forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.native_versatility ${c`i'}  ${s1}, absorb(region) vce(robust)
 }
forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.native_versatility2 ${c`i'}  ${s1}, absorb(region) vce(robust)
 }
 forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.suit_versatility ${c`i'}  ${s1}, absorb(region) vce(robust)
 }
estout using reg-rf-s1-gap-region.tex, style(tex) cells(b(star f(3)) se(par f(3))) starlevels(* 0.10 ** 0.05 *** 0.01)  order(1.fem_lfp#c.native_versatility native_versatility 1.fem_lfp#c.native_versatility2 native_versatility2 1.fem_lfp#c.suit_versatility suit_versatility) drop(_cons 0.fem_lfp 0.fem_lfp#c.native_versatility 0.fem_lfp#c.native_versatility2 0.fem_lfp#c.suit_versatility) label ml(none) collabels(none) stats(j N r2  , labels(" " "Observations" "R-squared"   ) fmt(%9.1gc %9.1gc %4.3f %9.2fc)) replace


* Spices
eststo clear
forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.native_spice_vers ${c`i'}  ${s1}, absorb(region) vce(robust)
 }
forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.native_spice_vers2 ${c`i'} ${s1}, absorb(region) vce(robust)
 }
 forvalue i=1/4{ 
eststo: reghdfe LFP i.fem_lfp##c.suit_spice_vers ${c`i'} ${s1}, absorb(region) vce(robust)
 }
estout using reg-rfsp-s1-gap-region.tex, style(tex) cells(b(star f(3)) se(par f(3))) starlevels(* 0.10 ** 0.05 *** 0.01)  order(1.fem_lfp#c.native_spice_vers native_spice_vers 1.fem_lfp#c.native_spice_vers2 native_spice_vers2 1.fem_lfp#c.suit_spice_vers suit_spice_vers) drop(_cons 0.fem_lfp 1.fem_lfp 0.fem_lfp#c.native_spice_vers 0.fem_lfp#c.native_spice_vers2 0.fem_lfp#c.suit_spice_vers) label ml(none) collabels(none) stats(j N r2  , labels(" " "Observations" "R-squared"   ) fmt(%9.1gc %9.1gc %4.3f %9.2fc)) replace 



*------------------------------------------*
**# 		     Regressions 	 	       *
*          Steve's specification 
*------------------------------------------*

use "$codedata\iv_versatility\first_stage_dataset_native_m_c.dta", clear

global c1 "numrecipes LFP"
global c2 "numrecipes avg_suitability  al_mn LFP"
global c3 "numrecipes avg_suitability  al_mn precip ph_mn abslat lon LFP"
global c4 "numrecipes  avg_suitability  al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability LFP"

encode region, gen(region_cat)

gen LFP_female = LFP if fem_lfp == 1
gen LFP_male   = LFP if fem_lfp == 0

* creating the LFP gap at the country-level
collapse (mean) $c4 LFP_male LFP_female median_spices w_mean_spices native_spice_vers native_spice_vers2 suit_spice_vers (first) continent region_cat cl_md , by(adm0)

gen LFP_gap = LFP_female-LFP_male

preserve 
use "${versatility}\native_versatility_m_c_dist.dta", clear
collapse (mean) native_spice_vers2_dist, by(adm0)
tempfile distance
save `distance'
restore

merge 1:1 adm0 using `distance', keep(3) nogen

* relabel everything
foreach v of varlist * {
    local lbl : variable label `v'

    * Clean up symbols
    local lblclean : subinstr local lbl "_" " ", all
    local lblclean : subinstr local lblclean "(" "", all
    local lblclean : subinstr local lblclean ")" "", all

    * Remove "mean " if it occurs at the beginning (within first 5 characters)
    if strpos(lower(substr("`lblclean'", 1, 5)), "mean") {
        local lblclean = substr("`lblclean'", 6, .)
    }

    label variable `v' "`lblclean'"
}

**#**************** FLFP **************************************
*--- OLS

eststo clear
forvalue i=1/4{ 
eststo: reghdfe LFP_female c.w_mean_spices ${c`i'}  , absorb(region_cat cl_md) vce(robust)
 }
forvalue i=1/4{ 
eststo: reghdfe LFP_female c.median_spices ${c`i'} , absorb(region_cat cl_md) vce(robust)
 }

 cd "$tables"
 
estout using reg_flfp_OLS.tex, ///
    style(tex) ///
	prehead("\begin{tabular}{lcccccccc}" "\toprule") ///
    postfoot("\bottomrule" "\end{tabular}") ///
    cells(b(star f(3)) se(par f(3))) ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    order(w_mean_spices median_spices) ///
    drop(_cons) ///
    label ml(none) collabels(none) ///
    stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
    replace


*--- REDUCED FORM

eststo clear
forvalue i=1/4{ 
eststo: reghdfe LFP_female c.native_spice_vers ${c`i'} , absorb(region_cat cl_md) vce(robust)
 }
forvalue i=1/4{ 
eststo: reghdfe LFP_female c.native_spice_vers2 ${c`i'}, absorb(region_cat cl_md) vce(robust)
 }
 forvalue i=1/4{ 
eststo: reghdfe LFP_female c.native_spice_vers2_dist ${c`i'} , absorb(region_cat cl_md) vce(robust)
 }

 cd "$tables"
 
estout using reg_flfp_RF.tex, ///
    style(tex)  ///
	prehead("\begin{tabular}{lcccccccccccc}" "\toprule") ///
    postfoot("\bottomrule" "\end{tabular}") ///
    cells(b(star f(3)) se(par f(3))) ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    order(native_spice_vers native_spice_vers2 native_spice_vers2_dist) ///
    drop(_cons) ///
    label ml(none) collabels(none) ///
    stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
    replace

* IV REGRESSIONS FOR native_spice_vers, native_spice_vers2, native_spice_vers2_dist2

eststo clear

forvalue i=1/4 { 
    eststo: ivreg2 LFP_female (w_mean_spices = native_spice_vers) ${c`i'} i.region_cat i.cl_md, robust first
}

forvalue i=1/4 { 
    eststo: ivreg2 LFP_female (w_mean_spices = native_spice_vers2) ${c`i'} i.region_cat i.cl_md, robust first
}

forvalue i=1/4 { 
    eststo: ivreg2 LFP_female (w_mean_spices = native_spice_vers2_dist) ${c`i'} i.region_cat i.cl_md, robust first
}

cd "${tables}"

* Export table with F-stat
estout using reg_flfp_IV.tex, ///
    style(tex) ///
    prehead("\begin{tabular}{lcccccccccccc}" "\toprule") ///
    postfoot("\bottomrule" "\end{tabular}") ///
    cells(b(star f(3)) se(par f(3))) ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    order(w_mean_spices) ///
    drop(_cons *.region_cat *.cl_md) ///
    label ml(none) collabels(none) ///
    stats(j N r2 widstat, ///
          labels(" " "Observations" "R-squared" "First-stage F-stat") ///
          fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
    replace


*--------- Control for MLFP instead of LFP -----------------*

global c5 "numrecipes LFP_male"
global c6 "numrecipes avg_suitability  al_mn LFP_male"
global c7 "numrecipes avg_suitability  al_mn precip ph_mn abslat lon LFP_male"
global c8 "numrecipes  avg_suitability  al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability LFP_male"

*--- OLS

eststo clear
forvalue i=5/8{ 
eststo: reghdfe LFP_female c.w_mean_spices ${c`i'}  , absorb(region_cat cl_md) vce(robust)
 }
forvalue i=5/8{ 
eststo: reghdfe LFP_female c.median_spices ${c`i'} , absorb(region_cat cl_md) vce(robust)
 }

 cd "$tables"
 
estout using reg_flfp_OLS_c.tex, ///
    style(tex) ///
	prehead("\begin{tabular}{lcccccccc}" "\toprule") ///
    postfoot("\bottomrule" "\end{tabular}") ///
    cells(b(star f(3)) se(par f(3))) ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    order(w_mean_spices median_spices) ///
    drop(_cons) ///
    label ml(none) collabels(none) ///
    stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
    replace


*--- REDUCED FORM

eststo clear
forvalue i=5/8{ 
eststo: reghdfe LFP_female c.native_spice_vers ${c`i'} , absorb(region_cat cl_md) vce(robust)
 }
forvalue i=5/8{ 
eststo: reghdfe LFP_female c.native_spice_vers2 ${c`i'}, absorb(region_cat cl_md) vce(robust)
 }
 forvalue i=5/8{ 
eststo: reghdfe LFP_female c.native_spice_vers2_dist ${c`i'} , absorb(region_cat cl_md) vce(robust)
 }

 cd "$tables"
 
estout using reg_flfp_RF_c.tex, ///
    style(tex)  ///
	prehead("\begin{tabular}{lcccccccccccc}" "\toprule") ///
    postfoot("\bottomrule" "\end{tabular}") ///
    cells(b(star f(3)) se(par f(3))) ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    order(native_spice_vers native_spice_vers2 native_spice_vers2_dist) ///
    drop(_cons) ///
    label ml(none) collabels(none) ///
    stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
    replace

* IV REGRESSIONS FOR native_spice_vers, native_spice_vers2, native_spice_vers2_dist2

eststo clear
forvalues i=5/8 { 
    ivreg2 LFP_female (w_mean_spices = native_spice_vers ) ${c`i'} i.region_cat i.cl_md, robust
    local fstat = e(widstat)  
    estadd scalar F_first = `fstat'   
    eststo
}

forvalues i=5/8 { 
    ivreg2 LFP_female (w_mean_spices = native_spice_vers2 ) ${c`i'} i.region_cat i.cl_md, robust
    local fstat = e(widstat)
    estadd scalar F_first = `fstat'
    eststo
}

forvalues i=5/8 { 
    ivreg2 LFP_female (w_mean_spices = native_spice_vers2_dist ) ${c`i'} i.region_cat i.cl_md, robust
    local fstat = e(widstat)
    estadd scalar F_first = `fstat'
    eststo
}

 cd "${tables}"
 
estout using reg_flfp_IV_c.tex, ///
    style(tex) ///
    prehead("\begin{tabular}{lcccccccccccc}" "\toprule") ///
    postfoot("\bottomrule" "\end{tabular}") ///
    cells(b(star f(3)) se(par f(3))) ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    order(w_mean_spices) ///
    drop(_cons *.region_cat *.cl_md) ///
    label ml(none) collabels(none) ///
    stats(F_first j N r2, labels("F-stat First Stage" " " "Observations" "R-squared") fmt(%9.2f %9.1gc %9.1gc %4.3f)) ///
    replace

**#**************** MLFP **************************************
*--- OLS

eststo clear
forvalue i=1/4{ 
eststo: reghdfe LFP_male c.w_mean_spices ${c`i'}  , absorb(region_cat cl_md) vce(robust)
 }
forvalue i=1/4{ 
eststo: reghdfe LFP_male c.median_spices ${c`i'} , absorb(region_cat cl_md) vce(robust)
 }

 cd "$tables"
 
estout using reg_mlfp_OLS.tex, ///
    style(tex) ///
	prehead("\begin{tabular}{lcccccccc}" "\toprule") ///
    postfoot("\bottomrule" "\end{tabular}") ///
    cells(b(star f(3)) se(par f(3))) ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    order(w_mean_spices median_spices) ///
    drop(_cons) ///
    label ml(none) collabels(none) ///
    stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
    replace


*--- REDUCED FORM

eststo clear
forvalue i=1/4{ 
eststo: reghdfe LFP_male c.native_spice_vers ${c`i'} , absorb(region_cat cl_md) vce(robust)
 }
forvalue i=1/4{ 
eststo: reghdfe LFP_male c.native_spice_vers2 ${c`i'}, absorb(region_cat cl_md) vce(robust)
 }
 forvalue i=1/4{ 
eststo: reghdfe LFP_male c.native_spice_vers2_dist ${c`i'} , absorb(region_cat cl_md) vce(robust)
 }

 cd "$tables"
 
estout using reg_mlfp_RF.tex, ///
    style(tex)  ///
	prehead("\begin{tabular}{lcccccccccccc}" "\toprule") ///
    postfoot("\bottomrule" "\end{tabular}") ///
    cells(b(star f(3)) se(par f(3))) ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    order(native_spice_vers native_spice_vers2 native_spice_vers2_dist) ///
    drop(_cons) ///
    label ml(none) collabels(none) ///
    stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
    replace

* IV REGRESSIONS FOR native_spice_vers, native_spice_vers2, native_spice_vers2_dist2

eststo clear

forvalue i=1/4 { 
    eststo: ivreg2 LFP_male (w_mean_spices = native_spice_vers) ${c`i'} i.region_cat i.cl_md, robust first
}

forvalue i=1/4 { 
    eststo: ivreg2 LFP_male (w_mean_spices = native_spice_vers2) ${c`i'} i.region_cat i.cl_md, robust first
}

forvalue i=1/4 { 
    eststo: ivreg2 LFP_male (w_mean_spices = native_spice_vers2_dist) ${c`i'} i.region_cat i.cl_md, robust first
}

cd "${tables}"

* Export table including F-stat
estout using reg_mlfp_IV.tex, ///
    style(tex) ///
    prehead("\begin{tabular}{lcccccccccccc}" "\toprule") ///
    postfoot("\bottomrule" "\end{tabular}") ///
    cells(b(star f(3)) se(par f(3))) ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    order(w_mean_spices) ///
    drop(_cons *.region_cat *.cl_md) ///
    label ml(none) collabels(none) ///
    stats(j N r2 widstat, ///
          labels(" " "Observations" "R-squared" "First-stage F-stat") ///
          fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
    replace

	
*--------- Control for FLFP instead of LFP -----------------*

global c9 "numrecipes LFP_female"
global c10 "numrecipes avg_suitability  al_mn LFP_female"
global c11 "numrecipes avg_suitability  al_mn precip ph_mn abslat lon LFP_female"
global c12 "numrecipes  avg_suitability  al_mn precip ph_mn abslat lon rough temp landlocked distcr staple_suitability LFP_female"

*--- OLS

eststo clear
forvalue i=9/12{ 
eststo: reghdfe LFP_male c.w_mean_spices ${c`i'}  , absorb(region_cat cl_md) vce(robust)
 }
forvalue i=9/12{ 
eststo: reghdfe LFP_male c.median_spices ${c`i'} , absorb(region_cat cl_md) vce(robust)
 }

 cd "$tables"
 
estout using reg_mlfp_OLS_c.tex, ///
    style(tex) ///
	prehead("\begin{tabular}{lcccccccc}" "\toprule") ///
    postfoot("\bottomrule" "\end{tabular}") ///
    cells(b(star f(3)) se(par f(3))) ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    order(w_mean_spices median_spices) ///
    drop(_cons) ///
    label ml(none) collabels(none) ///
    stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
    replace


*--- REDUCED FORM

eststo clear
forvalue i=9/12{ 
eststo: reghdfe LFP_male c.native_spice_vers ${c`i'} , absorb(region_cat cl_md) vce(robust)
 }
forvalue i=9/12{ 
eststo: reghdfe LFP_male c.native_spice_vers2 ${c`i'}, absorb(region_cat cl_md) vce(robust)
 }
 forvalue i=9/12{ 
eststo: reghdfe LFP_male c.native_spice_vers2_dist ${c`i'} , absorb(region_cat cl_md) vce(robust)
 }

 cd "$tables"
 
estout using reg_mlfp_RF_c.tex, ///
    style(tex)  ///
	prehead("\begin{tabular}{lcccccccccccc}" "\toprule") ///
    postfoot("\bottomrule" "\end{tabular}") ///
    cells(b(star f(3)) se(par f(3))) ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    order(native_spice_vers native_spice_vers2 native_spice_vers2_dist) ///
    drop(_cons) ///
    label ml(none) collabels(none) ///
    stats(j N r2, labels(" " "Observations" "R-squared") fmt(%9.1gc %9.1gc %4.3f)) ///
    replace

* IV REGRESSIONS FOR native_spice_vers, native_spice_vers2, native_spice_vers2_dist2

eststo clear

forvalue i=9/12 { 
    eststo: ivreg2 LFP_male (w_mean_spices = native_spice_vers) ${c`i'} i.region_cat i.cl_md, robust first
}

forvalue i=9/12 { 
    eststo: ivreg2 LFP_male (w_mean_spices = native_spice_vers2) ${c`i'} i.region_cat i.cl_md, robust first
}

forvalue i=9/12 { 
    eststo: ivreg2 LFP_male (w_mean_spices = native_spice_vers2_dist) ${c`i'} i.region_cat i.cl_md, robust first
}

cd "${tables}"

* Export table with F-stat
estout using reg_mlfp_IV_c.tex, ///
    style(tex) ///
    prehead("\begin{tabular}{lcccccccccccc}" "\toprule") ///
    postfoot("\bottomrule" "\end{tabular}") ///
    cells(b(star f(3)) se(par f(3))) ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    order(w_mean_spices) ///
    drop(_cons *.region_cat *.cl_md) ///
    label ml(none) collabels(none) ///
    stats(j N r2 widstat, ///
          labels(" " "Observations" "R-squared" "First-stage F-stat") ///
          fmt(%9.1gc %9.1gc %4.3f %4.2f)) ///
    replace