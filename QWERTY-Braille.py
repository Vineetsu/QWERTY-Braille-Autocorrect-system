import streamlit as st
from typing import List, Tuple, Dict, Optional

class BrailleAutocorrect:
    DOT_MAPPING = {'D': 1, 'W': 2, 'Q': 3, 'K': 4, 'O': 5, 'P': 6}
    REVERSE_DOT_MAPPING = {1: 'D', 2: 'W', 3: 'Q', 4: 'K', 5: 'O', 6: 'P'}

    BRAILLE_UNICODE_MAPPING = {
        'a': [1], 'b': [1, 2], 'c': [1, 4], 'd': [1, 4, 5], 'e': [1, 5],
        'f': [1, 2, 4], 'g': [1, 2, 4, 5], 'h': [1, 2, 5], 'i': [2, 4], 'j': [2, 4, 5],
        'k': [1, 3], 'l': [1, 2, 3], 'm': [1, 3, 4], 'n': [1, 3, 4, 5], 'o': [1, 3, 5],
        'p': [1, 2, 3, 4], 'q': [1, 2, 3, 4, 5], 'r': [1, 2, 3, 5], 's': [2, 3, 4],
        't': [2, 3, 4, 5], 'u': [1, 3, 6], 'v': [1, 2, 3, 6], 'w': [2, 4, 5, 6],
        'x': [1, 3, 4, 6], 'y': [1, 3, 4, 5, 6], 'z': [1, 3, 5, 6]
    }

    class BKTreeNode:
        def __init__(self, word: str, pattern: List[str]):
            self.word = word
            self.pattern = pattern
            self.children = {}

    def __init__(self, dictionary: Optional[Dict[str, List[str]]] = None):
        self.bk_tree = None
        self.dictionary = dictionary or {}
        if dictionary:
            self.build_bk_tree()

    def normalize_braille_char(self, char: str) -> str:
        return ''.join(sorted(char))

    def normalize_word(self, word: List[str]) -> List[str]:
        return [self.normalize_braille_char(ch) for ch in word]

    @staticmethod
    def levenshtein(seq1: List[str], seq2: List[str]) -> int:
        m, n = len(seq1), len(seq2)
        dp = [[0]*(n+1) for _ in range(m+1)]

        for i in range(m+1):
            dp[i][0] = i
        for j in range(n+1):
            dp[0][j] = j

        for i in range(1, m+1):
            for j in range(1, n+1):
                cost = 0 if seq1[i-1] == seq2[j-1] else 1
                dp[i][j] = min(
                    dp[i-1][j] + 1,
                    dp[i][j-1] + 1,
                    dp[i-1][j-1] + cost
                )
        return dp[m][n]

    def build_bk_tree(self):
        if not self.dictionary:
            return

        first_word = next(iter(self.dictionary))
        self.bk_tree = self.BKTreeNode(
            first_word,
            self.normalize_word(self.dictionary[first_word])
        )

        for word, pattern in self.dictionary.items():
            if word != first_word:
                self._insert_to_bk_tree(word, self.normalize_word(pattern))

    def _insert_to_bk_tree(self, word: str, pattern: List[str]):
        node = self.BKTreeNode(word, pattern)
        current = self.bk_tree
        while True:
            dist = self.levenshtein(pattern, current.pattern)
            if dist in current.children:
                current = current.children[dist]
            else:
                current.children[dist] = node
                break

    def _search_bk_tree(self, pattern: List[str], max_dist: int) -> List[Tuple[str, int]]:
        results = []

        def _search(node):
            dist = self.levenshtein(pattern, node.pattern)
            if dist <= max_dist:
                results.append((node.word, dist))
            for d in range(max(0, dist - max_dist), dist + max_dist + 1):
                if d in node.children:
                    _search(node.children[d])

        if self.bk_tree:
            _search(self.bk_tree)
        return sorted(results, key=lambda x: x[1])

    def suggest(self, user_input: List[str], max_distance: int = 2, max_suggestions: int = 3) -> str:
        if not self.dictionary:
            return "Dictionary is empty. No suggestions available."

        normalized_input = self.normalize_word(user_input)
        suggestions = self._search_bk_tree(normalized_input, max_distance)

        if not suggestions:
            return "No suggestions found."

        top_suggestions = suggestions[:max_suggestions]
        if len(top_suggestions) == 1:
            return f"Suggestion: '{top_suggestions[0][0]}' (distance: {top_suggestions[0][1]})"

        suggestions_str = ", ".join(f"'{s[0]}' (distance: {s[1]})" for s in top_suggestions)
        return f"Top suggestions: {suggestions_str}"

    def get_braille_for_word(self, word: str) -> Optional[List[str]]:
        result = []
        for ch in word.lower():
            if ch in self.BRAILLE_UNICODE_MAPPING:
                dots = self.BRAILLE_UNICODE_MAPPING[ch]
                keys = ''.join(sorted([self.REVERSE_DOT_MAPPING[d] for d in dots]))
                result.append(keys)
            else:
                result.append('?')
        return result

