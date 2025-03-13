import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.ui import IDUNTUI

def main():
    IDUNTUI().run()

if __name__ == "__main__":
    main()
