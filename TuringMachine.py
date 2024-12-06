import streamlit as st
import json
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

def load_machine_config(name: str) -> Optional[TuringConfig]:
    """Carga la configuración de la máquina desde un archivo JSON."""
    try:
        with open(f"machines/{name}.json", "r") as f:
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
        st.error(f"No se encontró la configuración para la máquina '{name}'.")
        return None

def validate_input(input_str: str, alphabet: List[str]) -> bool:
    """Valida que todos los caracteres de la entrada estén en el alfabeto permitido."""
    return all(c in alphabet for c in input_str)

def step_machine(config: TuringConfig, state: TuringState) -> Optional[TuringState]:
    """Ejecuta un paso de la máquina de Turing."""
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

def run_machine(config: TuringConfig, input_str: str, speed: float):
    """Simula la ejecución de la máquina de Turing paso a paso."""
    tape = list(input_str)
    state = TuringState(tape=tape, head=0, state=config.initial)
    
    st.write("### Estado inicial")
    st.write(f"**Cinta**: {''.join(state.tape)}")
    st.write(f"**Cabezal**: {state.head}")
    st.write(f"**Estado**: {state.state}")
    
    while state.state not in config.finals:
        time.sleep(speed)
        state = step_machine(config, state)
        if state is None:
            st.error("No se encontró transición válida. La máquina se detuvo.")
            return
        
        st.write(f"**Cinta**: {''.join(state.tape)}")
        st.write(f"**Cabezal**: {state.head}")
        st.write(f"**Estado**: {state.state}")
    
    st.success("¡La máquina ha terminado con éxito!")
    st.write(f"**Resultado final**: {''.join(state.tape)}")

def main():
    st.set_page_config(
        page_title="Máquina de Turing",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("Simulador de Máquina de Turing")
    
    machine_name = st.selectbox(
        "Selecciona la máquina:",
        ["unary_add", "unary_sub", "is_palindrome"],
        format_func=lambda x: {
            "unary_add": "Suma Unaria",
            "unary_sub": "Resta Unaria",
            "is_palindrome": "Comprobador de Palíndromos"
        }[x]
    )
    
    config = load_machine_config(machine_name)
    if not config:
        return
    
    input_str = st.text_input(
        "Introduce la entrada:",
        help="Debe coincidir con el alfabeto de la máquina."
    )
    if input_str and not validate_input(input_str, config.alphabet):
        st.error("La entrada contiene caracteres no válidos para esta máquina.")
        return
    
    speed = st.slider("Velocidad de animación:", 0.1, 2.0, 0.5)
    
    if st.button("Ejecutar Máquina"):
        if input_str:
            run_machine(config, input_str, speed)
        else:
            st.error("Por favor, introduce una entrada válida.")

if __name__ == "__main__":
    main()
