
General Data types and hash extraction table

| Data type | Data names  | Patterns   | Games                      | Examples                                       | Expected hash extraction/s |
|-----------|-------------|------------|----------------------------|------------------------------------------------|----------------------------|
| SCR       | Variables   | var_       | bo3, bo4, bocw, mwiii, bo6 | var_1069f2d4, level.var_9578a7ed2d4e36ed       | 1069f2d4, 9578a7ed2d4e36ed |
| SCR       | Functions   | function_  | bo3, bo4, bocw, mwiii, bo6 | function_385ef18d, function_936cbcc0667fb087   | 385ef18d, 936cbcc0667fb087 |
| SCR       | Namespace   | namespace_ | bo3, bo4, bocw, mwiii, bo6 | namespace_9c39c8b3, namespace_4848403b6f5b0da0 | 9c39c8b3, 4848403b6f5b0da0 |
| SCR       | Classes     | class_     | bo3, bo4, bocw             | class_7c51d14d                                 | 7c51d14d                   |
| SCR       | Events      | event      | bo4, bocw                  | event_eae361ae                                 | eae361ae                   |
| RESOURCES | Hashes      | #"hash_    | bo3, bo4, bocw, mwiii, bo6 | #"hash_52b06792de26b86b"                       | 52b06792de26b86b           |
| RESOURCES | Hashes      | "#hash_    | bo3, bo4, bocw, mwiii, bo6 | "#hash_448210df69276e85"                       | 448210df69276e85           |
| RESOURCES | Hashes      | #hash_     | bo3, bo4, bocw, mwiii, bo6 | #hash_d0453aea97fe80a6                         | d0453aea97fe80a6           |
| RESOURCES | Hashes      | hash_      | bo3, bo4, bocw, mwiii, bo6 | hash_52b06792de26b86b                          | 52b06792de26b86b           |
| RESOURCES | Scripts     | script_    | bo4, bocw, mwiii, bo6      | script_19163c4e4e504a5e                        | 19163c4e4e504a5e           |
| RESOURCES | R_Hashes    | r"hash_    | mwiii, bo6                 | r"hash_619f3b379de7ef46"                       | 619f3b379de7ef46           |
| RESOURCES | %_Hashes    | %"hash_    | mwiii, bo6                 | %"hash_4f1c2cdc046bbe60"                       | 4f1c2cdc046bbe60           |
| RESOURCES | &_Hashes    | &"hash_    | bo6                        | %"hash_4f1c2cdc046bbe60"                       | 4f1c2cdc046bbe60           |
| RESOURCES | t_Hashes    | t"hash_    | mwiii, bo6                 | %"hash_4f1c2cdc046bbe60"                       | 4f1c2cdc046bbe60           |
| IW Dvars  | Dvars       | @"hash_    | mwiii, bo6                 | @"hash_794056489aa0efdd"                       | 794056489aa0efdd           |
| Omnvars   | Omnvars     | @o"hash_   | bo6                        | @o"hash_4F690C78D6DA9218"                      | 4F690C78D6DA9218           |

Specific SCR detail

|Game full name     | Game short name | SCR algorithm      | Patterns                          |
|-------------------|-----------------|--------------------|-----------------------------------|
|Black Ops 3        | bo3             | black_ops_3_scr    | Always                            |
|Black Ops 4        | bo4             | hash_bo4cw_scr     | Always                            |
|Black Ops Cold War | bocw            | hash_bo4cw_scr     | Always                            |
|Moder Warfare III  | mwiii           | mwii_iii_scr       | Always                            |
|Black Ops 6        | bo6             | black_ops_6_scr    | If script is NOT inside SP folder |
|Black Ops 6        | bo6             | black_ops_6_sp_scr | If script is inside SP folder     |

Specific RESOURCES detail

