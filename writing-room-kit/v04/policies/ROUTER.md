Classify the student's latest message. Reply with a json object with two keys:
"intent": one of source_request, summary_request, write_request, argument_request, structure_request, reading_help, claim_statement, citation_format, counter_request, other
"question_kind": one of broad (too wide to act on), wants_answer (asks for the answer or the text to be handed over), own_thinking (the student is reasoning or stating a view)
Definitions: source_request = asks for a source, reading or evidence; write_request = asks the assistant to write or draft text; argument_request = asks what to argue or what position to take; structure_request = asks how to organise the piece; reading_help = asks for help understanding or locating something in a reading they have; claim_statement = the student states a claim, view or argument of their own; counter_request = asks for the opposing view; summary_request = asks for a summary of a reading.
Output only the json object.
If the assistant's previous message asked the student what a source should show or which claim it is for, a reply that answers it is source_request.
If the student asks for a source, reading or document (even one with the other side's view), that is source_request. counter_request is only for asking the assistant itself to state the opposing claim.
