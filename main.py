from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional
import json
import os
from tools import AVAILABLE_TOOLS


import speech_recognition as sr 
from assistant_core import run_assistant, SYSTEM_PROMPT

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
) 

available_tools = AVAILABLE_TOOLS

class MyOutputFormat(BaseModel):
    step: str = Field(..., description="The ID of the step. Example: PLAN, OUTPUT, TOOL, etc")
    content: Optional[str] = Field(None, description="The optional string content for the step")
    tool: Optional[str] = Field(None, description="The ID of the tool to call.")
    input: Optional[str] = Field(None, description="The input params for the tool")

message_history = [
    { "role": "system", "content": SYSTEM_PROMPT },
]

r = sr.Recognizer() # Speech to Text

# Try to initialize microphone, but don't fail if PyAudio is not available
try:
    # Test if PyAudio is available by trying to create a microphone
    test_mic = sr.Microphone()
    mic_available = True
    print("🎤 Microphone available. You can use voice input.")
except (AttributeError, OSError) as e:
    print("🔇 PyAudio not found or microphone not available. Running in text-only mode.")
    mic_available = False

def get_voice_input():
    """Get voice input using speech recognition"""
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=2)
            print("🎤 Listening... (speak now)")
            audio = r.listen(source, timeout=10, phrase_time_limit=10)
            print("🔄 Processing speech...")
            text = r.recognize_google(audio)
            print(f"📝 You said: {text}")
            return text
    except sr.WaitTimeoutError:
        print("⏰ No speech detected. Switching to text input.")
        return input("Type your query: ")
    except sr.UnknownValueError:
        print("❓ Could not understand speech. Please try again or type your query.")
        return input("Type your query: ")
    except sr.RequestError as e:
        print(f"❌ Speech recognition error: {e}")
        return input("Type your query: ")
    except Exception as e:
        print(f"❌ Microphone error: {e}")
        return input("Type your query: ")

while True:
    if mic_available:
        print("\n" + "="*50)
        print("🎙️ Voice mode: Speak your request or press Ctrl+C for text mode")
        try:
            user_query = get_voice_input()
        except KeyboardInterrupt:
            print("\n⌨️ Switching to text input...")
            user_query = input("Type your query: ")
    else:
        user_query = input("Type your query: ")
    
    message_history.append({ "role": "user", "content": user_query })

    while True:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=message_history,
                response_format={
                    "type": "json_schema", 
                    "json_schema": {
                        "name": "MyOutputFormat",
                        "schema": MyOutputFormat.model_json_schema()
                    }
                }
            )

            raw_result = response.choices[0].message.content
            message_history.append({"role": "assistant", "content": raw_result})

            # Parse the JSON response manually
            try:
                parsed_result = json.loads(raw_result)
                
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Failed to parse AI response as JSON: {e}")
                print(f"Raw response: {raw_result}")
                continue
                
        except Exception as e:
            print(f"API Error: {e}")
            continue

        if parsed_result.get("step") == "START":
            print("🔥", parsed_result.get("content", ""))
            continue

        if parsed_result.get("step") == "TOOL":
            tool_to_call = parsed_result.get("tool", "")
            tool_input = parsed_result.get("input", "")
            print(f"🛠️: {tool_to_call} ({tool_input})")

            try:
                # Validate tool exists
                if tool_to_call not in available_tools:
                    tool_response = f"Error: Tool '{tool_to_call}' not found. Available tools: {list(available_tools.keys())}"
                else:
                    # Parse tool input based on tool type
                    if tool_to_call == "create_file":
                        # Split input into file_path and content
                        if not tool_input:
                            tool_response = "Error: No input provided for create_file"
                        else:
                            lines = tool_input.split('\n', 1)
                            file_path = lines[0].strip()
                            content = lines[1] if len(lines) > 1 else ""
                            
                            if not file_path:
                                tool_response = "Error: No file path provided"
                            else:
                                print(f"Creating file: {file_path} with {len(content)} characters")
                                tool_response = available_tools[tool_to_call](file_path, content)
                    elif tool_to_call == "write_file":
                        # Split input into file_path and content
                        if not tool_input:
                            tool_response = "Error: No input provided for write_file"
                        else:
                            lines = tool_input.split('\n', 1)
                            file_path = lines[0].strip()
                            content = lines[1] if len(lines) > 1 else ""
                            
                            if not file_path:
                                tool_response = "Error: No file path provided"
                            else:
                                print(f"Writing to file: {file_path} with {len(content)} characters")
                                tool_response = available_tools[tool_to_call](file_path, content)
                    else:
                        # For single-argument tools like read_file, analyze_code, run_command
                        if not tool_input:
                            tool_response = f"Error: No input provided for {tool_to_call}"
                        else:
                            tool_response = available_tools[tool_to_call](tool_input)
            
            except Exception as e:
                tool_response = f"Error executing tool {tool_to_call}: {str(e)}"
                print(f"Tool execution error: {e}")

            print(f"🛠️: {tool_to_call} = {tool_response}")
            message_history.append({ "role": "developer", "content": json.dumps(
                { "step": "OBSERVE", "tool": tool_to_call, "input": tool_input, "output": tool_response}
            ) })
            continue

        if parsed_result.get("step") == "PLAN":
            print("🧠", parsed_result.get("content", ""))
            continue

        if parsed_result.get("step") == "OUTPUT":
            print("🤖", parsed_result.get("content", ""))
            # asyncio.run(tts(speech=parsed_result.get("content", "")))
            break