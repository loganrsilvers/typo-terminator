import jellyfish
import random
import numpy as np
from pathlib import Path
from pyodide.http import pyfetch
import json
import asyncio

PHONETIC_SUBS = {
    'e': ['i'],
    'i': ['e'],
    'd': ['t'],
    't': ['d'],
    'b': ['p'],
    'p': ['b'],
    'k': ['g'],
    'g': ['k'],
    'm': ['n'],
    'n': ['m'],
}

DIGRAPH_FOLLOWERS = set('aeiouwh')
BATCH_SIZE        = 20
API_TIMEOUT       = 5


def is_short_vowel(word, i):
    ch = word[i]
    if ch not in 'aeiou':
        return False
    before = word[i - 1] if i > 0 else ''
    after  = word[i + 1] if i < len(word) - 1 else ''
    return before not in DIGRAPH_FOLLOWERS and after not in DIGRAPH_FOLLOWERS


def phonetic_code(word):
    return {
        "soundex":   jellyfish.soundex(word),
        "metaphone": jellyfish.metaphone(word),
        "nysiis":    jellyfish.nysiis(word)
    }


def phonetic_distance(code1, code2):
    dists = []
    for key in code1:
        if key in code2:
            dists.append(jellyfish.levenshtein_distance(code1[key], code2[key]))
    return np.mean(dists) if dists else 1.0


def local_candidates(word):
    orig_code  = phonetic_code(word)
    candidates = []
    for i, ch in enumerate(word):
        if i == 0:
            continue
        subs = PHONETIC_SUBS.get(ch, [])
        if not subs:
            continue
        if ch in 'aeiou' and not is_short_vowel(word, i):
            continue
        for sub in subs:
            typo = word[:i] + sub + word[i + 1:]
            if typo == word:
                continue
            try:
                if phonetic_distance(orig_code, phonetic_code(typo)) <= 0.67:
                    candidates.append(typo)
            except Exception:
                continue
    return candidates


async def claude_approves(original, typo):
    prompt = (
        f'Phonetics judge for a word game.\n'
        f'Original: "{original}" | Misspelling: "{typo}"\n'
        f'Do these sound NEARLY IDENTICAL when spoken aloud in American English?\n'
        f'Good: scooter→scooder, bed→bid, tip→dip\n'
        f'Bad: sentence→zentence, fresh→frech\n'
        f'Answer ONLY: YES or NO'
    )
    try:
        fetch_coro = pyfetch(
            "https://api.anthropic.com/v1/messages",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
                "anthropic-dangerous-direct-browser-access": "true",
            },
            body=json.dumps({
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 5,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        response = await asyncio.wait_for(fetch_coro, timeout=API_TIMEOUT)
        data     = await response.json()
        answer   = data["content"][0]["text"].strip().upper()
        approved = answer.startswith("YES")
        print(f"[Claude] {original} → {typo} : {answer}")
        return approved
    except asyncio.TimeoutError:
        print(f"[Claude] TIMEOUT on {original} → {typo}, accepting")
        return True
    except Exception as e:
        print(f"[Claude] ERROR: {e}")
        return False


class TypoGenerator:
    def __init__(self, word_bank_file):
        try:
            text = Path(word_bank_file).read_text(encoding="utf-8")
            all_words = [w.strip().lower() for w in text.replace("\n", " ").split(",") if w.strip()]
        except Exception as e:
            print(f"[TypoGenerator] wordbank error: {e}")
            all_words = ["programming", "backend", "database", "interface",
                         "columbia", "chicago", "wrestling", "software"]

        self.candidate_pool = {}
        for word in all_words:
            cands = local_candidates(word)
            if cands:
                self.candidate_pool[word] = cands

        print(f"[TypoGenerator] {len(self.candidate_pool)} / {len(all_words)} words passed local filter")
        self.approved = []

    async def warm_up(self, on_progress=None):
        """
        Validate BATCH_SIZE pairs via Claude.
        on_progress(current_word, current_typo, api_call_num, max_calls, approved_count, batch_size)
        is called on every single API attempt so the bar moves word-by-word.
        """
        words     = list(self.candidate_pool.keys())
        random.shuffle(words)
        api_calls = 0
        max_calls = BATCH_SIZE * 5  # absolute ceiling — never loops forever

        for word in words:
            if len(self.approved) >= BATCH_SIZE:
                break
            if api_calls >= max_calls:
                print("[warm_up] hit max API call limit")
                break

            candidates = self.candidate_pool[word][:]
            random.shuffle(candidates)

            for typo in candidates[:3]:
                if api_calls >= max_calls:
                    break

                api_calls += 1

                # ── notify before the call so the label updates immediately ──
                if on_progress:
                    on_progress(
                        word, typo,
                        api_calls, max_calls,
                        len(self.approved), BATCH_SIZE
                    )

                approved = await claude_approves(word, typo)

                if approved:
                    self.approved.append((word, typo))
                    print(f"[warm_up] approved {len(self.approved)}/{BATCH_SIZE}: {word} → {typo}")
                    break  # one good pair per word, move on

        # Fill any remaining slots locally if Claude was too strict
        if len(self.approved) < BATCH_SIZE:
            print(f"[warm_up] filling {BATCH_SIZE - len(self.approved)} slots locally")
            for word, cands in self.candidate_pool.items():
                if len(self.approved) >= BATCH_SIZE:
                    break
                pair = (word, cands[0])
                if pair not in self.approved:
                    self.approved.append(pair)
                    if on_progress:
                        on_progress(
                            word, cands[0],
                            api_calls, max_calls,
                            len(self.approved), BATCH_SIZE
                        )

        print(f"[warm_up] done — {len(self.approved)} pairs ready")

    def get_challenge(self):
        """Synchronous pop from pre-approved cache."""
        if not self.approved:
            for word, cands in self.candidate_pool.items():
                self.approved.append((word, cands[0]))
                if len(self.approved) >= BATCH_SIZE:
                    break

        if not self.approved:
            return "backend", "backent"

        pair = random.choice(self.approved)
        self.approved.remove(pair)
        return pair