import multiprocessing.sharedctypes
import os
import time
#start_time:float = time.time()
#print("--- %s seconds ---" % (time.time() - start_time))

import multiprocessing
from multiprocessing import Process, cpu_count, Value, Array
import ctypes

from Classes import module_files
from Classes import module_hasher
#from Classes import module_dehasher


debug:bool = True

t7:bool = False
t8_short:bool = False
t8_long:bool = True
t9_short:bool = False
t9_long:bool = False


def check_word_combinations( working:multiprocessing.sharedctypes.synchronized, searching_string:multiprocessing.sharedctypes.synchronized ) -> None:

    print( f"pased string {searching_string.value.decode()}" )

    start_time:float = time.time()
    proc = Process( target=check_string_hashes, args = [ searching_string.value.decode() ] )
    proc.start()
    proc.join()
    print("First word check done!")
    print("--- %s seconds ---" % (time.time() - start_time))

    return # Make it a single search for debugging porpuses

    while working.value:
        time.sleep( 0.25 )

        #get_string_to_search( global_dehasher )
        #string_to_search = global_dehasher.searching_string

        #a_new_thread = Process( target=check_string_hashes, args = [ global_dehasher, string_to_search, ] )
        #a_new_thread.start()
        #return
    
    print("WORKING SET TO FALSE")

def check_string_hashes( string:str ) -> None:

    print("CHECKING STRING HASHES")

    if string == None:
        print("Error, no string to check hash")
        module_files.log_new_message( f"Error, no string to check hash" )
        return
    if string == "":
        print("Error, string is empty to search for hash")
        module_files.log_new_message( f"Error, string is empty to search for hash" )
        return

    module_files.log_new_message( f"Checking hashes for word '{string}'" )
    print( f"Checking hashes for word '{string}'" )

    hash_list:list = []    

    '''
    if t7 and os.path.exists( "t7_32.txt" ):

        manager_t7_32:class_file_manager = class_file_manager.File_Manager()
        class_file_manager.assign_file( manager_t7_32, "t7_32.txt", "r" )

        a_thread = Process( target=class_file_manager.check_existing_hash, args = [ manager_t7_32, string, global_dehasher, class_hasher.get_t7_32_hash] )
        a_thread.start()

    if t8_short and os.path.exists( "t8_32.txt" ):

        manager_t8_32:class_file_manager = class_file_manager.File_Manager()
        class_file_manager.assign_file( manager_t8_32, "t8_32.txt", "r")

        b_thread = Process( target=class_file_manager.check_existing_hash, args = [ manager_t8_32, string, global_dehasher, class_hasher.get_t8_32_hash] )
        b_thread.start()
    '''
    if t8_long and os.path.exists( "t8_64.txt" ):

        hash_list = module_files.get_hex_lines( "t8_64.txt" )
        print("Starting Hash Lookup")
        hash_lookup( string, module_hasher.get_fnva1_hex( string ), hash_list, "t8_64_found.txt")

    '''
    if t9_short and os.path.exists( "t9_32.txt" ):

        manager_t9_32:class_file_manager = class_file_manager.File_Manager()
        class_file_manager.assign_file( manager_t9_32, "t9_32.txt", "r")


        d_thread = Process( target=class_file_manager.check_existing_hash, args = [ manager_t9_32, string, global_dehasher, class_hasher.get_t8_32_hash] )
        d_thread.start()

    if t9_long and os.path.exists( "t9_64.txt" ):
        manager_t9_64:class_file_manager = class_file_manager.File_Manager()
        class_file_manager.assign_file( manager_t9_64, "t9_64.txt", "r")

        e_thread = Process( target=class_file_manager.check_existing_hash, args = [ manager_t9_64, string, global_dehasher, class_hasher.get_fnva1_hash] )
        e_thread.start()
    '''

def hash_lookup( word:str, hash:hex, hash_list:list, found_file_name) -> bool:

    print( f"Searching {word} => {hash}" )

    # average 0.22
    if hash in hash_list:
        module_files.log_new_message( f"HASH FOUND! {word} => {hash}" )
        print( f"HASH FOUND! {word} => {hash}" )
        module_files.add_found_hash( found_file_name, f"{word} => {hash}\n")
        return True

    



