global projectfolder "C:\Users\mgafargo\Dropbox\food4thought\analysis23"

use "$projectfolder\data\raw\appliances\imports\datos\modificados\appliances.dta", clear 

*------------------------------------------------------------------
* 1. Prepare nominal import value (USD)
*------------------------------------------------------------------
gen imp_usd = 1000 * Importin1000USD
label var imp_usd "Imports (USD)"

*------------------------------------------------------------------
* 2. Compute quantity-weighted average price
*    (continent x appliance x year)
*------------------------------------------------------------------
rename ReporterRegion Continent 
collapse (sum) imp_usd Quantity, by(Continent  appliance Year )

gen price_wa = imp_usd / Quantity if Quantity>0
label var price_wa "Quantity-weighted average price"

 summ price_wa, detail

local p5 = r(p5)
local p95 = r(p95)

gen price_wa_w = price_wa
replace price_wa_w = . if price_wa < `p5'
replace price_wa_w = . if price_wa > `p95'
*------------------------------------------------------------------
* 4. Normalize to index = 100 in base year
*------------------------------------------------------------------

* Get base-year price by continent-appliance
destring Year, replace

bys Continent appliance: egen base_price =median(price_wa_w)
 
gen price_index = 100 * price_wa / base_price if base_price>0
label var price_index "Price index (base=`baseyear'=100)"


sum price_index, d
gen cooking = 0

replace cooking = 1 if ///
    appliance == "Coffee machines" | ///
    appliance == "Electric grills" | ///
    appliance == "Food processors" | ///
    appliance == "Microwaves" | ///
    appliance == "Toasters"  | ///
	appliance == "Freezers"  | ///
	appliance == "Dishwashers" 
	

label define cooklbl 0 "Non-cooking" 1 "Cooking"
label values cooking cooklbl

 
 
*------------------------------------------------------------------
* 5. Average indices across appliances within continent
*------------------------------------------------------------------

bys Continent Year: egen index_all = mean(price_index)


* ALL appliances
preserve
collapse (mean) index_all = price_index, by(Continent Year)
save "$projectfolder\data\raw\appliances\imports\datos\modificados\continent_index_all.dta", replace
restore

* COOKING appliances
preserve
keep if cooking==1
collapse (mean) index_cooking = price_index, by(Continent Year)
save "$projectfolder\data\raw\appliances\imports\datos\modificados\continent_index_cooking.dta", replace
restore

* NON-COOKING appliances
preserve
keep if cooking==0
collapse (mean) index_noncooking = price_index, by(Continent Year)
save "$projectfolder\data\raw\appliances\imports\datos\modificados\continent_index_noncooking.dta", replace
restore


 use "$projectfolder\data\raw\appliances\imports\datos\modificados\appliances.dta", clear 
keep Country Year ReporterISO3 ReporterRegion
bys ReporterISO3 Year: egen s=seq()
keep if s==1
drop s

rename ReporterRegion Continent 
destring Year, replace 
merge m:1 Year Continent using  "$projectfolder\data\raw\appliances\imports\datos\modificados\continent_index_all.dta", nogen
merge m:1 Year Continent using  "$projectfolder\data\raw\appliances\imports\datos\modificados\continent_index_cooking.dta", nogen
merge m:1 Year Continent using  "$projectfolder\data\raw\appliances\imports\datos\modificados\continent_index_noncooking.dta", nogen

rename ReporterISO3 adm0
rename Year year
rename Country cntr_name
save "$projectfolder\data\raw\appliances\imports\datos\modificados\country_index_noncooking.dta", replace



/// merge with other data 

use "$versatility\first_stage_native_m_c_series.dta", clear
bys country year: egen aux=mean(LFP_male)
replace LFP_male=aux if LFP_male==. 
drop if LFP_female==. 

 drop _merge
merge 1:1 adm0 year using "$projectfolder\data\raw\appliances\imports\datos\modificados\country_index_noncooking.dta"



scatter rel_EU_HICP index_all
