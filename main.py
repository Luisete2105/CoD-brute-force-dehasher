import os
import ctypes
import time
#start_time:float = time.time()
#print("--- %s seconds ---" % (time.time() - start_time))

from datetime import datetime
from multiprocessing import Value, Array
from threading import Thread

import main_dehasher
import main_collector

from Classes import module_hasher
from Classes import module_files
from Classes import module_dehasher




'''
Hashing 'pleudir'
T7 32 => 0x86775f0c | 86775f0c
T8 32 => 0xfc7cb164 | fc7cb164
FNVA1 => 0x53627c60c07a09f2 | 53627c60c07a09f2
HashIWRes => 0x549afccc4758bdeb | 549afccc4758bdeb
HashIWTag => 0x3e163d52 | 3e163d52
HashJupScr => 0x89b6b9b94add5236 | 89b6b9b94add5236
HashIWDVar => 0xef63d32cf0037237 | ef63d32cf0037237
HashT10Scr => 0x876e0ac813f9e747 | 876e0ac813f9e747
HashT10ScrSP => 0xa1753b83db2c84b7 | a1753b83db2c84b7
'''

debug:bool = False

def print_menu_title_message(message:str) -> None:

    print( ">================================<" )
    print( datetime.now().strftime("%H:%M:%S")+": "+message )
    print( ">================================<" )

def print_menu_options() -> None:

    print( "\n>==================<" )
    print( "0 / Exit / Quit => Close the program" )
    print( "1 / Try Hash    => You enter a string and get the hashes for it" )
    print( "2 / List        => Hash list maker from ATE's Dehasher tool" )
    print( "3 / Collect     => Collect hashes from a source repository" )
    print( "4 / Dehasher    => Brute force dehasher" )
    print( ">==================<\n" )

def translate_option( option:str ) -> int:

    if option == "4" or option == "dehasher":
        return 4
    if option == "3" or option == "collect":
        return 3
    if option == "2" or option == "list":
        return 2
    if option == "1" or option == "hash" or option == "try hash":
        return 1
    elif option == "0" or option == "exit" or option == "quit":
        return 0
    else:
        return 69

def execute_menu_task( option:int ) -> None:

    if option == 1:
        hash_menu()
        pass
    if option == 2:
        files_menu()
        pass
    if option == 3:
        source_menu()
        pass
    if option == 4:
        dehash_menu()
        pass
    
def start_menu() -> None:

    print_menu_title_message( "Starting program" )

    while True:

        print_menu_options()

        str_option:str = input().lower()
        int_option:int = translate_option( str_option )
        
        if debug:
            print( datetime.now().strftime("%H:%M:%S")+": "+"Option chosen => "+str_option+" / "+str(int_option)+"\n" )
        
        if int_option == 69:
            print( "\n"+datetime.now().strftime("%H:%M:%S")+": "+"Unknown task chosen, try again\n")
            continue
        elif int_option == 0:
            return
        else:
            execute_menu_task( int_option )


# module_hasher START

