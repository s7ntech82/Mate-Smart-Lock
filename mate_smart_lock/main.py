import sys
import logging
import signal
from .app import MateSmartLockApp

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Allow SIGINT (Ctrl+C) to close the GTK app cleanly from terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    app = MateSmartLockApp()
    sys.exit(app.run(sys.argv))

if __name__ == '__main__':
    main()
