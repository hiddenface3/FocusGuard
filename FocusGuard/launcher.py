import sys
import traceback
import main

try:
    main.main()
except Exception as e:
    with open("crash.log", "w", encoding="utf-8") as f:
        traceback.print_exc(file=f)
