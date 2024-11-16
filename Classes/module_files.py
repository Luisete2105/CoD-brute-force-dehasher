from datetime import datetime

import os

debug:bool = False

class Files_class:

    def __init__(self) -> None:
        
        global debug
        if debug:
            print( "[__init__] Class Files created!\n" )

        self.file_name:str = ""
        self.file_mode:str = ""
        self.file = None

    def __del__(self) -> None:

        global debug
        if not self.file == None:
            if debug:
                print( "[__del__] Closing "+self.file_name+" file!\n" )
            self.file.close()
        else:
            if debug:
                print( "[__del__] There is no file to close on searcher\n" )

        if debug:
            print( "[__del__] Class Files deleted!\n" )


    def has_valid_file(self) -> bool:

        if self.file == None:
            return False
        else:
            return True

    def close_file(self) -> None:

        global debug
        if self.has_valid_file():
            if debug:
                print( "[close_file] Closing file '"+self.file_name+"'\n" )
            self.file.close()
            self.file = None
            self.file_name = ""
            self.file_mode = ""
        elif debug:
            print( "[close_file] There is no file to close\n" )

    def set_file(self, file_name:str, file_mode:str) -> None:

        global debug
        # r = read | w = write | a = append (only add info at the end of the file) | r+ = read and write

        if debug:
            print( "[set_file] File name => "+file_name+" | File mode => "+file_mode )

        if self.has_valid_file():
            if debug:
                print( "[set_file] Closing current file" )
            self.close_file()

        if file_mode == "r" or file_mode == "r+":
            #file = open(file_name, file_mode)

            try:

                file = open(file_name, file_mode)

            except Exception as e: # Only when exception happens on 'try'

                #print(e) # Prints python error exception
                print( "[set_file] Error, couldnt open file to READ '"+file_name+"'\n" )

                file_name = ""
                file_mode = ""
                file = None

        else:
            file = open(file_name, file_mode)

        self.file_name = file_name
        self.file_mode = file_mode
        self.file = file

        if debug and self.has_valid_file():
            print( "[set_file] Successfully opened '"+file_name+"' with mode '"+file_mode+"'!\n" )

    def write_to_file(self, text:str) -> None:

        if not self.has_valid_file():
            print( "Error, file is NOT assigned" )
            return
        if not self.file.writable():
            print( f"Error, NO PERMS to write \nFile mode => { self.file_mode }\nFile name => { self.file_name }" )
            return

        self.file.write( text )

# Class Files END

global_logger:Files_class = Files_class()
global_logger.set_file("lui_log.txt", "a")

def log_new_message( message:str ) -> None:

    global debug
    if debug:
        #print( "[log_new_message] message: "+message )
        pass

    global global_logger
    global_logger.file.write( datetime.now().strftime("%H:%M:%S")+": "+message+"\n" )


global_files:Files_class = Files_class()

def get_t7_hashes( comp:Files_class, hashes:Files_class ) -> None:

    global global_files

    if os.path.exists( "t7_32.txt" ):
        os.remove( "t7_32.txt" )

    # Checks for valid files were done before calling this function
    if( comp.has_valid_file() ): # Comp exists
        lines = comp.file.readlines()
        
        if( hashes.has_valid_file() ): # Comp AND Hashes exist
            lines += hashes.file.readlines() # Just discovered that you can combine arrays in python like that
    else:
        lines = hashes.file.readlines()
    
    global_files.set_file( "t7_32.txt", "w" )
    write_hashes( lines )
    global_files.close_file()

def get_t8_hashes( comp:Files_class, hashes:Files_class ) -> None:

    global global_files

    if( comp.has_valid_file() ): # Comp exists
        if os.path.exists( "t8_32.txt" ):
            os.remove( "t8_32.txt" )

        global_files.set_file( "t8_32.txt", "w" )
        write_hashes( comp.file.readlines() )
        global_files.close_file()
            
    if( hashes.has_valid_file() ): # Comp exists
        if os.path.exists( "t8_64.txt" ):
            os.remove( "t8_64.txt" )

        global_files.set_file( "t8_64.txt", "w" )
        write_hashes( hashes.file.readlines() )
        global_files.close_file()

