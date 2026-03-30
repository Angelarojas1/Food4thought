* **************************************************************************** *
* Cuisine Complexity and Female Labor Force Participation
* Distance-weighted import versatility instrument with suitability extension
* **************************************************************************** *

*-------------------------------------------------------*
* 0. Create percentile ranks of suitability by ingredient
*-------------------------------------------------------*
use "${versatility}/milla_ciat_ing_suit.dta", clear

bys ingredient: egen suit_rank = rank(suitability), field
bys ingredient: egen n = count(suitability)

gen suit_score = ceil(100 * suit_rank / n)
gen suit_w = suit_score / 100

keep adm0 ingredient suit_w
tempfile suit_ranked
save `suit_ranked'

* Make renamed copy for destination-side merge on ingredient2
use `suit_ranked', clear
rename (adm0 ingredient suit_w) (adm0 ingredient2 suit_w2)
tempfile suit_ranked2
save `suit_ranked2'

* Make renamed copy for origin-side merge on nativeadm0 + ingredient2
use `suit_ranked', clear
rename (adm0 ingredient suit_w) (nativeadm0 ingredient2 suit_native)
tempfile suit_ranked_native
save `suit_ranked_native'

*-------------------------------------------------------*
* 1. Load main data
*-------------------------------------------------------*
use "$versatility/native_versatility_m_c1.dta", clear
ren (ingredient1 ingredient) (ingredient ingredient2)

*-------------------------------------------------------*
* 1A. Merge suitability for ingredient2 in destination country
*-------------------------------------------------------*
merge m:1 adm0 ingredient2 using `suit_ranked2', keep(1 3) nogen

*-------------------------------------------------------*
* 1B. Merge flavor data
*-------------------------------------------------------*
merge m:1 ingredient ingredient2 using "${versatility}/common_flavor_clean_m_c.dta"
keep if _merge == 3
drop _merge

tempfile main
save `main', replace

*-------------------------------------------------------*
* 2. Native origin pairs WITH origin suitability
*-------------------------------------------------------*
preserve
use `main', clear
keep if only_native == 1
keep ingredient2 adm0
rename adm0 nativeadm0
duplicates drop

merge m:1 nativeadm0 ingredient2 using `suit_ranked_native', keep(3) nogen

tempfile nativepairs
save `nativepairs', replace
restore

*-------------------------------------------------------*
* 3. Distance matrix
*-------------------------------------------------------*
use "${versatility}/distance_capital.dta", clear
tempfile distances
save `distances', replace

*-------------------------------------------------------*
* 4. Empty container for best scores
*-------------------------------------------------------*
clear
gen adm0 = ""
gen ingredient2 = ""

foreach i in Capital PreColumb PostColumb {
    foreach hl_dist in 500 1000 2000 3000 {
        gen best_score`i'_`hl_dist' = .
    }
}

tempfile results
save `results', replace

*-------------------------------------------------------*
* 5. Loop over ingredient2 and compute best origin
*-------------------------------------------------------*
use `main', clear
levelsof ingredient2, local(ings)

foreach ing of local ings {

    di as text "Processing ingredient: `ing'"

    preserve
    keep if ingredient2 == "`ing'"
    keep adm0 ingredient2
    duplicates drop
    tempfile subset
    save `subset', replace

    use `nativepairs', clear
    keep if ingredient2 == "`ing'"
    if _N == 0 {
        restore
        continue
    }

    tempfile nativesub
    save `nativesub', replace

    * Cross destination countries with native origin countries
    use `subset', clear
    cross using `nativesub'

    * Merge distances
    merge m:1 adm0 nativeadm0 using `distances', nogen keep(match)

    foreach hl_dist in 500 1000 2000 3000 {

        * Capital-distance version
        gen scoreCapital_`hl_dist'_pW = suit_native / (1 + distance/`hl_dist')
        bys adm0: egen best_scoreCapital_`hl_dist'_pW = max(scoreCapital_`hl_dist'_pW)

        * placeholders for future pre- and post-Columbian versions
        gen scorePreColumb_`hl_dist'_pW = suit_native / (1 + distance/`hl_dist')
        bys adm0: egen best_scorePreColumb_`hl_dist'_pW = max(scorePreColumb_`hl_dist'_pW)

        gen scorePostColumb_`hl_dist'_pW = suit_native / (1 + distance/`hl_dist')
        bys adm0: egen best_scorePostColumb_`hl_dist'_pW = max(scorePostColumb_`hl_dist'_pW)
    }

    keep adm0 ingredient2 best_score*
    duplicates drop

    append using `results'
    save `results', replace

    restore
}

*-------------------------------------------------------*
* 6. Merge best scores back to main data
*-------------------------------------------------------*
use `main', clear
merge m:1 adm0 ingredient2 using `results', nogen

*-------------------------------------------------------*
* 7. Create weights
*-------------------------------------------------------*
foreach i in Capital PreColumb PostColumb {
    foreach hl_dist in 500 1000 2000 3000 {

        gen weight`i'_`hl_dist'_pW = .

        * Native case
        replace weight`i'_`hl_dist'_pW = suit_w2 if only_native == 1

        * Non-native case
        replace weight`i'_`hl_dist'_pW = best_score`i'_`hl_dist'_pW ///
            if only_native == 0 & best_score`i'_`hl_dist'_pW < .
    }
}

*-------------------------------------------------------*
* 8. Compute instrument
*-------------------------------------------------------*
foreach i in Capital PreColumb PostColumb {
    foreach hl_dist in 500 1000 2000 3000 {

        * Sum of weights
        bys adm0: egen wsum`i'_`hl_dist'_pW = total(weight`i'_`hl_dist'_pW) if spice == 1

        * Relative weights
        gen w_rel`i'_`hl_dist'_pW = weight`i'_`hl_dist'_pW / ///
            wsum`i'_`hl_dist'_pW if spice == 1

        * Versatility
        bys adm0: egen vers_dist`i'_`hl_dist'_pW = ///
            mean(common * weight`i'_`hl_dist'_pW) if spice == 1

        sort adm0 native
        bys adm0 (vers_dist`i'_`hl_dist'_pW): ///
            replace vers_dist`i'_`hl_dist'_pW = ///
            vers_dist`i'_`hl_dist'_pW[_n-1] if missing(vers_dist`i'_`hl_dist'_pW)

        * Trade exposure
        bys adm0: egen trade_dist`i'_`hl_dist'_pW = ///
            mean(weight`i'_`hl_dist'_pW) if spice == 1

        sort adm0 native
        bys adm0 (trade_dist`i'_`hl_dist'_pW): ///
            replace trade_dist`i'_`hl_dist'_pW = ///
            trade_dist`i'_`hl_dist'_pW[_n-1] if missing(trade_dist`i'_`hl_dist'_pW)
    }
}

*-------------------------------------------------------*
* 9. Assign 0 to countries without any native spices
*-------------------------------------------------------*
bys adm0: egen has_native_spice = max(native == 1 & spice == 1)

foreach var of varlist vers_dist* trade_dist* {
    replace `var' = 0 if has_native_spice == 0
}
drop has_native_spice

keep adm0 vers_dist* trade_dist*
duplicates drop

foreach var of varlist vers_dist* trade_dist* {
    replace `var' = 0 if missing(`var')
}

*-------------------------------------------------------*
* 10. Save
*-------------------------------------------------------*
save "$versatility/native_versatility_m_c_dist_pWeight.dta", replace

