# RoPaSci360

## Part A
Implement a simplified, single-player (non-adversarial), search-based variant of the game.

In part A, as this is single-player there will be following modifications:
* No throw action, instead the game begins with tokens already on the board.
* Lower's tokens never move. On each turn, all of Upper's tokens move simultaneously.
* The player must repeatedly move the Upper tokens to defeat all of Lower's tokens to win. If the last Upper token is defeated in the same turn as the last Lower token, the player still wins.
* Block tokens prevent other tokens from occupying their hexes. Block tokens never move. No token can slide or swing onto or over a Block token.

To run the program: python3 -m search "test case filename"

NOTE: More details on the specifications.

## Part B