def get_t9_hashes( comp:Files_class, hashes:Files_class ) -> None:

    global global_files

    if( comp.has_valid_file() ): # Comp exists
        if os.path.exists( "t9_32.txt" ):
            os.remove( "t9_32.txt" )

        global_files.set_file( "t9_32.txt", "w" )
        write_hashes( comp.file.readlines() )
        global_files.close_file()

    if( hashes.has_valid_file() ): # Comp exists
        if os.path.exists( "t9_64.txt" ):
            os.remove( "t9_64.txt" )

        global_files.set_file( "t9_64.txt", "w" )
        write_hashes( hashes.file.readlines() )
        global_files.close_file()


def write_hashes( lines ) -> None:

    if len( lines ) < 1: # Error check
        print("Error, Hashes didnt copy???")
        log_new_message( "Error, Hashes didnt copy???" )
        return

    global global_files

    temp = []
    for line in lines: # Copy the lines
        temp.append( int( line.split(",")[0], base = 16) ) #We only want the bytes of the hash, we dont care if its a script, namespace, func, var or string

    temp.sort() # Sort the lines in hexadecimal numbers, otherwise its not accurate for some reason


    
    # Hex
    global_files.file.write( str( hex( temp[0] )+"\n") ) # Now we write the hashes but skip the duplicated ones
    last_string:hex = hex( temp[0] )

    for i in range(1, len(temp)-1 ):

        if last_string == hex( temp[i] ): # Skip if its the same as the last hash
            #print("detected duplicated")
            continue

        global_files.file.write( str( hex( temp[i] )+"\n") )
        last_string = hex( temp[i] )
    

    # Str
    '''
    global_files.file.write( str(hex(temp[0]))[2:]+"\n" ) # Now we write the hashes but skip the duplicated ones
    last_string = str(hex(temp[0]))[2:]+"\n"

    for i in range(1, len(temp)-1 ):

        if last_string == str(hex(temp[i]))[2:]+"\n": # Skip if its the same as the last hash
            #print("detected duplicated")
            continue

        global_files.file.write( str(hex(temp[i]))[2:]+"\n" )
        last_string = str(hex(temp[i]))[2:]+"\n"
    '''

def check_savedata_exists( first_letter:str ) -> str:

    global global_files

    if not os.path.exists( "save_data.cfg" ):

        if debug:
            print( "Creating save_data.cfg\n" )

        global_files.set_file("save_data.cfg", "w")
        global_files.write_to_file( first_letter )

    else:
        
        if debug:
            print( "Reading save_data.cfg\n" )

        global_files.set_file( "save_data.cfg", "r+" )
        first_letter = global_files.file.readlines()[0]

    global_files.close_file()
    return first_letter

def write_savedata( new_savedata:str ) -> None:

    global global_files

    if not os.path.exists( "save_data.cfg" ):

        print( "ERROR, cant find save_data.cfg\n" )
        return

    global global_files
        
    if debug:
        print( f"Saving '{new_savedata}' in save_data.cfg\n" )

    global_files.set_file( "save_data.cfg", "r+" )
    global_files.write_to_file( new_savedata )

    global_files.close_file()
 



def get_hex_lines( file_name:str ) -> list:

    global global_files

    list_of_hex:list = []

    global_files.set_file( file_name, "r" )

    for line in global_files.file.readlines():
        list_of_hex.append( hex(int(line.strip(), base = 16)) )
        #log_new_message( f"line '{line}'" )
    
    global_files.close_file()

    return list_of_hex

def add_found_hash( found_file_name:str, message:str ) -> None:

    global global_files

    global_files.set_file( found_file_name, "a" )
    global_files.write_to_file( message )

    global_files.close_file()



def get_str_lines( file_name:str ) -> list:

    global global_files

    list_of_hex:list = []

    global_files.set_file( file_name, "r" )

    for line in global_files.file.readlines():
        line = line.strip()

        list_of_hex.append( line )
        #log_new_message( f"line '{line}'" )
    
    global_files.close_file()

    return list_of_hex



