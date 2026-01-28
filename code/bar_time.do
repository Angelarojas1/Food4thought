/* ------------------------------------------------------------------------
        Cuisine Complexity and Female Labor Force Participation	    

Authors: Girija Borker, Margarita Gafaro, Steve Beggreen

Created on: January 28, 2026
Created by: Angela Rojas

Last modified: 

Description:
This code creates bar graph for cooking time around the world
------------------------------------------------------------------------ */

*--- Import cuisine variables database
	
	use "$codedata/merge/cooking_time_world.dta", clear
	
	*- Create bar graph
	graph bar female_min male_min, ///
	over(country, sort(FLFP) label(angle(vertical))) ///
	bar(1, fcolor(maroon) lcolor(maroon)) ///
	bar(2, fcolor(navy) lcolor(navy)) ///
	ylabel(, nogrid angle(vertical)) ///
	ytitle("Minutes") ///
	legend(order(1 "Female" 2 "Male" ) position(6) region(lcolor(black)) col(3)) ///
	graphregion(color(white)) bgcolor(white)
	
	graph export "${figures}/bar_cook_time.pdf", replace
