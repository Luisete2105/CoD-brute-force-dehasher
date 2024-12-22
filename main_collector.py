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

    extension:str = filename.split('.')[1]

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
                return



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

