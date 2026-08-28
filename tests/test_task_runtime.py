import pytest

from gever.tasks.models import Capability, TaskStatus
from gever.tasks.runtime import TaskRuntime


class Echo(Capability):
    name = "echo"
    def execute(self, context):
        return context
    def verify(self, result):
        return result == "ok"


def test_runtime_verifies_and_records_lifecycle():
    events = []
    runtime = TaskRuntime(progress_callback=events.append)
    outcome = runtime.run(Echo(), "ok")
    assert outcome.result == "ok"
    assert outcome.verified and outcome.status == TaskStatus.COMPLETED
    assert runtime.last_outcome is outcome
    assert outcome.started_at <= outcome.finished_at
    assert outcome.started_at.tzinfo is not None
    assert [event["status"] for event in events] == ["started", "running", "verifying", "completed"]
    assert {event["task_id"] for event in events} == {outcome.task_id}
    assert runtime.run(Echo(), "ok").task_id != outcome.task_id


def test_failed_verification_does_not_claim_completion():
    outcome = TaskRuntime().run(Echo(), "bad")
    assert outcome.status == TaskStatus.FAILED
    assert not outcome.verified and outcome.error


@pytest.mark.parametrize("phase", ["execute", "verify"])
def test_exceptions_are_contained_and_next_run_can_succeed(phase):
    class Broken(Echo):
        def execute(self, context):
            if phase == "execute":
                raise ValueError("worker failed")
            return super().execute(context)
        def verify(self, result):
            if phase == "verify":
                raise ValueError("verification failed")
            return super().verify(result)
    runtime = TaskRuntime()
    outcome = runtime.run(Broken(), "ok")
    assert outcome.status == TaskStatus.FAILED
    assert not outcome.verified and "failed" in outcome.error
    assert runtime.run(Echo(), "ok").verified


def test_observer_exception_does_not_break_execution():
    def broken_observer(event):
        raise RuntimeError("UI disconnected")
    assert TaskRuntime(progress_callback=broken_observer).run(Echo(), "ok").verified


def test_steps_pass_verified_results_forward():
    class Step(Echo):
        def execute(self, context):
            return context["previous_result"] + 1 if context["previous_result"] is not None else context["input"]
        def verify(self, result):
            return type(result) is int
    outcomes = TaskRuntime().run_steps([Step(), Step()], 10)
    assert [o.result for o in outcomes] == [10, 11]
    assert all(o.verified for o in outcomes)


def test_steps_stop_on_failure_before_running_next_worker():
    class MustNotRun(Echo):
        def execute(self, context):
            raise AssertionError("must not run")
    outcomes = TaskRuntime().run_steps([Echo(), MustNotRun()], "bad")
    assert len(outcomes) == 1
    assert not outcomes[0].verified


def test_progress_snapshot_is_bounded_and_does_not_expose_result():
    runtime = TaskRuntime()
    runtime.run(Echo(), "ok")
    events = runtime.progress_snapshot()
    assert [e["status"] for e in events] == ["started", "running", "verifying", "completed"]
    assert all("result" not in e and "timestamp" in e for e in events)
    events[0]["status"] = "tampered"
    assert runtime.progress_snapshot()[0]["status"] == "started"
    for _ in range(30):
        runtime.run(Echo(), "ok")
    assert len(runtime.progress_snapshot()) == 100
