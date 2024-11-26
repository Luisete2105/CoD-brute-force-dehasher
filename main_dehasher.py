import multiprocessing.sharedctypes
import os
import time
#start_time:float = time.time()
#print("--- %s seconds ---" % (time.time() - start_time))

import multiprocessing
from multiprocessing import Process, cpu_count, Value

#print(f'Number of physical cores: {psutil.cpu_count(logical=False)}')
import ctypes

from Classes import module_files
from Classes import module_hasher
from Classes import module_dehasher


debug:bool = False

t7:bool = False
t8_short:bool = False
t8_long:bool = True
t9_short:bool = False
t9_long:bool = False


def check_word_combinations( working:multiprocessing.sharedctypes.synchronized, searching_string:multiprocessing.sharedctypes.synchronized ) -> None:

    n_searches = Value( ctypes.c_int, 0)

    proc = Process( target=check_string_hashes, args = [ searching_string.value.decode(), n_searches ] )
    proc.start()

    max_searches:int = ( (cpu_count()/2) -1) # This should be fine for most systems
    #max_searches = 8 # in case you want a custom number of processes
    #max_searches:int = cpu_count() # Full cpu usage (This lags a lot)

    #return # Make it a single search for debugging porpuses

    while working.value:
        #time.sleep( 1 )

        if n_searches.value >= max_searches:
            #print( f"WAITING FOR A SEARCH TO STOP \n{n_searches.value} >= {max_searches}" )
            while n_searches.value >= max_searches:
                time.sleep( 0.05 ) # Like GSC

        #print( f"Creating new thread | {n_searches.value}" )

        n_searches.value += 1

        searching_string.value = get_string_to_search( searching_string.value.decode() ).encode()


        a_new_process = Process( target=check_string_hashes, args = [ searching_string.value.decode(), n_searches ] )
        a_new_process.start()

        #check_string_hashes( searching_string.value.decode(), n_searches ) # Without multithreading

    
    #print("WORKING SET TO FALSE, SAVING PROGRESS")
    module_files.write_savedata( searching_string.value.decode() )

    if n_searches.value > 0:
        print( f"WAITING FOR ALL SEARCHES TO STOP! {n_searches.value}" )
        a_new_process.join()


def check_string_hashes( string:str, n_searches:multiprocessing.sharedctypes.synchronized ) -> None:

    if string == None:
        print("Error, no string to check hash")
        module_files.log_new_message( f"Error, no string to check hash" )
        n_searches.value -= 1
        return
    
    if string == "":
        print("Error, string is empty to search for hash")
        module_files.log_new_message( f"Error, string is empty to search for hash" )
        n_searches.value -= 1
        return

    if debug:
        module_files.log_new_message( f"Checking hashes for word '{string}'" )
        print( f"Checking hashes for word '{string}'" )

    hash_list:list = []    
  
    if t7 and os.path.exists( "t7_32.txt" ):

        hash_list = module_files.get_hex_lines( "t7_32.txt" )
        hash_lookup( string, module_hasher.get_t7_32_hex, hash_list, "t7_32_found.txt")

    if t8_short and os.path.exists( "t8_32.txt" ):

        hash_list = module_files.get_hex_lines( "t8_32.txt" )
        hash_lookup( string, module_hasher.get_t8_32_hex, hash_list, "t8_32_found.txt")

    if t8_long and os.path.exists( "t8_64.txt" ):

        hash_list = module_files.get_hex_lines( "t8_64.txt" )
        hash_lookup( string, module_hasher.get_fnva1_hex, hash_list, "t8_64_found.txt")

    if t9_short and os.path.exists( "t9_32.txt" ):

        hash_list = module_files.get_hex_lines( "t9_32.txt" )
        hash_lookup( string, module_hasher.get_t8_32_hex, hash_list, "t9_32_found.txt")

    if t9_long and os.path.exists( "t9_64.txt" ):

        hash_list = module_files.get_hex_lines( "t9_64.txt" )
        hash_lookup( string, module_hasher.get_fnva1_hex, hash_list, "t9_64_found.txt")

    n_searches.value -= 1

