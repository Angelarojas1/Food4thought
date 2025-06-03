   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *																	  *
   * - Inputs: ""											      		  *
   * - Output: ""	      									    		  *
   *		   ""												  		  *
   * ******************************************************************** *
   
   ** IDS Var: adm0
   ** Description: Cleans population data
   ** Written by: Ángela Rojas
   ** Last modified: October 8, 2024
   
   * Import population dataset
   import delimited "${rawdata}/population/population.csv", varnames(5) clear
   
   * Drop variables not needed
   drop v69
   
   * Rename variables with label values
	foreach v of varlist v5-v68{
		local x: variable label `v'
		rename `v' year`x'
}
	describe, full
	
	* reshape dataset from wide format to long format
reshape long year, i(countryname countrycode) j(y)

	* rename variables
	rename year pop
	rename y year
	rename countryname country
	rename countrycode adm0
	
	* Organize country variable
	* correct country names
	replace country = "Bahamas" if country == "Bahamas, The"
	replace country = "Bosnia And Herzegovina" if country == "Bosnia and Herzegovina"
	replace country = "Cote D'Ivoire" if country == "Cote d'Ivoire"
	replace country = "Egypt" if country == "Egypt, Arab Rep."
	replace country = "Iran" if country == "Iran, Islamic Rep."
	replace country = "Kyrgyzstan" if country == "Kyrgyz Republic"
	replace country = "Laos" if country == "Lao PDR"
	replace country = "North Korea" if country == "Korea, Dem. People's Rep."
	replace country = "Russia" if country == "Russian Federation"
	replace country = "Slovakia" if country == "Slovak Republic"
	replace country = "South Korea" if country == "Korea, Rep."
	replace country = "Syria" if country == "Syrian Arab Republic"
	replace country = "Venezuela" if country == "Venezuela, RB"
	
	* Drop missings
	drop if pop == .
	
	* Drop observations different to country 
	drop if strpos(country,"African")>0
	drop if strpos(country,"Europe")>0
	drop if strpos(country,"income")>0
	drop if strpos(country,"demographic")>0
	drop if strpos(country,"HIPC")>0
	drop if strpos(country,"IDA")>0
	drop if strpos(country,"IBRD")>0
	drop if strpos(country,"OECD")>0
	drop if strpos(country,"conflict")>0
	drop if strpos(country,"Latin America")>0
	drop if strpos(country,"Asia")>0
	drop if strpos(country,"developed")>0
	drop if strpos(country,"Africa Eastern")>0
	drop if strpos(country,"Africa Western")>0
	drop if strpos(country,"North Africa")>0
	drop if strpos(country,"small states")>0
	drop if strpos(country,"World")>0
	drop if strpos(country,"West Bank")>0
	
	* Format population data
	format %16.0g pop
	
	** keep the most recent year
	keep if year == 2019 | year == 2023
	unique country
	note: There are `r(sum)' countries in population data.
	
	** save dataset
save "${pop}/populationlong2019_2023.dta", replace
note
   