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