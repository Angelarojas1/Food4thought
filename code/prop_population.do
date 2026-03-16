use "$cookpad/cookpad_adm0.dta", replace 

keep if  vers_distCapital_2000 != 0 & covid == 0 

keep adm0 country

duplicates drop

merge 1:1 adm0 using "${pop}/populationlong2019.dta"

egen sample = sum(population) if _merge == 3
sort sample 
replace sample = sample[_n-1] if missing(sample)

egen total = sum(population) 


gen prop = (sample/total)*100

tab prop


use "$recipes/complexity_recipe.dta", replace 

keep country 
unique country

replace country = "Czechia" if country == "Czech Republic"
replace country = "Turkiye" if country == "Turkey"
replace country = "Viet Nam" if country == "Vietnam"


merge 1:1 country using "${pop}/populationlong2019.dta"

egen sample = sum(population) if _merge == 3
sort sample 
replace sample = sample[_n-1] if missing(sample)

egen total = sum(population) 


gen prop = (sample/total)*100

tab prop