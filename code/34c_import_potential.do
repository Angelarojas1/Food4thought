* **************************************************************************** *
*                                                                               *
*            Ingredient Import Potential                                        *
*            Author: Steve Berggreen                                            *
*                                                                               *
*  For each country, computes:                                                  *
*    (1) num_native_ingredients: count of native ingredients                    *
*    (2) import_potential: sum over all partner countries of                    *
*           (partner's native ingredient count) / distance                      *
*        analogous to a gravity-model numerator (like GDP in trade models)      *
*                                                                               *
* **************************************************************************** *


* -----------------------------------------------------------------------*
* 1. Build country-level native ingredient counts                        *
* -----------------------------------------------------------------------*

use "$versatility/native_versatility_m_c1.dta", clear

	* Keep only native ingredient-country pairs
	keep if only_native == 1
	keep adm0 ingredient
	duplicates drop

	* Count native ingredients per country
	bys adm0: gen num_native_ingredients = _N
	keep adm0 num_native_ingredients
	duplicates drop

	label var num_native_ingredients "Number of native ingredients in country"

	tempfile native_counts
	save `native_counts', replace


* -----------------------------------------------------------------------*
* 2. Load capital-to-capital distance matrix                             *
* -----------------------------------------------------------------------*

use "$versatility/distance_capital.dta", clear

	* Expected variables: adm0, nativeadm0, distance
	* (adm0 = importer/focal country; nativeadm0 = partner country)
	* Rename partner country for clarity
	rename nativeadm0 partner_adm0

	tempfile distances
	save `distances', replace


* -----------------------------------------------------------------------*
* 3. Merge partner native ingredient counts into the distance matrix     *
* -----------------------------------------------------------------------*

	* Prepare a version of native_counts keyed on partner_adm0 for the merge
	* (avoids variable name clash with the existing adm0 in the distance data)
	use `native_counts', clear
	rename adm0 partner_adm0
	rename num_native_ingredients partner_native_count
	tempfile partner_counts
	save `partner_counts', replace

use `distances', clear

	merge m:1 partner_adm0 using `partner_counts', keep(match master) nogen

	* Countries with no matched native ingredients get 0
	replace partner_native_count = 0 if missing(partner_native_count)

	* Countries with no matched native ingredients get 0
	replace partner_native_count = 0 if missing(partner_native_count)

	tempfile dist_with_counts
	save `dist_with_counts', replace


* -----------------------------------------------------------------------*
* 4. Compute import potential for each focal country                     *
* -----------------------------------------------------------------------*

use `dist_with_counts', clear

	* Drop self-pairs (distance = 0 would cause division by zero)
	drop if adm0 == partner_adm0

	* Drop pairs with missing distance
	drop if missing(distance) | distance == 0

	* Gravity-style term: partner ingredient count / distance^1
	gen gravity_term = partner_native_count / distance

	* Sum across all partners for each focal country
	bys adm0: egen import_potential = total(gravity_term)

	label var import_potential  ///
		"Import potential: sum of (partner native ingredients / distance)"

	keep adm0 import_potential
	duplicates drop

	tempfile import_potential
	save `import_potential', replace


* -----------------------------------------------------------------------*
* 5. Assemble final country-level dataset                                *
* -----------------------------------------------------------------------*

use `native_counts', clear

	merge 1:1 adm0 using `import_potential', nogen

	* Countries with no partners in the distance file get 0
	replace import_potential = 0 if missing(import_potential)

	* Optional: log-transform for convenience in regressions
	gen ln_import_potential = ln(import_potential + 1)
	label var ln_import_potential "Log(1 + import potential)"

	gen ln_native_ingredients = ln(num_native_ingredients + 1)
	label var ln_native_ingredients "Log(1 + native ingredient count)"

	sort adm0
	order adm0 num_native_ingredients ln_native_ingredients ///
	           import_potential ln_import_potential


* -----------------------------------------------------------------------*
* 6. Save                                                                *
* -----------------------------------------------------------------------*

save "$versatility/ingredient_import_potential.dta", replace

di as text "Done. Dataset saved to ingredient_import_potential.dta"
di as text "Observations: `=_N' countries"
sum num_native_ingredients import_potential
