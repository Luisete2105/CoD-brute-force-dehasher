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
        self.base_32:int        = 0x4B9ACE2F            # 1268436527    #HashT89
        self.prime:int          = 0x1000193             # 16777619      #HashT7

        # From Ate's CoD Tools

        self.MASK32             = 0xFFFFFFFF
        self.MASK62             = 0xFFFFFFFFFFFFFFF
        self.MASK63             = 0x7FFFFFFFFFFFFFFF
        self.IV_DEFAULT         = 0x100000001b3
        self.IV_32_DEFAULT      = 0x1000193
        self.IV_TYPE2           = 0x10000000233

        self.FNV1A_PRIME        = 0xcbf29ce484222325
        self.FNV1A_32_PRIME     = 0x811C9DC5

        self.FNV1A_IW_PRIME     = 0x47F5817A5EF961BA
        self.FNV1A_IW_SCR_PRIME = 0x79D6530B0BB9B5D1
        self.FNV1A_IW_DVAR_OFFSET = 0xD86A3B09566EBAAC
        self.FNV1A_T10_SCR_OFFSET = 0x1C2F2E3C8A257D07
        self.FNV1A_32_T7_PRIME  = 0x4B9ACE2F

        self.XHASHSEC_DVAR_STR  = "q6n-+7=tyytg94_*"
        self.XHASHSEC_T10_SCR_STR = "zt@f3yp(d[kkd=_@"


    def __del__(self) -> None:

        self.fnv64Offset    = None
        self.fnv64Prime     = None
        self.base_32        = None
        self.prime          = None

        # From Ate's CoD Tools

        self.MASK32             = None
        self.MASK62             = None
        self.MASK63             = None
        self.IV_DEFAULT         = None
        self.IV_32_DEFAULT      = None
        self.IV_TYPE2           = None

        self.FNV1A_PRIME        = None
        self.FNV1A_32_PRIME     = None

        self.FNV1A_IW_PRIME     = None
        self.FNV1A_IW_SCR_PRIME = None
        self.FNV1A_IW_DVAR_OFFSET = None
        self.FNV1A_T10_SCR_OFFSET = None
        self.FNV1A_32_T7_PRIME  = None

        self.XHASHSEC_DVAR_STR  = None
        self.XHASHSEC_T10_SCR_STR = None

        global debug
        if debug:
            print( "[__del__] Class Hasher deleted!\n" )
    

    def t7_32( self, string:str ) -> int:

        base:int = self.base_32

        for c in bytes(string, 'utf-8'):
            base = ( c ^ base ) * self.prime & 0xFFFFFFFF

        base = ( base * self.prime ) & 0xFFFFFFFF

        global debug
        if debug:
            print( f"[t7_32] String '{ string }' => { hex( base ) }" )
            
        return base
        return hex(base)
        return int_address_to_string( base )
    
    def t8_32( self, string:str ) -> int:

        hash:int = self.base_32

        for c in bytes(string, 'utf-8'):
            hash = ((((c + hash) & 0xFFFFFFFF) ^ (((c + hash) & 0xFFFFFFFF) << 10)) & 0xFFFFFFFF) + ((((((c + hash) & 0xFFFFFFFF) ^ (((c + hash) & 0xFFFFFFFF) << 10)) & 0xFFFFFFFF) >> 6) & 0xFFFFFFFF)

        hash = (0x8001 * (((9 * hash) & 0xFFFFFFFF) ^ (((9 * hash) & 0xFFFFFFFF) >> 11))) & 0xFFFFFFFF

        global debug
        if debug:
            print( f"[t8_32] String '{ string }' => { hex(hash) }" )

        return hash
        return hex(hash)
        return int_address_to_string( hash )

    def fnva1( self, string:str ) -> int:

        hash:int = self.fnv64Offset

        for byte in  bytes(string, 'utf-8'):
            hash = ( ( (hash ^ byte) * self.fnv64Prime ) & 0x7FFFFFFFFFFFFFFF )

        global debug
        if debug:
            print( f"[fnva1] String '{ string }' => { hex( hash ) }" )

        return hash
        return hex(hash)
        return int_address_to_string( hash )


    def Hash64A( self, str, start = None, iv = None ) -> int:

        if start == None:
            start = self.FNV1A_PRIME

        if iv == None:
            iv = self.IV_DEFAULT

        hash:int = start

        for byte in  bytes( str, 'utf-8'):
            hash = ( ( hash ^ ( byte & 0xFF ) ) * iv ) & 0xFFFFFFFFFFFFFFFF

        return hash
	
    def HashSecure( self, pattern:str, start:int, str:str, iv:int ) -> int:

        if str == None or str == "":
            print("Error, missing str in 'HashSecure' Function")
            return 0

        _hash:int = start
        for byte in  bytes( str[0] + pattern + str[1:], 'utf-8'):
            _hash = ( iv * ( byte ^ _hash ) ) & 0xFFFFFFFFFFFFFFFF

        return _hash
    
    def Hash64( self, str, start = None, iv = None ) -> int:

        if start == None:
            start = self.FNV1A_PRIME

        if iv == None:
            iv = self.IV_DEFAULT

        hash:int = start

        for byte in  bytes( str, 'utf-8'):
            hash = ( ( hash ^ ( byte & 0xFF ) ) * iv )

        return hash & self.MASK63
	

    def HashIWRes( self, string:str, start:int =None, iv = None ) -> int: # HashIWRes is for the script names

        return self.Hash64( string, self.FNV1A_IW_PRIME )

    def HashIWTag( self, string:str, start:int =None, iv = None ) -> int: # HashIWTag Idk

        return ( self.Hash64( string, self.FNV1A_32_PRIME, self.IV_32_DEFAULT ) & self.MASK32 )

    def HashIWDVar( self, string:str ) -> int: # HashIWDVar for the dvars

        return self.HashSecure( self.XHASHSEC_DVAR_STR, self.FNV1A_IW_DVAR_OFFSET, string, self.IV_TYPE2 )


    def HashJupScr( self, string:str, start:int =None, iv = None ) -> int: # HashJupScr for mwiii scr (the equivalent of the hash32 of t89)

        return self.Hash64A( string, self.FNV1A_IW_SCR_PRIME, self.IV_TYPE2 )


    def HashT10Scr( self, string:str ) -> int: # HashT10Scr for bo6 mp scr

        return self.HashSecure( self.XHASHSEC_T10_SCR_STR, self.FNV1A_T10_SCR_OFFSET, string, self.IV_TYPE2 )



        
    def HashT10ScrSPPre( self, string:str, start = 0 ) -> int:
        
        start = self.FNV1A_T10_SCR_OFFSET

        return self.Hash64A( string, self.FNV1A_T10_SCR_OFFSET, self.IV_TYPE2 )

    def HashT10ScrSPPost( self, string:str ) -> int:
        
        return self.Hash64A( self.XHASHSEC_T10_SCR_STR, string )

    def HashT10ScrSP( self, string:str ) -> int: # HashT10Scr for bo6 mp scr
        
        return self.HashT10ScrSPPost( self.HashT10ScrSPPre( string ) )