braille_dict = {
    "cat": ["DK", "D", "KOQW"],
    "can": ["DK", "D", "DKOQ"],
    "dog": ["DKO", "DOQ", "DKOW"],
    "cap": ["DK", "D", "DKQW"],
    "cot": ["DK", "DOQ", "KOQW"],
    "dot": ["DKO", "DOQ", "KOQW"],
    "hello": ["DOW", "DO", "DQW", "DQW", "DOQ"],
    "world": ["KOPW", "DOQ", "DOQW", "DQW", "DKO"],
    "test": ["KOQW", "DO", "KQW", "KOQW"],
    "python": ["DKQW", "DKOPQ"," KOQW", "DOW", "DOQ", "DKOQ"],
    "example": ["DO", "DKPQ", "D", "DKQ", "DKQW", "DQW", "DO"],
    "braille": ["DW", "DOQW", "D", "KW", "DQW", "DQW", "DO"]
}




def main():
    st.set_page_config(page_title="Braille Autocorrect", layout="wide")
    autocorrect = BrailleAutocorrect(braille_dict)

    with st.sidebar:
        st.header("About")
        st.markdown("""
        This system helps correct Braille input typed using QWERTY keys:

        | Braille Dot | QWERTY Key |
        |-------------|------------|
        | Dot 1       | D          |
        | Dot 2       | W          |
        | Dot 3       | Q          |
        | Dot 4       | K          |
        | Dot 5       | O          |
        | Dot 6       | P          |
        """)
        st.header("Dictionary")
        st.json(braille_dict)

    st.title("🧑‍🦯 Braille Autocorrect System")
    st.markdown("Enter your Braille input below (comma separated characters, e.g., `DK,D,DW`)")

    if "user_input" not in st.session_state:
        st.session_state.user_input = "DK,D,DW"

    col1, col2 = st.columns([3, 1])
    with col1:
        user_input = st.text_input("Braille Input:", st.session_state.user_input, key="input_field")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Clear Input"):
            st.session_state.user_input = ""
            st.rerun()

    with st.expander("Advanced Options"):
        col1, col2 = st.columns(2)
        with col1:
            max_distance = st.slider("Maximum edit distance:", 1, 5, 2)
        with col2:
            max_suggestions = st.slider("Maximum suggestions:", 1, 10, 3)

    if st.button("Get Suggestions", type="primary"):
        with st.spinner("Searching for suggestions..."):
            try:
                input_sequence = [part.strip().upper() for part in user_input.split(",") if part.strip()]
                if not input_sequence:
                    st.warning("Please enter at least one Braille character")
                else:
                    suggestions = autocorrect.suggest(input_sequence, max_distance, max_suggestions)
                    st.subheader("Results")
                    if suggestions.startswith("Suggestion:"):
                        st.success(suggestions)
                    else:
                        st.info(suggestions)

                    st.markdown("### Input Visualization")
                    cols = st.columns(len(input_sequence))
                    for i, char in enumerate(input_sequence):
                        with cols[i]:
                            st.markdown(f"**Character {i+1}**")
                            st.code(char)
            except Exception as e:
                st.error(f"Error processing input: {str(e)}")

    st.markdown("---")
    st.subheader("Try these examples:")
    examples = st.columns(3)
    def update_example(example_text):
        st.session_state.user_input = example_text
        st.rerun()
    examples[0].button("cat → DK,D,DWO", on_click=lambda: update_example("DK,D,DWO"))
    examples[1].button("dog → DK,O,QK", on_click=lambda: update_example("DK,O,QK"))
    examples[2].button("hello → DW,D,Q,Q,O", on_click=lambda: update_example("DW,D,Q,Q,O"))

    st.markdown("---")
    st.header("🔁 Reverse Lookup: Word to QWERTY Braille")
    word_input = st.text_input("Enter any word:", "hello")
    if st.button("Convert to Braille"):
        result = autocorrect.get_braille_for_word(word_input)
        if result:
            st.success(f"Braille QWERTY for '{word_input}':")
            st.code(", ".join(result))
        else:
            st.error("Unable to convert some characters.")

if __name__ == "__main__":
    main()