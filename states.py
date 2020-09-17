
GENERAL_STATES = {key: value for value, key in enumerate(["BAHNHOF_START",
                                                          "ABSCHLUSS",
                                                          "INFO_END",
                                                          "ENDE"])}

INTRO_STATES = {key: value for value, key in enumerate(["NAME",
                                                        "NAME_AENDERN",
                                                        "STARTPUNKT",
                                                        "ROUTE_AUSWAEHLEN",
                                                        "TESTROUTE_BESTAETIGEN"
                                                        ],10)}

INFO_STATES = {key: value for value, key in enumerate(["INFO"],20)}

BAHNHOF_STATES = {key: value for value, key in enumerate(["BAHNHOF_FRAGE_GIF",
                                                          "BAHNHOF_FRAGE_GIF_AUFLOESUNG",
                                                          "BAHNHOF_FRAGE",
                                                          "BAHNHOF_FRAGE_AUFLOESUNG",
                                                          "WEG01",
                                                          "FRAGE_QUIZ",
                                                          "FRAGE_QUIZ_AUFLOESUNG",
                                                          "WEG01A",
                                                          "FRAGE_UBAHN",
                                                          "FRAGE_UBAHN_AUFLOESUNG",
                                                          "WEG02",
                                                          "FRAGE_WEINMEISTERATRASSE",
                                                          "FRAGE_WEINMEISTERATRASSE_AUFLOESUNG",
                                                          "FEHLERBILD_REIHERBERG",
                                                          "FEHLERBILD_REIHERBERG_AUFLOESUNG",
                                                          "AUFSTIEG_REIHERBERG",
                                                          "SCHAETZFRAGE_REIHERBERG",
                                                          "SCHAETZFRAGE_REIHERBERG_AUFLOESUNG",
                                                          "FOTO_REIHERBERG",
                                                          "FOTO_REIHERBERG_AUFLOESUNG"],30)}

ABSCHLUSS_STATES = {key: value for value, key in enumerate(["ENDE"],50)}