def hash_menu() -> None:

    print_menu_title_message( "Hash converter menu" )

    while True:

        print( "Type your word to hash\n" )
        hash:str = input( "\n" ).lower()

        print( "Hashing '"+hash+"'\n" )
        '''
        print( f"T7 32 => { module_hasher.get_t7_32_str( hash ) }\n"
              f"T8 32 => { module_hasher.get_t8_32_str( hash ) }\n"
              f"FNVA1 => { module_hasher.get_fnva1_str( hash ) }\n"
              f"HashIWRes => { module_hasher.get_HashIWRes_str( hash ) }\n"
              f"HashIWTag => { module_hasher.get_HashIWTag_str( hash ) }\n"
              f"HashJupScr => { module_hasher.get_HashJupScr_str( hash ) }\n"
              f"HashIWDVar => { module_hasher.get_HashIWDVar_str( hash ) }\n"
              f"HashT10Scr => { module_hasher.get_HashT10Scr_str( hash ) }\n"
              f"HashT10ScrSPPre => { module_hasher.get_HashT10ScrSPPre_str( hash ) }\n"
              f"HashT10ScrSPPost => { module_hasher.get_HashT10ScrSPPost_str( hash ) }\n"
              f"HashT10ScrSP => { module_hasher.get_HashT10ScrSP_str( hash ) }\n"

              "\nDo you want to try another Hash?\n" )
        '''
        print( f"T7 32 => { module_hasher.get_t7_32_hex( hash ) } | { module_hasher.get_t7_32_str( hash ) }\n"
              f"T8 32 => { module_hasher.get_t8_32_hex( hash ) } | { module_hasher.get_t8_32_str( hash ) }\n"
              f"FNVA1 => { module_hasher.get_fnva1_hex( hash ) } | { module_hasher.get_fnva1_str( hash ) }\n"
              f"HashIWRes => { module_hasher.get_HashIWRes_hex( hash ) } | { module_hasher.get_HashIWRes_str( hash ) }\n"
              f"HashIWTag => { module_hasher.get_HashIWTag_hex( hash ) } | { module_hasher.get_HashIWTag_str( hash ) }\n"
              f"HashJupScr => { module_hasher.get_HashJupScr_hex( hash ) } | { module_hasher.get_HashJupScr_str( hash ) }\n"
              f"HashIWDVar => { module_hasher.get_HashIWDVar_hex( hash ) } | { module_hasher.get_HashIWDVar_str( hash ) }\n"
              f"HashT10Scr => { module_hasher.get_HashT10Scr_hex( hash ) } | { module_hasher.get_HashT10Scr_str( hash ) }\n"
              #f"HashT10ScrSPPre => { module_hasher.get_HashT10ScrSPPre_hex( hash ) } | { module_hasher.get_HashT10ScrSPPre_str( hash ) }\n"
              #f"HashT10ScrSPPost => { module_hasher.get_HashT10ScrSPPost_hex( hash ) } | { module_hasher.get_HashT10ScrSPPost_str( hash ) }\n"
              f"HashT10ScrSP => { module_hasher.get_HashT10ScrSP_hex( hash ) } | { module_hasher.get_HashT10ScrSP_str( hash ) }\n"

              "\nDo you want to try another Hash?\n" )
        try_again:str = input( "Y / Yes | To try another Hash\n" ).lower()

        if try_again != "y" and try_again != "yes":
            #print(f"try_again = {try_again}")
            break
        
    print("Going back to menu")

# module_hasher END
    

# module_files START

def files_menu() -> None:

    print( "\n>==================<" )
    print( "0 => Bo3" )
    print( "1 => Bo4" )
    print( "2 => CW" )
    print( "Anything else => Cancel\n" )
    print( ">==================<\n" )

    str_option:str = input().lower()
    
    if str_option != "0" and str_option != "1" and str_option != "2": # Check if the player dont want to collect the hashes of a game
        print( "Canceling hash list maker...\n" )
        return
    
    if not os.path.exists( "comp.txt" ) and not os.path.exists( "hashes.txt" ): # Check if there isnt any valid hash file
        print( "Error, couldnt find 'comp.txt' or 'hashes.txt'\n" )
        return
    
    # comp.txt
    comp:module_files.Files_class = module_files.Files_class()
    comp.set_file( "comp.txt", "r" )

    # hashes.txt
    hashes:module_files.Files_class = module_files.Files_class()
    hashes.set_file( "hashes.txt", "r" )

    if str_option == "0":

        module_files.log_new_message( "T7 selected" )
        module_files.get_t7_hashes( comp, hashes )

    elif str_option == "1":

        module_files.log_new_message( "T8 selected" )        
        module_files.get_t8_hashes( comp, hashes )

    elif str_option == "2":

        module_files.log_new_message( "T9 selected" )
        module_files.get_t9_hashes( comp, hashes )

    del comp
    del hashes

# module_files END
    

# main_dehasher START