def get_string_to_search( global_dehasher ) -> None:

    ''' String data
        global_dehasher.searching_string                                            | string to search except the last letterself

        global_dehasher.letters[ global_dehasher.letters.size-1 ]                   | string last letter of the array of letters to compare (global_dehasher.letters)
        global_dehasher.letters[ 0 ]                                                | string first letter of the array of letters to compare


        global_dehasher.letters       | if I give a number, I get a letter
        global_dehasher.letters_index | if I give a letter, I get a number
    '''
    # global_dehasher.letters_index[ global_dehasher.searching_string[i] ]

    for i in range( len( global_dehasher.searching_string ) ): # Checking all characters on the string to search

        if global_dehasher.searching_string[i] == global_dehasher.letters[ len( global_dehasher.letters )-1 ]: # If the string is in the last letter we want to check, we skip to the next character position
            #print("last letter detected! | "+global_dehasher.searching_string+"\n")
            continue
        else:
            string = ""
            for j in range(0, i): # We reset the chars before the one we want to upgrade
                string += global_dehasher.letters[0]
            
            counter = 1
            next_letter = global_dehasher.letters[ global_dehasher.letters_index[ global_dehasher.searching_string[i] ] +counter ]

            test_string = string
            test_string += next_letter

            for j in range (i+1, len( global_dehasher.searching_string ) ): # We copy the rest of the string
                #print( global_dehasher.searching_string )
                test_string += global_dehasher.searching_string[j]

            #print("=================================\n")
            #print(" [get_string_to_search] test_string = "+test_string+" | string = "+string+"\n")
            
            while not is_valid_string(test_string, i, next_letter): # We check if its a valid letter AND its not the last one "_"

                if next_letter == global_dehasher.letters[ len(global_dehasher.letters)-1 ]:
                    #print("GOING WEIRD CODE\n")
                    check_last_letter_string(global_dehasher, test_string, i, next_letter)
                    return

                counter += 1
                next_letter = global_dehasher.letters[ global_dehasher.letters_index[ global_dehasher.searching_string[i] ] +counter ]

                #print("2) Preordering strings = "+test_string+" | string = "+string+" | next_letter = "+next_letter+"\n")

                test_string = string
                test_string += next_letter

                #print("Ready to order strings = "+test_string+" | string = "+string+" | next_letter = "+next_letter+"\n")

                for j in range(i+1, len(global_dehasher.searching_string) ):
                    test_string += global_dehasher.searching_string[j] # We copy the rest of the string
                

                #print("Strings ordered! = "+test_string+" | string = "+string+" | next_letter = "+next_letter+"\n")

            #print("3) test_string = "+test_string+" | string = "+string+"\n")

            string += next_letter

            for j in range(i+1, len(global_dehasher.searching_string) ):
                string += global_dehasher.searching_string[j]  # We copy the rest of the string
                
            #print("4) test_string = "+test_string+" | string = "+string+"\n")

            global_dehasher.searching_string = string

            #print("Hello 7 "+global_dehasher.searching_string+" | "+string)
            return

        print("Error, you shouldnt be here, out of loop | "+global_dehasher.searching_string+" | "+str)
        return
        
    # We checked all the strings and all of them are the last one we want to check!

    str = ""

    for i in range(0, len(global_dehasher.searching_string)+1):
        str += global_dehasher.letters[0]

    #if debug:
        #print("All letters are the last one! Adding a new one | "+global_dehasher.searching_string+" => "+str)
    global_dehasher.searching_string = str
                
def check_last_letter_string( global_dehasher, test_string:str, i:int, next_letter:str ) -> None:

    #print("[check_last_letter_string] test_string = "+test_string+" | i = "+str(i)+" | next_letter = "+next_letter+"\n")

    string = ""

    if i == len(test_string)-2:

        for j in range(0, len(test_string)+1 ):
            string += global_dehasher.letters[0]

        #print("1) String = "+string+"\n")

    else:

        carry = False
        for j in range(0, len(test_string) ):
            if test_string[j] == next_letter:
                carry = True
                string += global_dehasher.letters[0]
            elif carry:
                string += global_dehasher.letters[ global_dehasher.letters_index[ test_string[j] ] +1 ]
                carry = False
            else:
                string += test_string[j]

        if carry: # If we had to change the last letter
            string = ""
            for j in range(0, len(test_string)+1 ):
                string += global_dehasher.letters[0]
            #print("Last letter had to be changed! | String = "+string+"\n")

    #print("2) String = "+string+"\n")

    set_letters = ""

    # Since we are adding a new letter, we have to check again all positions, this time from right to left
    for i in range( len(string)-1, -1, -1 ):

        #print("LOOP "+str(i)+"///////////////////\n")

        counter = global_dehasher.letters_index[ string[i] ]
        next_letter = global_dehasher.letters[ counter ]
        test_string = ""

        #print("A) i = "+str(i)+" counter = "+str(counter)+" | next_letter = "+next_letter+" | test_string = "+test_string+"\n")

        for j in range(0, i): # Copying the current testing letters
            test_string += string[j]
        
        #print("B) i = "+str(i)+" counter = "+str(counter)+" | next_letter = "+next_letter+" | test_string = "+test_string+"\n")

        #print("Start Letter Index: "+str(counter)+" | test string "+test_string+" | next_letter "+next_letter+" | pos "+str(i)+" | set letters "+set_letters+"\n")

        test_string += next_letter # We add the letter we want to check to current position
        test_string += set_letters # We add the already set letters from right to left

        #print("Start Letter Index: "+str(counter)+" | test string "+test_string+" | next_letter "+next_letter+" | pos "+str(i)+" | set letters "+set_letters+"\n")

        while next_letter != global_dehasher.letters[ len(global_dehasher.letters)-1 ] and not is_valid_string( test_string, i, next_letter):
        
            #print("D) counter = "+str(counter)+" | next_letter = "+next_letter+" | test_string = "+test_string+"\n")

            counter += 1
            next_letter = global_dehasher.letters[ counter ]
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

    global_dehasher.searching_string = set_letters


#
##
#

def is_valid_string( string:str, position:int, new_letter:str) -> bool:

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