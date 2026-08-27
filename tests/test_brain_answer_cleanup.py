from gever.brain import GeversBrain


def test_clean_answer_removes_think_block_and_keeps_final_answer():
    raw = "<think>The user asked for a summary. We need to answer in Spanish.</think>Claro. Encontré tres oportunidades."
    assert GeversBrain._clean_answer(raw) == "Claro. Encontré tres oportunidades."


def test_clean_answer_removes_common_english_reasoning_preamble():
    raw = "The user asked me to explain the result. We need to respond in Spanish.\n\nEncontré tres oportunidades válidas."
    assert GeversBrain._clean_answer(raw) == "Encontré tres oportunidades válidas."


def test_clean_answer_removes_multiline_reasoning_without_blank_separator():
    raw = "Okay, the user just said ahora dime which means now tell me in Spanish. Let me check the context.\nLooking at the system prompt, we need to answer the user directly.\nThe user wants a concise answer.\nClaro. Esto es lo que encontré."
    assert GeversBrain._clean_answer(raw) == "Claro. Esto es lo que encontré."


def test_clean_answer_does_not_remove_normal_user_facing_english_content():
    raw = "The estimate is ready and I can translate it to Spanish."
    assert GeversBrain._clean_answer(raw) == raw
