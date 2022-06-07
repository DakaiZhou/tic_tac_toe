# tic_tac_toe

# Introduction
This is a demo api for tic tac toe game. The API has some endpoints that a user to regester as players and play game with other players.

## Features/Functions
1. Player registration endpoint: open to anyone who wants to registr to play the game.
2. Create game endpoint: registered player can create a game and share game identify to other players to invite them to the game.
3. Join game endpoint: players(different from game creator) can join the game by providing game identify.
4. Make move endpoint: players can make only meaningful moves in turns with this endpoint.
5. High score list endpoint: players can get a top n high score player list by given parameter top-n.
6. View token endpoint: if a player forget the token, they can provide their account credential to call the token.

## Authentication
All endpoint except one endpoint use a static token for authentication. Then token should be places in the Authorization header:

    Authorization: Bearer {{apiAccessToken}}
    
The token is created when you finsih your registration and can be obtained by accounts/token/.

## HTTP Response codes
* 200: ok code, this means the operation was successful.
* 201: created code, this means the instance is created successfully.
* 401: unauthorized code, credantial is wrong.
* 403: forbiddencode, the request is forbidden.
* 404: not found code, the resource was not found.
* 405: method not allowed code, the request method is not allowed .
* 409: conflict code, the request is conflict with resource requirements

## Endpoints
### Account Registration POST

    accounts/registration/
    
To create game account. 
#### Body parameters
|Parameters|Description|
|----------|:----------|
|username|required, the name for the player|
|email|required, email connect to the user account|
|password|required, account password|

### Get Account Token POST
    accounts/token/
To get your api token. Username and password need to be provided for basic authentication.

### Create a game POST
    game/create/
To create a game. Token authentication required.

### Join a game PUT
    game/join/<game_id>/
To join a game. Token authentication required.

### Make moves PUT
    game/make-move/
To make a move in the game. Token authentication required.
#### Body parameters
|Parameters|Description|
|----------|:----------|
|game_id|required, identify of the game|
|row|required, row number of the movement you want to make|
|col|required, column number of the movement you want to make|

### Get a high scores list GET
    game/list/high-score/
To get a top n high scores list. Token authentication required.
#### Query parameters
|Parameters|Description|
|----------|:----------|
|top_n|required, The length of the list|
