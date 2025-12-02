# PicoGPT.py
# ChatGPT client for PicoCalc using gpt-5.1 model
# This file should be placed directly in /apps/ folder

import ujson as json
import urequests as requests

# Ensure ujson dumps properly
def json_dumps_safe(obj):
    """Safely dump JSON for urequests"""
    try:
        return json.dumps(obj)
    except Exception as e:
        log_error(f"JSON DUMP ERROR: {e}")
        raise

# API Configuration
OPENAI_API_KEY = "YOUR_API_KEY_HERE"  # Replace with your OpenAI API key
OPENAI_MODEL = "gpt-4o-mini"  # Using standard model that works
API_URL = "https://api.openai.com/v1/chat/completions"  # Standard endpoint

HEADERS = {
    "Authorization": "Bearer " + OPENAI_API_KEY,
    "Content-Type": "application/json; charset=utf-8",
}

SYSTEM_INSTRUCTION = (
    "You are a helpful assistant running on a tiny calculator. "
    "Keep answers short (1–3 sentences) and avoid long lists."
)

# Global state variables
_chat_alert = None
_chat_history = []
_chat_user_input = ""
_chat_waiting_for_input = False
_chat_request_in_progress = False
_chat_displaying_result = False
_chat_last_reply = ""
_chat_input_text = ""  # Current text being entered
_chat_error_displaying = False  # Flag for error display mode
_chat_error_lines = []  # Lines of error text
_chat_error_scroll_offset = 0  # Current scroll position


def __reset_chat_state() -> None:
    """Reset chat state flags"""
    global _chat_waiting_for_input, _chat_request_in_progress, _chat_displaying_result
    global _chat_error_displaying, _chat_error_lines, _chat_error_scroll_offset
    _chat_waiting_for_input = False
    _chat_request_in_progress = False
    _chat_displaying_result = False
    _chat_error_displaying = False
    _chat_error_lines = []
    _chat_error_scroll_offset = 0


def log_error(error_msg):
    """Log error to file for debugging"""
    try:
        with open("/error_log.txt", "a") as f:
            from utime import localtime
            try:
                t = localtime()
                timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                    t[0], t[1], t[2], t[3], t[4], t[5]
                )
            except:
                timestamp = "unknown"
            f.write(f"[{timestamp}] {error_msg}\n")
    except:
        pass  # Silently fail if logging doesn't work


def ask_model(user_text, history=None):
    """
    Send a prompt to the OpenAI API and return the reply.
    Uses standard /v1/chat/completions endpoint.
    """
    # Build messages array (standard format)
    messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    
    # Add recent conversation history if provided
    if history and isinstance(history, list) and len(history) > 0:
        recent = history[-6:] if len(history) > 6 else history
        messages.extend(recent)
    
    # Add current user message
    messages.append({"role": "user", "content": user_text})
    
    # Construct payload (standard chat/completions format)
    payload = {
        "model": OPENAI_MODEL,
        "messages": messages
    }
    
    # Log the request details
    try:
        log_error(f"REQUEST: URL={API_URL}, Model={OPENAI_MODEL}")
        log_error(f"REQUEST: Payload={json.dumps(payload)}")
    except:
        pass
    
    # Send POST request
    resp = None
    try:
        # urequests doesn't support json= parameter, need to use data= with json.dumps
        # ujson.dumps returns a string
        payload_str = json_dumps_safe(payload)
        
        # Log the actual JSON string to verify it's valid
        log_error(f"REQUEST: Payload JSON string (len={len(payload_str)})")
        log_error(f"REQUEST: First 300 chars: {payload_str[:300]}")
        
        # Verify it's valid JSON by trying to parse it back
        try:
            test_parse = json.loads(payload_str)
            log_error(f"REQUEST: JSON validation passed")
        except Exception as parse_err:
            log_error(f"REQUEST: JSON validation FAILED: {parse_err}")
            log_error(f"REQUEST: Invalid JSON string: {payload_str}")
            raise RuntimeError(f"Invalid JSON payload: {parse_err}")
        
        # urequests.post() with data= parameter
        # Some versions of urequests need bytes, not string
        # Convert to bytes for proper encoding
        if isinstance(payload_str, str):
            payload_bytes = payload_str.encode('utf-8')
        else:
            payload_bytes = payload_str
        
        log_error(f"REQUEST: Sending as bytes (len={len(payload_bytes)})")
        
        # Send the request with bytes
        resp = requests.post(API_URL, headers=HEADERS, data=payload_bytes)
        
        log_error(f"RESPONSE: Status={resp.status_code}")
        
        # Check status code
        if resp.status_code != 200:
            error_text = resp.text if hasattr(resp, 'text') else str(resp.status_code)
            error_msg = "HTTP {}: {}".format(resp.status_code, error_text)
            log_error(f"ERROR: {error_msg}")
            log_error(f"ERROR: Response text={error_text}")
            raise RuntimeError(error_msg)
        
        # Parse JSON response
        try:
            data = resp.json()
            log_error(f"RESPONSE: Successfully parsed JSON")
        except Exception as e:
            log_error(f"ERROR: Failed to parse JSON: {e}")
            log_error(f"ERROR: Response text={resp.text}")
            raise
        
        # Extract answer text (standard chat/completions format)
        if "choices" in data and len(data["choices"]) > 0:
            reply = data["choices"][0]["message"]["content"]
            log_error(f"SUCCESS: Got reply (len={len(reply)})")
        else:
            error_msg = "No 'choices' field in response"
            log_error(f"ERROR: {error_msg}")
            log_error(f"ERROR: Response data={json.dumps(data)}")
            raise RuntimeError(error_msg)
        
        # Update history if provided
        if history is not None and isinstance(history, list):
            history.append({"role": "user", "content": user_text})
            history.append({"role": "assistant", "content": reply})
            # Trim history to keep only last 8 messages (4 exchanges)
            if len(history) > 8:
                history[:] = history[-8:]
        
        return reply
        
    except Exception as e:
        # Log any exception
        log_error(f"EXCEPTION: {type(e).__name__}: {str(e)}")
        import sys
        try:
            import uio
            import uio as io
            error_details = str(sys.exc_info())
            log_error(f"EXCEPTION DETAILS: {error_details}")
        except:
            pass
        raise
    finally:
        # Always close the response
        if resp is not None:
            resp.close()


