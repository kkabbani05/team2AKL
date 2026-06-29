-- Seed data for guesses table
-- Feedback format: G=gray (not in word), Y=yellow (in word, wrong position), GR=green (correct position)
INSERT INTO guesses (game_id, attempt_no, guess_word, feedback) VALUES
-- Game 1: PLANT
(1, 1, 'STARE', 'G,Y,GR,G,G'),
(1, 2, 'PLANT', 'GR,GR,GR,GR,GR'),
-- Game 2: TRACK (in progress - no winning guess yet)
(2, 1, 'SLATE', 'G,G,GR,Y,G'),
(2, 2, 'CRANE', 'Y,GR,GR,G,G'),
-- Game 3: FLAME
(3, 1, 'STALE', 'G,G,GR,G,Y'),
(3, 2, 'FLAKE', 'GR,GR,GR,G,Y'),
(3, 3, 'FLAME', 'GR,GR,GR,GR,GR'),
-- Game 4: BEACH (in progress - no winning guess yet)
(4, 1, 'STARE', 'G,G,GR,Y,G'),
(4, 2, 'REACH', 'G,GR,GR,Y,GR'),
-- Game 5: SOUND
(5, 1, 'STARE', 'G,G,G,Y,G'),
(5, 2, 'SOUND', 'GR,GR,GR,GR,GR'),
-- Game 6: TOAST (abandoned)
(6, 1, 'STARE', 'Y,Y,GR,G,G'),
(6, 2, 'ROAST', 'G,GR,GR,GR,GR');
