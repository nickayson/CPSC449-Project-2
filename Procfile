# game1: hypercorn game --reload --debug --bind game.local.gd:5100 --access-logfile - --error-logfile - --log-level DEBUG 
# game2: hypercorn game --reload --debug --bind game.local.gd:5200 --access-logfile - --error-logfile - --log-level DEBUG 
# game3: hypercorn game --reload --debug --bind game.local.gd:5300 --access-logfile - --error-logfile - --log-level DEBUG 
user: hypercorn user --reload --debug --bind user.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG
primary: ./bin/litefs -config ./etc/primary.yml
secondary: ./bin/litefs -config ./etc/secondary.yml
third: ./bin/litefs -config ./etc/third.yml