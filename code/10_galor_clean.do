* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               RA: Angela Rojas
* 				Last date modified: Sept 23, 2025 						   	   *
*				Galor datasets cleaning
*
* **************************************************************************** *

	
	*--- Import dataset
	use "${rawdata}/Galor/CountryLevel.dta", clear
	
	*--- Create file with variables names and labels
/*
	preserve
	ds
	local vars `r(varlist)'

	tempfile varlabels
	postfile handle str80 varname str244 varlabel using `varlabels', replace

	foreach v of local vars {
		local lbl : variable label `v'
		if "`lbl'" == "" local lbl = ""
		post handle ("`v'") ("`lbl'")
	}

	postclose handle

	use `varlabels', clear

	export excel using "${rawdata}/Galor/varnames_labels.xlsx", firstrow(variables) replace
	restore
*/
	
	*- Organize dataset to merge it later for the regression
	rename code adm0
	
	*- Update ISO3 codes
	replace adm0 = "SRB" if adm0 == "YUG" //Serbia
	replace adm0 = "ROU" if adm0 == "ROM" //Romania

	keep adm0 precip temp abslat rough landlocked distcr 
	
	save "${versatility}/galor_controls.dta", replace