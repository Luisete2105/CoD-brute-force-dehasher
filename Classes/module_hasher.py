debug:bool = False

class Hasher_class:

    def __init__(self) -> None:

        global debug
        if debug:
            print( "[__init__] Class Hasher created!\n" )

        # FNVA1-64
        self.fnv64Offset:int    = 0xcbf29ce484222325    # 14695981039346656037
        self.fnv64Prime:int     = 0x100000001b3         # 1099511628211

        # Hash 32
        self.base_32:int        = 0x4B9ACE2F            # 1268436527
        self.prime:int          = 0x1000193             # 16777619

    def __del__(self) -> None:

        self.fnv64Offset    = None
        self.fnv64Prime     = None
        self.base_32        = None
        self.prime          = None

        global debug
        if debug:
            print( "[__del__] Class Hasher deleted!\n" )
    

    def t7_32( self, string:str ) -> str:

        base:int = self.base_32

        for c in bytes(string, 'utf-8'):
            base = ( c ^ base ) * self.prime & 0xFFFFFFFF

        base = ( base * self.prime ) & 0xFFFFFFFF

        global debug
        if debug:
            print( f"[t7_32] String '{ string }' => { hex( base ) }" )
            
        return hex(base)
        return int_address_to_string( base )
    
    def t8_32( self, string:str ) -> str:

        hash:int = self.base_32

        for c in bytes(string, 'utf-8'):
            hash = ((((c + hash) & 0xFFFFFFFF) ^ (((c + hash) & 0xFFFFFFFF) << 10)) & 0xFFFFFFFF) + ((((((c + hash) & 0xFFFFFFFF) ^ (((c + hash) & 0xFFFFFFFF) << 10)) & 0xFFFFFFFF) >> 6) & 0xFFFFFFFF)

        hash = (0x8001 * (((9 * hash) & 0xFFFFFFFF) ^ (((9 * hash) & 0xFFFFFFFF) >> 11))) & 0xFFFFFFFF

        global debug
        if debug:
            print( f"[t8_32] String '{ string }' => { hex(hash) }" )

        return hex(hash)
        return int_address_to_string( hash )

    def fnva1( self, string:str ) -> str:

        hash:int = self.fnv64Offset

        for byte in  bytes(string, 'utf-8'):
            hash = ( ( (hash ^ byte) * self.fnv64Prime ) & 0x7FFFFFFFFFFFFFFF )

        global debug
        if debug:
            print( f"[fnva1] String '{ string }' => { hex( hash ) }" )

        return hex(hash)
        return int_address_to_string( hash )

# Class Hasher END

global_hasher:Hasher_class = Hasher_class()

def int_address_to_string( hash_hex:hex ) -> str:
    
    global debug
    if debug:
        print( f"[int_address_to_string] Converted Hash | { hash_hex } => { str( hash_hex )[2:] } \n")
    
    return str( hash_hex )[2:]


def get_t7_32_str( word:str ) -> str:

    global global_hasher

    return int_address_to_string( global_hasher.t7_32( word ) )

def get_t8_32_str( word:str ) -> str:

    global global_hasher

    return int_address_to_string( global_hasher.t8_32( word ) )

def get_fnva1_str( word:str ) -> str:

    global global_hasher

    return int_address_to_string( global_hasher.fnva1( word ) )


def get_t7_32_hex( word:str ) -> str:

    global global_hasher

    return global_hasher.t7_32( word )

def get_t8_32_hex( word:str ) -> str:

    global global_hasher

    return global_hasher.t8_32( word )

def get_fnva1_hex( word:str ) -> str:

    global global_hasher

    return global_hasher.fnva1( word )
