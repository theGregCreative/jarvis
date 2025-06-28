import os

# Path to the directory where models are stored
model_dir = os.path.expanduser("~") + "/projects/jarvis/tts_models"  # Modify the path if necessary

# Print the directory for debugging purposes
print(f"Checking the contents of the directory: {model_dir}")

# Check if the directory exists
if os.path.exists(model_dir):
    # List all directories and files in the specified path
    print("\nContents of the model directory:")
    for item in os.listdir(model_dir):
        print(item)
else:
    print(f"The directory {model_dir} does not exist. Please check the path.")
