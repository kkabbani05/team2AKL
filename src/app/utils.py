def calculate_feedback(word, guess_string):
    tally = dict()
    for c in word:
        if c in tally:
            tally[c] += 1
        else:
            tally[c] = 1

    colors = {}
    # check one to one positions for green tiles
    for i, c in enumerate(guess_string):
        if c == word[i]:
            colors[str(i)]  = "full"
            tally[c] -= 1

    # check for yellow
    for i, c in enumerate(guess_string):
        if str(i) not in colors:
            if c in word and tally[c] > 0:
                colors[str(i)] = "partial"
                tally[c] -= 1
            else:
                colors[str(i)] = "none"
    return colors
