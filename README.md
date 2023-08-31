# pyqt-text-generation-inference-gui
GUI version of text-generation-inference

My computer is not good enough to test this out (because my good old pal OutOfMemoryError!), so how about you try this?

## Requirements
* PyQt5>=5.14 (for GUI)
* ansi2html (for showing colorful console)
* text_generation (for using text-generation-inference)

## How to Use

Before using this, you need to install Docker Desktop and run it. This will not work if you don't have it

1. clone this!
2. pip install -r requirements.txt
3. cd src
4. python main.py

Set the model that you want to use in main.py

![image](https://github.com/yjg30737/pyqt-text-generation-inference-gui/assets/55078043/9f9d8701-c1e5-41f1-853e-1c904ef98592)

#### You need Access Tokens if you want to test llama2, falcon, etc. 

## Result

![image](https://github.com/yjg30737/pyqt-text-generation-inference-gui/assets/55078043/58bd221a-bd7b-4c09-b170-ac694538a776)

![image](https://github.com/yjg30737/pyqt-text-generation-inference-gui/assets/55078043/cbd168bd-7e7b-446f-8e16-41530b3223c4)

I'm using bigscience/bloom-560m in this example. 

## TroubleShooting
### Server is not running?

This error indicates that 127.0.0.1:8080 is not running. Run the docker-desktop, 

search the port with

netstat -ano | findstr 8080 

and remove any service & software which port 8080 is allocated.

## Note

This project is not complete, but i probably rarely touch this one, so i need collaborator :)

If you want to collaborate feel free to join. I want to work with a team, please.