def start(view_manager) -> bool:
    """Start the app"""
    global _chat_alert
    
    try:
        if _chat_alert:
            del _chat_alert
            _chat_alert = None
        
        draw = view_manager.get_draw()
        wifi = view_manager.get_wifi()
        
        # Check if WiFi is available
        if not wifi:
            from picoware.gui.alert import Alert
            from time import sleep
            
            _chat_alert = Alert(
                draw,
                "WiFi not available..",
                view_manager.get_foreground_color(),
                view_manager.get_background_color(),
            )
            _chat_alert.draw("Error")
            sleep(2)
            return False
        
        # Check if WiFi is connected
        if not wifi.is_connected():
            from picoware.applications.wifi.utils import connect_to_saved_wifi
            from picoware.gui.alert import Alert
            from time import sleep
            
            _chat_alert = Alert(
                draw,
                "WiFi not connected yet",
                view_manager.get_foreground_color(),
                view_manager.get_background_color(),
            )
            _chat_alert.draw("Error")
            sleep(2)
            connect_to_saved_wifi(view_manager)
            return False
        
        from picoware.system.vector import Vector
        
        # Reset state for fresh start
        __reset_chat_state()
        global _chat_history
        _chat_history = []
        
        # Show welcome screen
        draw.clear(Vector(0, 0), draw.size, view_manager.get_background_color())
        draw.text(Vector(5, 5), "PicoGPT Ready!")
        draw.text(Vector(5, 20), "Press CENTER to ask")
        draw.text(Vector(5, 35), "Press LEFT to go back")
        draw.swap()
        
        return True
    except Exception as e:
        # If there's an error, try to show it
        try:
            from picoware.gui.alert import Alert
            from time import sleep
            draw = view_manager.get_draw()
            error_msg = f"Start error: {str(e)[:30]}"
            _chat_alert = Alert(
                draw,
                error_msg,
                view_manager.get_foreground_color(),
                view_manager.get_background_color(),
            )
            _chat_alert.draw("Error")
            sleep(3)
        except:
            pass
        return False


