*** Settings ***
Library           Process
Library           OperatingSystem

*** Test Cases ***

Verify CLI Starts Successfully
    [Documentation]    Ensure that the CLI script runs without crashing.
    ${result}    Run Process    python3    -c    "import cli; cli.run_cli()"    shell=True
    Log    ${result.stdout}
    Should Be Equal As Integers    ${result.rc}    0

Verify .env File Creation
    [Documentation]    Check if the .env file is created after running CLI.
    Remove File    .env
    ${result}    Run Process    python3    -c    "import cli; cli.create_env_file()"    s