def hash_lookup( word:str, hashing_func, hash_list:list, found_file_name) -> None:

    if debug:
        print( f"Searching {word} => {hashing_func(word)} | {found_file_name.split("_found")[0]}" )

    if hashing_func(word) in hash_list: # Search the string without prefixes or suffixes
        save_found_hash(word, hashing_func(word), found_file_name)

    global_dehasher = module_dehasher.get_dehasher()

    for category in global_dehasher.prefixes.keys(): # Search the string with all combinations of prefixes and suffixes

        if word[0] != "_": # Can add prefixes

            if word[ len(word)-1 ] != "_": # Can add suffixes

                for prefix in global_dehasher.prefixes[category]: # Looping thorugh prefixes

                    if hashing_func(prefix+word) in hash_list:
                        save_found_hash(prefix+word, hashing_func(prefix+word), found_file_name)

                    for suffix in global_dehasher.suffixes[category]: # Looping though suffixes

                        if hashing_func(word+suffix) in hash_list:
                            save_found_hash(word+suffix, hashing_func(word+suffix), found_file_name)

                        if hashing_func(prefix+word+suffix) in hash_list:
                            save_found_hash(prefix+word+suffix, hashing_func(prefix+word+suffix), found_file_name)

            else: # Can add prefixes but not suffixes
                    
                    for prefix in global_dehasher.prefixes[category]: # Looping trough prefixes

                        if hashing_func(prefix+word) in hash_list:
                            save_found_hash(prefix+word, hashing_func(prefix+word), found_file_name)
        
        else: # Cant add prefixes

            if word[ len(word)-1 ] != "_": # Cant add prefixes but can add suffixes

                for suffix in global_dehasher.suffixes[category]: # Looping through suffixes

                    if hashing_func(word+suffix) in hash_list:
                        save_found_hash(word+suffix, hashing_func(word+suffix), found_file_name)


def save_found_hash( word:str, hash:hex, found_file_name:str) -> None:

    module_files.log_new_message( f"HASH FOUND! {word} => {hash}" )
    print( f"HASH FOUND! {word} => {hash}" )
    module_files.add_found_hash( found_file_name, f"{word} => {hash}\n")





def get_string_to_search( searching_string ) -> str:

    ''' String data
        global_dehasher.searching_string                                            | string to search except the last letterself

        global_dehasher.letters[ global_dehasher.letters.size-1 ]                   | string last letter of the array of letters to compare (global_dehasher.letters)
        global_dehasher.letters[ 0 ]                                                | string first letter of the array of letters to compare


        global_dehasher.letters       | if I give a number, I get a letter
        global_dehasher.letters_index | if I give a letter, I get a number
    '''
    # global_dehasher.letters_index[ global_dehasher.searching_string[i] ]

    for i in range( len( searching_string ) ): # Checking all characters on the string to search

        if searching_string[i] == module_dehasher.get_last_possible_letter(): # If the string is in the last letter we want to check, we skip to the next character position
            #print("last letter detected! | "+global_dehasher.searching_string+"\n")
            continue
        else:
            string = ""
            for j in range(0, i): # We reset the chars before the one we want to upgrade
                string += module_dehasher.get_first_possible_letter()
            
            counter = 1
            #next_letter = global_dehasher.letters[ global_dehasher.letters_index[ global_dehasher.searching_string[i] ] +counter ]
            next_letter = module_dehasher.get_next_letter( searching_string[i], counter)

            test_string = string
            test_string += next_letter

            for j in range (i+1, len( searching_string ) ): # We copy the rest of the string
                #print( global_dehasher.searching_string )
                test_string += searching_string[j]

            #print("=================================\n")
            #print(" [get_string_to_search] test_string = "+test_string+" | string = "+string+"\n")
            
            while not is_valid_string(test_string, i, next_letter): # We check if its a valid letter AND its not the last one "_"

                if next_letter == module_dehasher.get_last_possible_letter():
                    #print("GOING WEIRD CODE\n")
                    str = check_last_letter_string( test_string, i, next_letter)
                    #print("Weird code changed the searching string")
                    return str

                counter += 1
                #next_letter = global_dehasher.letters[ global_dehasher.letters_index[ global_dehasher.searching_string[i] ] +counter ]
                next_letter = module_dehasher.get_next_letter( searching_string[i], counter)

                #print("2) Preordering strings = "+test_string+" | string = "+string+" | next_letter = "+next_letter+"\n")

                test_string = string
                test_string += next_letter

                #print("Ready to order strings = "+test_string+" | string = "+string+" | next_letter = "+next_letter+"\n")

                for j in range(i+1, len(searching_string) ):
                    test_string += searching_string[j] # We copy the rest of the string
                

                #print("Strings ordered! = "+test_string+" | string = "+string+" | next_letter = "+next_letter+"\n")

            #print("3) test_string = "+test_string+" | string = "+string+"\n")

            string += next_letter

            for j in range(i+1, len(searching_string) ):
                string += searching_string[j]  # We copy the rest of the string
                
            #print("4) test_string = "+test_string+" | string = "+string+"\n")
            #global_dehasher.searching_string = string
            #print("Hello 7 "+global_dehasher.searching_string+" | "+string)
            return string

        print("Error, you shouldnt be here, out of loop | "+global_dehasher.searching_string+" | "+str)
        return
        
    # We checked all the strings and all of them are the last one we want to check!

    str = ""

    for i in range(0, len(searching_string)+1):
        #str += global_dehasher.letters[0]
        str += module_dehasher.get_first_possible_letter()

    #if debug:
        #print("All letters are the last one! Adding a new one | "+global_dehasher.searching_string+" => "+str)
    #global_dehasher.searching_string = str
    return str
                
