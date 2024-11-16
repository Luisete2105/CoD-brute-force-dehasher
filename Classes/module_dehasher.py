import multiprocessing.sharedctypes
import os
import time
#start_time:float = time.time()
#print("--- %s seconds ---" % (time.time() - start_time))

import multiprocessing
from multiprocessing import Process, cpu_count, Value, Array
import ctypes
from Classes import module_files

debug:bool = False


class Dehasher_class:

    def __init__(self) -> None:

        if debug:
            print( "[__init__] Class Dehasher created!\n" )

        self.searching_string:str
        self.active_searches:int = 0

        self.letters = [
            "a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z", #26
            #"0","1","2","3","4","5","6","7","8","9", # 10
            "_" # 1
        ]
        # 37

        self.letters_index = {}

        for i in range( len( self.letters ) ):
            self.letters_index[ self.letters[i] ] = i

        self.prefixes = {}
        self.suffixes = {}

        '''
        self.add_prefix( "weapons", [
            "ar_", "hero_", "launcher_", "lmg_", "pistol_", "shotgun_", "smg_", "sniper_", "special_", "tr_", "ww_"
            ] )
        self.add_suffix( "weapons", [
            "_t8", "_t8_upgraded", "_t8_dw" "_t8_dw_upgraded",
            "_t9", "_t9_upgraded" "_t9_dw", "_t9_dw_upgraded"
            ] )
        
        self.add_prefix( "items", [
            "zitem_", "ztable_", "zblueprint_"
            ] )
        self.add_suffix( "items", [
            "_part_1", "_part_2", "_part_3",
            "_lvl1_part_1", "_lvl1_part_2", "_lvl1_part_3",
            "_lvl2_part_1", "_lvl2_part_2", "_lvl2_part_3",
            "_lvl3_part_1", "_lvl3_part_2", "_lvl3_part_3"
            ] )
        
        self.add_prefix( "equipment", [
            "sig_", "killstreak_", "eq_", "equip_","zhield_", "ability_","gadget_"
            ] )
        self.add_suffix( "equipment", [
            "_cover", "_mine", "_grenade", "_wire", "_lh", "_dw", "_lh_upgraded", "_dw_upgraded", "_turret", "_turret_upgraded"
            ] )
        
        self.add_prefix( "blundergats", [
            "ww_", "ww_blundergat_", "ww_blundergat_acid_"
            ] )
        self.add_suffix( "blundergats", [
            "_t8", "_t8_unfinished",
            "_acid_t8", "_acid_t8_unfinished",
            "_projectile", "_t8_projectile", "_projectile_t8",
            "_t8_projectile_unfinished", "_acid_t8_projectile_unfinished"
            ] )

        self.add_prefix( "dolls", [
            "nesting_", "nesting_dolls_", "nestingdolls_", "dolls_", "zombie_nesting_dolls_","zm_nesting_dolls_", "nesting_dolls_single_", "zombie_nesting_dolls_single_","zm_nesting_dolls_single_",
            "takeo_", "takeo_nesting_dolls_", "takeo_nestingdolls_", "takeo_zm_nesting_dolls_", "takeo_dolls_", "takeo_single_", "takeo_dolls_single_", "takeo_nesting_single_", "takeo_nestingdolls_single_"
            ] )
        self.add_suffix( "dolls", [
            "_doll", "_dolls", "_nesting_dolls", "_nestingdolls", "_doll_single", "_dolls_single", "_nesting_dolls_single", "_nestingdolls_single",
            "_doll_takeo", "_dolls_takeo", "_nesting_dolls_takeo", "_nestingdolls_takeo", "_doll_single_takeo", "_dolls_single_takeo", "_nesting_dolls_single_takeo", "_nestingdolls_single_takeo"
            ] )
        
        self.add_prefix( "dont_ww", [
            "ww_", "ww_akud_"
            "ww_annihilator_", "hero_annihilator_", "ww_hero_annihilator_", "ww_annihilator_hero_" "annihilator_",
            "ww_revolver_", "ww_pistol_"
            ] )
        self.add_suffix( "dont_ww", [
            "_lv1", "_lvl1", "_t8_lv1", "_t8_lvl1",
            "_lv2", "_lvl2", "_t8_lv2", "_t8_lvl2",
            "_lv3", "_lvl3", "_t8_lv3", "_t8_lvl3"
            ] )
        '''        
        
        self.add_prefix( "weapons_strings", [
            "zombie/", "zombie/ww_", "zombie/hero_", 
            "zmweapon/", "zmweapon/ww_", "zmweapon/hero_",
            "weapon/", "weapon/ww_", "weapon/hero_",
            ] )
        self.add_suffix( "weapons_strings", [
            "_t8", "_t8_zm", "_upgraded", "_t8_upgraded", "_zm", "_t8_upgraded_zm"
            "_t8_lv1_zm", "_t8_lv2_zm", "_t8_lv3_zm"
            ] )        

    def __del__(self) -> None:

        if debug:
            print( "[__del__] Class Brute Force Dehasher deleted!\n" )


    def add_prefix(self, category:str, list) -> None:

        self.prefixes[ category ]  = []
        for prefix in list:
            self.prefixes[ category ].append( prefix )

        if debug:
            module_files.log_new_message("\n")
            module_files.log_new_message("Created new PREFIX category '"+category+"'")

            for i in range( len( self.prefixes[ category ] ) ):
                module_files.log_new_message( category+"["+str(i)+"] => "+self.prefixes[ category ][i] )

            module_files.log_new_message("\n\n")

    def add_suffix(self, category:str, list) -> None:

        self.suffixes[ category ]  = []
        for suffix in list:
            self.suffixes[ category ].append( suffix )

        if debug:
            module_files.log_new_message("\n")
            module_files.log_new_message("Created new SUFFIX category '"+category+"'")

            for i in range( len( self.suffixes[ category ] ) ):
                module_files.log_new_message( category+"["+str(i)+"] => "+self.suffixes[ category ][i] )
            
            module_files.log_new_message("\n")

# Class Dehasher END

global_dehasher:Dehasher_class = Dehasher_class()


def get_first_possible_letter() -> str:
    global global_dehasher

    return global_dehasher.letters[ 0 ]

def get_last_possible_letter() -> str:
    global global_dehasher

    return global_dehasher.letters[ global_dehasher.letters.size-1 ] 