def run(view_manager) -> None:
    """Run the app"""
    from picoware.system.vector import Vector
    from picoware.system.buttons import (
        BUTTON_BACK,
        BUTTON_LEFT,
        BUTTON_RIGHT,
        BUTTON_CENTER,
        BUTTON_UP,
        BUTTON_DOWN,
    )
    
    global _chat_alert, _chat_history
    global _chat_user_input, _chat_waiting_for_input, _chat_input_text
    global _chat_request_in_progress, _chat_displaying_result, _chat_last_reply
    global _chat_error_displaying, _chat_error_lines, _chat_error_scroll_offset
    
    input_manager = view_manager.get_input_manager()
    button = input_manager.get_last_button()
    draw = view_manager.get_draw()
    
    # Log button presses for debugging
    if button is not None:
        try:
            log_error(f"BUTTON: Detected button={button}")
        except:
            pass
    
    # Handle back button
    if button in (BUTTON_LEFT, BUTTON_BACK):
        input_manager.reset()
        # If showing error, exit error display
        if _chat_error_displaying:
            _chat_error_displaying = False
            _chat_error_lines = []
            _chat_error_scroll_offset = 0
            __reset_chat_state()
            try:
                log_error(f"ERROR: Exited error display")
            except:
                pass
            return
        # If in input mode, cancel input
        if _chat_waiting_for_input:
            _chat_input_text = ""
            _chat_waiting_for_input = False
            return
        __reset_chat_state()
        view_manager.back()
        return
    
    # Handle scroll buttons if showing error (before other button handlers)
    if _chat_error_displaying:
        if button == BUTTON_DOWN:  # Scroll down
            input_manager.reset()
            max_lines = len(_chat_error_lines)
            max_visible = 25  # Approximate lines visible on screen
            if _chat_error_scroll_offset + max_visible < max_lines:
                _chat_error_scroll_offset += 1
                try:
                    log_error(f"SCROLL: Down to offset {_chat_error_scroll_offset}")
                except:
                    pass
            return
        elif button == BUTTON_UP:  # Scroll up
            input_manager.reset()
            if _chat_error_scroll_offset > 0:
                _chat_error_scroll_offset -= 1
                try:
                    log_error(f"SCROLL: Up to offset {_chat_error_scroll_offset}")
                except:
                    pass
            return
    
    # Handle center/right button - start new question
    if button in (BUTTON_RIGHT, BUTTON_CENTER):
        input_manager.reset()
        
        # If showing error, allow retry
        if _chat_error_displaying:
            _chat_error_displaying = False
            _chat_error_lines = []
            _chat_error_scroll_offset = 0
            _chat_waiting_for_input = True
            _chat_input_text = ""
            return
        
        # If we're displaying a result, start new question
        if _chat_displaying_result:
            __reset_chat_state()
            _chat_waiting_for_input = True
            _chat_input_text = ""  # Reset input text
            return
        
        # If waiting for input, handle text input submission
        if _chat_waiting_for_input:
            try:
                log_error(f"BUTTON: CENTER pressed, waiting_for_input=True, input_text='{_chat_input_text}'")
            except:
                pass
            
            # If there's input text, submit it
            if _chat_input_text and _chat_input_text.strip():
                _chat_user_input = _chat_input_text.strip()
                _chat_input_text = ""
                _chat_waiting_for_input = False
                _chat_request_in_progress = True
                
                try:
                    log_error(f"SUBMIT: Sending question: {_chat_user_input}")
                except:
                    pass
                
                # Start API request
                try:
                    reply = ask_model(_chat_user_input, _chat_history)
                    _chat_last_reply = reply
                    _chat_displaying_result = True
                    _chat_request_in_progress = False
                except Exception as e:
                    # Log error to file
                    try:
                        log_error(f"UI ERROR: {type(e).__name__}: {str(e)}")
                    except:
                        pass
                    
                    # Set up scrollable error display
                    error_msg = str(e)
                    error_type = type(e).__name__
                    
                    # Build display text with word wrapping
                    display_lines = ["API ERROR:", "", f"Type: {error_type}", ""]
                    
                    # Split error message into lines that fit on screen
                    words = error_msg.split()
                    current_line = ""
                    max_width = 30  # Characters per line
                    
                    for word in words:
                        if len(current_line) + len(word) + 1 <= max_width:
                            current_line += (" " if current_line else "") + word
                        else:
                            if current_line:
                                display_lines.append(current_line)
                            current_line = word
                    if current_line:
                        display_lines.append(current_line)
                    
                    display_lines.extend(["", "Check /error_log.txt"])
                    
                    # Store error lines and reset scroll
                    global _chat_error_displaying, _chat_error_lines, _chat_error_scroll_offset
                    _chat_error_lines = display_lines
                    _chat_error_scroll_offset = 0
                    _chat_error_displaying = True
                    
                    # Reset other states
                    _chat_request_in_progress = False
                    _chat_displaying_result = False
                    _chat_waiting_for_input = False
                    return
            else:
                # No input text yet - this shouldn't happen if display section set it
                # But just in case, set it now
                _chat_input_text = "Hello, how are you?"
                try:
                    log_error(f"INPUT: No input text, setting default")
                except:
                    pass
                return
        else:
            # Initial state (or after error) - start waiting for input
            _chat_waiting_for_input = True
            _chat_input_text = ""  # Will be set to default in display section
            try:
                log_error(f"BUTTON: CENTER pressed from initial state, setting waiting_for_input=True")
            except:
                pass
            return
    
    # Display result if available
    if _chat_displaying_result and _chat_last_reply:
        # Show conversation history and latest reply
        display_text = "You: " + _chat_user_input + "\n\n"
        display_text += "AI: " + _chat_last_reply + "\n\n"
        display_text += "Press CENTER for new question\n"
        display_text += "Press LEFT to go back"
        
        draw.clear(Vector(0, 0), draw.size, view_manager.get_background_color())
        draw.text(Vector(0, 5), display_text, view_manager.get_foreground_color())
        draw.swap()
        return
    
    # Show thinking indicator if request in progress
    if _chat_request_in_progress:
        draw.clear(Vector(0, 0), draw.size, view_manager.get_background_color())
        draw.text(Vector(5, 5), "Thinking...")
        draw.swap()
        return
    
    # Show input screen if waiting for input
    if _chat_waiting_for_input:
        # For now, use a simple test question since keypad input is complex
        # TODO: Implement proper keypad text input
        if not _chat_input_text:
            # Use a default test question for now
            _chat_input_text = "Hello, how are you?"
            try:
                log_error(f"INPUT: Set default question: {_chat_input_text}")
            except:
                pass
        
        display_text = "Question:\n\n"
        display_text += _chat_input_text
        display_text += "\n\nCENTER: Send this\nLEFT: Cancel"
        
        draw.clear(Vector(0, 0), draw.size, view_manager.get_background_color())
        draw.text(Vector(5, 5), display_text, view_manager.get_foreground_color())
        draw.swap()
        return
    
    # Show error display if in error mode
    if _chat_error_displaying:
        from picoware.system.vector import Vector
        draw.clear(Vector(0, 0), draw.size, view_manager.get_background_color())
        
        # Calculate which lines to show based on scroll offset
        max_visible = 25  # Approximate lines visible on screen
        start_line = _chat_error_scroll_offset
        end_line = min(start_line + max_visible, len(_chat_error_lines))
        
        # Display visible lines
        y_pos = 5
        for i in range(start_line, end_line):
            if y_pos > 300:  # Screen limit
                break
            line = _chat_error_lines[i]
            draw.text(Vector(5, y_pos), line, view_manager.get_foreground_color())
            y_pos += 12
        
        # Show scroll indicators on right side
        if start_line > 0:
            draw.text(Vector(220, 5), "▲", view_manager.get_foreground_color())
        if end_line < len(_chat_error_lines):
            draw.text(Vector(220, 295), "▼", view_manager.get_foreground_color())
        
        # Show controls at bottom (only once, no overlay)
        controls_y = 295
        if end_line >= len(_chat_error_lines):
            # At bottom, show controls
            draw.text(Vector(5, controls_y), "UP: Scroll | LEFT: Exit", view_manager.get_foreground_color())
        elif start_line == 0:
            # At top, show controls
            draw.text(Vector(5, controls_y), "DOWN: Scroll | LEFT: Exit", view_manager.get_foreground_color())
        else:
            # In middle, show both
            draw.text(Vector(5, controls_y), "UP/DOWN: Scroll | LEFT: Exit", view_manager.get_foreground_color())
        
        draw.swap()
        return
    
    # Show initial prompt if nothing is happening
    if not _chat_waiting_for_input and not _chat_request_in_progress and not _chat_displaying_result:
        # Log state for debugging
        try:
            log_error(f"STATE: Showing ready screen (waiting={_chat_waiting_for_input}, in_progress={_chat_request_in_progress}, displaying={_chat_displaying_result})")
        except:
            pass
        
        draw.clear(Vector(0, 0), draw.size, view_manager.get_background_color())
        draw.text(Vector(5, 5), "PicoGPT Ready!")
        draw.text(Vector(5, 20), "Press CENTER to ask")
        draw.text(Vector(5, 35), "Press LEFT to go back")
        draw.swap()


def stop(view_manager) -> None:
    """Stop the app"""
    __reset_chat_state()
    
    global _chat_alert, _chat_history, _chat_last_reply
    
    if _chat_alert:
        del _chat_alert
        _chat_alert = None
    
    _chat_history = []
    _chat_last_reply = ""
