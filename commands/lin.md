Your job is simple: get the Linear issue details using the Linear MCP tool and present them clearly. The fomrat for querying issue is NS-[arguement].

```bash
# Get the issue number from arguments
! ISSUE_NUM=$(echo "$ARGUMENTS" | tr -d ' ')
