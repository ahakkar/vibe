*** Settings ***
Library    BuiltIn
Library    Process
Library    backend.service1.src.stt  # Importing directly from stt.py

*** Variables ***
${DEVICE_INDEX}    0  # Change if needed

*** Test Cases ***

Initialize SpeechToTextService
    [Documentation]  Test that the SpeechToTextService can be initialized without errors.
    ${stt_service}=  Evaluate  SpeechToTextService()  modules=backend.service1.src.stt.py
    Should Not Be Empty  ${stt_service}

Process Empty Audio Data
    [Documentation]  Test that processing empty audio data does not cause errors.
    ${stt_service}=  Evaluate  SpeechToTextService()  modules=backend.service1.src.stt.py
    ${empty_audio_data}=  Create List  # Empty audio data
    ${transcription}=  Run Keyword  ${stt_service.process_audio}  ${empty_audio_data}
    Should Be Empty  ${transcription}
