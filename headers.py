'''
Hashing 'br_challenges'
T7 32 => 0xa6660c9a | a6660c9a
T8 32 => 0xe7878c75 | e7878c75
FNVA1 => 0x55837a19cb8844ec | 55837a19cb8844ec
HashIWRes => 0x1fd29e3ba4984b6d | 1fd29e3ba4984b6d
HashJupScr => 0x19eeeadf24e6b5f8 | 19eeeadf24e6b5f8
HashIWDVar => 0x7f6b66095fad8061 | 7f6b66095fad8061
HashT10Scr => 0x7d05a3652487350d | 7d05a3652487350d
HashT10ScrSP => 0x15ee02a1a1b976c5 | 15ee02a1a1b976c5
'''

# Hash types

#global_config   = [ 'var_', 'function_', 'namespace_', 'script_', '#"hash_', '#hash_', 'class_' 'event_', 'r"hash_', '%"hash_', '&"hash_', '@"hash_' ]

    # var       : source hash
    # function  : source hash
    # namespace : source hash
    # script    : fnva1 hash
    # #"hash    : fnva1 hash in gsc
    # #hash     : fnva1 hash in csv
    # class     : source hash
    # event     : source hash
    # r"hash    : resource hash
    # %"hash    : resource hash
    # @"hash    : dvar hash

bo3_config    = [ 'var_', 'function_', 'namespace_', '#"hash_', 'class_' ]
bo4_config    = [ 'var_', 'function_', 'namespace_', 'script_', '#"hash_', '#hash_', 'class_', 'event_' ]
cw_config     = [ 'var_', 'function_', 'namespace_', 'script_', '#"hash_', '#hash_', 'class_', 'event_' ]
mwiii_config  = [ 'var_', 'function_', 'namespace_', 'script_', '#"hash_', '#hash_', '%"hash_', '@"hash_' ]
bo6_config    = [ 'var_', 'function_', 'namespace_', 'script_', '#"hash_', '#hash_', 'event_', 'r"hash_', '%"hash_', '@"hash_' ]

config = {}
config[ "bo3" ]    = bo3_config
config[ "bo4" ]    = bo4_config
config[ "cw" ]     = cw_config
config[ "mwiii" ]  = mwiii_config
config[ "bo6" ]    = bo6_config

bo3_source_names    = [ 't7', 'bo3', 'blackops3', 'blackops-3', 'black-ops-3' ]
bo4_source_names    = [ 't8', 'bo4', 'blackops4', 'blackops-4', 'black-ops-4' ]
cw_source_names     = [ 't9', 'cw', 'coldwar', 'bocw', 'blackopscoldwar', 'cold-war', 'black-ops-cold-war' ]
mwiii_source_names  = [ 'jup', 'mwiii', 'modernwarfareiii', 'modern-warfare-iii' ]
bo6_source_names    = [ 't10', 'bo6', 'blackops6', 'black-ops-6' ]

# Source names

game_source_names = {}
game_source_names[ "bo3" ]  = bo3_source_names
game_source_names[ "bo4" ]  = bo4_source_names
game_source_names[ "cw" ]   = cw_source_names
game_source_names[ "mwiii" ]= mwiii_source_names
game_source_names[ "bo6" ]  = bo6_source_names

def file_name_by_expresion( expresion:str )->str:

    expresion = expresion.replace('"', '')
    return expresion.replace('_', '')