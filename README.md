# PicoGPT

A ChatGPT client for PicoCalc running on Picoware firmware. This app allows you to interact with OpenAI's GPT models directly from your PicoCalc device.

## Features

- 🤖 Chat with OpenAI GPT models (currently using `gpt-4o-mini`)
- 📱 Native Picoware GUI integration
- 📜 Scrollable error display for debugging
- 🔄 Conversation history management
- 📝 Detailed error logging to `/error_log.txt`

## Setup

1. **Install on PicoCalc**: Copy `PicoGPT.py` to your PicoCalc's `/apps/` directory

2. **Configure API Key**: 
   - Open `PicoGPT.py` in a text editor
   - Find the line: `OPENAI_API_KEY = "YOUR_API_KEY_HERE"`
   - Replace `YOUR_API_KEY_HERE` with your actual OpenAI API key

3. **WiFi Connection**: Ensure your PicoCalc is connected to WiFi before using the app

## Usage

1. Launch the app from the Applications menu on your PicoCalc
2. Press **CENTER** to ask a question
3. The app will send your question to OpenAI and display the response
4. Press **LEFT** to go back or exit

## Error Handling

If an error occurs:
- The full error message is displayed in a scrollable view
- Use **UP/DOWN** buttons to scroll through long error messages
- Press **LEFT** to exit the error display
- Detailed logs are saved to `/error_log.txt` on the device

## Development

### Test Scripts

- `test_api.py`: Test OpenAI API calls locally on your Mac
- `test_urequests.py`: Simulate `urequests` behavior for testing

## Requirements

- PicoCalc device with Picoware firmware
- WiFi connection
- OpenAI API key with credits

## License

MIT

