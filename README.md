This is a demonstration how to rebuild the state of a Mersenne Twister by using only parts of its output. Have fun.

For details see https://spideroak.com/blog/20121205114003-exploit-information-leaks-in-random-numbers-from-python-ruby-and-php

The Mersenne Twister implementation is in twister.py.

rebuild_random.py and rebuild_random_multicore.py demonstrate that it works.

Boring output of the example program:
```
$ python rebuild_random_multicore.py 
Loading Magic
Done.
REBUILDING RANDOM-POOL [                                                              ]
REBUILDING RANDOM-POOL [##                                                            ]
REBUILDING RANDOM-POOL [####                                                          ]
REBUILDING RANDOM-POOL [#######                                                       ]
REBUILDING RANDOM-POOL [#########                                                     ]
REBUILDING RANDOM-POOL [############                                                  ]
REBUILDING RANDOM-POOL [##############                                                ]
REBUILDING RANDOM-POOL [################                                              ]
REBUILDING RANDOM-POOL [###################                                           ]
REBUILDING RANDOM-POOL [#####################                                         ]
REBUILDING RANDOM-POOL [########################                                      ]
REBUILDING RANDOM-POOL [##########################                                    ]
REBUILDING RANDOM-POOL [############################                                  ]
REBUILDING RANDOM-POOL [###############################                               ]
REBUILDING RANDOM-POOL [#################################                             ]
REBUILDING RANDOM-POOL [####################################                          ]
REBUILDING RANDOM-POOL [######################################                        ]
REBUILDING RANDOM-POOL [########################################                      ]
REBUILDING RANDOM-POOL [###########################################                   ]
REBUILDING RANDOM-POOL [#############################################                 ]
REBUILDING RANDOM-POOL [################################################              ]
REBUILDING RANDOM-POOL [##################################################            ]
REBUILDING RANDOM-POOL [####################################################          ]
REBUILDING RANDOM-POOL [#######################################################       ]
REBUILDING RANDOM-POOL [#########################################################     ]
REBUILDING RANDOM-POOL [############################################################  ]
RANDOM POOL SUCCESSFULLY REBUILT!
```

Frank Sievertsen
@fx5
