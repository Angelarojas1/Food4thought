/* ------------------------------------------------------------------------
        Cuisine Complexity and Female Labor Force Participation	    

Authors: Girija Borker, Margarita Gafaro, Steve Beggreen

Created on: January 25, 2026
Created by: Angela Rojas

Last modified: 

Description:
This code created heat maps for LFP variables: Female, male and the gap.
------------------------------------------------------------------------ */

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
	
	drop if ISO_A3 == "-99"
	rename ISO_A3 adm0
	
	keep adm0 _ID _CX _CY
	*rename (_CX _CY) (_X _Y)
		
*--. Merge with FLFP 
	merge 1:1 adm0 using "${flfp}/FLFPlong2019.dta", nogen
	
*--. Merge with MLFP 
	merge 1:1 adm0 using "${mlfp}/MLFPlong2019.dta", keep(3) nogen 
	// The ones in using that don't merge are not countries but regions
	
	rename *, lower
	
*--- Create gap variable
	gen gap = flfp - mlfp // 30 missings, countries we don't have information for

	format flfp mlfp gap %12.0f
	
*--------------------*
*    Create maps     *
*--------------------*
	
	*- FLFP
	grmap flfp, clmethod(custom) ///
	clbreaks(6 10 20 30 40 50 60 70 84) ///
	fcolor( ///
		white ///
		"254 232 200" ///
		"253 187 132" ///
		"251 106 74" ///
		"215 35 35" ///   
		"165 15 21" ///   
		"121 15 15" /// 
		"70 0 10" /// 
	) ///
	ndfcolor(gs14)
	
	graph export "$figures/flpf_heat_map.pdf", replace

	*- MLFP
	grmap mlfp, clnumber(9) clmethod(custom) ///
	clbreaks(24 40 50 60 65 70 75 80 96) ///
	fcolor( ///
		white ///
		"225 235 250" ///  
		"158 202 225" /// 
		"107 174 214" /// 
		"49 130 189" ///  
		"8 81 156" ///     
		"0 33 141" ///      
		"5 30 80" ///
	) ///
	ndfcolor(gs14)
	
	graph export "$figures/mlpf_heat_map.pdf", replace

	*- GAP
	grmap gap, clnumber(9) clmethod(custom) ///
	clbreaks(-60 -50 -40 -30 -20 -10 0 10 20 30) ///
	fcolor( ///
		"127 39 4" ///  
		"166 54 3" /// 
		"217 72 1" ///
		"253 141 60" /// 	
		"253 208 162" ///    	
		"254 230 206" ///      
		"217 239 139" ///
		"102 189 99" ///
		"0 104 55" ///
	) ///
	ndfcolor(gs14)
	
	graph export "$figures/gaplpf_heat_map.pdf", replace

