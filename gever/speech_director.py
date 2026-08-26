import re


class GeversSpeechDirector:
    """Prepare existing answer text for energetic spoken delivery.

    This director is deliberately extractive: it may shorten or remove
    generic assistant phrasing, but it does not generate new facts or words.
    """

    MAX_WORDS = 70

    GENERIC_CLOSINGS = (
        r"¿quieres que te ayude con algo más\??",
        r"si necesitas algo más[^.?!]*[.?!]?",
        r"estoy aquí para ayudarte[^.?!]*[.?!]?",
    )

    def direct(self, text):
        if not text:
            return ""

        spoken = re.sub(r"\s+", " ", str(text)).strip()

        for pattern in self.GENERIC_CLOSINGS:
            spoken = re.sub(pattern, "", spoken, flags=re.IGNORECASE)

        spoken = re.sub(r"\s+", " ", spoken).strip(" ,")

        if len(spoken.split()) <= self.MAX_WORDS:
            return spoken

        sentences = re.split(r"(?<=[.!?])\s+", spoken)
        selected = []
        count = 0

        for sentence in sentences:
            words = sentence.split()
            if not words:
                continue
            if selected and count + len(words) > self.MAX_WORDS:
                break
            selected.append(sentence)
            count += len(words)

        if selected:
            return " ".join(selected).strip()

        return " ".join(spoken.split()[: self.MAX_WORDS]).strip()