def check_last_letter_string( test_string:str, i:int, next_letter:str ) -> str:

    #print("[check_last_letter_string] test_string = "+test_string+" | i = "+str(i)+" | next_letter = "+next_letter+"\n")

    string = ""

    if i == len(test_string)-2:

        for j in range(0, len(test_string)+1 ):
            #string += global_dehasher.letters[0]
            string += module_dehasher.get_first_possible_letter()

        #print("1) String = "+string+"\n")

    else:

        carry = False
        for j in range(0, len(test_string) ):
            if test_string[j] == next_letter:
                carry = True
                #string += global_dehasher.letters[0]
                string += module_dehasher.get_first_possible_letter()
            elif carry:
                #string += global_dehasher.letters[ global_dehasher.letters_index[ test_string[j] ] +1 ]
                string += module_dehasher.get_next_letter( test_string[j], 1 )
                carry = False
            else:
                string += test_string[j]

        if carry: # If we had to change the last letter
            string = ""
            for j in range(0, len(test_string)+1 ):
                #string += global_dehasher.letters[0]
                string += module_dehasher.get_first_possible_letter()
            #print("Last letter had to be changed! | String = "+string+"\n")

    #print("2) String = "+string+"\n")

    set_letters = ""

    # Since we are adding a new letter, we have to check again all positions, this time from right to left
    for i in range( len(string)-1, -1, -1 ):

        #print("LOOP "+str(i)+"///////////////////\n")

        #counter = global_dehasher.letters_index[ string[i] ]
        counter = module_dehasher.from_letter_to_index( string[i] )
        #next_letter = global_dehasher.letters[ counter ]
        next_letter = module_dehasher.from_index_to_letter( counter )
        test_string = ""

        #print("A) i = "+str(i)+" counter = "+str(counter)+" | next_letter = "+next_letter+" | test_string = "+test_string+"\n")

        for j in range(0, i): # Copying the current testing letters
            test_string += string[j]
        
        #print("B) i = "+str(i)+" counter = "+str(counter)+" | next_letter = "+next_letter+" | test_string = "+test_string+"\n")

        #print("Start Letter Index: "+str(counter)+" | test string "+test_string+" | next_letter "+next_letter+" | pos "+str(i)+" | set letters "+set_letters+"\n")

        test_string += next_letter # We add the letter we want to check to current position
        test_string += set_letters # We add the already set letters from right to left

        #print("Start Letter Index: "+str(counter)+" | test string "+test_string+" | next_letter "+next_letter+" | pos "+str(i)+" | set letters "+set_letters+"\n")

        #while next_letter != global_dehasher.letters[ len(global_dehasher.letters)-1 ] and not is_valid_string( test_string, i, next_letter):
        while next_letter != module_dehasher.get_last_possible_letter() and not is_valid_string( test_string, i, next_letter):
        
            #print("D) counter = "+str(counter)+" | next_letter = "+next_letter+" | test_string = "+test_string+"\n")

            counter += 1
            #next_letter = global_dehasher.letters[ counter ]
            next_letter = module_dehasher.from_index_to_letter( counter )
            test_string = ""

            #print("E) counter = "+str(counter)+" | next_letter = "+next_letter+" | test_string = "+test_string+"\n")

            for j in range(0, i):
                test_string += string[j]

            #print("F) counter = "+str(counter)+" | next_letter = "+next_letter+" | test_string = "+test_string+"\n")

            test_string += next_letter # We add the letter we want to check to current position
            test_string += set_letters # We add the already set letters from right to left

            #print("G) counter = "+str(counter)+" | next_letter = "+next_letter+" | test_string = "+test_string+"\n")

        set_letters = next_letter + set_letters

        #print("H) i = "+str(i)+" counter = "+str(counter)+" | next_letter = "+next_letter+" | test_string = "+test_string+"\n")

        #print("HEY SPYRO, POR AQUI\n")

    #print("Final string | set_letters = "+set_letters+"\n")

    #global_dehasher.searching_string = set_letters
    return set_letters


