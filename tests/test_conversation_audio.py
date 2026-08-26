import unittest

from gever.conversation_audio import ConversationAudioState


class ConversationAudioStateTests(unittest.TestCase):
    def test_begin_and_finish_track_microphone_ownership(self):
        state = ConversationAudioState()
        self.assertTrue(state.begin())
        self.assertTrue(state.is_active)
        state.finish()
        self.assertFalse(state.is_active)

    def test_cancel_blocks_next_capture_until_reset(self):
        state = ConversationAudioState()
        state.cancel()
        self.assertFalse(state.begin())
        state.reset()
        self.assertTrue(state.begin())

    def test_cancel_marks_active_capture_for_discard(self):
        state = ConversationAudioState()
        self.assertTrue(state.begin())
        state.cancel()
        self.assertTrue(state.cancel_requested)
        state.finish()
        self.assertFalse(state.is_active)


if __name__ == "__main__":
    unittest.main()
