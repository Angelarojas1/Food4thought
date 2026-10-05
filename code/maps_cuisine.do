/* ------------------------------------------------------------------------
        Cuisine Complexity and Female Labor Force Participation	    

Authors: Girija Borker, Margarita Gafaro, Steve Beggreen

Created on: February 13, 2026
Created by: Angela Rojas

Last modified: 

Description:
This code created heat maps for LFP variables: Female, male and the gap.
------------------------------------------------------------------------ */

	
*********************************************************
*            Maps for cuisine variables                 *
*********************************************************
grmap, activate
cd "$rawdata/world_admin_shp"

*--- Import shapefile to Stata
	spshape2dta ne_10m_admin_0_countries_lakes, replace saving(countries)

*--- Open dta
	use "$rawdata/world_admin_shp/countries.dta", replace
	
	*- Organize variable for merging
	tab ADMIN if ISO_A3 == "-99"
	
	replace ISO_A3 = "XKX" if ADMIN == "Kosovo"
	replace ISO_A3 = "FRA" if ADMIN == "France"
	replace ISO_A3 = "NOR" if ADMIN == "Norway"
	replace ADMIN = "United States" if ADMIN == "United States of America"
	replace ADMIN = "Bosnia And Herzegovina" if ADMIN == "Bosnia and Herzegovina"
	replace ADMIN = "Cote D'Ivoire" if ADMIN == "Ivory Coast"
	replace ADMIN = "Serbia" if ADMIN == "Republic of Serbia"
	replace ADMIN = "Czech Republic" if ADMIN == "Czechia"
	replace ADMIN = "Bahamas" if ADMIN == "The Bahamas"

	drop if ISO_A3 == "-99"
	rename (ISO_A3 ADMIN) (adm0 country)
	
	keep country adm0 _ID _CX _CY
	*rename (_CX _CY) (_X _Y)

	merge 1:1 country using "$recipes/complexity_recipe.dta"
	
	gen clock_label = "⏰" + string(median_totaltime, "%9.0f")
	replace clock_label = "" if strpos(clock_label,".")>0
	
	gen spices_label = "🌶️" + string(median_spices, "%9.0f")
	replace spices_label = "" if strpos(spices_label,".")>0

	gen ingredients_label = "🥕" + string(median_ingredients, "%9.0f")
	replace ingredients_label = "" if strpos(ingredients_label,".")>0

*--------------------*
*    Create maps     *
*--------------------*
	
	*- Median time
	
	spmap median_totaltime using countries_shp.dta, ///
    id(_ID) ///
    clmethod(quantile) clnumber(5) ///
    fcolor(Oranges) ///
    ndfcolor(gs14) ///
    label(label(clock_label)  ///
          size(*0.6) xcoor(_CX) ycoor(_CY)) ///
    legend(off) 
	
	graph export "$figures/time_map.pdf", replace	
	
	*- Spices
	spmap w_mean_spices using countries_shp.dta, ///
    id(_ID) ///
    clmethod(quantile) clnumber(5) ///
    fcolor("245 240 230" ///
       "222 205 175" ///
       "196 167 125" ///
       "140 100 60" ///
       "90 60 30") ///
    ndfcolor(gs14) ///
    label(label(spices_label)  ///
          size(*0.6) xcoor(_CX) ycoor(_CY)) ///
    legend(off)
	
	graph export "$figures/spices_map.pdf", replace	
	
	*- Median ingredients
	spmap median_ingredients using countries_shp.dta, ///
    id(_ID) ///
    clmethod(quantile) clnumber(5) ///
    fcolor(Greens) ///
    ndfcolor(gs14) ///
    label(label(ingredients_label)  ///
          size(*0.6) xcoor(_CX) ycoor(_CY)) ///
    legend(off) 
	
	graph export "$figures/ing_map.png", replace	