#
##
#

def is_valid_string( string:str, position:int, new_letter:str) -> bool:

    # return True # Add a return True at the begining to make a full brute force search

    #print( "string = "+string+" | position = "+str(position)+" | new_letter = "+new_letter+"\n")

    # Bad letter combination
    if not is_last_letter( string, position) and not bad_letter_combo( new_letter, string[position+1] ):
        #if debug:
            #print("Bad combo str | "+string+" | pos "+str(position)+" | new letter "+new_letter+" next letter "+string[position+1])
        return False
    
    # No triple rule
    if is_next_letter( string, position, new_letter)  and is_next_letter( string, position+1, new_letter):
        #if debug:
            #print("No triple rule with: "+string)
        return False

    # No 3 vocals in a row
    if len(string) >= position+4 and is_vocal(string[position+1]) and is_vocal(string[position+2]) and is_vocal(string[position+3]):
        #if debug:
            #print("No Quad No vocal rule "+string)
        return False 

    # No 4 no vocals in a row
    if len(string) >= position+5 and not is_vocal(string[position+1]) and not is_vocal(string[position+2]) and not is_vocal(string[position+3]) and not is_vocal(string[position+4]):
        return False
    
    #if debug:
        #print("Valid string! => "+string+"\n")

    return True

def is_last_letter( string:str, position:int) -> bool:


    #if position > len(string)-1:
        #print("[is_last_letter] ERROR, POSITION IS BIGGER THAN THE STRING!\n")
        #return False # I know that this should return true but forcing a folse raises a exception by getting out of the string index making the program to stop

    return len(string)-1 == position

    if len(string)-1 == position:
        if debug:
            print( "Last pos... | "+string+" | "+str(position) )
        return True
    else:
        if debug:
            print( "Not last pos! | "+string+" | "+str(position) )
        return False
    

def is_previous_vocal(str:str, position:int) -> bool:

    if( len( str )  == 1)   : return False # The word only has 1 letter
    if( position == 0)      : return False # Cant be a previous letter because we are on the first position

    if str[position-1] == "a" or str[position-1] == "e" or str[position-1] == "i" or str[position-1] == "o" or str[position-1] == "u":
        return True
    else:
        return False

def is_next_vocal(str:str, position:int) -> bool:

    if len( str )  == 1         : return False # The word only has 1 letter
    if position == len( str ) -1   : return False # Cant be a previous letter because we are on the first position

    if str[position+1] == "a" or str[position-1] == "e" or str[position-1] == "i" or str[position-1] == "o" or str[position-1] == "u":
        return True
    else:
        return False

def is_vocal(letter:str) -> bool:

    if letter == "a" or letter == "e" or letter == "i" or letter == "o" or letter == "u":
        return True
    else:
        return False

