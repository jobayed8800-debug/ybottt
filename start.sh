
import os

# Create data directory placeholder
os.makedirs('/mnt/agents/output/data', exist_ok=True)

with open('/mnt/agents/output/data/.gitkeep', 'w') as f:
    f.write('')

# Create a startup script
start_script = '''#!/bin/bash
# Free Fire Tournament Bot - Startup Script

echo "🎮 Starting Free Fire Tournament Bot..."

# Create data directory if not exists
mkdir -p data

# Check if config is set
if grep -q "YOUR_BOT_TOKEN_HERE" config.py; then
    echo "❌ ERROR: Please set your BOT_TOKEN in config.py"
    exit 1
fi

echo "✅ Configuration check passed"
echo "🚀 Starting services..."

# Start web server in background
echo "🌐 Starting Web Server..."
python web_server.py &
WEB_PID=$!

# Wait for web server
sleep 3

# Start bot
echo "🤖 Starting Telegram Bot..."
python bot.py &
BOT_PID=$!

echo ""
echo "✅ All services started!"
echo "🌐 Web Server PID: $WEB_PID"
echo "🤖 Bot PID: $BOT_PID"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $WEB_PID $BOT_PID; exit" INT
wait
'''

with open('/mnt/agents/output/start.sh', 'w') as f:
    f.write(start_script)

os.chmod('/mnt/agents/output/start.sh', 0o755)

# List all created files
print("📁 All created files:")
for root, dirs, files in os.walk('/mnt/agents/output'):
    level = root.replace('/mnt/agents/output', '').count(os.sep)
    indent = ' ' * 2 * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = ' ' * 2 * (level + 1)
    for file in files:
        filepath = os.path.join(root, file)
        size = os.path.getsize(filepath)
        print(f'{subindent}{file} ({size} bytes)')
