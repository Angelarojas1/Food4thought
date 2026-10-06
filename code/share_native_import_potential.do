/*===========================================================================
  mean_native_recipes_import.do

  Merges country-level mean native ingredients with import potential, then runs regressions and scatter plots.

===========================================================================*/

clear all
set more off


*---------------------------------------------------------------------------
* 0. PATHS
*---------------------------------------------------------------------------
global maindata  "$versatility/native_versatility_m_c_dist_all.dta"
global impdata   "$versatility/ingredient_import_potential.dta"
global cookpad   "$cookpad/cookpad_adm0.dta"
global recnat    "$recipes/recipes_native.dta"


*---------------------------------------------------------------------------
* 1. BUILD COUNTRY-MEAN CROSSWALK
*---------------------------------------------------------------------------
input str40 country_name str3 adm0 float pct_native
"Afghanistan"           "AFG"  9.4
"Albania"               "ALB"  10.5
"Algeria"               "DZA"  5.9
"Argentina"             "ARG"  2.3
"Armenia"               "ARM"  13.7
"Aruba"                 "ABW"  2.1
"Australia"             "AUS"  2.8
"Austria"               "AUT"  3.1
"Bahamas"               "BHS"  .8
"Bangladesh"            "BGD"  9.4
"Barbados"              "BRB"  1.3
"Belarus"               "BLR"  1.3
"Belgium"               "BEL"  4.1
"Belize"                "BLZ"  6.5
"Benin"                 "BEN"  8.1
"Bolivia"               "BOL"  9.6
"Bosnia And Herzegovina" "BIH" 4.6
"Botswana"              "BWA"  3.2
"Brazil"                "BRA"  7.2
"Bulgaria"              "BGR"  2.4
"Cabo Verde"            "CPV"  1.0
"Cambodia"              "KHM"  6.2
"Cameroon"              "CMR"  10.6
"Canada"                "CAN"  .6
"Chile"                 "CHL"  1.4
"China"                 "CHN"  17.3
"Colombia"              "COL"  5.6
"Comoros"               "COM"  0.0
"Costa Rica"            "CRI"  7.3
"Cote D'Ivoire"         "CIV"  11.7
"Croatia"               "HRV"  3.4
"Cuba"                  "CUB"  2.7
"Cyprus"                "CYP"  4.8
"Czech Republic"        "CZE"  2.8
"Denmark"               "DNK"  1.4
"Dominica"              "DMA"  1.3
"Dominican Republic"    "DOM"  2.5
"Ecuador"               "ECU"  6.9
"Egypt"                 "EGY"  5.4
"El Salvador"           "SLV"  6.6
"Eritrea"               "ERI"  2.9
"Estonia"               "EST"  0.0
"Ethiopia"              "ETH"  2.7
"Fiji"                  "FJI"  0.0
"Finland"               "FIN"  1.3
"France"                "FRA"  8.6
"Georgia"               "GEO"  8.1
"Germany"               "DEU"  3.6
"Ghana"                 "GHA"  12.1
"Greece"                "GRC"  7.9
"Guatemala"             "GTM"  5.6
"Guinea"                "GIN"  3.3
"Guyana"                "GUY"  1.9
"Haiti"                 "HTI"  3.4
"Honduras"              "HND"  6.7
"Hungary"               "HUN"  .4
"Iceland"               "ISL"  .6
"India"                 "IND"  13.0
"Indonesia"             "IDN"  6.5
"Iran"                  "IRN"  8.2
"Iraq"                  "IRQ"  11.5
"Ireland"               "IRL"  .9
"Israel"                "ISR"  10.1
"Italy"                 "ITA"  9.2
"Jamaica"               "JAM"  2.0
"Japan"                 "JPN"  6.0
"Jordan"                "JOR"  54.6
"Kazakhstan"            "KAZ"  12.9
"Kenya"                 "KEN"  5.6
"Kosovo"                "XKX"  1.0
"Kuwait"                "KWT"  6.4
"Kyrgyzstan"            "KGZ"  16.1
"Laos"                  "LAO"  7.9
"Latvia"                "LVA"  1.1
"Lebanon"               "LBN"  13.8
"Liberia"               "LBR"  9.5
"Libya"                 "LBY"  2.5
"Liechtenstein"         "LIE"  8.9
"Lithuania"             "LTU"  1.5
"Luxembourg"            "LUX"  2.0
"Madagascar"            "MDG"  .4
"Malaysia"              "MYS"  5.5
"Maldives"              "MDV"  7.7
"Malta"                 "MLT"  6.8
"Mauritius"             "MUS"  0.0
"Mexico"                "MEX"  9.7
"Moldova"               "MDA"  .8
"Mongolia"              "MNG"  8.3
"Morocco"               "MAR"  9.7
"Mozambique"            "MOZ"  1.1
"Myanmar"               "MMR"  12.6
"Nepal"                 "NPL"  11.9
"Netherlands"           "NLD"  3.8
"New Zealand"           "NZL"  0.0
"Nicaragua"             "NIC"  7.1
"Niger"                 "NER"  2.5
"North Korea"           "PRK"  6.7
"Norway"                "NOR"  2.4
"Pakistan"              "PAK"  14.0
"Panama"                "PAN"  5.1
"Paraguay"              "PRY"  4.5
"Peru"                  "PER"  8.2
"Philippines"           "PHL"  9.2
"Poland"                "POL"  3.2
"Portugal"              "PRT"  7.0
"Romania"               "ROU"  2.2
"Russia"                "RUS"  2.8
"Samoa"                 "WSM"  .3
"Senegal"               "SEN"  10.4
"Serbia"                "SRB"  3.2
"Singapore"             "SGP"  2.7
"Slovakia"              "SVK"  .2
"Slovenia"              "SVN"  2.7
"Solomon Islands"       "SLB"  1.2
"South Africa"          "ZAF"  .5
"South Korea"           "KOR"  7.3
"Spain"                 "ESP"  14.2
"Sri Lanka"             "LKA"  6.9
"Sudan"                 "SDN"  4.5
"Suriname"              "SUR"  3.9
"Sweden"                "SWE"  1.5
"Switzerland"           "CHE"  2.5
"Syria"                 "SYR"  13.5
"Tajikistan"            "TJK"  12.6
"Thailand"              "THA"  8.5
"Tonga"                 "TON"  0.0
"Tunisia"               "TUN"  5.1
"Turkey"                "TUR"  7.5
"Turkmenistan"          "TKM"  4.3
"Tuvalu"                "TUV"  0.0
"Ukraine"               "UKR"  1.3
"United Arab Emirates"  "ARE"  8.1
"United Kingdom"        "GBR"  .9
"United States"         "USA"  4.6
"Uruguay"               "URY"  .8
"Vanuatu"               "VUT"  1.2
"Venezuela"             "VEN"  2.3
"Vietnam"               "VNM"  8.8
"Zimbabwe"              "ZWE"  .1
end

