import unittest

from gever.session import SessionController, SessionState


class FakeSentinel:
    def __init__(self, events):
        self.events = events
        self.running = False

    def start(self, on_activate):
        self.events.append("sentinel:start")
        self.running = True
        self.on_activate = on_activate

    def stop(self):
        self.events.append("sentinel:stop")
        self.running = False


class FakeConversation:
    def __init__(self, events):
        self.events = events
        self.active = False
        self.cancelled = 0

    @property
    def is_active(self):
        return self.active

    def cancel(self):
        self.events.append("conversation:cancel")
        self.cancelled += 1
        self.active = False


class SessionControllerTests(unittest.TestCase):
    def make_controller(self):
        events = []
        sentinel = FakeSentinel(events)
        conversation = FakeConversation(events)
        return events, sentinel, conversation, SessionController(sentinel, conversation)

    def test_startup_is_sentinel_only(self):
        _, sentinel, conversation, controller = self.make_controller()
        controller.start()
        self.assertEqual(controller.state, SessionState.SENTINEL)
        self.assertTrue(sentinel.running)
        self.assertFalse(conversation.is_active)

    def test_open_session_stops_sentinel_first(self):
        events, sentinel, _, controller = self.make_controller()
        controller.start()
        events.clear()
        controller.open_session("clap")
        self.assertEqual(events[0], "sentinel:stop")
        self.assertFalse(sentinel.running)
        self.assertEqual(controller.state, SessionState.SESSION)
        self.assertEqual(controller.last_trigger, "clap")

    def test_orion_opens_session_without_clap(self):
        _, sentinel, _, controller = self.make_controller()
        controller.start()
        controller.open_session("orion")
        self.assertFalse(sentinel.running)
        self.assertEqual(controller.state, SessionState.SESSION)
        self.assertEqual(controller.last_trigger, "orion")

    def test_close_session_cancels_conversation_before_sentinel(self):
        events, sentinel, conversation, controller = self.make_controller()
        controller.start()
        controller.open_session("orion")
        conversation.active = True
        events.clear()
        controller.close_session("voice")
        self.assertEqual(events[:2], ["conversation:cancel", "sentinel:start"])
        self.assertEqual(conversation.cancelled, 1)
        self.assertTrue(sentinel.running)
        self.assertEqual(controller.state, SessionState.SENTINEL)

    def test_stop_releases_both_audio_paths(self):
        events, sentinel, conversation, controller = self.make_controller()
        controller.start()
        controller.open_session("clap")
        conversation.active = True
        events.clear()
        controller.stop()
        self.assertIn("conversation:cancel", events)
        self.assertIn("sentinel:stop", events)
        self.assertFalse(sentinel.running)
        self.assertFalse(conversation.is_active)
        self.assertEqual(controller.state, SessionState.STOPPED)


if __name__ == "__main__":
    unittest.main()
