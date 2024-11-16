import os
import ctypes
import time
#start_time:float = time.time()
#print("--- %s seconds ---" % (time.time() - start_time))

from datetime import datetime
from multiprocessing import Process, Value, Array

import main_dehasher

from Classes import module_hasher
from Classes import module_files
from Classes import module_dehasher

#FNV-A1 53627c60c07a09f2,pleudir |T7 32 86775f0c,pleudir |T8 32 fc7cb164,pleudir
#0xDDDA9606, compiler // T7 32
#0xC5D43415, create_task_timer // T7 32


debug:bool = False

def print_menu_title_message(message:str) -> None:

    print( ">================================<" )
    print( datetime.now().strftime("%H:%M:%S")+": "+message )
    print( ">================================<" )

def print_menu_options() -> None:

    print( "\n>==================<" )
    print( "0 / Exit / Quit => Close the program" )
    print( "1 / Try Hash    => You enter a string and get the hashes for it" )
    print( "2 / List        => Hash list maker" )
    print( "3 / Dehasher    => Brute force dehasher" )
    print( ">==================<\n" )

def translate_option( option:str ) -> int:

    if option == "3" or option == "dehasher":
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
        print( f"T7 32 => { module_hasher.get_t7_32_str( hash ) }\nT8 32 => { module_hasher.get_t8_32_str( hash ) }\nFNVA1 => { module_hasher.get_fnva1_str( hash ) }\nDo you want to try another Hash?\n" )

        try_again:str = input( "Y / Yes | To try another Hash\n" ).lower()

        if try_again != "y" or try_again != "yes":
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
    

# module_files START

def dehash_menu() -> None:

    working = Value( ctypes.c_bool, True )
    searching_string = Array( ctypes.c_char, module_files.check_savedata_exists( module_dehasher.get_first_possible_letter() ).encode() )
    print( f"Starting dehashing, currently at => {searching_string.value.decode()}" )

    new_thread = Process( target=main_dehasher.check_word_combinations, args = [ working, searching_string ] )
    new_thread.start()

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



# module_files END


if __name__ == "__main__":

    start_menu()
    print_menu_title_message( "Exiting program" )

