
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
                                                          "FOTO_REIHERBERG_AUFLOESUNG",
                                                          "WEG_KIRCHE_1",
                                                          "WEG_KIRCHE_2",
                                                          "KIRCHE_WORTRAETSEL",
                                                          "FRAGE_KIRCHE",
                                                          "KIRCHE_AUFLOESEUNG",
                                                          "FRAGE_STORCHENBANK",
                                                          "KAPELLE",
                                                          "WEG_SCHULE",
                                                          "SCHULE",
                                                          "WEG_LANDHOTEL",
                                                          "FEUERWEHR",
                                                          "FRAGE_FEUERWEHR",
                                                          "FRAGE_FEUERWEHR_AUFLOESUNG",
                                                          "WEG_VIERSEITENHOF",
                                                          "VIERSEITENHOF",
                                                          "RUECKWEG_BAHNHOF_1",
                                                          "RUECKWEG_BAHNHOF_2"],50)}

ABSCHLUSS_STATES = {key: value for value, key in enumerate(["ENDE"],50)}