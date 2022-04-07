# eggman
Discord bot for Eggs Benedic Mafia server

General usage is similar to most command-line functions, but slightly different:

Invoke eggman bot with `eggman` trigger word, followed by a list of commands with their arguments.
```
!<cmd[0]> <arg[0,0]> <arg[0,1]> ... <arg[0,n]> !<cmd[2]> <arg[2,0]> ... !<cmd[n]> ...
```
For example
```
eggman !echo this
```
Arguments can be specified separately with spaces, and a single argument that contains spaces can be specified with quotes
```
eggman !echo arg0 "this is cool" arg2
```
Or, if the command doesn't take particular arguments in an order
```
eggman !echo this is cool
```
Both examples above lead to `this is cool` being sent by eggman

Multi-command example:
```
eggman !echo this is neat !echo "this is super cool" !greet
```
The above commands will all be executed in that order. Note that `!echo` was used twice, with two different arguments: both will still be executed.

There are also some special commands, such as `gn eggman` that trigger eggman functionalities, and they don't require the trigger word `eggman` or the command prefix `!`