|Game full name     | Game short name | RESOURCES algorithm | Patterns                                 |
|-------------------|-----------------|--------------------|-------------------------------------------|
|Black Ops 3        | bo3             | black_ops_3_scr    | #"hash_                                   |
|Black Ops 3        | bo3             | black_ops_3_scr    | hash_                                     |
|Black Ops 4        | bo4             | base_fnv1a_63      | #"hash_                                   |
|Black Ops 4        | bo4             | base_fnv1a_63      | "#hash_                                   |
|Black Ops 4        | bo4             | base_fnv1a_63      | #hash_                                    |
|Black Ops 4        | bo4             | base_fnv1a_63      | hash_                                     |
|Black Ops 4        | bo4             | base_fnv1a_63      | script_                                   |
|Black Ops Cold War | bocw            | base_fnv1a_63      | #"hash_                                   |
|Black Ops Cold War | bocw            | base_fnv1a_63      | "#hash_                                   |
|Black Ops Cold War | bocw            | base_fnv1a_63      | #hash_                                    |
|Black Ops Cold War | bocw            | base_fnv1a_63      | hash_                                     |
|Black Ops Cold War | bocw            | base_fnv1a_63      | script_                                   |
|Moder Warfare III  | mwiii           | base_fnv1a_63      | #"hash_                                   |
|Moder Warfare III  | mwiii           | base_fnv1a_63      | "#hash_                                   |
|Moder Warfare III  | mwiii           | base_fnv1a_63      | #hash_                                    |
|Moder Warfare III  | mwiii           | base_fnv1a_63      | hash_                                     |
|Moder Warfare III  | mwiii           | iw_resources       | script_                                   |
|Moder Warfare III  | mwiii           | iw_resources       | r"hash_                                   |
|Moder Warfare III  | mwiii           | iw_resources       | %"hash_                                   |
|Moder Warfare III  | mwiii           | mwii_iii_scr       | &"hash_                                   |
|Moder Warfare III  | mwiii           | base_fnv1a_32      | t"hash_                                   |
|Black Ops 6        | bo6             | base_fnv1a_64      | #"hash_                                   |
|Black Ops 6        | bo6             | base_fnv1a_64      | "#hash_                                   |
|Black Ops 6        | bo6             | base_fnv1a_64      | #hash_                                    |
|Black Ops 6        | bo6             | base_fnv1a_64      | hash_                                     |
|Black Ops 6        | bo6             | iw_resources       | script_                                   |
|Black Ops 6        | bo6             | iw_resources       | r"hash_                                   |
|Black Ops 6        | bo6             | iw_resources       | %"hash_                                   |
|Black Ops 6        | bo6             | black_ops_6_scr    | &"hash_ If script is NOT inside SP folder |
|Black Ops 6        | bo6             | black_ops_6_sp_scr | &"hash_ If script is inside SP folder     |
|Black Ops 6        | bo6             | base_fnv1a_32      | t"hash_                                   |

IW Dvars detail

|Game full name     | Game short name | SCR algorithm      | Patterns                          |
|-------------------|-----------------|--------------------|-----------------------------------|
|Black Ops 3        | bo3             | doesnt appear      |                                   |
|Black Ops 4        | bo4             | doesnt appear      |                                   |
|Black Ops Cold War | bocw            | doesnt appear      |                                   |
|Moder Warfare III  | mwiii           | iw_dvars           | @"hash_                           |
|Black Ops 6        | bo6             | iw_dvars           | @"hash_                           |

Omnivars detail

|Game full name     | Game short name | SCR algorithm       | Patterns                          |
|-------------------|-----------------|---------------------|-----------------------------------|
|Black Ops 3        | bo3             | doesnt appear       |                                   |
|Black Ops 4        | bo4             | doesnt appear       |                                   |
|Black Ops Cold War | bocw            | doesnt appear       |                                   |
|Moder Warfare III  | mwiii           | doesnt appear       |                                   |
|Black Ops 6        | bo6             | black_ops_6_omnvars | @o"hash_  Only in .lua files      |