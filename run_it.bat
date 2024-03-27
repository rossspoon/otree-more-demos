set OTREE_ADMIN_PASSWORD=b9rry@
set OTREE_AUTH_LEVEL=1

REM Comment out this line to turn on debug mode
set OTREE_PRODUCTION=1

REM Change this to control access
set OTREE_AUTH_LEVEL=STUDY
REM set OTREE_AUTH_LEVEL=DEMO

set SSE_NUM_ROUNDS=1
set SSE_NUM_PRACTICE_ROUNDS=1


set DATABASE_URL=postgres://vteconlab:econvt!@localhost/otreemore


REM otree resetdb
otree prodserver econlabhost18s:80
