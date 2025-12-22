# Environment setup for Antigravity Agent

# User specific environment (from original .bashrc)
if ! [[ "$PATH" =~ "$HOME/.local/bin:$HOME/bin:" ]]; then
    PATH="$HOME/.local/bin:$HOME/bin:$PATH"
fi

# LM Studio CLI
export PATH="$PATH:/home/mohan/.lmstudio/bin"

export PATH
