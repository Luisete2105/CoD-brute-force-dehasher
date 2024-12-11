import os
import re

from Classes import module_files

global_config   = [ 'var_', 'function_', 'namespace_', 'script_', '#"hash_', 'event_', 'r"hash_', '%"hash_', '&"hash_', '@"hash_' ]

bo3_prefixes    = [ 'var_', 'function_', 'namespace_', '#"hash_', ]
bo4_prefixes    = [ 'var_', 'function_', 'namespace_', 'script_', '#"hash_', 'event_', ]
CW_prefixes     = [ 'var_', 'function_', 'namespace_', 'script_', '#"hash_', 'event_' ]
mwiii_config    = [ 'var_', 'function_', 'namespace_', 'script_', '#"hash_', 'r"hash_', '%"hash_', '@"hash_' ]
bo6_prefixes    = [ 'var_', 'function_', 'namespace_', 'script_', '#"hash_', 'event_', 'r"hash_', '%"hash_', '@"hash_' ]



file_writer = module_files.Files_class()
file_temp = module_files.Files_class()
file_reader = module_files.Files_class()

lui_test:int = 0

def read_paths_files( read_this ):

    counter:int = 0
    global lui_test

    for thing_to_read in read_this:
        module_files.log_new_message( str(lui_test)+"/"+str(counter)+" | "+str(thing_to_read) )
        counter += 1

    for file in read_this[2]:
        module_files.log_new_message( str(read_this[0])+"/2 FILES | "+str(file) )

    lui_test += 1


def collector()->None:

    print( os.path.dirname( os.path.realpath( __file__ ) ) )
    #os.walk( os.path.dirname( os.path.realpath( "GSC Source\\mwiii-source" ) ) )

    counter:int = 0

    file_writer.set_file( "read_test.txt", 'w' )
    file_temp.set_file( "temp.txt", 'w' )

    temp_buffer = []

    hashes_types = {}
    for config in mwiii_config:
        hashes_types[ config ] = []

    for file_content in os.walk( os.path.dirname( os.path.realpath( "GSC Source\\mwiii-source" ) ) ):

        counter += 1
        #read_paths_files(file_content)
        
        file_writer.write_to_file( str(counter)+"/ PATH: '"+str( file_content[0] )+"'\n"   )

        for file_name in file_content[2]:
            #file_writer.write_to_file( "File name '"+file_name[:-4]+" | Extension '"+file_name[-3:]+"'\n"   )

            extension = file_name[-3:]
            if extension == "csv": # Lets skip CSV's for now
                continue

            #file_writer.write_to_file( "File name '"+file_name+" | Extension '"+extension+"' | "+str(extension=="csv")+"\n\n" )
            file_reader.set_file( file_content[0]+"\\"+file_name, 'r' )
            #all_lines = file_reader.file.readlines()

            all_lines = file_reader.file.read()
            #file_writer.write_to_file( "File name '"+file_name+" | Extension '"+extension+"' | "+str(extension=="csv")+"\n\n" )
            #file_writer.write_to_file( all_lines )

            for expresion in mwiii_config:
                #search = re.findall(r'\b'+expresion+r'\w+' , all_lines)
                search = re.findall(r''+expresion+r'\w+' , all_lines)

                if search == None or len(search) < 1: # If we didnt find any just skip to next
                    continue

                for found_hash in search:

                    try:
                        hash = int( found_hash[len(expresion):], base=16 )

                        if hash not in hashes_types[ expresion ]:
                            hashes_types[ expresion ].append( hash )
                        
                    except:
                        continue

        
        file_writer.write_to_file( "\n\n"   )

        #if counter > 18: # Limit the amount of scripts searched for Debuging purposes
        #    break

    for expresion in mwiii_config:

        hashes_types[ expresion ].sort()
        file_name = "mwiii_"+file_name_by_expresion(expresion)+".txt"

        os.makedirs("mwiii", exist_ok=True)

        file_temp.set_file( "mwiii\\"+file_name, 'w')

        for hash in hashes_types[ expresion ]:
            #file_temp.write_to_file( str( hex(hash) )[2:]+"\n" )
            new_expresion = ""
            for char in expresion:
                if char == '"':
                    continue
                new_expresion += char

            file_temp.write_to_file( str( hex(hash) )[2:]+","+new_expresion+str( hex(hash) )[2:]+"\n" ) # Ate style




def file_name_by_expresion( expresion )->str:

    new_name:str = ""

    for char in expresion:
        if char == '"' or char == '_':
            continue
        new_name += char

    return new_name



#print( os.path.dirname( os.path.realpath( "main.py" ) ) )
#print( os.path.dirname( os.path.realpath( "main_dehasher.py" ) ) )
#print( os.path.dirname( os.path.realpath( "Classes\\module_dehasher.py" ) ) )
#print( os.path.dirname( os.path.realpath( "GSC Source\\mwiii-source" ) ) )
#print( os.path.dirname( os.path.realpath( "GSC Source\\" ) ) )
#print( os.path.dirname( os.path.realpath( "GSC Source" ) ) )









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