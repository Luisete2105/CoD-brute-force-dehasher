import multiprocessing.sharedctypes
import os
import time
#start_time:float = time.time()
#print("--- %s seconds ---" % (time.time() - start_time))

import multiprocessing
from multiprocessing import Process, Value, Array
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
        self.add_prefix( "items", [
            "zitem_", "ztable_", "zblueprint_",
            ] )
        self.add_suffix( "items", [
            "_part_1", "_part_2", "_part_3",
            "_lvl1_part_1", "_lvl1_part_2", "_lvl1_part_3",
            "_lvl2_part_1", "_lvl2_part_2", "_lvl2_part_3",
            "_lvl3_part_1", "_lvl3_part_2", "_lvl3_part_3",
            ] )


        self.add_prefix( "equipment", [
            "sig_", "killstreak_", "eq_", "equip_","zhield_", "ability_","gadget_"
            ] )
        self.add_suffix( "equipment", [
            "_cover", "_mine", "_grenade", "_wire", "_lh", "_dw", "_lh_upgraded", "_dw_upgraded", "_turret", "_turret_upgraded"
            ] )


        self.add_prefix( "weapons", [
            "ar_", "launcher_", "lmg_", "pistol_", "shotgun_", "smg_", "sniper_", "special_", "tr_",
            "ww_", "hero_", "ray_", "ray_gun_",
            ] )
        self.add_suffix( "weapons", [
            "_t8", "_t8_upgraded", "_t8_dw" "_t8_dw_upgraded",
            "_t9", "_t9_upgraded" "_t9_dw", "_t9_dw_upgraded",
            ] )


        self.add_prefix( "script_path", [
            "scripts/zm/weapons/zm_weap_",
            ] )
        self.add_suffix( "script_path", [
            ".csc", ".gsc",
            ] ) 
        '''

        '''
        self.add_prefix( "mini_dolls", [
            "eq_nesting_doll_grenade_", "nesting_doll_grenade_", "doll_grenade_",
            "doll_grenade", "nesting_doll_grenade_",

            "wpn_t8_zm_eqp_doll_", "wpn_t8_zm_eqp_nesting_doll_", "wpn_t8_zm_eqp_nesting_doll_single_",
            "wpn_t8_zm_eqp_doll_grenade_", "wpn_t8_zm_eqp_nesting_doll_grenade_", "wpn_t8_zm_eqp_nesting_doll_grenade_single_",
            "wpn_t8_grenade_doll_", "wpn_t8_grenade_nesting_doll_", "wpn_t8_grenade_nesting_doll_single_",

            "wpn_t7_zm_eqp_doll_", "wpn_t7_zm_eqp_nesting_doll_", "wpn_t7_zm_eqp_nesting_doll_single_",
            "wpn_t7_zm_eqp_doll_grenade_", "wpn_t7_zm_eqp_nesting_doll_grenade_", "wpn_t7_zm_eqp_nesting_doll_grenade_single_",
            "wpn_t7_grenade_doll_" "wpn_t7_grenade_nesting_doll_", "wpn_t7_grenade_nesting_doll_single_",

            "wpn_t8_zm_eq_nesting_doll_grenade_single_", "wpn_t8_zm_nesting_doll_grenade_single_", "wpn_t8_zm_nesting_doll_single_", "wpn_t8_zm_doll_single_",
            "wpn_t8_zm_eq_nesting_doll_grenade_", "wpn_t8_zm_nesting_doll_grenade_", "wpn_t8_zm_nesting_doll_", "wpn_t8_zm_doll_",

            "wpn_t8_eqp_nesting_doll_grenade_single_cluster_projectile_", "wpn_t8_eqp_nesting_doll_grenade_cluster_projectile_", "wpn_t8_eqp_nesting_doll_cluster_projectile_"
            "wpn_t8_eqp_nesting_doll_grenade_single_cluster_", "wpn_t8_eqp_nesting_doll_grenade_cluster_", "wpn_t8_eqp_nesting_doll_cluster_",

            "wpn_t8_eqp_nesting_doll_grenade_cluster_projectile_", "wpn_t8_eqp_nesting_doll_cluster_projectile_", "wpn_t8_eqp_nesting_doll_cluster_"
            "wpn_t8_eqp_nesting_doll_grenade_cluster_",


            "nesting_dolls_"
            "zombie_nesting_doll_single_",
            ] )
        
        self.add_suffix( "mini_dolls", [
            "_projectile", "_world", "_mini_world", "_view", "_mini_view",
            "_cluster", "_small", "_smaller", "_mini",
            ] )  
        '''
        
        '''
        self.add_prefix( "script_path", [
            "scripts/",
            "scripts/lui/",
            "scripts/hud/",
            "scripts/lui_hud/",


            "scripts/core_common/",
            "scripts/core_common/lua/",
            "scripts/core_common/hud/",
            "scripts/core_common/lui/",
            ] )
        '''


        
        self.add_prefix( "generic", [

            "a_", "b_", "s_", "t_", "m_", "v_", "w_",
            "a_w_", "a_b_", "a_s_", "a_t_", "a_m_", "a_v_", "a_w_", "a_e_",

            "sp_", "a_sp", "fx_", "ent_",

            "mdl_", "a_mdl_", "m_a_mdl_" "model_", "trigger_", "dir_",
            "zm_", "zombie_",
            "margwa_", "keeper_", "shadowman_", "trasher_", "mangler_", "rapz", "wasp_", "spider_",
            "player_", "a_player_", "s_player_", "players_", "a_players_", "s_players_",

            "ee_", "devgui_", "dev_", "debug_"

            ] )
        
        self.add_suffix( "generic", [

            "_zombie", "_zm", "_uid", "_id", "_ent", "_clip", "_ent", "_weapon",
            "_trigger", "_spawn", "_dir", "_pos", "_trig", "_switch", "_lever", "_button",

            "_ee", "_devgui", "_dev", "_debug",
            "_shadowman"


            ] )  
        


    def __del__(self) -> None:

        if debug:
            print( "[__del__] Class Brute Force Dehasher deleted!\n" )


    def add_prefix(self, category:str, list) -> None:

        # Check if the actual prefix already exists
        try:
            self.prefixes[ category ].append( "lui" )
        except:
            if debug:
                print(print( f"'{category}' prefix is NOT defined!") )
            
            self.prefixes[ category ]  = []

        else:
            self.prefixes[ category ].remove( "lui" )
            
        
        # Create empty suffix it doesnt exist to avoid errors when using brute force dehasher
        try:
            self.suffixes[ category ].append( "lui" )
        except:
            if debug:
                print(print( f"'{category}' prefix is NOT defined!") )
            
            self.suffixes[ category ]  = []
        else:
            self.suffixes[ category ].remove( "lui" )


        for prefix in list:
            self.prefixes[ category ].append( prefix )

        if debug:
            module_files.log_new_message("\n")
            module_files.log_new_message("Created new PREFIX category '"+category+"'")

            for i in range( len( self.prefixes[ category ] ) ):
                module_files.log_new_message( category+"["+str(i)+"] => "+self.prefixes[ category ][i] )

            module_files.log_new_message("\n\n")

    def add_suffix(self, category:str, list) -> None:

        # Check if the actual suffix already exists
        try:
            self.suffixes[ category ].append( "lui" )
        except:
            if debug:
                print(print( f"'{category}' prefix is NOT defined!") )
            
            self.suffixes[ category ]  = []

        else:
            self.suffixes[ category ].remove( "lui" )


        # Create empty preffix it doesnt exist to avoid errors when using brute force dehasher
        try:
            self.prefixes[ category ].append( "lui" )
        except:
            if debug:
                print(print( f"'{category}' prefix is NOT defined!") )
            
            self.prefixes[ category ]  = []
        else:
            self.prefixes[ category ].remove( "lui" )

        for prefix in list:
            self.prefixes[ category ].append( prefix )



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

    return global_dehasher.letters[ len(global_dehasher.letters)-1 ]

def get_next_letter( current_letter:str, counter:int ) -> str:
    global global_dehasher

    next_letter = global_dehasher.letters[ global_dehasher.letters_index[ current_letter ] +counter ]

    if debug:
        print( f"[get_next_letter] {current_letter} => {next_letter}" )

    return next_letter

def from_letter_to_index( current_letter:str ) -> int:
    global global_dehasher

    index = global_dehasher.letters_index[ current_letter ]

    if debug:
        print( f"[from_letter_to_index] {current_letter} => {index}" )

    return index

def from_index_to_letter( index:int ) -> str:
    global global_dehasher

    letter = global_dehasher.letters[ index ]

    if debug:
        print( f"[from_index_to_letter] {index} => {letter}" )

    return letter

def get_dehasher():

    global global_dehasher

    return global_dehasher