import streamlit as st
import json
import time
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
                    {'+' if machine_name == 'unary_add' else '-'}
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
            input_str = f"{num1}{'+' if machine_name == 'unary_add' else '-'}{num2}="
            return input_str, is_utm
            
    return None, False

def main():
    st.set_page_config(
        page_title="Alan Turing's A-Machine",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.title("Alan Turing's A-Machine")
    st.image("images/turing.jpg", caption="Alan Turing (1912-1954)", use_column_width=True)
    
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
    
    speed = st.slider("Animation Speed", 0.1, 10.0, step=0.1, help="Adjust the simulation speed")

    # Input generation
    input_str, is_utm = create_machine_input(machine_name)
    if input_str:
        st.write(f"Input string: {input_str}")
