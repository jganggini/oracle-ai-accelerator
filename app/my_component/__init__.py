import os
import streamlit.components.v1 as components


_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "my_component",
        url="http://localhost:3001",  
    )
else:
    build_dir = os.path.join(os.path.dirname(__file__), "frontend/build")
    _component_func = components.declare_component("my_component", path=build_dir)

def my_component(key=None, **kwargs):
    """
    Wrapper de Python para el componente MyComponent (usa micrófono del navegador).
    """
    return _component_func(key=key, default=None, **kwargs)