label var pct_native   "Mean % native ingredients (from recipes)"
label var country_name "Country name"

tempfile crosswalk
save `crosswalk'


*---------------------------------------------------------------------------
* 2. MERGE INTO MAIN DATA
*---------------------------------------------------------------------------
use "$maindata", clear

merge 1:1 adm0 using `crosswalk', keepusing(pct_native country_name) gen(_merge_recipes)

* Drop the 14 recipe-only countries not present in the main data
drop if _merge_recipes == 2

merge 1:m adm0 using "$impdata", keep(1 3) nogen
merge 1:m adm0 using "$cookpad",           nogen

gen eurasia = cond(reg2_global == 4 | reg2_global == 6, 0, cond(reg2_global != ., 1, .))

collapse ///
    (mean)  pct_native trade_distCapital_2000 coltime cont_cat ///
            avg_suitability import_potential ln_import_potential ///
            num_native_ingredients ln_native_ingredients ///
    (first) eurasia numNative, ///
    by(adm0)

merge 1:m adm0 using "$recnat", nogen

collapse ///
    (mean)  pct_native trade_distCapital_2000 coltime cont_cat prop_native ///
            avg_suitability import_potential ln_import_potential ///
            num_native_ingredients ln_native_ingredients ///
    (first) eurasia numNative, ///
    by(adm0)


*---------------------------------------------------------------------------
* 3. REGRESSIONS
*---------------------------------------------------------------------------
foreach v of varlist import_potential num_native_ingredients {
    sum `v'
    gen `v'_std = (`v' - r(mean)) / r(sd)
}

eststo clear 

* Main regressions (excluding Jordan outlier)
eststo: reg pct_native import_potential_std num_native_ingredients_std if adm0 != "JOR", robust
		qui sum pct_native if e(sample)
		estadd scalar Mean = r(mean)

eststo: reg pct_native c.import_potential_std##c.num_native_ingredients_std if adm0 != "JOR", robust
		qui sum pct_native if e(sample)
		estadd scalar Mean = r(mean)

* TODO: export this as one table with two columns and put in presentation

estout using "${tables}/reg_pct_native.tex", ///
    style(tex) ///
    cells(b(star f(3)) se(par f(3))) ///
	drop(_cons) ///
	varlabels("import_potential_std" "Import potential" "num_native_ingredients_std" "Number of native ingredients" "c.import_potential_std#c.num_native_ingredients_std" "Import potential x Number native ingredients") ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    label ml(none) collabels(none) ///
    stats(Mean N , labels("Mean dep. var." "Observations") fmt(%9.3f %9.1gc %4.3f)) ///
    postfoot("\hline") ///
    replace

*---------------------------------------------------------------------------
* 4. SCATTER PLOTS (residualized)
*---------------------------------------------------------------------------

* Residualize pct_native on each control separately, then plot against the other
reg pct_native num_native_ingredients if adm0 != "JOR", robust
predict double res_on_native, resid

reg pct_native import_potential if adm0 != "JOR", robust
predict double res_on_import, resid

* Share native | num_native vs. import potential (Eurasia only)
twoway ///
    (scatter res_on_native import_potential_std,    mlabel(adm0) mlabsize(vsmall)) ///
    (lfit    res_on_native import_potential_std) ///
    if adm0 != "JOR", ///
    ytitle("Share native (%), residualized") xtitle("Import potential (standardized)") ///
	legend(pos(6) col(2))

* TODO: save this figure and put in presentation	
graph export "${figures}/res_native_vs_import.pdf", replace

* Share native | import_potential vs. num. native ingredients (Eurasia only)
twoway ///
    (scatter res_on_import num_native_ingredients, mlabel(adm0) mlabsize(vsmall)) ///
    (lfit    res_on_import num_native_ingredients) ///
    if adm0 != "JOR", ///
    ytitle("Share native (%), residualized") xtitle("Number of native ingredients") ///
	legend(pos(6) col(2))
	
* TODO: save this figure and put in presentation
graph export "${figures}/res_import_vs_native.pdf", replace


* Share native | num_native vs. log import potential (never-colonized only)
twoway ///
    (scatter res_on_native import_potential_std, mlabel(adm0) mlabsize(vsmall)) ///
    (lfit    res_on_native import_potential_std) ///
    if adm0 != "JOR" & coltime == 0, ///
    ytitle("Share native (%), residualized")  xtitle("Import potential (standardized)")
