#!/bin/bash

# Claude Code Status Line Script
# Displays: user@hostname:directory | git-branch | Model | Context Usage with Breakdown

# Read JSON input from stdin
input=$(cat)

# Extract values from JSON
model_name=$(echo "$input" | jq -r '.model.display_name')
current_dir=$(echo "$input" | jq -r '.workspace.current_dir')
total_input=$(echo "$input" | jq -r '.context_window.total_input_tokens // 0')
total_output=$(echo "$input" | jq -r '.context_window.total_output_tokens // 0')
context_size=$(echo "$input" | jq -r '.context_window.context_window_size // 0')

# Fixed costs (in tokens) - system overhead
FIXED_COSTS=35300  # System prompt (3.4k) + System tools (15.6k) + Memory files (6.3k) + MCP tools (10k)

# Calculate total tokens used (conversation + fixed overhead)
conversation_tokens=$((total_input + total_output))
total_tokens_with_overhead=$((conversation_tokens + FIXED_COSTS))

# Calculate percentage
if [ "$context_size" -gt 0 ]; then
    total_percentage=$((total_tokens_with_overhead * 100 / context_size))
else
    total_percentage=0
fi

# Function to shorten path with ~ for home directory
shorten_path() {
    local path="$1"
    local max_length=40

    # Replace home directory with ~
    path="${path/#$HOME/~}"

    # If still too long, truncate with ...
    if [[ ${#path} -gt $max_length ]]; then
        local len=${#path}
        local keep=$((max_length - 3))
        path="...${path:$((len - keep))}"
    fi

    echo "$path"
}

# Function to get git information
get_git_info() {
    local dir="$1"

    # Check if we're in a git repository (skip optional locks)
    if ! git -C "$dir" --no-optional-locks rev-parse --git-dir &>/dev/null; then
        return 1
    fi

    # Get branch name
    local branch=$(git -C "$dir" --no-optional-locks branch --show-current 2>/dev/null)
    if [[ -z "$branch" ]]; then
        branch=$(git -C "$dir" --no-optional-locks describe --tags --exact-match 2>/dev/null || echo "detached")
    fi

    # Check git status for dirty state
    local status_output=$(git -C "$dir" --no-optional-locks status --porcelain 2>/dev/null)
    local git_status=""

    if [[ -z "$status_output" ]]; then
        git_status="✓"  # Clean
    else
        git_status="●"  # Dirty
    fi

    printf " \033[2m|\033[0m \033[36m%s\033[0m \033[2m%s\033[0m" "$branch" "$git_status"
}

# Function to format token count
format_tokens() {
    local tokens="$1"

    # Convert to number (remove any non-numeric characters)
    tokens=$(echo "$tokens" | sed 's/[^0-9]//g')

    # Handle empty or zero
    if [[ -z "$tokens" ]] || [[ "$tokens" -eq 0 ]]; then
        echo "0k"
        return
    fi

    # Calculate thousands with one decimal
    local thousands=$(echo "scale=1; $tokens / 1000" | bc 2>/dev/null || echo "0")

    # Remove trailing .0 if present
    thousands=$(echo "$thousands" | sed 's/\.0$//')

    echo "${thousands}k"
}

# Build the status line
shortened_dir=$(shorten_path "$current_dir")

# Start with shell-like prompt: user@hostname:directory
printf "\033[32m%s@%s\033[0m:\033[34m%s\033[0m" "$(whoami)" "$(hostname -s)" "$shortened_dir"

# Add git info if available
git_info=$(get_git_info "$current_dir")
if [[ $? -eq 0 ]]; then
    printf "%s" "$git_info"
fi

# Add model info
printf " \033[2m|\033[0m \033[35m%s\033[0m" "$model_name"

# Format token values
total_formatted=$(format_tokens "$total_tokens_with_overhead")
context_formatted=$(format_tokens "$context_size")

# Add simple context window usage: total/max (percentage%)
printf " \033[2m|\033[0m \033[33m%s/%s\033[0m \033[2m(%s%%)\033[0m" "$total_formatted" "$context_formatted" "$total_percentage"

# End with newline
echo