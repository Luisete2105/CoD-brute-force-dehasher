# CoD brute force dehasher
 My attempt to port the brute force dehasher I made on GSC to Python so I dont need to keep bo4 open and hopefully it will be faster

# 1.0

- Try Hash:
    Hashes your input to various algorithms

    Currently supports: T7 canon, T89 Canon, FNVA1 #62, IW Resources, Jup Source, IW Dvar, FNVA1 #63, T10 SCR, T10 SCR SP

- Collect:
    Gets the hashes for Bo3, Bo4, CW, MWiii or Bo6. The source folder must be placed in 'GSC Source' folder.

    The name of the folder must be a combination of the game's name and -source / -source-main, eg: bo3, t8-source, coldwar-source, jup-source-main, modern-warfare-iii or blackops6

- Dehasher:
    Starts a customizable brute force dehasher.

    When a hash is found, a folder is created called "Found", inside another folder with the game's name is created and then a text file named "game+hash_type+_found.txt" which contains the found hashes

    Default string is "a", it can be changed in "save_data.cfg" which is created on the root folder once the brute force has started, you can manually delete it to reset it.

    The letters allowed to use for the brute force dehasher are the ones in "Classes//module_dehasher.py" at lines 26, 27 and 28, you can just comment or delete the ones you want to be skipped

    Prefixes and suffixes can be customized in "Classes//module_dehasher.py" aswell from line 40, the structure is:
        'self.add_prefix("name_of_category", [foo, bar]) / self.add_suffix("name_of_category", [foo, bar])'
    Combinations of prefixes and suffixes will only happen when a prefix list and a suffix list has the same category name

    This brute force skips "unlikely" string combinations, it follows certain rules to skip combinations which can be found at "main_dehasher.py" on the function "is_valid_string", the rules are:
    -Same character can not appear 3 times in a row
    -3 vocals in a row are not allowed
    -4 no vocals in a row are not allowed
    -No weird 2 character combinations

    The map of the "weird 2 character combinations" can be found scrolling down on the same file on a giant table, this table has every letter on each row and column, when a "weird" match happens, said combination is writen in the chart where they meet, blank spaces mean its allowed.
    The giant "switch" (if/elif) right under is a translation of the table.
