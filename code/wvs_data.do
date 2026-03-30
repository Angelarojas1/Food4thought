   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *																	  *
   * - Note [AR 20241028]: 												  *	
   *	I am using Albesina plough paper as a guide for this			  *
   * ******************************************************************** *
   
   ** IDS Var: 
   ** Description: Get gender norms persistence data
   ** Written by: Ángela Rojas
   ** Last modified: October 28, 2024
   
   *- Import database
   use "${rawdata}/WVS/WVS_Time_Series_1981-2022_stata_v5_0.dta", clear
   
   *--- Variables of interest
   *-- When jobs are scarce, men should have more right to a job than women
   tab C001, nolab
   
   *- Drop observations which the respondents answer neither
   gen jobscarce = 1 if C001 == 1
   replace jobscarce = 0 if C001 == 2
   
   * On the whole, men make better political leaders than women do
   gen political_leaders = 1 if D059 == 4 // strongly disagree
   replace political_leaders = 2 if D059 == 3 // Disagree
   replace political_leaders = 3 if D059 == 2 // Agree
   replace political_leaders = 4 if D059 == 1 // Agree strongly
   
   sum jobscarce political_leaders
   
   * Albesina runs a regression where these variables are the outcome 
   collapse (mean) jobscarce political_leaders, by(COW_NUM S020)
   
   * Está re desbalanceada, hay países que tienen un resto de info y otros que nada

   xtset COW_NUM S020
   *tsfill, full
   
   drop if S020 < 1995
   tab COW_NUM
   
   drop political_leaders
   * Primero, asegúrate de que `COW_NUM` es de tipo string (si no, conviértelo)
	tostring COW_NUM, replace

* Cambia el formato para que cada país tenga su propia columna
	reshape wide jobscarce, i(S020) j(COW_NUM)
	
  * tsline jobscarce, over(COW_NUM)
   
   