def dehash_menu() -> None:

    working = Value( ctypes.c_bool, True )
    searching_string = Array( ctypes.c_char, "aaaaaaaaaaaaaaaa".encode() )
    searching_string.value =  module_files.check_savedata_exists( module_dehasher.get_first_possible_letter() ).encode()
    print( f"Starting dehashing, currently at => {searching_string.value.decode()}" )

    new_thread = Thread( target=main_dehasher.check_word_combinations, args = [ working, searching_string ] )
    new_thread.start()

    #new_thread = Process( target=main_dehasher.check_word_combinations, args = [ working, searching_string ] )
    #new_thread.start()

    #return # Make it a single search for debugging purposes

    while( True ):
        time.sleep( 0.5 )

        print( ">==================<" )
        print("Type '1', 's' or 'show' to see current word and found words\nType '0', 'e' or 'exit' to stop`dehashing")
        print( ">==================<\n" )
        int_input:int = get_option_input( input().lower() )

        if int_input == 0:
            print( f"\nCurrent word: {searching_string.value.decode()}\n" )
            continue
        elif int_input == 1:
            working.value = False
            break
        else:
            continue
        
    #print("Stopping dehasher")

    if new_thread.is_alive():
        print("Waiting for thread to end")
        new_thread.join()

        if new_thread.is_alive():
            print("ERROR: Killing problematic thread")
            new_thread.terminate()


def get_option_input( str_input:str ) -> int:

    if str_input == "1" or str_input == "s" or str_input == "show":
        return 0
    if str_input == "0" or str_input == "e" or str_input == "exit":
        return 1
    else:
        return 2

# main_dehasher END

# main_collector START
    
def source_menu() -> None:

    print( "\n>==================<" )
    print( "0 => Bo3" )
    print( "1 => Bo4" )
    print( "2 => CW" )
    print( "3 => MWiii" )
    print( "4 => Bo6" )
    print( "Anything else => Cancel\n" )
    print( ">==================<\n" )

    #str_option:str = input().lower()

    try:
        option:int = int(input().lower())

    except ValueError:
        print("Not a number, canceling source menu")
        return
    except:
        print("Unknown error")
        return
    
    else:
        if option < 0 or option > 4:
            print("Canceling source menu")
            return



    if option == 0:
        print("Bo3 selected")
    elif option == 1:
        print("Bo4 selected")
    elif option == 2:
        print("CW selected")
    elif option == 3:
        print("MWiii selected")
    elif option == 1:
        print("Bo6 selected")




    print("Ended source")
    return
    
    
    if not os.path.exists( "comp.txt" ) and not os.path.exists( "hashes.txt" ): # Check if there isnt any valid hash file
        print( "Error, couldnt find 'comp.txt' or 'hashes.txt'\n" )
        return
    
    # comp.txt
    comp:module_files.Files_class = module_files.Files_class()
    comp.set_file( "comp.txt", "r" )

    # hashes.txt
    hashes:module_files.Files_class = module_files.Files_class()
    hashes.set_file( "hashes.txt", "r" )

    if str_option == "0":

        module_files.log_new_message( "T7 selected" )
        module_files.get_t7_hashes( comp, hashes )

    elif str_option == "1":

        module_files.log_new_message( "T8 selected" )        
        module_files.get_t8_hashes( comp, hashes )

    elif str_option == "2":

        module_files.log_new_message( "T9 selected" )
        module_files.get_t9_hashes( comp, hashes )

    del comp
    del hashes

# main_collector END

def hash_dvar(dvar : str):
    OFFSET_BASIS = 0xD86A3B09566EBAAC
    PRIME = 0x10000000233
    MOD = 2 ** 64
    _hash = OFFSET_BASIS

    EXTRA = 'q6n-+7=tyytg94_*'
    NEW_STR = dvar[0] + EXTRA + dvar[1:]

    for char in NEW_STR.lower():
        _hash = PRIME * (ord(char) ^ _hash) % MOD

    return _hash

#module_files.log_new_message( f"cg_fovScale = {hex(hash_dvar("cg_fovScale"))}\n" )





if __name__ == "__main__":

    #start_menu()

    main_collector.collector()




    print_menu_title_message( "Exiting program" )

