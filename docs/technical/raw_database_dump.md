# Raw Database Dump

## players.sqlite

### player table
```
name     pitch              yaw               posX            posY               posZ               hp  breath  creation_date        modification_date  
-------  -----------------  ----------------  --------------  -----------------  -----------------  --  ------  -------------------  -------------------
ToddLLM  1.20000004768372   8.30999755859375  4095.75         161.869995117188   -3656.10009765625  2   10      2025-08-01 20:04:01  2025-08-02 01:50:44
Chelsea  7.78000020980835   161.859985351563  4105.490234375  200                -3621.15991210938  11  10      2025-08-01 20:07:28  2025-08-02 00:49:49
Dev      -37.9900016784668  221.410003662109  -1288           -64.9899978637695  2538.36010742188   20  10      2025-08-01 20:10:45  2025-08-01 20:23:35
```

### player_inventories table
```
id  player_id  width  type            size
--  ---------  -----  --------------  ----
1   1          8      main            32  
2   1          3      craft           9   
3   1          1      craftpreview    1   
4   1          1      craftresult     1   
5   2          8      main            32  
6   2          3      craft           9   
7   2          1      craftpreview    1   
8   2          1      craftresult     1   
9   3          8      main            32  
10  3          3      craft           9   
11  3          1      craftpreview    1   
12  3          1      craftresult     1   
```

### player_inventory_items table (only non-empty slots)
```
player   inv_id  slot_id  item                                                        
-------  ------  -------  ------------------------------------------------------------
Dev      0       0        default:sword_wood                                          
Dev      0       9        default:leaves                                              
Dev      0       10       default:dirt 17                                             
Dev      0       11       default:wood                                                
Dev      0       12       default:tree 10                                             
Dev      0       13       default:stick 3                                             
Chelsea  0       0        default:apple                                               
Chelsea  0       1        default:ladder_wood 99                                      
Chelsea  0       2        stairs:slab_goldblock 99                                    
Chelsea  0       3        default:pick_mese                                           
Chelsea  0       4        nullifier_adventure:jetpack                                 
Chelsea  0       5        default:desert_sandstone 99                                 
Chelsea  0       24       default:chest                                               
Chelsea  0       25       default:chest 98                                            
Chelsea  0       26       nullifier_adventure:villager_spawn_egg 99                   
ToddLLM  0       0        default:book 98                                             
ToddLLM  0       1        default:chest 5                                             
ToddLLM  0       2        default:furnace 5                                           
ToddLLM  0       3        nullifier_adventure:villager_spawn_egg 3                    
ToddLLM  0       4        default:book_written 1 0 "\u0001title\u0002hello\u0003description\u0002\u001b(T@default)\"\u001bFhello\u001bE\" by \u001bFToddLLM\u001bE\u001bE\u0003owner\u0002ToddLLM\u0003page_max\u00021\u0003page\u00021\u0003"
```

### player_metadata table
```
player   metadata           value                                  
-------  -----------------  ---------------------------------------
Chelsea  sethome:home       (414.74502563477,15.5,-363.49798583984)
Chelsea  simple_skins:skin  character_7                            
ToddLLM  sethome:home       (414.09503173828,15.5,-363.42300415039)
ToddLLM  simple_skins:skin  character_6                            
```

## auth.sqlite

### auth table
```
id  name     password                                                      last_login
--  -------  ------------------------------------------------------------  ----------
1   ToddLLM  #1#vFsmN7anf+S37jtCykAF3Q#[512 char hash]                    1754092502
2   Chelsea  #1#JiwZl2H+/FasvQMGjqmFeg#[512 char hash]                    1754092503
3   Dev      #1#s/azTASj6c/bBWPMQFyuWw#[512 char hash]                    1754079041
```

### user_privileges table
```
id  privilege        
--  -----------------
3   interact         
3   shout            
3   privs            
3   teleport         
3   bring            
3   fast             
3   fly              
3   noclip           
3   creative         
3   give             
3   settime          
3   server           
3   protection_bypass
3   ban              
3   kick             
1   bring            
1   settime          
1   server           
1   protection_bypass
1   ban              
1   kick             
1   give             
1   password         
1   fly              
1   fast             
1   noclip           
1   ui_full          
1   rollback         
1   teleport         
1   basic_privs      
1   shout            
1   interact         
1   home             
1   privs            
1   debug            
1   creative         
2   bring            
2   settime          
2   server           
2   protection_bypass
2   ban              
2   kick             
2   give             
2   password         
2   fly              
2   fast             
2   noclip           
2   ui_full          
2   rollback         
2   teleport         
2   basic_privs      
2   shout            
2   interact         
2   home             
2   privs            
2   debug            
2   creative         
```

## mod_storage.sqlite

### entries table
```
modname  key      value          
-------  -------  ---------------
skinsdb  ToddLLM  character_200  
skinsdb  Chelsea  player_cool_guy
```

## map.sqlite

### blocks table
```
Total blocks: 143458

Sample blocks (pos, size in bytes):
pos        size
---------  ----
100626435  625 
100622339  628 
100618243  616 
100630531  287 
83849219   784 
83845123   720 
83841027   726 
83853315   483 
100626434  558 
100622338  857
```

## Other files

### beds_spawns
```
Chelsea 414.74502563477 16.5 -363.49798583984
ToddLLM 414.09503173828 16.5 -363.42300415039
```

### env_meta.txt
```
day_count = 34
game_time = 22705
time_of_day = 17399
```

### world.mt
```
enable_damage = false
creative_mode = false
mod_storage_backend = sqlite3
auth_backend = sqlite3
player_backend = sqlite3
backend = sqlite3
gameid = minetest
world_name = world
load_mod_simple_skins = true
load_mod_unified_inventory = true
load_mod_nullifier_adventure = true
```