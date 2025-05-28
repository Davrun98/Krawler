# Krawler
 K - Developer challenge (FST2)

 To Do:
- add output functionality to orchestrator.py
- add entrypoint
- add unit tests
- resolve issues with path filtering in processor.py
- readability refactor (think: junior friendly)
- populate readme
- complete section 2

Trade-offs:
In order to make the project completable some corners were cut:
- relative links are not supported by the processor
- backend is accessed as a cli tool with arguments rather than httpServer
- backend does not have effective logging / error handling
- some unit tests are simplified and therefor less reliable / effective
- conventions are somewhat inconsistent across the code