def is_previous_letter(str:str, position:int, letter:str):

    if len(str) == 1: return False # The word only has 1 letter
    if position == 0: return False # Cant be a previous letter because we are on the first position

    if str[position-1] == letter:
        return True
    else:
        return False

def is_next_letter(str:str, position:int, letter:str):

    if len(str) == 1            : return False # The word only has 1 letter
    if position == len(str) -1  : return False # Cant be a next letter because we are on the last position

    if str[position+1] == letter:
        return True
    else:
        return False




''' weird no vowels combo rule

        -No:
             B     C     D     F     G     H     I     J     K     L     M     N     P     Q      R     S     T     U     V     W     X     Y     Z     
                  
        B    'BB', 'CB',       'FB', 'GB', 'HB',       'JB', 'KB',                   'PB', 'QB',       'SB',             'VB', 'WB', 'XB',       'ZB'
        C    'BC', 'CC', 'DC', 'FC', 'GC', 'HC',       'JC', 'KC',       'MC',       'PC', 'QC',                         'VC', 'WC', 'XC',       'ZC'
        D    'BD', 'CD', 'DD', 'FD', 'GD', 'HD'        'JD', 'KD',       'MD',       'PD', 'QD',             'TD',       'VD', 'WD', 'XD', 'YD', 'ZD'
        F    'BF', 'CF', 'DF', 'FF', 'GF', 'HF',       'JF', 'KF',       'MF',       'PF', 'QF', 'RF', 'SF',             'VF', 'WF', 'XF', 'YF', 'ZF'
        G    'BG', 'CG',       'FG', 'GG', 'HG',       'JG', 'KG',       'MG',             'QG',       'SG',             'VG', 'WG', 'XG',       'ZG'
        H    'BH',       'DH', 'FH', 'GH', 'HH',       'JH', 'KH',       'MH',             'QH', 'RH', 'SH',             'VH',       'XH', 'YH', 'ZH'
        J    'BJ', 'CJ', 'DJ', 'FJ', 'GJ', 'HJ',       'JJ', 'KJ', 'LJ', 'MJ',       'PJ', 'QJ', 'RJ', 'SJ', 'TJ',       'VJ', 'WJ', 'XJ', 'YJ', 'ZJ'
        K    'BK',       'DK', 'FK', 'GK', 'HK',       'JK', 'KK',       'MK',       'PK', 'QK',             'TK',       'VK', 'WK', 'XK', 'YK', 'ZK'
        L                                              'JL',             'ML',             'QL',                         'VL', 'WL', 'XL',       'ZL'
        M    'BM', 'CM',       'FM',       'HM',       'JM', 'KM',       'MM', 'NM', 'PM', 'QM',             'TM',       'VM', 'WM', 'XM',       'ZM'
        N    'BN', 'CN', 'DN', 'FN',       'HN',       'JN',       'LN'  'MN', 'NN', 'PN', 'QN',             'TN',       'VN', 'WN', 'XN',       'ZN'
        P    'BP', 'CP', 'DP', 'FP', 'GP', 'HP',       'JP', 'KP', 'LP',                   'QP', 'RP',       'TP',       'VP', 'WP',             'ZP' 
        Q    'BQ', 'CQ', 'DQ', 'FQ', 'GQ', 'HQ',       'JQ', 'KQ', 'LQ', 'MQ', 'NQ', 'PQ', 'QQ', 'RQ', 'SQ', 'TQ',       'VQ', 'WQ', 'XQ', 'YQ', 'ZQ'
        R                                  'HR',       'JR', 'KR', 'LR', 'MR',             'QR', 'RR', 'SR',             'VR',       'XR',       'ZR'
        S    'BS', 'CS', 'DS', 'FS', 'GS', 'HS',       'JS', 'KS',       'MS',       'PS', 'QS',       'SS', 'TS',       'VS', 'WS', 'XS', 'YS', 'ZS'
        T    'BT',       'DT',       'GT',             'JT', 'KT',       'MT',             'QT',                         'VT', 'WT', 'XT',       'ZT' 
        V    'BV', 'CV', 'DV', 'FV', 'GV', 'HV',       'JV', 'KV', 'LV'  'MV',       'PV', 'QV', 'RV', 'SV', 'TV',       'VV', 'WV', 'XV', 'YV', 'ZV'
        W    'BW', 'CW',       'FW', 'GW', 'HW',       'JW', 'KW', 'LW', 'MW',       'PW', 'QW',       'SW',             'VW', 'WW', 'XW',       'ZW'
        X    'BX', 'CX', 'DX', 'FX', 'GX', 'HX',       'JX', 'KX', 'LX', 'MX', 'NX', 'PX', 'QX', 'RX', 'SX', 'TX',       'VX', 'WX', 'XX', 'YX', 'ZX'
        Y    'BY', 'CY', 'DY', 'FY', 'GY', 'HY', 'IY', 'JY', 'KY', 'LY', 'MY', 'NY', 'PY', 'QY', 'RY', 'SY', 'TY', 'UY', 'VY', 'WY', 'XY', 'YY', 'ZY'
        Z    'BZ', 'CZ', 'DZ', 'FZ', 'GZ', 'HZ',       'JZ', 'KZ', 'LZ', 'MZ', 'NZ', 'PZ', 'QZ', 'RZ', 'SZ', 'TZ',       'VZ', 'WZ', 'XZ', 'YZ', 'ZZ' 

'''

