# Special puzzles
Please see the [features doc](/docs/features.md#framework-for-writing-interactive-puzzles) for an overview of what kind of special puzzles we identified.

This doc gives a short overview of using each helper module. Check the 2022 puzzles for examples of using these.

## Session puzzles
A session puzzle is a short-lived communication channel between a single tab of a client's browser, and the server. If the client refreshes their tab, the session is over. Essentially, it's a session across time for a single tab.

Each session consists of a series of updates/action by the client. These actions must be sent with a strictly increasing sequence ID, and this is automatically checked by the [backend helper](session_puzzle.py) and implemented by the [frontend helper](../scripts/retriable-session-puzzle.ts).

A session's puzzle backend just defines a model, and a transformer that accepts client actions, transforms the model, and then returns a response. This is useful for puzzles where state needs to be hidden from the user, such as a card game or maze.

The helpers expose hooks to handle retrying if the client disconnects, and to restart or complete sessions.

## Team puzzles
Team puzzles are a general concept where there is state shared between the whole team. The state is then sent to each team member's (or possibly just part of the state) device.

It's been implemented with a series of plugins for [`TeamConsumer`](../core/team_consumer.py). The plugins can communicate with each other through a [simple event system](../core/plugins.py).

This plugin system helps puzzles pick-and-choose behavior. (I started with an inheritance hierarchy, and quickly ran into problems where no level of the inheritance hierarchy had the right combination of features for some puzzles.)

One small downside is that none of these plugins use Python's async feature, and so are synchronous and blocking in their code. Practically, this is fine, but the plugin system also helps enable choosing between sync & async modes, with less code duplication.

There's some messiness where [progress](#progress-plugin) and [session](#session-plugin) are basically the same. (The history there is that session was initially to power the leader plugin, and we needed something more powerful for plugins like state.)

### Leader plugin
This is behaviour [inherited from the 2021 hunt](https://github.com/YewLabs/2021-hunt/blob/master/hunt/teamwork.py#L275) but isn't actually used in this hunt.

 - Dependency: [session plugin](#session-plugin)
 - Model: It constrains the session plugin to use a subclass of `TeamLeaderModelBase` as the model.
 - Guarantee: There is at most one leader for a session, and if there are clients, a leader will be elected soon.
    - (not completely tested)
 - Hook: `claimed_leader` if the current consumer is now the leader.
 - Messages: It notifies the client when "is there currently a leader" changes

You might use this if the backend needs one consumer to take responsibility for an action such as rolling a dice.

### Minipuzzle plugin
 - Dependency: [puzzle plugin](#puzzle-plugin)
 - Guarantee: Shares progress on the minipuzzles within a puzzle with all members of the team.
 - Messages: It notifies the client every time a minipuzzle has "progress" such as a guess or a solve.

Minipuzzles are a general concept that can be used for an answer checker of a part of a puzzle, through to minigames that need to be "won" to unlock an answer (with the [`mark_minipuzzle_solved`](/spoilr/core/api/answer.py) helper).

There's some [dedicated UI](/docs/features.md#minipuzzles) for showing minipuzzles as well.

### Progress plugin
 - Dependency: [puzzle plugin](#puzzle-plugin)
 - Guarantee: Shares progress on a puzzle with all clients that are part of the team. Exposes hooks for initializing and projecting the progress, and allows the state to be transformed.
 - Messages: It notifies the client whenever the "progress" changes.

This is a more general way to notifying about "winning" minipuzzles.

### Puzzle plugin
- Guarantee: Performs extra authentication to ensure the team has access to the puzzle.

A helper plugin to centralize authentication, hold information about the current puzzle, and specify the Django channels group name.

### Room plugin
 - Dependency: [session plugin](#session-plugin)
 - Guarantee: Shares a list of all members of the team who are currently viewing this puzzle. It moves members through a state machine as they enter, verify the liveness of the room, and then are ready to participate.
    - Note: Before hunt, we decided to pull the puzzle that used this because of occasional connectivity issues that we didn't have time to debug. On request, I can share some of the code for the puzzle that used this plugin.
    - It's tricky because Django channels and websockets provide so few guarantees about messages when people enter or leave groups, and so there are a bunch of hard-to-debug failure modes, and the failure modes vary based on the environment.
    - Nevertheless, I think this is close to working correctly! And when it does, some of the complexity with the two-stage liveness check can probably be improved.
 - Messages: The list of participants in the room.
 - API: Actions to join and leave the room.

### Session plugin
 - Dependency: [puzzle plugin](#puzzle-plugin)
 - Guarantee: Exposes a backend-only session model for sharing data between all consumers. Not actually too useful directly, more of an implementation detail of other plugins.

### State plugin
 - Dependency: [session plugin](#session-plugin)
 - Guarantee: Shares some general state between all clients, and exposes an API for transforming the state.

This is a really powerful abstraction for writing complex puzzles that persist state across sessions, or where collaboration is important. It's kind of the collaborative equivalent of [session puzzles](#session-puzzles).

### State list plugin
 - Dependency: [state plugin](#state-plugin)
 - Guarantee: Allows for having multiple states in a single puzzle, so that teams can have separate collaboration spaces.

Also a really powerful abstraction! And it cooperates with the room plugin well if needed.

### Custom plugins
You can also write puzzle-specific plugins - take a look at [`P1004CountingPlugin`](/hunt/data/special_puzzles/samples/puzzle1004_counting.py).
