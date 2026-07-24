import socket

def print_to_zebra(printer_host, printer_port, zpl_data):
    """Sends ZPL code to a networked Zebra printer via raw socket."""
    try:
        # Create a network socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect to the printer
        print(f"Connecting to {printer_host}:{printer_port}...")
        s.connect((printer_host, printer_port))
        
        # Send the ZPL command (must be encoded as bytes)
        s.send(zpl_data.encode('utf-8'))
        
        # Close the connection
        s.close()
        print("Label sent successfully!")
        
    except Exception as e:
        print(f"Failed to print. Error: {e}")

# --- Configuration ---

# Use your printer's hostname or its actual IP address
PRINTER_HOST = "biie-label11" 
PRINTER_PORT = 9100

# --- The Label Design (ZPL Code) ---
# ^XA starts the label, ^XZ ends the label.
# ^FO sets the X/Y coordinates. ^A0N sets the font. ^FD is the text data. ^BC is a barcode.
# ^PQ sets the number of label you want to print, eg. 10
ZPL_CODE = """
^XA
^FO50,50^A0N,50,50^FDSeelig Group^FS
^PQ5
^XZ
"""

# Run the function
print_to_zebra(PRINTER_HOST, PRINTER_PORT, ZPL_CODE)