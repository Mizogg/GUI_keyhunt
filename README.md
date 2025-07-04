# KeyHunter Puzzles GUI

![photo_2025-05-26_16-27-18](https://github.com/user-attachments/assets/c0ad7c30-d4fc-45fc-8c52-8377645bf7dd)

Advanced Bitcoin and Ethereum Key Hunting Tool with both PyQt6 and Tkinter GUI interfaces.

A powerful GUI application for hunting private keys in the Bitcoin blockchain, featuring multi-instance support, theme customization, and advanced range management tools.

### GUI Versions

#### PyQt6 Version (main.py)
- Modern Qt-based interface
- Advanced styling and theming
- Rich text console output
- Multi-window support

#### Tkinter Version (tkmain.py)
- Lightweight native interface
- Multiple theme options
- Custom color schemes
- Cross-platform compatibility

![image](https://github.com/user-attachments/assets/ec1c3a65-ad6b-4544-ab60-8d4cf5576d91)

## Features

### Core Functionality
- Multiple scanning modes: address, bsgs, and rmd160
- Support for both BTC and ETH cryptocurrencies
- Configurable CPU usage per instance
- Advanced range management and splitting
- Progress tracking and file management

### Multi-Instance Support
- Run multiple instances simultaneously (1, 2, 4, 6, or 8 instances)
- Automatic CPU distribution across instances
- Each instance has its own console window for output
- Shared configuration across all instances
- Single start/stop control for all instances

### Theme Support
- Light and dark theme options
- Theme settings persist between sessions
- Consistent styling across all components
- Customizable through the Settings menu

### Range Management Tools
- Hexadecimal range calculator
- Range splitting into equal parts
- Percentage-based range calculations
- Visual range slider (1-256 bits)
- Support for both compressed and uncompressed keys

### File Management
- Input file browser
- Progress file management
- Automatic key found detection
- File format validation

### User Interface
- Modern, responsive design
- Clear console output
- Configurable console threshold
- Copy and clear console functions
- Tooltips with helpful information

## Configuration

### CPU Settings
- Automatic CPU count detection
- CPU allocation based on number of instances
- Example: With 8 CPUs and 8 instances, each instance gets 1 CPU
- Example: With 8 CPUs and 4 instances, each instance can use up to 2 CPUs

### Range Settings
- Default range: 400000000000000000:7FFFFFFFFFFFFFFFFF (71 bits)
- Adjustable through slider or direct input
- Range splitting for multi-instance operation
- Support for custom hex ranges

### Mode Settings
- Address mode: Search for specific addresses
- BSGS mode: Baby-Step Giant-Step algorithm
- RMD160 mode: RIPEMD-160 hash search
- Configurable movement modes (sequential, random, etc.)

## Usage

1. Select the number of instances from the Instances menu
2. Configure your scanning parameters:
   - Choose mode (address, bsgs, rmd160)
   - Select cryptocurrency (BTC/ETH)
   - Set CPU count per instance
   - Configure range and other options
3. Click "Start All Instances" to begin scanning
4. Monitor progress in individual console windows
5. Use "Stop All Instances" to halt scanning

## Theme Customization

Access theme settings through:
1. File menu -> Settings
2. Choose between light and dark themes
3. Settings are saved in config.ini
4. Changes apply immediately

## Requirements

- Python 3.6 or higher
- PyQt6
- Windows/Linux operating system
- Sufficient RAM for selected k-value:
  - 2 GB RAM: -k 128
  - 4 GB RAM: -k 256
  - 8 GB RAM: -k 512
  - 16 GB RAM: -k 1024
  - 32 GB RAM: -k 2048

## Installation

### Requirements
```
Python 3.8 or higher
PyQt6 (for main.py)
tkinter (usually comes with Python)
configparser
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

#### PyQt6 Version
```bash
python main.py
```

#### Tkinter Version
```bash
python tkmain.py
```

## Support

For support and updates:
- Visit: https://mizogg.com
- Visit: https://mizogg.co.uk
- Telegram: https://t.me/TeamHunter_GUI

## Credits

Made by Team Mizogg
© mizogg.com 2018 - 2025
