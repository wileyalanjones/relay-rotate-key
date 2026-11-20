# Decision Log 

1:15pm PT: Initial repo 
1:15pm PT: Look into redact.py to see issues
1:19pm PT: Redact doesn't work work with new lines or hyphens.
1:20pm PT: Correct AI for changing file without asking
1:22pm PT: Make file that shows basic failures on hyphens and newlines
1:23pm PT: Make Evidence file and add inputs and results. 
1:26pm PT: Correct AI on evidence file 
1:29pm PT: Check the Bear Section of the redact
1:32pm PT: Correct AI on Bearer Relay Key format
1:34pm PT: Add results to evidence file 
1:36pm PT: Write test file with unittests for redact.py
1:40pm PT: Start Unverified list with what kind of line break is the comment. Unknown with current information. 
1:43pm PT: Correct AI on verbosity of the tests. 
1:48pm PT: Write a new redact file.
1:50pm PT: Correct AI on redact file.
1:54pm PT: Added extra redacting on the second pattern with Bearer as precaution. 
1:55pm PT: trade off as new line character at end of the bearer section could redact the next word but worth it for safety.
1:57pm PT: Write the script file to run the tests against both redact files. 
2:00pm PT: Look at the review items 
2:04pm PT: Item 1 Make small script to see if secret would be available with PS
2:06pm PT: Item 2 redact is not safe as shown before.
2:10pm PT: Item 3 retry. Could be race condition but unsure. 
2:15pm PT: Argue with AI about whether there could be orphan keys.
2:20pm PT: Item 4 Jira comments are public to all customers so rejected
2:24pm PT: Item 5 --force flag reject with cavet in case there is something missing here. If it is redact file then there is no --force 
2:30pm PT: Add gitignore and delete "__pycache__" files from tracking
2:35pm PT: Completed Evidence file moving onto skill rewriting
2:40pm PT: Correcting 