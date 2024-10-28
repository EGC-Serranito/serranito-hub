#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m' 
NC='\033[0m' 

if [ ! -d ".git" ]; then
  echo -e "${RED}ERROR: You are not in the root directory of a Git repository.${NC}"
  exit 1
fi

 # Commit messages hook validation
 
HOOK_PATH=".git/hooks/commit-msg"

if [ -f "$HOOK_PATH" ]; then
  echo -e "${YELLOW}WARNING: The commit-msg hook already exists. No changes were made.${NC}"
else
  cat > "$HOOK_PATH" << 'EOF'
#!/bin/sh

commit_message=$(cat "$1")

if ! echo "$commit_message" | grep -Eq '^(feat|fix|docs|test|chore|ci|style|refactor|revert): [a-z]+ '; then
  echo "\033[0;31mERROR: The commit message does not follow the required format:\033[0m"
  echo "Format: <type>: <imperative_verb> message content"
  echo "Where type can be: \033[1;33mfeat, fix, docs, test, chore, ci, style, refactor, revert\033[0m"
  echo "Example: \033[1;33mfeat: implement email validation on user registration\033[0m"
  exit 1
fi
EOF

  chmod +x "$HOOK_PATH"
  echo -e "${GREEN}commit-msg hook successfully created in .git/hooks/commit-msg.${NC}"
fi

 # Python dependencies installation
 
if [ -f "requirements.txt" ]; then
  echo -e "${NC}requirements.txt found. Installing Python dependencies...${NC}"

  if pip install -r requirements.txt > /dev/null 2>&1; then
    echo -e "${GREEN}Python dependencies installed successfully.${NC}"
  else
    echo -e "${RED}ERROR: Failed to install some Python dependencies. Check requirements.txt.${NC}"
  fi
else
  echo -e "${YELLOW}WARNING: No requirements.txt found. Skipping Python dependencies installation.${NC}"
fi

