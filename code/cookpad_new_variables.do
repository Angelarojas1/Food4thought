use "$cookpad/cookpad_adm0.dta", replace
merge m:1 adm0 using "$rawdata\suitability\spices\20250616-spices-suitability"
// BEN MLT and SGP not in spices data 
drop _merge 

merge m:1 adm0 using "$versatility/first_stage_dataset.dta"


ren (median_ingredients median_spices median_totaltime) (ingredients spices time)
ren (emp_ftemp emp_ftemp_pop emp_lfpr emp_work_hours) (ft p2p lfpr hours)
	
	
egen mealCook=rowtotal(numLunCook numDinCook)


gen husband_cooked = (wp19961 == 1 & gender == 1) | (wp19962 == 1 & gender == 2)
replace husband_cooked = . if wp1223 !=2

gen wife_cooked = (wp19961 == 1 & gender == 2) | (wp19962 == 1 & gender == 1)
replace wife_cooked = . if wp1223 != 2

gen m_lfpr = lfpr if gender == 1
gen f_lfpr = lfpr if gender == 2

gen m_hours = hours if gender == 1
gen f_hours = hours if gender == 2

