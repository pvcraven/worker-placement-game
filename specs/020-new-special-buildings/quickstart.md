# Quickstart: New Special Buildings

## Scenario 1: Royalty Collection — Basic Visit

**Setup**: 2-player game. Player A owns the Royalty Collection building. 3 buildings have been purchased total.

**Steps**:
1. Player B places a worker on the Royalty Collection building
2. Player B receives 3 coins (1 per building in play)
3. Player A receives 2 coins (owner bonus)
4. Quest completion check runs for Player B

**Verify**: Player B's coins increased by 3. Player A's coins increased by 2.

## Scenario 2: Royalty Collection — Self Visit

**Setup**: 2-player game. Player A owns the Royalty Collection building. 4 buildings in play.

**Steps**:
1. Player A places a worker on their own Royalty Collection building
2. Player A receives 4 coins (visitor reward)
3. Owner bonus does NOT trigger (self-visit)

**Verify**: Player A's coins increased by exactly 4 (no owner bonus).

## Scenario 3: Audition Showcase — Immediate Completion

**Setup**: 2-player game. Player A owns the Audition Showcase. Player B has enough resources to complete one of the face-up contracts.

**Steps**:
1. Player B places a worker on the Audition Showcase
2. Player B selects a face-up contract they can afford
3. Contract is added to Player B's hand; replacement drawn from deck
4. Quest completion window opens showing completable quests
5. The drawn contract appears with "+4VP bonus" text
6. Player B clicks the drawn contract to complete it
7. Normal quest rewards are processed + 4 bonus VP
8. Player A receives 2 VP (owner bonus)

**Verify**: Player B received quest rewards + 4 bonus VP. Player A received 2 VP.

## Scenario 4: Audition Showcase — Can't Afford Drawn Contract

**Setup**: Player B cannot afford the contract they select, but CAN complete a different quest in hand.

**Steps**:
1. Player B places a worker on the Audition Showcase
2. Player B selects a face-up contract they cannot afford
3. Contract goes into hand; replacement drawn
4. Quest completion window opens with other completable quests only
5. The drawn contract does NOT appear (no bonus text)
6. Player B may complete another quest at normal value or skip

**Verify**: No +4VP bonus text shown. Drawn contract is in hand for later.

## Scenario 5: Audition Showcase — No Quests Completable

**Setup**: Player B cannot afford any quest (neither drawn nor in hand).

**Steps**:
1. Player B places a worker on the Audition Showcase
2. Player B selects a face-up contract
3. Contract goes into hand; replacement drawn
4. Quest completion window is NOT shown (normal behavior)
5. Turn advances

**Verify**: Contract is in hand. No quest completion window appeared.

## Scenario 6: Audition Showcase — Skip Bonus, Complete Later

**Setup**: Player B can afford the drawn contract but chooses to skip.

**Steps**:
1. Player B completes the showcase flow but skips quest completion
2. Contract remains in hand
3. On a later turn, Player B completes the same contract normally

**Verify**: No bonus VP awarded on later completion. Normal quest rewards only.
