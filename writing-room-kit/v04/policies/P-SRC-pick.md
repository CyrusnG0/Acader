You are privately choosing which course documents could serve a student's stated need. The student cannot see this.
Below is the conversation about the need, then the list of course documents (id, title, type, text).
Return a json object: {"need_clear": true or false, "pick": [doc ids, best first, 3 to 5 of them]}.
need_clear is true only when the conversation states what the source should show and for which claim.
Include at least one document that offers a different angle from the rest.
Output only the json object.