# to do

def check_existing_hash( reader:Files_class, word:str, global_dehasher, hashing_func) -> None:

    #class_Dehasher_class.increment_search()

    #hash = hashing_func( word )


    lines = reader.file.readlines()


    is_hash_wanted( lines, reader.file_name, word, hashing_func( word ) )

    categories = global_dehasher.prefixes.keys()

    for category in categories:

        if word[0] != "_": # Can add prefixes

            if word[ len(word)-1 ] != "_": # Can add suffixes

                for prefix in global_dehasher.prefixes[category]:

                    is_hash_wanted( lines, reader.file_name, prefix+word, hashing_func( prefix+word ) )

                    for suffix in global_dehasher.suffixes[category]:

                        is_hash_wanted( lines, reader.file_name, prefix+word+suffix, hashing_func( prefix+word+suffix ) )
                        is_hash_wanted( lines, reader.file_name, word+suffix, hashing_func( word+suffix ) )

            else: # Can add prefixes but not suffixes
                    
                    for prefix in global_dehasher.prefixes[category]:

                        is_hash_wanted( lines, reader.file_name, prefix+word, hashing_func( prefix+word ) )
        
        else: # Cant add prefixes

            if word[ len(word)-1 ] != "_": # Cant add prefixes but can add suffixes

                for suffix in global_dehasher.suffixes[category]:

                    is_hash_wanted( lines, reader.file_name, word+suffix, hashing_func( word+suffix ) )

    #class_Dehasher_class.decrement_search()

def is_hash_wanted( lines, file_name, word, hash) -> None:

    for i in range( len( lines ) ): # Skipping lines from hashes shorter than what we are searching
        #logger.log_new_message( "\n "+hash+" "+str( len(hash) )+" > "+lines[i]+" "+str( len(lines[i]) )  )

        if len( hash ) > len( lines[i] )-1:
            continue
        else:
            break

    #logger.log_new_message( "\n"+file_name+"\nPrev line "+lines[i-1]+" | Curr line "+str(lines[i]) )

    last_char_found_pos:int = -1

    for j in range( i, len( lines ) ):
        if len( hash ) < len( lines[i] )-1: # If the hashes we are reading are bigger than what we are comparing we just stop
            #logger.log_new_message( "\nBigger than searching hash => Prev line "+lines[j-1]+" | Curr line "+str(lines[j]) )
            return
        
        found:bool = True
        for k in range( len( hash ) ):
            #logger.log_new_message( "\nComparing "+lines[j]+" | Char pos = "+str(k) )

            if hash[k] != lines[j][k]:

                if k-1 < last_char_found_pos or int( lines[j][k], 16 ) > int( hash[k], 16 ) : # If we are getting lest accurate hashes its not on the list
                    #logger.log_new_message( "\nLess accurate hashes "+lines[j]+" | Char pos = "+str(k) )
                    return
                
                #logger.log_new_message( "\nIncorrect letter  List char "+lines[j][k]+" | Hash char "+hash[k] )
                found = False
                break # Since its not less accurate its still possible to be on the list, we stop comparing chars and just go to next line of the hash list
            else:
                if k > last_char_found_pos:
                    #logger.log_new_message( "\nMore accurate hashes "+lines[j]+" | Line = "+str(j) )
                    last_char_found_pos = k

        if found: # We stop searching and we write it down

            logger = Files_class()
            logger.set_file("lui_log.txt", "a")
            logger.log_new_message( "\nA hash of the list has been found!\n"+file_name+" | "+word+" => "+hash )
            word_writer:Files_class = Files_class()

            found_file:str = ""
            for x in range(0, len( file_name ) -4 ):
                found_file += file_name[x]

            word_writer.set_file( found_file+"_found.txt", "a" )
            word_writer.write_to_file(  word+" => "+hash+"\n")
            print("new word found! '"+word+"'")
            return
        else:
            #logger.log_new_message( "\nSkipping to next hash of the list" )
            continue

