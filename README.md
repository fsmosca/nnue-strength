# nnue-strength
Compare NNUE strength with human players and other chess engines.

## Sample output

Get NNUE eval from Stockfish.

```
    GameNum                                                   Epd  MoveNum                    Name GameMove  GameMoveScore EngineMove  EngineScore NNUEMove  NNUEScore  HumanError  NNUEError
0         1   5rk1/1p1q1ppb/2p1p2p/4P3/R7/2Q3P1/1P2PPBP/6K1 w - -       23         Carlsen, Magnus      Rd4             48        Rd4           48      Rd4         48           0          0
1         1  5rk1/1p1q1ppb/2p1p2p/4P3/3R4/2Q3P1/1P2PPBP/6K1 b - -       23          Aronian, Levon      Qc7            -50        Qc7          -50     Qxd4       -487           0        437
2         1   5rk1/1pq2ppb/2p1p2p/4P3/3R4/2Q3P1/1P2PPBP/6K1 w - -       24         Carlsen, Magnus      Rd6             46        Qc5           55      Rd7       -528           9        583
3         1     5rk1/1pq2ppb/2pRp2p/4P3/8/2Q3P1/1P2PPBP/6K1 b - -       24          Aronian, Levon      Ra8            -52        Bb1          -43     Qxd6       -540           9        497
4         1     r5k1/1pq2ppb/2pRp2p/4P3/8/2Q3P1/1P2PPBP/6K1 w - -       25         Carlsen, Magnus      Bf3             59        Bf3           59     Rxc6       -460           0        519
..      ...                                                   ...      ...                     ...      ...            ...        ...          ...      ...        ...         ...        ...
74        5                    8/p7/1p5R/3P1kp1/8/1K5P/r7/8 b - -       38  Abdusattorov, Nodirbek      Ra1             72        Rd2           90      Rd2         90          18          0
75        5                    8/p7/1p5R/3P1kp1/8/1K5P/8/r7 w - -       39        Rapport, Richard      Kc4           -108         d6          -60      Kc4       -108          48         48
76        5                     8/p7/7R/1pKP1kp1/8/7P/8/3r4 b - -       42  Abdusattorov, Nodirbek       b4            203         b4          203       a5         20           0        183
77        5                    7R/p7/8/2KP1kp1/1p6/7P/8/3r4 b - -       43  Abdusattorov, Nodirbek       b3            199         b3          199       a5        137           0         62
78        5                  4R3/p7/8/2KP2p1/8/1p1k3P/8/3r4 w - -       46        Rapport, Richard       d6           -671        Rb8         -647       d6       -671          24         24

[79 rows x 12 columns]
AveHumanError: 8.0
AveNNUEError: 247.0
```
