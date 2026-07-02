-- INSERT INTO users (id, name) VALUES (33, 'tom');
-- INSERT INTO games (user_id, word_to_guess, status) VALUES (33, 'burble', 'in_progress');

INSERT INTO guesses (id, game_id, attempt_no, guess_word, feedback) 
VALUES (1, 2, 1, 'baubis', 'full,none,none,full,none,none');

INSERT INTO guesses (id, game_id, attempt_no, guess_word, feedback) 
VALUES (2, 2, 2, 'baubry', 'full,none,none,full,none,none');