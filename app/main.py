import streamlit.web.cli as stcli
import sys
import os

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "app/ui.py"]
    sys.exit(stcli.main())