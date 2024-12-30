import os
import re
import time

from headers import *
import headers

from Classes import module_files



file_writer = module_files.Files_class()
file_temp = module_files.Files_class()
file_reader = module_files.Files_class()

lui_test:int = 0
debug:bool = False



def should_skip_file( filename:str )->bool:

    splits:str = filename.split('.')

    if( len( splits ) < 2 ): # Doesnt have extension
        if debug:
            print(f"File '{filename}' skipped due to missing extension")
        return True

    extension:str = splits[1]

    if extension == "gsc" or extension == "csc" or extension == "csv" or extension == "ddl" or extension == "json":
        return False

    if debug:
        print(f"File '{filename}' skipped due to extension '{extension}' ")

    return True

#start_time:float = time.time()
#print("--- %s seconds ---" % (time.time() - start_time))

def get_source_for_game(path, game)->str:

    if debug:
        print(path)

    for name in game_source_names[ game ]:

        if os.path.exists(path+"\\"+name):
            return path+"\\"+name
        
        if os.path.exists(path+"\\"+name+"-source"):
            return path+"\\"+name+"-source"
        
        if os.path.exists(path+"\\"+name+"-source-main"):
            return path+"\\"+name+"-source-main"

    return ""

def collector( game:str )->None:

    global config

    if debug:
        start_time:float = time.time()

    path = os.path.dirname(os.path.realpath(__file__))+"\\GSC Source\\"
    if debug:
        print(path)

    path = get_source_for_game(path, game)

    if path == "":
        print( f"Cant find source for game '{game}' in path {path}\n" )
        print("Press any key to conti nue\n\n")
        input()
        return

    if debug:
        print(f"Exists '{path}' ? {os.path.exists(path)}")

    hashes_types = {}
    for hash_type in config[ game ]:
        if debug:
            print(f"Game {game} | {hash_type}")
        hashes_types[ hash_type ] = []

    for file_content in os.walk( path ):


        for file_name in file_content[2]:

            #if file_name "zm_zod_ee.csc": # debug line
            #continue

            if should_skip_file( file_name ): # Lets skip unnecessary files
                continue

            if file_name[-3:] == "csv":
                file_reader.set_file( file_content[0]+"\\"+file_name, 'r', 'utf8' )
            else:
                file_reader.set_file( file_content[0]+"\\"+file_name, 'r' )

            try:
                all_lines = file_reader.file.read()
                
            except Exception as err:
                print(f"Error reading file '{file_content[0]+"\\"+file_name}'")
                print(f"{type(err).__name__} was raised: {err}")
                module_files.log_new_message(f"Error reading file '{file_content[0]+"\\"+file_name}'")
                module_files.log_new_message(f"{type(err).__name__} was raised: {err}")
                #return

                file_reader.file = open(file_content[0]+"\\"+file_name, 'r', encoding = 'utf8', errors='ignore')




            for expresion in config[ game ]:

                if debug:
                    module_files.log_new_message(f"Searching for  '{expresion}' in file '{file_name}'")

                search = re.findall(expresion+r'\w+' , all_lines)

                if search == None or len(search) < 1: # If we didnt find any just skip to next
                    continue

                for found_hash in search:

                    try:
                        hash = int( found_hash[len(expresion):], base=16 )

                        if hash not in hashes_types[ expresion ]:
                            hashes_types[ expresion ].append( hash )
                        
                    except:
                        
                        if debug:
                            if found_hash == None:
                                module_files.log_new_message( f"Hash has no value \n{file_content[0]} " )
                            else:
                                module_files.log_new_message( f"Wrong hash '{found_hash}'\n{file_content[0]} " )
                        continue





    if '#"hash_' in hashes_types.keys() and '#hash_' in hashes_types.keys():
        for basic_hash in hashes_types[ '#"hash_' ]:
            if basic_hash not in hashes_types[ '#hash_' ]:
                hashes_types[ '#hash_' ].append( basic_hash )
            else:
                module_files.log_new_message(f"Repeated hash {basic_hash}")

        del hashes_types[ '#"hash_' ]

    for expresion in hashes_types.keys():

        hashes_types[ expresion ].sort()
        file_name = game+"_"+headers.file_name_by_expresion(expresion)+".txt"
        os.makedirs(game, exist_ok=True)
        file_temp.set_file( game+"\\"+file_name, 'w')

        for hash in hashes_types[ expresion ]:
            new_expresion = ""
            for char in expresion:
                if char == '"':
                    continue
                new_expresion += char

            file_temp.write_to_file( str( hex(hash) )[2:]+","+new_expresion+str( hex(hash) )[2:]+"\n" ) # Ate style

    if debug:
        print("--- %s seconds ---" % (time.time() - start_time))


