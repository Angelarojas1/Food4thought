   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *																	  *
   * - Inputs: ""											      		  *
   * - Output: ""	      									    		  *
   *		   ""												  		  *
   * ******************************************************************** *
   
   ** IDS Var: adm0
   ** Description: Cleans CPI data
   ** Written by: Ángela Rojas
   ** Last modified: 
   
   * Import population dataset
   import delimited "${rawdata}/appliances/fed/fredgraph.csv", ///
   encoding(UTF-8) varnames(1) case(lower) clear
   
   * Create year variable
   gen year = real(substr(observation_date, 1, 4))
   
   * Get annual mean
   collapse p* c*, by(year)
   
   * Rename variables 
   rename pcu33523352 US_PPI
   rename cp0531euccm086nest EU_HICP_m
   rename pcu335221335221p US_PPI_disc
   rename cp0530euccm086nest EU_HICP
   
   label var US_PPI "Producer Price Index by Industry: Household Appliance Manufacturing"
   label var EU_HICP_m "Major Household Appliances Whether Electric or Not and Small Electric Household Appliances "
   label var US_PPI_disc "Producer Price Index by Industry: Household Cooking Appliance Manufacturing: Primary Products (DISCONTINUED) "
   label var EU_HICP "Harmonized Index of Consumer Prices: Household Appliances "
   
   save "$codedata/appliances/price_index.dta", replace
