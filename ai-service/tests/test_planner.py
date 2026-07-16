from app.agent.planner import plan, split_comparison_question


def test_plan_routes_greeting_to_answer_directly() -> None:
    steps = plan("Cześć, kim jesteś?")

    assert len(steps) == 1
    assert steps[0].tool_name == "answer_directly"


def test_plan_routes_plain_question_to_search_documents() -> None:
    steps = plan("What is the maximum operating temperature of the compressor?")

    assert len(steps) == 1
    assert steps[0].tool_name == "search_documents"


def test_plan_routes_comparison_question_to_compare_sections() -> None:
    steps = plan("Porównaj procedurę kalibracji z procedurą serwisowania")

    assert len(steps) == 1
    assert steps[0].tool_name == "compare_sections"


def test_plan_splits_compound_question_into_multiple_search_steps() -> None:
    steps = plan("What is the max torque?; How do I reset the alarm?")

    assert len(steps) == 2
    assert all(step.tool_name == "search_documents" for step in steps)
    assert steps[0].sub_question != steps[1].sub_question


def test_split_comparison_question_returns_both_sides() -> None:
    sides = split_comparison_question("Compare procedure A and procedure B")

    assert sides == ("procedure A", "procedure B")


def test_split_comparison_question_returns_none_when_unsplittable() -> None:
    assert split_comparison_question("Compare") is None
