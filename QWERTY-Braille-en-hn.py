import streamlit as st

# Unified BrailleAutocorrect class handling both English and Hindi
class BrailleAutocorrect:
    def __init__(self, en_dict, hi_dict):
        self.en_dict = en_dict
        self.hi_dict = hi_dict

    def get_braille_for_word(self, word, lang='en'):
        result = []
        dict_map = self.en_dict if lang == 'en' else self.hi_dict

        for ch in word:
            if ch in dict_map:
                result.append(dict_map[ch])
            else:
                result.append('?')
        return result

    def suggest(self, sequence, max_distance=2, max_suggestions=3):
        # Placeholder suggestion method
        return f"Suggestion: '{''.join(sequence)}' (distance: 0)"

# English Braille dictionary (example)
braille_dict = {
    'a': 'D', 'b': 'DW', 'c': 'DK', 'd': 'DKO', 'e': 'DO',
    'f': 'DKW', 'g': 'DKOW', 'h': 'DOW', 'i': 'KW', 'j': 'KOW',
    'k': 'DQ', 'l': 'DQW', 'm': 'DQK', 'n': 'DQKO', 'o': 'DQO',
    'p': 'DQKW', 'q': 'DQKOW', 'r': 'DQOW', 's': 'KQ', 't': 'KQO',
    'u': 'DPQ', 'v': 'DPQW', 'w': 'KOW', 'x': 'DPQK', 'y': 'DPQKO', 'z': 'DPQO'
}

# Full Hindi Braille dictionary
hindi_dict = {
    'अ': 'D', 'आ': 'DW', 'इ': 'DQ', 'ई': 'DQW', 'उ': 'DK', 'ऊ': 'DKW',
    'ए': 'DQK', 'ऐ': 'DQKW', 'ओ': 'DO', 'औ': 'DWO', 'अं': 'DP', 'अः': 'DWP',
    'क': 'Q', 'ख': 'QW', 'ग': 'QK', 'घ': 'QWK', 'ङ': 'QO', 'च': 'QS',
    'छ': 'QWS', 'ज': 'QKS', 'झ': 'QWKS', 'ञ': 'QOS', 'ट': 'A', 'ठ': 'AW',
    'ड': 'AK', 'ढ': 'AWK', 'ण': 'AO', 'त': 'AS', 'थ': 'AWS', 'द': 'AKS',
    'ध': 'AWKS', 'न': 'AOS', 'प': 'DQ', 'फ': 'DQW', 'ब': 'DQK', 'भ': 'DQWK',
    'म': 'DQO', 'य': 'DK', 'र': 'DKW', 'ल': 'DKQ', 'व': 'DKS', 'श': 'DQKS',
    'ष': 'DQWKS', 'स': 'DQOS', 'ह': 'DKO',
    '्': 'P', 'ा': 'W', 'ि': 'Q', 'ी': 'WQ', 'ु': 'K', 'ू': 'WK',
    'े': 'QK', 'ै': 'WQK', 'ो': 'O', 'ौ': 'WO', 'ं': 'P', 'ः': 'WP',
    '०': 'DKOP', '१': 'D', '२': 'DW', '३': 'DQ', '४': 'DWQ', '५': 'DK',
    '६': 'DWK', '७': 'DQK', '८': 'DWQK', '९': 'DO'
}

autocorrect = BrailleAutocorrect(braille_dict, hindi_dict)

def main():
    st.set_page_config(page_title="Braille Autocorrect", layout="wide")

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
        st.header("English Dictionary")
        st.json(braille_dict)
        st.header("Hindi Dictionary")
        st.json(hindi_dict)

    st.title("🧑‍🦯 Braille Autocorrect System")
    st.markdown("Enter your Braille input below (comma separated characters, e.g., `DK,D,DW`) and select language.")

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
                    if suggestions.startswith("Suggestion:") or suggestions.startswith("सुझाव:"):
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
    lang_choice = st.radio("Choose language:", options=["English", "Hindi"], horizontal=True)

    if st.button("Convert to Braille"):
        lang_code = "hi" if lang_choice == "Hindi" else "en"
        result = autocorrect.get_braille_for_word(word_input, lang=lang_code)
        if result:
            clean_result = []
            for r, c in zip(result, word_input):
                if r == '?' or '⚠' in r:
                    clean_result.append(f"⚠ Unsupported: '{c}'")
                else:
                    clean_result.append(r)
            st.success(f"Braille QWERTY for '{word_input}' ({lang_choice}):")
            st.code(", ".join(clean_result))

            st.markdown("### Braille Pattern")
            cols = st.columns(len(clean_result))
            for i, char in enumerate(clean_result):
                with cols[i]:
                    st.markdown(f"**Character {i+1}**")
                    st.code(char)
        else:
            st.error("Unable to convert some characters. Make sure input is valid.")

if __name__ == "__main__":
    main()