#
## Checks for weird 2 letters combos
#
    
def bad_letter_combo(new_letter:str, next_letter:str) -> bool:

    if new_letter == "a"    : return check_a( next_letter )
    elif new_letter == "b"  : return check_b( next_letter )
    elif new_letter == "c"  : return check_c( next_letter )
    elif new_letter == "d"  : return check_d( next_letter )
    elif new_letter == "e"  : return check_e( next_letter )
    elif new_letter == "f"  : return check_f( next_letter )
    elif new_letter == "g"  : return check_g( next_letter )
    elif new_letter == "h"  : return check_h( next_letter )
    elif new_letter == "i"  : return check_i( next_letter )
    elif new_letter == "j"  : return check_j( next_letter )
    elif new_letter == "k"  : return check_k( next_letter )
    elif new_letter == "l"  : return check_l( next_letter )
    elif new_letter == "m"  : return check_m( next_letter )
    elif new_letter == "n"  : return check_n( next_letter )
    elif new_letter == "o"  : return True
    elif new_letter == "p"  : return check_p( next_letter )
    elif new_letter == "q"  : return check_q( next_letter )
    elif new_letter == "r"  : return check_r( next_letter )
    elif new_letter == "s"  : return check_s( next_letter )
    elif new_letter == "t"  : return check_t( next_letter )
    elif new_letter == "u"  : return check_u( next_letter )
    elif new_letter == "v"  : return check_v( next_letter )
    elif new_letter == "w"  : return check_w( next_letter )
    elif new_letter == "x"  : return check_x( next_letter )
    elif new_letter == "y"  : return check_y( next_letter )
    elif new_letter == "z"  : return check_z( next_letter )
    elif new_letter == "_"  : return check__( next_letter )
    else:
        print("\nError, unknown bad letter combo\nnew_letter => "+new_letter+"\nnext_letter => "+next_letter)
        return False


def check_a(next_letter:str) -> bool:

    if next_letter == "a":
        return False
    
    return True

def check_b(next_letter:str) -> bool:

    if is_vocal(next_letter) or next_letter == "l" or next_letter == "s" or next_letter == "_":
        return True
    
    return False

def check_c(next_letter:str) -> bool:

    if is_vocal(next_letter) or next_letter == "h" or next_letter == "k" or next_letter == "l" or next_letter == "r" or next_letter == "t" or next_letter == "t" or next_letter == "_":
        return True

    return False

def check_d(next_letter:str) -> bool:

    if is_vocal(next_letter) or next_letter == "b" or next_letter == "c" or next_letter == "g" or next_letter == "l" or next_letter == "m" or next_letter == "r" or next_letter == "w" or next_letter == "_":
        return True
    
    return False

def check_e(next_letter:str) -> bool:
    
    if next_letter == "e" or next_letter == "i":
        return False
    
    return True

