# ==========================================
# ⚙️ NASTAVENÍ CHOVÁNÍ HADA (SNAKE AI)
# ==========================================

# 1. ODMĚNY A TRESTY
ODMENA_ZA_JIDLO = 20.0      
ODMENA_ZA_VYHRU = 100.0     # NOVÉ: Obří bonus, když hru "dohraje"

# Rozdělené tresty
PENALE_ZA_ZED  = -10.0      
PENALE_ZA_OCAS = -10.0      
PENALE_ZA_KROK = -0.1       
PENALE_ZA_HLAD = -10.0      

# ------------------------------------------

# 2. LIMITY A PRAVIDLA
MAX_KROKU_BEZ_JIDLA = 100     # Smrt hlady

CILOVY_POCET_JABLEK = 30      # Pokud sní tolik jablek, vyhrál a hra končí.
                        

# ------------------------------------------

# 3. TRÉNINK
CELKOVY_POCET_HER = 2000       
UKAZKA_KAZDYCH_N_HER = 100     

# ------------------------------------------

# 4. GRAFIKA
RYCHLOST_HRY_NA_KONCI = 20