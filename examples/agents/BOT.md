# Agent: BOT Characteristics

|      | Start Position                                              | Moving                                                | Attacking                                                       |
|------|-------------------------------------------------------------|-------------------------------------------------------|-----------------------------------------------------------------|
| bot1 | The random empty tile                                       | Direct to closest Gold or Shield tile                 | ---                                                             |
| bot2 | The closest empty tile to center                            | Direct to closest Gold or Shield tile                 | ---                                                             |
| bot3 | The first tile next to a Shield or Gold tile                | Direct to closest Gold or Shield tile                 | ---                                                             |
| bot4 | The first empty tile next to a Shield or Gold tile          | Direct to closest Gold or Shield tile                 | Random around enemies                                           |
| bot5 | The random empty tile next to a Shield or Gold tile         | Direct to closest Gold or Shield tile                 | Random around enemies                                           |
| bot6 | The random empty tile next to a Shield or Gold tile         | Direct to closest Gold or Shield tile                 | Attack exactly if any enemy is sunk, else random around enemies |
| bot7 | The random empty tile next to a Shield or Gold tile         | Direct to closest Gold or Shield tile                 | Similar to bot6, but shot 2 missiles                            |
| bot8 | The random empty tile next to a Shield or Gold tile         | Similar to bot7, but avoid collision with other ships | Similar to bot6, but shot 2 missiles                            |
| bot9 | The random empty tile next to a Shield or maximum Gold tile | Similar to bot8, but choose the maximum Gold tile     | Similar to bot6, but shot 2 missiles                            |
