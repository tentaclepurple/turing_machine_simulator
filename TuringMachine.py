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
        st.error(f"Configuration file '{filename}' not found.")
        st.stop()

def validate_input(input_str: str, alphabet: List[str]) -> bool:
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
    st.markdown("""<style>.stRadio > label {font-size: 1.2rem; color: #DDD;}</style>""", unsafe_allow_html=True)

    is_utm = False
    if machine_name == "unary_add":
        is_utm = st.radio(
            "Machine Type",
            ["Standard", "Universal (UTM)"],
            help="Choose between standard Turing Machine or Universal Turing Machine"
        ) == "Universal (UTM)"

    if machine_name in ["unary_add", "unary_sub"]:
        col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
        with col1:
            num1 = st.text_input("First number:", key="num1", 
                                help="Use only 1's (e.g., 111 for 3)")
        with col2:
            st.markdown(f"""
                <div class="operator">
                    {'+'if machine_name == 'unary_add' else '-'}
                </div>
            """, unsafe_allow_html=True)
        with col3:
            num2 = st.text_input("Second number:", key="num2",
                                help="Use only 1's (e.g., 11 for 2)")
        with col4:
            st.markdown('<div class="operator">=</div>', unsafe_allow_html=True)
        
        if num1 and num2:
            if not all(c == "1" for c in num1 + num2):
                st.error("Please use only '1's for unary numbers")
                return None, False
            input_str = f"{num1}{'+'if machine_name == 'unary_add' else '-'}{num2}="
            return input_str, is_utm
            
    return None, False

def main():
    st.set_page_config(
        page_title="Alan Turing's A-Machine",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.markdown("""
        <div class="title-container">
            <h1>Alan Turing's A-Machine</h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.image("images/turing.jpg", caption="Alan Turing (1912-1954)", use_container_width=True)
    
    machine_name = st.selectbox(
        "Select Turing Machine:",
        ["unary_add", "unary_sub", "is_palindrome", "02n", "0n1n"],
        format_func=lambda x: {
            "unary_add": "Unary Addition",
            "unary_sub": "Unary Subtraction",
            "is_palindrome": "Palindrome Checker",
            "02n": "Even Number of Zeros",
            "0n1n": "Equal Number of Zeros and Ones"
        }[x]
    )
    
    speed = st.slider("Animation Speed", 
                     min_value=0
