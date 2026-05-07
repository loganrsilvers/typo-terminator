import jellyfish
import random
import numpy as np
from pathlib import Path


# Only pairs that sound genuinely similar in standard English.
# Removed l↔r (not a natural English confusion).
# Vowel subs only apply to SHORT vowel sounds — we guard against
# vowel digraphs (ow, oo, ai, etc.) in the substitution logic below.
PHONETIC_SUBS = {
    # Short vowels — similar tongue/mouth position
    'e': ['i'],        # "bed" → "bid"
    'i': ['e'],        # "bit" → "bet"

    # Voiced / unvoiced consonant pairs — same place of articulation
    'b': ['p'],        # "bin" → "pin"
    'p': ['b'],
    'd': ['t'],        # "den" → "ten"
    't': ['d'],
    'g': ['k'],        # "gap" → "kap"
    'k': ['g'],
    'v': ['f'],        # "vest" → "fest"
    'f': ['v'],
    's': ['z'],        # "sip" → "zip"
    'z': ['s'],

    # Nasals
    'm': ['n'],        # "mat" → "nat"
    'n': ['m'],
}

# If a vowel is followed by any of these letters it's part of a digraph
# (ow, oo, oa, ou, ai, ae, ie, etc.) — don't sub it.
DIGRAPH_FOLLOWERS = set('aeiouwh')


def is_short_vowel(word, i):
    """
    Return True only if word[i] is a standalone short vowel —
    not part of a digraph or diphthong.
    """
    ch = word[i]
    if ch not in 'aeiou':
        return False
    # Check the letter before and after for digraph partners
    before = word[i - 1] if i > 0 else ''
    after  = word[i + 1] if i < len(word) - 1 else ''
    if before in DIGRAPH_FOLLOWERS or after in DIGRAPH_FOLLOWERS:
        return False
    return True


class TypoGenerator:
    def __init__(self, word_bank_file):
        try:
            text = Path(word_bank_file).read_text(encoding="utf-8")
            self.words = [w.strip().lower() for w in text.replace("\n", " ").split(",") if w.strip()]
        except Exception as e:
            print(f"Error loading wordbank: {e}")
            self.words = ["programming", "backend", "database", "interface",
                          "columbia", "chicago", "wrestling", "software"]

    def phonetic_code(self, word):
        return {
            "soundex":   jellyfish.soundex(word),
            "metaphone": jellyfish.metaphone(word),
            "nysiis":    jellyfish.nysiis(word)
        }

    def phonetic_distance(self, code1, code2):
        dists = []
        for key in code1:
            if key in code2:
                dists.append(jellyfish.levenshtein_distance(code1[key], code2[key]))
        return np.mean(dists) if dists else 1.0

    def generate_typo(self, word):
        orig_code = self.phonetic_code(word)

        # Build list of valid substitution positions
        candidates = []
        for i, ch in enumerate(word):
            subs = PHONETIC_SUBS.get(ch, [])
            if not subs:
                continue
            # For vowels, only allow sub if it's a standalone short vowel
            if ch in 'aeiou' and not is_short_vowel(word, i):
                continue
            for sub in subs:
                typo = word[:i] + sub + word[i + 1:]
                if typo == word:
                    continue
                try:
                    dist = self.phonetic_distance(orig_code, self.phonetic_code(typo))
                    if dist <= 1:
                        candidates.append(typo)
                except Exception:
                    continue

        if candidates:
            return random.choice(candidates)
        return None

    def get_challenge(self):
        pool = self.words[:]
        random.shuffle(pool)

        for word in pool:
            typo = self.generate_typo(word)
            if typo and typo != word:
                return word, typo

        # Fallback — swap first voiced/unvoiced consonant found
        word = random.choice(self.words)
        simple = {'b':'p','p':'b','d':'t','t':'d','g':'k','k':'g'}
        for i, ch in enumerate(word):
            if ch in simple:
                return word, word[:i] + simple[ch] + word[i + 1:]
        return word, word


if __name__ == "__main__":
    tg = TypoGenerator("wordbank/600vocabWords.txt")
    print(f"{'ORIGINAL':<20} {'TYPO':<20}")
    print("-" * 40)
    for _ in range(15):
        original, typo = tg.get_challenge()
        print(f"{original:<20} {typo:<20}")
