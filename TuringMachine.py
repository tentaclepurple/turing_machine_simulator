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
    """Genera la cinta UTM para la suma unaria con la configuración específica"""
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
    st.markdown("""
        <style>
        .stRadio > label {
            font-size: 1.2rem;
            color: #DDD;
        }
        </style>
    """, unsafe_allow_html=True)

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
            
    elif machine_name == "is_palindrome":
        input_str = st.text_input("Enter a binary string:", 
                                 help="Use only 0s and 1s (e.g., 1001)")
        if input_str and not all(c in ["0", "1"] for c in input_str):
            st.error("Please use only 0s and 1s")
            return None, False
        return input_str, False
        
    elif machine_name == "02n":
        input_str = st.text_input("Enter a string of zeros:",
                                 help="Use only 0s (e.g., 0000)")
        if input_str and not all(c == "0" for c in input_str):
            st.error("Please use only 0s")
            return None, False
        return input_str, False
        
    elif machine_name == "0n1n":
        input_str = st.text_input("Enter a string:",
                                 help="Use 0s followed by 1s (e.g., 00111)")
        if input_str and not all(c in ["0", "1"] for c in input_str):
            st.error("Please use only 0s and 1s")
            return None, False
        return input_str, False
    
    return None, False

def main():
    st.set_page_config(
        page_title="Alan Turing's A-Machine",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.markdown("""
        <style>
            .stApp {
                background: #121212;
                color: #DDD;
            }
            section[data-testid="stSidebar"] {
                background: #1E1E1E;
            }
            .stSelectbox > div > div > div {
                background: #2D2D2D;
                color: #DDD;
            }
            .stButton button {
                width: 100%;
                background: #FF4B4B;
                color: white;
            }
            .stSlider span {
                color: #DDD;
            }
            h1, h2, h3, p {
                color: #DDD !important;
            }
            .title-container {
                text-align: center;
                margin: 2rem 0;
            }
            .description {
                text-align: center;
                font-size: 1.2rem;
                margin: 2rem auto;
                max-width: 800px;
            }
            .operator {
                font-size: 2.5rem;
                color: #DDD;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100%;
            }
            .image-container {
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 2rem 0;
            }
            .image-container img {
                max-width: 100%;
                height: auto;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="title-container">
            <h1>Alan Turing's A-Machine</h1>
        </div>
    """, unsafe_allow_html=True)

    # Imagen de Alan Turing
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.image("images/turing.jpg", caption="Alan Turing (1912-1954)", use_container_width=True)
    
    
    st.markdown("""
        <div class="description">
            A Turing machine is a mathematical model of computation that defines an abstract machine that manipulates 
            symbols on a strip of tape according to a table of rules. Despite the model's simplicity, given any computer 
            algorithm, a Turing machine capable of simulating that algorithm's logic can be constructed.
        </div>
    """, unsafe_allow_html=True)

    # Imagen de la máquina de Turing conceptual
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.image("images/turing_machine.jpg", caption="Conceptual Turing Machine", use_container_width=True)
    
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
                     min_value=0.1, 
                     max_value=10.0, 
                     value=1.0, 
                     step=0.1,
                     help="Adjust the speed of the tape animation (1.0 is normal speed, 4.0 is 4x faster)")
    
    input_result = create_machine_input(machine_name)
    
    col1, col2, col3 = st.columns([2,1,2])
    with col2:
        run_button = st.button("Run Machine", use_container_width=True)
    
    if input_result:
        input_str, is_utm = input_result
        if run_button:
            config = load_machine_config(machine_name, is_utm)
            
            if not validate_input(input_str, config.alphabet):
                st.error("Invalid input for selected machine")
                return
                
            if is_utm:
                input_str = get_utm_tape_for_unary_add(input_str)
                
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
                st.markdown("""
                    <div style='text-align: center; margin-top: 2rem;'>
                        <h2 style='color: #4CAF50;'>✓ Machine halted!</h2>
                        <h3>Final result: {}</h3>
                    </div>
                """.format("".join(state.tape)), unsafe_allow_html=True)
            else:
                st.error("Machine encountered an error")

if __name__ == "__main__":
    main()