# Class Hasher END

global_hasher:Hasher_class = Hasher_class()

def int_address_to_string( hash_hex:hex ) -> str:
    
    global debug
    if debug:
        print( f"[int_address_to_string] Converted Hash | { hash_hex } => { str( hash_hex )[2:] } \n")
    
    return str( hash_hex )[2:]



def get_t7_32_hex( word:str ) -> hex:

    global global_hasher

    return hex( global_hasher.t7_32( word ) )

def get_t8_32_hex( word:str ) -> hex:

    global global_hasher

    return hex( global_hasher.t8_32( word ) )

def get_fnva1_hex( word:str ) -> hex:

    global global_hasher

    return hex( global_hasher.fnva1( word ) )

def get_HashIWRes_hex( word:str ) -> hex:

    global global_hasher

    return hex( global_hasher.HashIWRes( word ) )

def get_HashIWTag_hex( word:str ) -> hex:

    global global_hasher

    return hex( global_hasher.HashIWTag( word ) )

def get_HashJupScr_hex( word:str ) -> hex:

    global global_hasher

    return hex( global_hasher.HashJupScr( word ) )

def get_HashIWDVar_hex( word:str ) -> hex:

    global global_hasher

    return hex( global_hasher.HashIWDVar( word ) )

def get_HashT10Scr_hex( word:str ) -> hex:

    global global_hasher

    return hex( global_hasher.HashT10Scr( word ) )

def get_HashT10ScrSPPre_hex( word:str ) -> hex:

    global global_hasher

    return hex( global_hasher.HashT10Scr( word ) )

def get_HashT10ScrSPPost_hex( word:str ) -> hex:

    global global_hasher

    return hex( global_hasher.HashT10ScrSPPost( word ) )

def get_HashT10ScrSP_hex( word:str ) -> hex:

    global global_hasher

    return hex( global_hasher.HashT10ScrSP( word ) )


#//////////////////////////////////////

def get_t7_32_str( word:str ) -> str:

    global global_hasher

    return int_address_to_string( get_t7_32_hex(word) )

def get_t8_32_str( word:str ) -> str:

    global global_hasher

    return int_address_to_string( get_t8_32_hex( word ) )

def get_fnva1_str( word:str ) -> str:

    global global_hasher

    return int_address_to_string( get_fnva1_hex( word ) )

def get_HashIWRes_str( word:str ) -> str:

    global global_hasher

    return int_address_to_string( get_HashIWRes_hex( word ) )

def get_HashIWTag_str( word:str ) -> str:

    global global_hasher

    return int_address_to_string( get_HashIWTag_hex( word ) )

def get_HashJupScr_str( word:str ) -> str:

    global global_hasher

    return int_address_to_string( get_HashJupScr_hex( word ) )

def get_HashIWDVar_str( word:str ) -> str:

    global global_hasher

    return int_address_to_string( get_HashIWDVar_hex( word ) )

def get_HashT10Scr_str( word:str ) -> str:

    global global_hasher

    return int_address_to_string( get_HashT10Scr_hex( word ) )


def get_HashT10ScrSPPre_str( word:str ) -> str:

    global global_hasher

    return int_address_to_string( get_HashT10ScrSPPre_hex( word ) )

def get_HashT10ScrSPPost_str( word ) -> str:

    global global_hasher

    return int_address_to_string( get_HashT10ScrSPPost_hex( word ) )

def get_HashT10ScrSP_str( word:str ) -> str:

    global global_hasher

    return int_address_to_string( get_HashT10ScrSP_hex( word ) )

