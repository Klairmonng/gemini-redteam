# Run this in the terminal where you set $env:GEMINI_API_KEY and $env:OPENAI_API_KEY.
# It saves them for your Windows account, so new terminals and the project scripts find them.
foreach ($name in "GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY") {
    $value = [Environment]::GetEnvironmentVariable($name, "Process")
    if ($value) {
        [Environment]::SetEnvironmentVariable($name, $value, "User")
        "Saved $name"
    } else {
        "Not set in this terminal, skipped: $name"
    }
}