def check_f(next_letter:str) -> bool:

    if is_vocal(next_letter) or next_letter == "l" or next_letter == "r" or next_letter == "t" or next_letter == "_":
        return True
    
    return False

def check_g(next_letter:str) -> bool:

    if is_vocal(next_letter) or next_letter == "l" or next_letter == "m" or next_letter == "n" or next_letter == "r" or next_letter == "_":
        return True
    
    return False

def check_h(next_letter:str) -> bool:

    if is_vocal(next_letter) or next_letter == "l" or next_letter == "t" or next_letter == "_":
        return True
    
    return False

def check_i(next_letter:str) -> bool:

    if next_letter == "i" or next_letter == "y":
        return False
    
    return True

def check_j(next_letter:str) -> bool:

    if is_vocal(next_letter) or next_letter == "_":
        return True
    
    return False

def check_k(next_letter:str) -> bool:

    if is_vocal(next_letter) or next_letter == "l" or next_letter == "n" or next_letter == "_":
        return True
    
    return False

def check_l(next_letter:str) -> bool:

    if next_letter == "j" or next_letter == "n" or next_letter == "p" or next_letter == "q" or next_letter == "r" or next_letter == "v" or next_letter == "w" or next_letter == "x" or next_letter == "y" or next_letter == "z" or next_letter == "_":
        return False
    
    return True

def check_m(next_letter:str) -> bool:

    if is_vocal(next_letter) or next_letter == "b" or next_letter == "p" or next_letter == "_":
        return True
    
    return False

def check_n(next_letter:str) -> bool:

    if next_letter == "m" or next_letter == "n" or next_letter == "q" or next_letter == "x" or next_letter == "y" or next_letter == "z" or next_letter == "_":
        return False

    return True

def check_p(next_letter:str) -> bool:

    if is_vocal(next_letter) or next_letter == "g" or next_letter == "h" or next_letter == "l" or next_letter == "q" or next_letter == "r" or next_letter == "t" or next_letter == "_":
        return True
    
    return False

def check_q(next_letter:str) -> bool:

    return next_letter == "u"

def check_r(next_letter:str) -> bool:

    if next_letter == "f" or next_letter == "h" or next_letter == "j" or next_letter == "p" or next_letter == "q" or next_letter == "r" or next_letter == "v" or next_letter == "x" or next_letter == "y" or next_letter == "z":
        return False

    return True

def check_s(next_letter:str) -> bool:

    if is_vocal(next_letter) or next_letter == "c" or next_letter == "d" or next_letter == "k" or next_letter == "l" or next_letter == "m" or next_letter == "n" or next_letter == "p" or next_letter == "t" or next_letter == "_":
        return True
    
    return False

def check_t(next_letter:str) -> bool:

    if next_letter == "d" or next_letter == "j" or next_letter == "k" or next_letter == "m" or next_letter == "n" or next_letter == "p" or next_letter == "q" or next_letter == "s" or next_letter == "v" or next_letter == "x" or next_letter == "y" or next_letter == "z":
        return False
    
    return True

def check_u(next_letter:str) -> bool:

    if next_letter == "u" or next_letter == "y":
        return False
    
    return True

def check_v(next_letter:str) -> bool:

    if is_vocal(next_letter)  or next_letter == "_":
        return True
    
    return False

def check_w(next_letter:str) -> bool:

    if is_vocal(next_letter) or next_letter == "h" or next_letter == "r" or next_letter == "_":
        return True
    
    return False

def check_x(next_letter:str) -> bool:

    if is_vocal(next_letter) or next_letter == "p" or next_letter == "_":
        return True
    
    return False

def check_y(next_letter:str) -> bool:

    if next_letter == "d" or next_letter == "f" or next_letter == "h" or next_letter == "j" or next_letter == "k" or next_letter == "q" or next_letter == "s" or next_letter == "v" or next_letter == "x" or next_letter == "y" or next_letter == "z":
        return False
    
    return True

def check_z(next_letter:str) -> bool:

    if is_vocal(next_letter) or next_letter == "_":
        return True
    
    return False

def check__(next_letter:str) -> bool:

    if next_letter == "_":
        return False
    
    return True