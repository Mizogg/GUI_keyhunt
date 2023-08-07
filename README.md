
# KeyHunt GUI
This is a graphical user interface (GUI) for the KeyHunt program , developed by albertobsd/keyhunt (https://github.com/albertobsd/keyhunt). 

KeyHunt is a tool used to hunt private keys for cryptocurrencies that use the secp256k1 elliptic curve.

![image](https://github.com/Mizogg/GUI_keyhunt/assets/88630056/07a7bf84-2d21-4739-9d74-6a249b0704b3)

##Other Versions available from https://mizogg.co.uk/keyhunt/

## Features
Scans for private keys using different modes (address, xpoint, rmd160, bsgs, vanity).
Supports CPU parallelization with adjustable thread count.
Allows customization of search parameters such as key space, move mode, look, stride, and K value.
Supports different cryptocurrencies (BTC and ETH).
Provides an option to enable endomorphism search (only for address, rmd160, and vanity modes).
Enables vanity address search with a specified prefix.
Matrix screen option for a hacker-style experience (may affect performance).

# Prerequisites
Python 3.x
PyQt6 library
keyhunt command-line tool (make sure it is installed and accessible via the command line)

# Installation and Usage

Clone or download the repository to your local machine.
Install the required dependencies using the following command:
```
pip install PyQt6
```

Run the program using the following command:
```
python GUI_keyhunt.py
```

Configure the desired search parameters and click the "Start scanning" button to initiate the keyhunt process.

The program will display the output in the console window.

Use the provided options to customize the search and control the scanning process.

## Contributing
Contributions to the KeyHunt GUI are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License
This program is licensed under the MIT License. See the LICENSE file for more information.

## Acknowledgements
This GUI is based on the KeyHunt program developed by Alberto albertobsd. For more information about Keyhunt albertobsd@gmail.com &
https://albertobsd.dev/ . For more information about the GUI KeyHunt tool, visit github.com/Mizogg or mizogg.co.uk


