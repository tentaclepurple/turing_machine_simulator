import streamlit as st
import json
import time
from PIL import Image
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple


@dataclass
class TuringState:
    tape: List[str]
    head: int
    state: str


@dataclass
class TuringConfig:
    name: str
    alphabet: List[str]
    blank: str
    states: List[str]
    initial: str
    finals: List[str]
    transitions: Dict[str, List[Dict[str, str]]]


def load_machine_config(name: str, is_utm: bool = False) -> TuringConfig:
    filename = f"utm_{name}.json" if is_utm else f"{name}.json"
    try:
        with open(f"machines/{filename}", "r") as f:
            data = json.load(f)
            return TuringConfig(
                name=data["name"],
                alphabet=data["alphabet"],
                blank=data["blank"],
                states=data["states"],
                initial=data["initial"],
                finals=data["finals"],
                transitions=data["transitions"]
            )
    except FileNotFoundError:
        st.error(f"Machine configuration file '{filename}' not found.")
        return None


def validate_input(input_str: str, alphabet: List[str]) -> bool:
    if not input_str or not alphabet:
        return False
    return all(c in alphabet for c in input_str)


def step_machine(config: TuringConfig, state: TuringState) -> Optional[TuringState]:
    if state.head < 0:
        state.tape.insert(0, config.blank)
        state.head = 0
    elif state.head >= len(state.tape):
        state.tape.append(config.blank)

    current_symbol = state.tape[state.head]
    transitions = config.transitions.get(state.state, [])
    transition = next((t for t in transitions if t["read"] == current_symbol), None)

    if not transition:
        return None

    state.tape[state.head] = transition["write"]
    state.state = transition["to_state"]
    state.head += 1 if transition["action"] == "RIGHT" else -1

    return state


def get_utm_tape_for_unary_add(input_str: str) -> str:
    utm_prefix = "1.+= . ABC aA1B.> bB1B1> bB+B1> bB=C.> #"
    utm_suffix = " @"
    return f"{utm_prefix}{input_str}{utm_suffix}"


def render_tape(tape: List[str], head: int, state: str) -> str:
    css = """
    <style>
        .turing-tape {
            font-family: monospace;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            gap: 0.5rem;
            margin: 2rem 0;
            background: #1E1E1E;
            padding: 2rem;
            border-radius: 10px;
        }
        .tape-cells {
            display: flex;
            border: 2px solid #444;
            border-radius: 5px;
            background: #2D2D2D;
            padding: 5px;
            overflow-x: auto;
            max-width: 90vw;
        }
        .cell {
            min-width: 60px;
            height: 60px;
            border-right: 1px solid #444;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: bold;
            color: #DDD;
            position: relative;
            transition: background-color 0.3s ease;
            padding: 0 10px;
        }
        .cell:last-child {
            border-right: none;
        }
        .cell.current {
            background: #404040;
        }
        .state-display {
            font-size: 24px;
            color: #DDD;
            margin-bottom: 1rem;
            padding: 10px 20px;
            background: #2D2D2D;
            border-radius: 5px;
            border: 1px solid #444;
        }
    </style>
    """

    cells_html = ""
    for i, symbol in enumerate(tape):
        current_class = "current" if i == head else ""
        cells_html += f'<div class="cell {current_class}">{symbol}</div>'

    tape_html = f"""
    {css}
    <div class="turing-tape">
        <div class="state-display">Current State: {state}</div>
        <div class="tape-cells">
            {cells_html}
        </div>
    </div>
    """

    return tape_html


def create_machine_input(machine_name: str) -> Tuple[Optional[str], bool]:
    is_utm = False
    if machine_name == "unary_add":
        is_utm = st.radio(
            "Machine Type",
            ["Standard", "Universal (UTM)"],
            help="Choose between standard Turing Machine or Universal Turing Machine"
        ) == "Universal (UTM)"

    if machine_name in ["unary_add", "unary_sub"]:
        num1 = st.text_input("First number (use only '1's):", key="num1")
        num2 = st.text_input("Second number (use only '1's):", key="num2")

        if num1 and num2:
            if not all(c == "1" for c in num1 + num2):
                st.error("Please use only '1's for unary numbers.")
                return None, False
            input_str = f"{num1}{'+' if machine_name == 'unary_add' else '-'}{num2}="
            return input_str, is_utm

    return None, False


def main():
    st.set_page_config(
        page_title="Alan Turing's A-Machine",
        page_icon="🤖",
        layout="wide"
    )

    st.title("Alan Turing's A-Machine")

    machine_name = st.selectbox(
        "Select Turing Machine:",
        ["unary_add", "unary_sub"]
    )
    speed = st.slider("Animation Speed", 0.1, 10.0, 1.0)

    input_result = create_machine_input(machine_name)

    if input_result:
        input_str, is_utm = input_result
        config = load_machine_config(machine_name, is_utm)

        if not config:
            return

        if not validate_input(input_str, config.alphabet):
            st.error("Invalid input for selected machine.")
            return

        state = TuringState(
            tape=list(input_str),
            head=0,
            state=config.initial
        )

        vis_placeholder = st.empty()
        while state and state.state not in config.finals:
            vis_placeholder.markdown(
                render_tape(state.tape, state.head, state.state),
                unsafe_allow_html=True
            )
            state = step_machine(config, state)
            time.sleep(1.0 / speed)

        if state:
            vis_placeholder.markdown(
                render_tape(state.tape, state.head, state.state),
                unsafe_allow_html=True
            )
            st.success("✓ Machine halted!")
        else:
            st.error("Machine encountered an error.")


if __name__ == "__main__":
    main()