def sort_found_hashes() -> None:
    
    path = os.path.dirname(os.path.realpath(__file__))+"\\Found\\"

    if not os.path.exists(path): # Not found hashes
        print( "Cant find 'Found' folder...")
        return
    else:
        if debug:
            print( "Fond folder located!")
    
    for game in config.keys():

        game_path = path+game
        if not os.path.exists(game_path):
            #print("There are not found hashes for game: "+{game})
            continue

        all_lines:list = []

        for file_content in os.walk( game_path ):
            
            for file_name in file_content[2]:

                #print(f"Sorting {file_name}")

                file_reader.set_file( file_content[0]+"\\"+file_name, 'r+', 'utf8' )
                new_lines = file_reader.file.readlines()
                for line in new_lines:
                    if line not in all_lines:
                        all_lines.append( line )

        indexed_hash_list = []
        for line in all_lines:
            if len( line.split(',') ) != 2:
                #print(f"{game}: Skipping bad line '{line}'")
                all_lines.remove( line )
                continue
            indexed_hash_list.append( int( line.split(',')[0], base = 16 ) )

        indexed_hash_list.sort()



        #all_lines.sort()

        file_reader.set_file( path+"\\"+game+"-scr.csv", 'w', 'utf8' )

        #module_files.log_new_message(f"\n\nGame: {game}\n\n")

        #for sorted_line in all_lines:
        for sorted_line in indexed_hash_list:

            #module_files.log_new_message(f"Searching for {sorted_line}")

            for line in all_lines:
                hash = int( line.split(',')[0], base = 16 )
                if hash == sorted_line:
                    #module_files.log_new_message(f"Found! {hash} => '{line.strip()}'")

                    file_reader.write_to_file( line )
                    all_lines.remove( line )
                    break

            #file_reader.write_to_file(sorted_line)


        #print(f"game: {game}")

    #print(f"All found hashes sorted!")
    file_reader.close_file


def add_found_hashes_to_src() -> None:
    
    found_path = os.path.dirname(os.path.realpath(__file__))+"\\Found\\"

    if not os.path.exists(found_path): # Not found hashes
        print( "Cant find 'Found' folder...")
        os.makedirs(found_path, exist_ok=True)
        #return
    else:
        if debug:
            print( "Found folder located!")


    hash_scr_path = os.path.dirname(os.path.realpath(__file__))+"\\hashes\\"

    if not os.path.exists(hash_scr_path): # Not found hashes
        print( "Cant find 'hashes' folder...\nCreated a folder to place game-scr.csv from Ate47 hash index repository")
        os.makedirs(hash_scr_path, exist_ok=True)
        return
    else:
        if debug:
            print( "hashes folder located!")

    if not os.path.exists(found_path): # Not found hashes
        print( "Cant find 'Found' folder...")
        return
    else:
        if debug:
            print( "Fond folder located!")

    for game in config.keys():
        
        found_hash_scr_path = found_path+game+"-scr.csv"
        if not os.path.exists(found_hash_scr_path):
            module_files.log_new_message(f"There are not found hashes for game: {game}")
            print(f"There are not found hashes for game: {game}")
            continue

        index_hash_scr_path = hash_scr_path+game+"-scr.csv"
        if not os.path.exists(index_hash_scr_path):
            print(f"There are not index hashes for game: {game}")
            file_reader.set_file( index_hash_scr_path, 'a', 'utf8' )
            print(f"Created a hash-scr file for game: {game}")
            #continue

        temp_array:list = []
        all_lines:list = []

        file_reader.set_file( found_hash_scr_path, 'r', 'utf8' )
        temp_array = file_reader.file.readlines()

        for line in temp_array:
            if line not in all_lines:
                all_lines.append( line )

        file_reader.set_file( index_hash_scr_path, 'r+', 'utf8' )
        temp_array = []

        temp_array = file_reader.file.readlines()
        for line in temp_array:
            if line not in all_lines:
                all_lines.append( line )
            else:
                if debug:
                    module_files.log_new_message(f"Duplicated hash! Game: {game} | {line}")


        indexed_hash_list:list = []
        for line in all_lines:
            if len( line.split(',') ) != 2:
                #print(f"Skipping bad line{line}")
                continue
            indexed_hash_list.append( int( line.split(',')[0], base = 16 ) )

        indexed_hash_list.sort()
        file_reader.set_file( index_hash_scr_path, 'w', 'utf8' )

        for sorted_line in indexed_hash_list:

            #module_files.log_new_message(f"Searching for {sorted_line}")

            for line in all_lines:
                if len( line.split(',') ) != 2:
                    #print(f"Skipping bad line{line}")
                    continue

                hash = int( line.split(',')[0], base = 16 )
                if hash == sorted_line:
                    #module_files.log_new_message(f"Found! {hash} => '{line.strip()}'")

                    file_reader.write_to_file( line )
                    all_lines.remove(line)
                    break


        print(f"game: {game}")

    print(f"All found hashes sorted AND mixed!")
    file_reader.close_file


#print( os.path.dirname( os.path.realpath( "main.py" ) ) )
#print( os.path.dirname( os.path.realpath( "main_dehasher.py" ) ) )
#print( os.path.dirname( os.path.realpath( "Classes\\module_dehasher.py" ) ) )
#print( os.path.dirname( os.path.realpath( "GSC Source\\mwiii-source" ) ) )
#print( os.path.dirname( os.path.realpath( "GSC Source\\" ) ) )
#print( os.path.dirname( os.path.realpath( "GSC Source" ) ) )


# UNUSED

def read_paths_files( read_this ):

    counter:int = 0
    global lui_test

    for thing_to_read in read_this:
        module_files.log_new_message( str(lui_test)+"/"+str(counter)+" | "+str(thing_to_read) )
        counter += 1

    for file in read_this[2]:
        module_files.log_new_message( str(read_this[0])+"/2 FILES | "+str(file) )

    lui_test += 1

